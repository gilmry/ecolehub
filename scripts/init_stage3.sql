-- EcoleHub Stage 3 Database Schema
-- Extends Stage 2 with Shop and Education modules

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Stage 3: Shop Products (collaborative buying)
CREATE TABLE IF NOT EXISTS shop_products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    base_price DECIMAL(10,2) NOT NULL,
    image_url VARCHAR(500),
    printful_id VARCHAR(100),  -- For custom EcoleHub items
    category VARCHAR(50) NOT NULL,
    min_quantity INTEGER DEFAULT 10,  -- Minimum for group order
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Stage 3: Shop Interest (group buying system)
CREATE TABLE IF NOT EXISTS shop_interests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES shop_products(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 1,
    notes TEXT,  -- Special requirements, size, etc.
    status VARCHAR(20) DEFAULT 'interested' CHECK (status IN ('interested', 'confirmed', 'cancelled')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(product_id, user_id)
);

-- Stage 3: Shop Orders (when group threshold is met)
CREATE TABLE IF NOT EXISTS shop_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES shop_products(id),
    total_quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    mollie_payment_id VARCHAR(100),  -- Mollie payment reference
    printful_order_id VARCHAR(100),  -- Printful order reference
    status VARCHAR(30) DEFAULT 'pending' CHECK (status IN ('pending', 'payment_pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled')),
    estimated_delivery DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Stage 3: Individual order items (link users to group orders)
CREATE TABLE IF NOT EXISTS shop_order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES shop_orders(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    notes TEXT,
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'refunded')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Stage 3: Education Resources
CREATE TABLE IF NOT EXISTS education_resources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,  -- 'homework', 'calendar', 'forms', 'announcements'
    class_name VARCHAR(10),  -- For class-specific resources
    file_url VARCHAR(500),  -- MinIO file path
    file_type VARCHAR(50),  -- pdf, doc, image, etc.
    file_size INTEGER,  -- in bytes
    is_public BOOLEAN DEFAULT false,  -- Public or parent-only
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Stage 3: Resource Access (who can view what)
CREATE TABLE IF NOT EXISTS resource_access (
    resource_id UUID REFERENCES education_resources(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    access_type VARCHAR(20) DEFAULT 'read' CHECK (access_type IN ('read', 'write', 'admin')),
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (resource_id, user_id)
);

-- Performance indexes Stage 3
CREATE INDEX IF NOT EXISTS idx_shop_products_category ON shop_products(category);
CREATE INDEX IF NOT EXISTS idx_shop_products_active ON shop_products(is_active);
CREATE INDEX IF NOT EXISTS idx_shop_interests_product ON shop_interests(product_id);
CREATE INDEX IF NOT EXISTS idx_shop_interests_user ON shop_interests(user_id);
CREATE INDEX IF NOT EXISTS idx_shop_interests_status ON shop_interests(status);

CREATE INDEX IF NOT EXISTS idx_shop_orders_status ON shop_orders(status);
CREATE INDEX IF NOT EXISTS idx_shop_orders_created ON shop_orders(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_shop_order_items_order ON shop_order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_shop_order_items_user ON shop_order_items(user_id);

CREATE INDEX IF NOT EXISTS idx_education_resources_category ON education_resources(category);
CREATE INDEX IF NOT EXISTS idx_education_resources_class ON education_resources(class_name);
CREATE INDEX IF NOT EXISTS idx_education_resources_public ON education_resources(is_public);
CREATE INDEX IF NOT EXISTS idx_resource_access_user ON resource_access(user_id);

-- Triggers for updated_at Stage 3
CREATE TRIGGER update_shop_products_updated_at BEFORE UPDATE ON shop_products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_shop_orders_updated_at BEFORE UPDATE ON shop_orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_education_resources_updated_at BEFORE UPDATE ON education_resources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Sample shop products for EcoleHub
INSERT INTO shop_products (name, description, base_price, category, min_quantity, created_by) VALUES
('Cahier EcoleHub', 'Cahier ligné avec logo de l''école, 96 pages, format A4', 3.50, 'fournitures', 20, (SELECT id FROM users LIMIT 1)),
('T-shirt EcoleHub', 'T-shirt coton bio avec logo EcoleHub', 12.00, 'vetements', 15, (SELECT id FROM users LIMIT 1)),
('Agenda scolaire 2024-2025', 'Agenda personnalisé avec calendrier belge et logo école', 8.50, 'fournitures', 25, (SELECT id FROM users LIMIT 1)),
('Sac EcoleHub', 'Sac à dos résistant avec logo brodé EcoleHub', 25.00, 'vetements', 10, (SELECT id FROM users LIMIT 1)),
('Trousse EcoleHub', 'Trousse fermeture éclair avec nom école', 6.00, 'fournitures', 30, (SELECT id FROM users LIMIT 1));

-- Sample education resources
INSERT INTO education_resources (title, description, category, class_name, is_public, created_by) VALUES
('Calendrier scolaire 2024-2025', 'Calendrier officiel EcoleHub avec vacances belges', 'calendar', NULL, true, (SELECT id FROM users LIMIT 1)),
('Liste fournitures P1', 'Liste complète des fournitures scolaires pour la 1ère primaire', 'forms', 'P1', true, (SELECT id FROM users LIMIT 1)),
('Liste fournitures P2', 'Liste complète des fournitures scolaires pour la 2ème primaire', 'forms', 'P2', true, (SELECT id FROM users LIMIT 1)),
('Liste fournitures P3', 'Liste complète des fournitures scolaires pour la 3ème primaire', 'forms', 'P3', true, (SELECT id FROM users LIMIT 1)),
('Liste fournitures P4', 'Liste complète des fournitures scolaires pour la 4ème primaire', 'forms', 'P4', true, (SELECT id FROM users LIMIT 1)),
('Liste fournitures P5', 'Liste complète des fournitures scolaires pour la 5ème primaire', 'forms', 'P5', true, (SELECT id FROM users LIMIT 1)),
('Liste fournitures P6', 'Liste complète des fournitures scolaires pour la 6ème primaire', 'forms', 'P6', true, (SELECT id FROM users LIMIT 1)),
('Règlement intérieur EcoleHub', 'Règlement intérieur de l''EcoleHub', 'announcements', NULL, true, (SELECT id FROM users LIMIT 1)),
('Projet éducatif école', 'Présentation du projet pédagogique de l''EcoleHub', 'announcements', NULL, true, (SELECT id FROM users LIMIT 1));

-- Sample shop interests to show group buying concept
INSERT INTO shop_interests (product_id, user_id, quantity, notes) 
SELECT 
    p.id,
    u.id,
    CASE WHEN random() > 0.5 THEN 2 ELSE 1 END,
    CASE WHEN random() > 0.7 THEN 'Taille M' ELSE NULL END
FROM shop_products p 
CROSS JOIN users u 
WHERE p.name LIKE '%T-shirt%' 
LIMIT 5;