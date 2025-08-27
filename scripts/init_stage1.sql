-- EcoleHub Stage 1 Database Initialization
-- PostgreSQL 15 with UUID support

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create updated users table with UUID
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create children table with UUID references
CREATE TABLE children (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    class_name VARCHAR(10) NOT NULL CHECK (class_name IN ('M1','M2','M3','P1','P2','P3','P4','P5','P6')),
    birth_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- SEL: Services offered by parents
CREATE TABLE sel_services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    units_per_hour INTEGER DEFAULT 60, -- Standard: 60 units = 1 hour
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- SEL: Transactions between users
CREATE TABLE sel_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_user_id UUID NOT NULL REFERENCES users(id),
    to_user_id UUID NOT NULL REFERENCES users(id),
    service_id UUID REFERENCES sel_services(id),
    units INTEGER NOT NULL CHECK (units > 0),
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'completed', 'cancelled')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- SEL: User balances with Belgian limits
CREATE TABLE sel_balances (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    balance INTEGER DEFAULT 120, -- Initial: 120 units (2 hours credit)
    total_given INTEGER DEFAULT 0,
    total_received INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    -- Belgian SEL limits: -300 to +600 units
    CONSTRAINT balance_limits CHECK (balance >= -300 AND balance <= 600)
);

-- SEL: Service categories for organization
CREATE TABLE sel_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50), -- For frontend display
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_children_parent ON children(parent_id);
CREATE INDEX idx_sel_services_user ON sel_services(user_id);
CREATE INDEX idx_sel_services_category ON sel_services(category);
CREATE INDEX idx_sel_services_active ON sel_services(is_active);
CREATE INDEX idx_sel_transactions_from_user ON sel_transactions(from_user_id);
CREATE INDEX idx_sel_transactions_to_user ON sel_transactions(to_user_id);
CREATE INDEX idx_sel_transactions_status ON sel_transactions(status);
CREATE INDEX idx_sel_transactions_created ON sel_transactions(created_at DESC);

-- Trigger function for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_children_updated_at BEFORE UPDATE ON children
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sel_services_updated_at BEFORE UPDATE ON sel_services
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sel_transactions_updated_at BEFORE UPDATE ON sel_transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default SEL categories
INSERT INTO sel_categories (name, description, icon) VALUES
    ('garde', 'Garde d''enfants et baby-sitting', '👶'),
    ('devoirs', 'Aide aux devoirs et soutien scolaire', '📚'),
    ('transport', 'Transport scolaire et activités', '🚗'),
    ('cuisine', 'Préparation repas et aide cuisine', '🍽️'),
    ('bricolage', 'Petits travaux et réparations', '🔨'),
    ('jardinage', 'Entretien jardin et plantes', '🌱'),
    ('menage', 'Aide ménagère et nettoyage', '🧹'),
    ('courses', 'Courses et commissions', '🛒'),
    ('proposition', 'Proposition de nouveaux services', '💭'),
    ('autre', 'Autres services', '💡');

-- Create initial admin user (optional, for testing)
-- Password: admin123 (hashed with bcrypt)
INSERT INTO users (email, first_name, last_name, hashed_password, is_verified) VALUES
    ('admin@ndi.be', 'Admin', 'EcoleHub', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqyc/Zo/.VjLaU0LYaOlOta', true);

-- Create initial balance for admin
INSERT INTO sel_balances (user_id, balance) 
SELECT id, 120 FROM users WHERE email = 'admin@ndi.be';