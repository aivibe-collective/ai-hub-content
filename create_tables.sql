-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create content_inventory table
CREATE TABLE IF NOT EXISTS content_inventory (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  content_id text NOT NULL UNIQUE,
  section text,
  subsection text,
  title text,
  content_type text,
  status text DEFAULT 'Not Started',
  priority text,
  dependencies text,
  audience_technical_level text,
  audience_role text,
  audience_constraints text,
  primary_mission_pillar_1 text,
  primary_mission_pillar_2 text,
  secondary_mission_pillars text,
  smart_objectives text,
  practical_components text,
  estimated_dev_time text,
  required_expertise text,
  assigned_creator text,
  assigned_reviewers text,
  review_status text,
  platform_requirements text,
  notes text,
  metadata jsonb,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Create indexes for content_inventory
CREATE INDEX IF NOT EXISTS content_inventory_content_id_idx ON content_inventory (content_id);
CREATE INDEX IF NOT EXISTS content_inventory_section_idx ON content_inventory (section);
CREATE INDEX IF NOT EXISTS content_inventory_status_idx ON content_inventory (status);

-- Create prompt_logs table
CREATE TABLE IF NOT EXISTS prompt_logs (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id text NOT NULL,
  prompt_type text,
  prompt_text text,
  model text,
  temperature float,
  content_id text,
  user_id text,
  created_at timestamp with time zone DEFAULT now()
);

-- Create indexes for prompt_logs
CREATE INDEX IF NOT EXISTS prompt_logs_session_id_idx ON prompt_logs (session_id);
CREATE INDEX IF NOT EXISTS prompt_logs_content_id_idx ON prompt_logs (content_id);

-- Create generation_outputs table
CREATE TABLE IF NOT EXISTS generation_outputs (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  prompt_id uuid REFERENCES prompt_logs(id),
  output_text text,
  content_id text,
  status text DEFAULT 'completed',
  metadata jsonb,
  created_at timestamp with time zone DEFAULT now()
);

-- Create indexes for generation_outputs
CREATE INDEX IF NOT EXISTS generation_outputs_prompt_id_idx ON generation_outputs (prompt_id);
CREATE INDEX IF NOT EXISTS generation_outputs_content_id_idx ON generation_outputs (content_id);

-- Create content_files table
CREATE TABLE IF NOT EXISTS content_files (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  output_id uuid REFERENCES generation_outputs(id),
  content_type text,
  file_content text,
  created_at timestamp with time zone DEFAULT now()
);

-- Create index for content_files
CREATE INDEX IF NOT EXISTS content_files_output_id_idx ON content_files (output_id);

-- Create test_table (optional, for testing only)
CREATE TABLE IF NOT EXISTS test_table (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  test_id text NOT NULL UNIQUE,
  test_name text,
  test_data jsonb,
  created_at timestamp with time zone DEFAULT now()
);

-- Insert a test record into content_inventory
INSERT INTO content_inventory (content_id, section, subsection, title, content_type, status)
VALUES ('TEST-001', 'Test', 'Test Section', 'Test Content', 'Test', 'Not Started')
ON CONFLICT (content_id) DO NOTHING;

-- Output success message
SELECT 'Tables created successfully' as message;
