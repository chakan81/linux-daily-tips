-- Linux Daily Tips Database Schema Initialization
-- PostgreSQL 15 with JSONB support for flexible data storage

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For full-text search performance
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For JSONB indexing

-- Create database schema
CREATE SCHEMA IF NOT EXISTS linux_tips;
SET search_path TO linux_tips, public;

-- Enum types for better data integrity
CREATE TYPE difficulty_level AS ENUM ('beginner', 'intermediate', 'advanced');
CREATE TYPE draft_status AS ENUM ('draft', 'approved', 'rejected');
CREATE TYPE terminal_status AS ENUM ('active', 'terminated', 'expired');

-- Tips table - stores approved and published tips
CREATE TABLE tips (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    difficulty difficulty_level NOT NULL DEFAULT 'beginner',
    category JSONB NOT NULL DEFAULT '[]'::jsonb,
    publish_date DATE NOT NULL DEFAULT CURRENT_DATE,
    terminal_setup JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT true,
    view_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Admin users table - for authentication and authorization
CREATE TABLE admin_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_superuser BOOLEAN NOT NULL DEFAULT false,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Draft weeks table - stores LLM-generated weekly drafts
CREATE TABLE draft_weeks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    week_start_date DATE NOT NULL,
    status draft_status NOT NULL DEFAULT 'draft',
    generated_by VARCHAR(100) NOT NULL DEFAULT 'llm',
    approved_by UUID REFERENCES admin_users(id),
    approval_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP WITH TIME ZONE
);

-- Draft tips table - individual tips within a draft week
CREATE TABLE draft_tips (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    draft_week_id UUID NOT NULL REFERENCES draft_weeks(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 1 AND day_of_week <= 7),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    difficulty difficulty_level NOT NULL DEFAULT 'beginner',
    category JSONB NOT NULL DEFAULT '[]'::jsonb,
    terminal_setup JSONB NOT NULL DEFAULT '{}'::jsonb,
    llm_confidence_score DECIMAL(3,2) CHECK (llm_confidence_score >= 0 AND llm_confidence_score <= 1),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Terminal sessions table - track active terminal emulator sessions
CREATE TABLE terminal_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tip_id UUID REFERENCES tips(id) ON DELETE CASCADE,
    container_id VARCHAR(255),
    status terminal_status NOT NULL DEFAULT 'active',
    ip_address INET,
    user_agent TEXT,
    session_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '30 minutes'),
    terminated_at TIMESTAMP WITH TIME ZONE
);

-- Analytics events table - track user interactions
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL,
    tip_id UUID REFERENCES tips(id) ON DELETE SET NULL,
    session_id UUID,
    ip_address INET,
    user_agent TEXT,
    event_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance optimization
-- Tips table indexes
CREATE INDEX idx_tips_publish_date ON tips(publish_date DESC);
CREATE INDEX idx_tips_difficulty ON tips(difficulty);
CREATE INDEX idx_tips_is_active ON tips(is_active);
CREATE INDEX idx_tips_category_gin ON tips USING gin(category);
CREATE INDEX idx_tips_search ON tips USING gin(to_tsvector('english', title || ' ' || content));

-- Draft weeks indexes
CREATE INDEX idx_draft_weeks_status ON draft_weeks(status);
CREATE INDEX idx_draft_weeks_week_start ON draft_weeks(week_start_date);
CREATE UNIQUE INDEX idx_draft_weeks_unique_week ON draft_weeks(week_start_date) WHERE status != 'rejected';

-- Draft tips indexes
CREATE INDEX idx_draft_tips_week_id ON draft_tips(draft_week_id);
CREATE INDEX idx_draft_tips_day ON draft_tips(day_of_week);
CREATE UNIQUE INDEX idx_draft_tips_unique_day ON draft_tips(draft_week_id, day_of_week);

-- Admin users indexes
CREATE INDEX idx_admin_users_username ON admin_users(username);
CREATE INDEX idx_admin_users_email ON admin_users(email);
CREATE INDEX idx_admin_users_is_active ON admin_users(is_active);

-- Terminal sessions indexes
CREATE INDEX idx_terminal_sessions_tip_id ON terminal_sessions(tip_id);
CREATE INDEX idx_terminal_sessions_status ON terminal_sessions(status);
CREATE INDEX idx_terminal_sessions_expires_at ON terminal_sessions(expires_at);

-- Analytics events indexes
CREATE INDEX idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_events_tip_id ON analytics_events(tip_id);
CREATE INDEX idx_analytics_events_created_at ON analytics_events(created_at DESC);
CREATE INDEX idx_analytics_events_session_id ON analytics_events(session_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_tips_updated_at BEFORE UPDATE ON tips
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_admin_users_updated_at BEFORE UPDATE ON admin_users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to auto-expire terminal sessions
CREATE OR REPLACE FUNCTION cleanup_expired_terminal_sessions()
RETURNS void AS $$
BEGIN
    UPDATE terminal_sessions
    SET status = 'expired', terminated_at = CURRENT_TIMESTAMP
    WHERE status = 'active' AND expires_at < CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Views for common queries
-- Daily tip view with analytics
CREATE VIEW daily_tip_with_stats AS
SELECT
    t.*,
    COUNT(ae.id) FILTER (WHERE ae.event_type = 'tip_view') as view_count_today,
    COUNT(ts.id) FILTER (WHERE ts.status = 'active') as active_terminals
FROM tips t
LEFT JOIN analytics_events ae ON t.id = ae.tip_id AND ae.created_at::date = CURRENT_DATE
LEFT JOIN terminal_sessions ts ON t.id = ts.tip_id
WHERE t.is_active = true
GROUP BY t.id;

-- Weekly draft summary view
CREATE VIEW weekly_draft_summary AS
SELECT
    dw.*,
    COUNT(dt.id) as tip_count,
    AVG(dt.llm_confidence_score) as avg_confidence_score
FROM draft_weeks dw
LEFT JOIN draft_tips dt ON dw.id = dt.draft_week_id
GROUP BY dw.id;

-- Set default search path
ALTER DATABASE linux_daily_tips SET search_path TO linux_tips, public;

-- Grant permissions
GRANT USAGE ON SCHEMA linux_tips TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA linux_tips TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA linux_tips TO postgres;

-- Success message
\echo 'Linux Daily Tips database schema initialized successfully!'