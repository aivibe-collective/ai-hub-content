-- Reference Management System Tables

-- Reference Sources Table
CREATE TABLE IF NOT EXISTS reference_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    authors TEXT,
    publication_date TIMESTAMP WITH TIME ZONE,
    url TEXT,
    doi TEXT,
    publication_name TEXT,
    reference_type TEXT NOT NULL,
    content TEXT,
    abstract TEXT,
    keywords TEXT[],
    categories UUID[],
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by TEXT,
    metadata JSONB
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_reference_sources_title ON reference_sources (title);
CREATE INDEX IF NOT EXISTS idx_reference_sources_authors ON reference_sources (authors);
CREATE INDEX IF NOT EXISTS idx_reference_sources_reference_type ON reference_sources (reference_type);
CREATE INDEX IF NOT EXISTS idx_reference_sources_is_active ON reference_sources (is_active);

-- Reference Quality Assessment Table (CRAAP Test)
CREATE TABLE IF NOT EXISTS reference_quality (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reference_id UUID NOT NULL REFERENCES reference_sources(id) ON DELETE CASCADE,
    currency_score INTEGER CHECK (currency_score BETWEEN 1 AND 5),
    relevance_score INTEGER CHECK (relevance_score BETWEEN 1 AND 5),
    authority_score INTEGER CHECK (authority_score BETWEEN 1 AND 5),
    accuracy_score INTEGER CHECK (accuracy_score BETWEEN 1 AND 5),
    purpose_score INTEGER CHECK (purpose_score BETWEEN 1 AND 5),
    overall_score INTEGER GENERATED ALWAYS AS (
        (COALESCE(currency_score, 0) +
         COALESCE(relevance_score, 0) +
         COALESCE(authority_score, 0) +
         COALESCE(accuracy_score, 0) +
         COALESCE(purpose_score, 0)) /
        NULLIF(
            (CASE WHEN currency_score IS NOT NULL THEN 1 ELSE 0 END +
             CASE WHEN relevance_score IS NOT NULL THEN 1 ELSE 0 END +
             CASE WHEN authority_score IS NOT NULL THEN 1 ELSE 0 END +
             CASE WHEN accuracy_score IS NOT NULL THEN 1 ELSE 0 END +
             CASE WHEN purpose_score IS NOT NULL THEN 1 ELSE 0 END),
            0
        )
    ) STORED,
    assessment_notes TEXT,
    assessed_by TEXT,
    assessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for reference quality
CREATE INDEX IF NOT EXISTS idx_reference_quality_reference_id ON reference_quality(reference_id);
CREATE INDEX IF NOT EXISTS idx_reference_quality_overall_score ON reference_quality(overall_score);

-- Content References Junction Table
CREATE TABLE IF NOT EXISTS content_references (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id TEXT NOT NULL,
    reference_id UUID NOT NULL REFERENCES reference_sources(id) ON DELETE CASCADE,
    citation_key TEXT,
    citation_context TEXT,
    relevance_score INTEGER CHECK (relevance_score BETWEEN 1 AND 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(content_id, reference_id)
);

-- Create indexes for content references
CREATE INDEX IF NOT EXISTS idx_content_references_content_id ON content_references(content_id);
CREATE INDEX IF NOT EXISTS idx_content_references_reference_id ON content_references(reference_id);

-- Reference Categories Table
CREATE TABLE IF NOT EXISTS reference_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    parent_id UUID REFERENCES reference_categories(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for reference categories
CREATE INDEX IF NOT EXISTS idx_reference_categories_name ON reference_categories(name);

-- Reference Types Table
CREATE TABLE IF NOT EXISTS reference_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    required_fields JSONB DEFAULT '["title"]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default reference types
INSERT INTO reference_types (name, description, required_fields)
VALUES
    ('Article', 'Journal or magazine article', '["title", "authors", "publication_name"]'),
    ('Book', 'Book or e-book', '["title", "authors"]'),
    ('Website', 'Website or webpage', '["title", "url"]'),
    ('Report', 'Technical or research report', '["title", "authors"]'),
    ('Conference', 'Conference paper or proceedings', '["title", "authors", "publication_name"]'),
    ('Video', 'Video content', '["title", "url"]'),
    ('Podcast', 'Podcast episode', '["title", "url"]'),
    ('Social Media', 'Social media post', '["title", "url"]'),
    ('Interview', 'Interview transcript or recording', '["title", "authors"]'),
    ('Dataset', 'Dataset or database', '["title", "url"]'),
    ('Software', 'Software or application', '["title", "url"]'),
    ('Other', 'Other reference type', '["title"]')
ON CONFLICT (name) DO NOTHING;

-- Insert default reference categories
INSERT INTO reference_categories (name, description)
VALUES
    ('AI Technology', 'References about AI technology, algorithms, and implementations'),
    ('Business', 'References about business applications, strategy, and management'),
    ('Ethics', 'References about ethical considerations, guidelines, and frameworks'),
    ('Sustainability', 'References about environmental sustainability and responsible practices'),
    ('Inclusion', 'References about diversity, equity, and inclusion'),
    ('Policy', 'References about policy, regulation, and governance'),
    ('Education', 'References about education, training, and learning'),
    ('Research', 'References about academic and scientific research'),
    ('Case Studies', 'References about real-world examples and case studies'),
    ('Industry Reports', 'References about industry trends, forecasts, and analyses')
ON CONFLICT (name) DO NOTHING;

-- Create index for reference types
CREATE INDEX IF NOT EXISTS idx_reference_types_name ON reference_types(name);

-- Comments
COMMENT ON TABLE reference_sources IS 'Stores reference information for content sources';
COMMENT ON TABLE reference_quality IS 'Stores quality assessments for references using CRAAP criteria';
COMMENT ON TABLE content_references IS 'Junction table linking content items to references';
COMMENT ON TABLE reference_categories IS 'Categories for organizing references';
COMMENT ON TABLE reference_types IS 'Types of references with required fields';
