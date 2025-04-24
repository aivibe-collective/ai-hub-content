-- Prompt Management System Tables

-- Prompt Templates Table
CREATE TABLE prompt_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_text TEXT NOT NULL,
    category VARCHAR(255),
    tags JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1,
    parent_id UUID REFERENCES prompt_templates(id),
    metadata JSONB
);

-- Create index on name
CREATE INDEX idx_prompt_templates_name ON prompt_templates(name);

-- Create index on category
CREATE INDEX idx_prompt_templates_category ON prompt_templates(category);

-- Create index on is_active
CREATE INDEX idx_prompt_templates_is_active ON prompt_templates(is_active);

-- Prompt Variables Table
CREATE TABLE prompt_variables (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID NOT NULL REFERENCES prompt_templates(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    default_value TEXT,
    required BOOLEAN DEFAULT FALSE,
    variable_type VARCHAR(50) DEFAULT 'string',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on template_id
CREATE INDEX idx_prompt_variables_template_id ON prompt_variables(template_id);

-- Prompt Usage Table
CREATE TABLE prompt_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID NOT NULL REFERENCES prompt_templates(id),
    prompt_id UUID REFERENCES prompt_logs(id),
    variables JSONB,
    rendered_prompt TEXT NOT NULL,
    model VARCHAR(255),
    temperature FLOAT,
    content_id VARCHAR(255) REFERENCES content_inventory(content_id) ON DELETE SET NULL,
    success BOOLEAN,
    metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id VARCHAR(255)
);

-- Create index on template_id
CREATE INDEX idx_prompt_usage_template_id ON prompt_usage(template_id);

-- Create index on prompt_id
CREATE INDEX idx_prompt_usage_prompt_id ON prompt_usage(prompt_id);

-- Create index on content_id
CREATE INDEX idx_prompt_usage_content_id ON prompt_usage(content_id);

-- Prompt Feedback Table
CREATE TABLE prompt_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usage_id UUID NOT NULL REFERENCES prompt_usage(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    feedback_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id VARCHAR(255)
);

-- Create index on usage_id
CREATE INDEX idx_prompt_feedback_usage_id ON prompt_feedback(usage_id);

-- Prompt Categories Table
CREATE TABLE prompt_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default categories
INSERT INTO prompt_categories (name, description) VALUES
('Content Generation', 'Prompts for generating main content'),
('Source Collection', 'Prompts for finding and evaluating sources'),
('Content Structuring', 'Prompts for organizing and structuring content'),
('Content Editing', 'Prompts for editing and improving content'),
('Content Review', 'Prompts for reviewing and evaluating content'),
('Content Summarization', 'Prompts for summarizing content');

-- Comments
COMMENT ON TABLE prompt_templates IS 'Stores prompt templates with versioning support';
COMMENT ON TABLE prompt_variables IS 'Stores variables used in prompt templates';
COMMENT ON TABLE prompt_usage IS 'Tracks usage of prompts and their performance';
COMMENT ON TABLE prompt_feedback IS 'Stores feedback on prompt effectiveness';
COMMENT ON TABLE prompt_categories IS 'Categorizes prompts by their purpose';
