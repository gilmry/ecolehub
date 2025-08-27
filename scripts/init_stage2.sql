-- EcoleHub Stage 2 Database Schema
-- Extends Stage 1 with Messaging and Events

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Stage 1 tables (users, children, SEL system) already exist
-- Adding Stage 2 tables only

-- Stage 2: Conversations for messaging
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200),
    type VARCHAR(20) NOT NULL CHECK (type IN ('direct', 'group', 'announcement', 'class')),
    class_name VARCHAR(10), -- For class-specific groups (M1, M2, P1, etc.)
    created_by UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Stage 2: Messages in conversations
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text' CHECK (message_type IN ('text', 'image', 'file', 'system')),
    edited_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Stage 2: Conversation participants
CREATE TABLE IF NOT EXISTS conversation_participants (
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    last_read_at TIMESTAMPTZ DEFAULT NOW(),
    is_admin BOOLEAN DEFAULT false,
    PRIMARY KEY (conversation_id, user_id)
);

-- Stage 2: Events (school events, parent meetings, activities)
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ,
    location VARCHAR(200),
    max_participants INTEGER,
    registration_required BOOLEAN DEFAULT false,
    registration_deadline TIMESTAMPTZ,
    event_type VARCHAR(50) DEFAULT 'general' CHECK (event_type IN ('general', 'class', 'school', 'parent_meeting', 'activity', 'celebration')),
    class_name VARCHAR(10), -- For class-specific events
    created_by UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Stage 2: Event participants/registrations
CREATE TABLE IF NOT EXISTS event_participants (
    event_id UUID REFERENCES events(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    registered_at TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'registered' CHECK (status IN ('registered', 'attended', 'cancelled')),
    notes TEXT,
    PRIMARY KEY (event_id, user_id)
);

-- Stage 2: User online status (Redis cache alternative)
CREATE TABLE IF NOT EXISTS user_status (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    is_online BOOLEAN DEFAULT false,
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    status_message VARCHAR(100),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance indexes for Stage 2
CREATE INDEX IF NOT EXISTS idx_conversations_type ON conversations(type);
CREATE INDEX IF NOT EXISTS idx_conversations_class ON conversations(class_name);
CREATE INDEX IF NOT EXISTS idx_conversations_created_by ON conversations(created_by);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversation_participants_user ON conversation_participants(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_participants_conversation ON conversation_participants(conversation_id);

CREATE INDEX IF NOT EXISTS idx_events_start_date ON events(start_date);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_class ON events(class_name);
CREATE INDEX IF NOT EXISTS idx_events_created_by ON events(created_by);
CREATE INDEX IF NOT EXISTS idx_events_active ON events(is_active);

CREATE INDEX IF NOT EXISTS idx_event_participants_event ON event_participants(event_id);
CREATE INDEX IF NOT EXISTS idx_event_participants_user ON event_participants(user_id);
CREATE INDEX IF NOT EXISTS idx_event_participants_status ON event_participants(status);

-- Updated_at triggers for Stage 2 tables
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_status_updated_at BEFORE UPDATE ON user_status
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Default conversations for Belgian classes
INSERT INTO conversations (name, type, class_name, created_by) 
SELECT 
    'Classe ' || class_name,
    'class',
    class_name,
    (SELECT id FROM users LIMIT 1)
FROM (VALUES ('M1'), ('M2'), ('M3'), ('P1'), ('P2'), ('P3'), ('P4'), ('P5'), ('P6')) AS classes(class_name)
ON CONFLICT DO NOTHING;

-- General school announcement conversation
INSERT INTO conversations (name, type, created_by)
SELECT 
    'Annonces École Notre-Dame Immaculée',
    'announcement', 
    (SELECT id FROM users LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM conversations WHERE type = 'announcement' AND name LIKE '%Notre-Dame%');

-- Sample school events (École Notre-Dame Immaculée specific)
INSERT INTO events (title, description, start_date, end_date, location, event_type, registration_required, max_participants, created_by)
SELECT 
    'Spaghetti de Saint-Nicolas',
    'Repas convivial traditionnel organisé par l''école pour célébrer la Saint-Nicolas. Spaghetti, boissons et animations pour toute la famille.',
    '2024-12-06 18:00:00'::timestamptz,
    '2024-12-06 21:00:00'::timestamptz,
    'Réfectoire école',
    'celebration',
    true,
    120,
    (SELECT id FROM users LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM events WHERE title LIKE '%Spaghetti%Saint%');

INSERT INTO events (title, description, start_date, end_date, location, event_type, registration_required, created_by)
SELECT 
    'Fancy Fair Notre-Dame Immaculée 2025',
    'Grande fête annuelle de l''école avec stands, tombola, jeux, restauration et spectacles des enfants',
    '2025-05-17 10:00:00'::timestamptz,
    '2025-05-17 18:00:00'::timestamptz,
    'Cour de récréation + Salle polyvalente',
    'celebration',
    false,
    300,
    (SELECT id FROM users LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM events WHERE title LIKE '%Fancy Fair%');

INSERT INTO events (title, description, start_date, end_date, location, event_type, registration_required, created_by)
SELECT 
    'Réunion de rentrée 2024-2025',
    'Réunion d''information pour les parents - présentation équipe éducative, projets et calendrier',
    '2024-09-10 19:00:00'::timestamptz,
    '2024-09-10 21:00:00'::timestamptz,
    'Salle polyvalente',
    'parent_meeting',
    true,
    80,
    (SELECT id FROM users LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM events WHERE title LIKE '%Réunion%rentrée%');

INSERT INTO events (title, description, start_date, end_date, location, event_type, class_name, registration_required, created_by)
SELECT 
    'Sortie P6 - Classes vertes',
    'Séjour de 3 jours en classes vertes pour les P6 - Ardennes belges',
    '2025-03-24 08:00:00'::timestamptz,
    '2025-03-26 17:00:00'::timestamptz,
    'Houffalize, Ardennes',
    'class',
    'P6',
    true,
    (SELECT id FROM users LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM events WHERE title LIKE '%Classes vertes%');

INSERT INTO events (title, description, start_date, end_date, location, event_type, registration_required, created_by)
SELECT 
    'Carnaval de l''école',
    'Défilé des enfants déguisés dans la cour, concours de costumes et goûter festif',
    '2025-02-28 14:00:00'::timestamptz,
    '2025-02-28 16:30:00'::timestamptz,
    'Cour de récréation',
    'celebration',
    false,
    200,
    (SELECT id FROM users LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM events WHERE title LIKE '%Carnaval%');

INSERT INTO events (title, description, start_date, end_date, location, event_type, registration_required, created_by)
SELECT 
    'Réunion parents P6 - CEB',
    'Information sur le Certificat d''Études de Base et préparation des élèves',
    '2025-01-15 19:30:00'::timestamptz,
    '2025-01-15 21:00:00'::timestamptz,
    'Classe P6',
    'parent_meeting',
    true,
    25,
    (SELECT id FROM users LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM events WHERE title LIKE '%CEB%');