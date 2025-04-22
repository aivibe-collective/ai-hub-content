-- Create content_versions table
CREATE TABLE IF NOT EXISTS content_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id TEXT NOT NULL REFERENCES content_inventory(content_id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    content_text TEXT NOT NULL,
    model TEXT,
    temperature REAL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Add a unique constraint to ensure each content_id has unique version numbers
    UNIQUE(content_id, version_number)
);

-- Add indexes
CREATE INDEX IF NOT EXISTS content_versions_content_id_idx ON content_versions(content_id);
CREATE INDEX IF NOT EXISTS content_versions_version_number_idx ON content_versions(version_number);

-- Add RLS policies
ALTER TABLE content_versions ENABLE ROW LEVEL SECURITY;

-- Allow anyone to select from content_versions
CREATE POLICY content_versions_select_policy ON content_versions
    FOR SELECT USING (true);

-- Allow authenticated users to insert into content_versions
CREATE POLICY content_versions_insert_policy ON content_versions
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Allow authenticated users to update content_versions
CREATE POLICY content_versions_update_policy ON content_versions
    FOR UPDATE USING (auth.role() = 'authenticated');

-- Allow authenticated users to delete from content_versions
CREATE POLICY content_versions_delete_policy ON content_versions
    FOR DELETE USING (auth.role() = 'authenticated');

-- Add a comment to the table
COMMENT ON TABLE content_versions IS 'Stores version history of content items';
