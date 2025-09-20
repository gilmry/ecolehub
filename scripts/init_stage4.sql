-- EcoleHub Stage 4 Database Initialization
-- Full stack with shop, education, analytics and multilingual

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Core Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    role VARCHAR(50) DEFAULT 'parent',
    preferred_language VARCHAR(5) DEFAULT 'fr-BE',
    -- Stage 4 privacy/consents
    consent_version VARCHAR(20),
    consented_at TIMESTAMPTZ,
    privacy_locale VARCHAR(10),
    consent_withdrawn_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ,
    consent_analytics_platform BOOLEAN DEFAULT false,
    consent_comms_operational BOOLEAN DEFAULT true,
    consent_comms_newsletter BOOLEAN DEFAULT false,
    consent_comms_shop_marketing BOOLEAN DEFAULT false,
    consent_cookies_preference BOOLEAN DEFAULT false,
    consent_photos_publication BOOLEAN DEFAULT false,
    consent_data_share_thirdparties BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Children with Belgian classes
CREATE TABLE children (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    class_name VARCHAR(10) CHECK (class_name IN ('M1','M2','M3','P1','P2','P3','P4','P5','P6')),
    birth_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User-Children relationships
CREATE TABLE user_children (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    child_id UUID REFERENCES children(id) ON DELETE CASCADE,
    relationship VARCHAR(50) DEFAULT 'parent',
    PRIMARY KEY (user_id, child_id)
);

-- SEL Services (Stage 1+)
CREATE TABLE sel_services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    units_per_hour INTEGER DEFAULT 60,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- SEL Transactions
CREATE TABLE sel_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_user_id UUID REFERENCES users(id),
    to_user_id UUID REFERENCES users(id),
    service_id UUID REFERENCES sel_services(id),
    units INTEGER NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- SEL Balances with Belgian constraints
CREATE TABLE sel_balances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE REFERENCES users(id),
    balance INTEGER DEFAULT 120,
    total_given INTEGER DEFAULT 0,
    total_received INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT balance_limits CHECK (balance >= -300 AND balance <= 600)
);

-- Messages & Conversations (Stage 2+)
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200),
    type VARCHAR(20) CHECK (type IN ('direct', 'group', 'announcement')),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE conversation_participants (
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (conversation_id, user_id)
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Events (Stage 2+)
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ,
    location VARCHAR(200),
    max_participants INTEGER,
    registration_deadline TIMESTAMPTZ,
    price DECIMAL(10,2) DEFAULT 0,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE event_registrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID REFERENCES events(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    child_id UUID REFERENCES children(id),
    registered_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT
);

-- Shop Products (Stage 3+)
CREATE TABLE shop_products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    base_price DECIMAL(10,2) NOT NULL,
    vat_rate DECIMAL(5,2) DEFAULT 21.00,
    min_quantity INTEGER DEFAULT 10,
    printful_id VARCHAR(100),
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Shop Interest tracking
CREATE TABLE shop_interests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES shop_products(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 1,
    size VARCHAR(20),
    color VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(product_id, user_id)
);

-- Educational Resources (Stage 3+)
CREATE TABLE educational_resources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    class_name VARCHAR(10),
    file_path VARCHAR(500),
    file_size INTEGER,
    file_type VARCHAR(50),
    is_public BOOLEAN DEFAULT false,
    uploaded_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Analytics (Stage 4)
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_sel_services_user ON sel_services(user_id);
CREATE INDEX idx_sel_services_category ON sel_services(category);
CREATE INDEX idx_sel_transactions_users ON sel_transactions(from_user_id, to_user_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at DESC);
CREATE INDEX idx_events_date ON events(start_date);
CREATE INDEX idx_shop_products_active ON shop_products(is_active);
CREATE INDEX idx_shop_interests_product ON shop_interests(product_id);
CREATE INDEX idx_educational_resources_class ON educational_resources(class_name);
CREATE INDEX idx_analytics_user_event ON analytics_events(user_id, event_type);

-- Update timestamp triggers
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_children_updated_at BEFORE UPDATE ON children
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_sel_services_updated_at BEFORE UPDATE ON sel_services
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON events
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_shop_products_updated_at BEFORE UPDATE ON shop_products
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_educational_resources_updated_at BEFORE UPDATE ON educational_resources
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Insert demo data
-- All passwords: jules20220902 (hashed with bcrypt)
INSERT INTO users (email, first_name, last_name, hashed_password, role) VALUES
('admin@ecolehub.be', 'Admin', 'EcoleHub', '$2b$12$SaTEtnlb2yOYXZl1Qy9Nb.MKbJnrePjpygTteWx0bWNByGnT5CC.e', 'admin'),
('direction@ecolehub.be', 'Direction', 'EcoleHub', '$2b$12$SaTEtnlb2yOYXZl1Qy9Nb.MKbJnrePjpygTteWx0bWNByGnT5CC.e', 'direction'),
('parent1@example.be', 'Marie', 'Dupont', '$2b$12$SaTEtnlb2yOYXZl1Qy9Nb.MKbJnrePjpygTteWx0bWNByGnT5CC.e', 'parent'),
('parent2@example.be', 'Jean', 'Martin', '$2b$12$SaTEtnlb2yOYXZl1Qy9Nb.MKbJnrePjpygTteWx0bWNByGnT5CC.e', 'parent');

-- Create default conversations
INSERT INTO conversations (name, type, created_by) VALUES
('Annonces Officielles', 'announcement', (SELECT id FROM users WHERE email = 'admin@ecolehub.be')),
('Groupe M1', 'group', (SELECT id FROM users WHERE email = 'admin@ecolehub.be')),
('Groupe P1', 'group', (SELECT id FROM users WHERE email = 'admin@ecolehub.be')),
('Groupe P6', 'group', (SELECT id FROM users WHERE email = 'admin@ecolehub.be'));

-- Demo SEL services
INSERT INTO sel_services (user_id, title, description, category, units_per_hour) VALUES
((SELECT id FROM users WHERE email = 'parent1@example.be'), 'Aide aux devoirs', 'Soutien scolaire pour primaire', 'Education', 60),
((SELECT id FROM users WHERE email = 'parent2@example.be'), 'Garde d''enfants', 'Garde occasionnelle après école', 'Garde', 60);

-- Demo shop products
INSERT INTO shop_products (name, description, category, base_price, min_quantity) VALUES
('Cahier EcoleHub A4', 'Cahier ligné avec logo école', 'Fournitures', 2.50, 20),
('T-shirt EcoleHub', 'T-shirt coton bio avec logo', 'Vêtements', 12.00, 15),
('Trousse EcoleHub', 'Trousse scolaire personnalisée', 'Fournitures', 8.50, 10);

-- Demo events
INSERT INTO events (title, description, start_date, location, max_participants, price, created_by) VALUES
('Spaghetti Saint-Nicolas', 'Tradition annuelle avec spectacle des enfants', '2024-12-06 18:00:00+01', 'Réfectoire EcoleHub', 200, 12.00, (SELECT id FROM users WHERE email = 'admin@ecolehub.be')),
('Fancy Fair 2025', 'Fête de l''école avec stands et activités', '2025-05-17 14:00:00+02', 'Cour de récréation', 500, 0, (SELECT id FROM users WHERE email = 'admin@ecolehub.be'));

COMMIT;
