-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema
CREATE SCHEMA IF NOT EXISTS innovusx;

-- Documents table for knowledge base
CREATE TABLE IF NOT EXISTS innovusx.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding vector(1536),
    source VARCHAR(255),
    category VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_documents_embedding
ON innovusx.documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Audit logs table
CREATE TABLE IF NOT EXISTS innovusx.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    correlation_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    action VARCHAR(50) NOT NULL,
    resource VARCHAR(255) NOT NULL,
    operation VARCHAR(50) NOT NULL,
    user_id VARCHAR(100),
    api_key_id VARCHAR(100),
    ip_address VARCHAR(50),
    user_agent TEXT,
    input_hash VARCHAR(64),
    output_hash VARCHAR(64),
    model_version VARCHAR(20),
    parameters JSONB DEFAULT '{}',
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    latency_ms INTEGER,
    pii_detected BOOLEAN DEFAULT FALSE,
    pii_entities JSONB DEFAULT '[]',
    compliance_checks JSONB DEFAULT '[]',
    previous_hash VARCHAR(64),
    chain_hash VARCHAR(64)
);

-- Index for audit log queries
CREATE INDEX IF NOT EXISTS idx_audit_logs_correlation
ON innovusx.audit_logs (correlation_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp
ON innovusx.audit_logs (timestamp);

CREATE INDEX IF NOT EXISTS idx_audit_logs_action
ON innovusx.audit_logs (action);

-- API keys table
CREATE TABLE IF NOT EXISTS innovusx.api_keys (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    key_hash VARCHAR(64) NOT NULL UNIQUE,
    role VARCHAR(20) NOT NULL,
    rate_limit INTEGER DEFAULT 60,
    allowed_origins TEXT[] DEFAULT ARRAY['*'],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Experiments table for MLflow integration
CREATE TABLE IF NOT EXISTS innovusx.experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    run_id VARCHAR(50),
    model_version VARCHAR(20),
    parameters JSONB DEFAULT '{}',
    metrics JSONB DEFAULT '{}',
    status VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for documents table
DROP TRIGGER IF EXISTS update_documents_updated_at ON innovusx.documents;
CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON innovusx.documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Insert sample API keys
INSERT INTO innovusx.api_keys (id, name, key_hash, role, rate_limit, allowed_origins)
VALUES
    ('key_demo_001', 'Demo Widget', 'demo_hash', 'anonymous', 100, ARRAY['http://localhost:*', 'https://innovus-x.com']),
    ('key_user_001', 'User API Key', 'user_hash', 'user', 500, ARRAY['*']),
    ('key_admin_001', 'Admin API Key', 'admin_hash', 'admin', 1000, ARRAY['*'])
ON CONFLICT (id) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA innovusx TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA innovusx TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA innovusx TO postgres;
