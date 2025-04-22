# Supabase Integration for AI Hub Content Creation

This document provides detailed information about the Supabase integration in the AI Hub Content Creation System, which provides database storage for content inventory, prompt logging, generation outputs, and content versions.

## Overview

The system uses Supabase as its primary database backend for storing and managing content-related data. Supabase provides a PostgreSQL database with a RESTful API, making it easy to interact with from Python.

The Supabase integration consists of the following components:

1. **Content Inventory**: Stores metadata about content items from the AI Hub Content Inventory
2. **Prompt Logging**: Logs prompts sent to the AI model
3. **Generation Outputs**: Stores the generated content
4. **Content Files**: Stores large content that exceeds database size limits
5. **Content Versions**: Tracks version history of content with metadata

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install the required Python packages, including:

- `supabase==2.0.3`: Python client for Supabase
- `python-dotenv==1.0.0`: For loading environment variables from .env files
- `flask==2.3.3`: For the web interface
- `google-generativeai==0.3.1`: For interacting with Google Generative AI

### 2. Configure Environment Variables

Create a `.env` file with the following variables:

```env
SUPABASE_URL="your-supabase-url"
SUPABASE_KEY="your-supabase-key"
GOOGLE_GENAI_API_KEY="your-google-genai-api-key"
FLASK_SECRET_KEY="your-flask-secret-key"
```

These environment variables are used in the code as follows:

```python
# In supabase_client.py
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
```

### 3. Create Supabase Tables

Create the following tables in your Supabase project. You can use the SQL scripts provided in the repository:

- `create_tables.sql`: Main database schema
- `sql/create_content_versions_table.sql`: Schema for content versions table

#### content_inventory

This table stores metadata about content items from the AI Hub Content Inventory.

```sql
CREATE TABLE content_inventory (
    id SERIAL PRIMARY KEY,
    content_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    section VARCHAR(255),
    subsection VARCHAR(255),
    content_type VARCHAR(255),
    status VARCHAR(255) DEFAULT 'Not Started',
    priority VARCHAR(255),
    dependencies VARCHAR(255),
    audience_technical_level VARCHAR(255),
    audience_role VARCHAR(255),
    audience_constraints VARCHAR(255),
    primary_mission_pillar_1 VARCHAR(255),
    primary_mission_pillar_2 VARCHAR(255),
    secondary_mission_pillars VARCHAR(255),
    smart_objectives TEXT,
    practical_components TEXT,
    estimated_dev_time VARCHAR(255),
    required_expertise VARCHAR(255),
    assigned_creator VARCHAR(255),
    assigned_reviewers VARCHAR(255),
    review_status VARCHAR(255),
    platform_requirements VARCHAR(255),
    notes TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on content_id
CREATE INDEX idx_content_inventory_content_id ON content_inventory(content_id);

-- Create index on status
CREATE INDEX idx_content_inventory_status ON content_inventory(status);

-- Create index on section
CREATE INDEX idx_content_inventory_section ON content_inventory(section);
```

#### prompt_logs

This table stores prompts sent to the AI model.

```sql
CREATE TABLE prompt_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL,
    prompt_type VARCHAR(255) NOT NULL,
    prompt_text TEXT NOT NULL,
    model VARCHAR(255) NOT NULL,
    temperature FLOAT NOT NULL,
    content_id VARCHAR(255),
    user_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (content_id) REFERENCES content_inventory(content_id) ON DELETE SET NULL
);

-- Create index on session_id
CREATE INDEX idx_prompt_logs_session_id ON prompt_logs(session_id);

-- Create index on content_id
CREATE INDEX idx_prompt_logs_content_id ON prompt_logs(content_id);
```

#### generation_outputs

This table stores generated content outputs.

```sql
CREATE TABLE generation_outputs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prompt_id UUID NOT NULL,
    output_text TEXT NOT NULL,
    content_id VARCHAR(255),
    status VARCHAR(255) DEFAULT 'completed',
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (prompt_id) REFERENCES prompt_logs(id) ON DELETE CASCADE,
    FOREIGN KEY (content_id) REFERENCES content_inventory(content_id) ON DELETE SET NULL
);

-- Create index on prompt_id
CREATE INDEX idx_generation_outputs_prompt_id ON generation_outputs(prompt_id);

-- Create index on content_id
CREATE INDEX idx_generation_outputs_content_id ON generation_outputs(content_id);
```

#### content_files

This table stores full content when it exceeds database limits.

```sql
CREATE TABLE content_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    output_id UUID NOT NULL,
    content_type VARCHAR(255) DEFAULT 'text/markdown',
    file_content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (output_id) REFERENCES generation_outputs(id) ON DELETE CASCADE
);

-- Create index on output_id
CREATE INDEX idx_content_files_output_id ON content_files(output_id);
```

#### content_versions

This table stores version history of content.

```sql
CREATE TABLE content_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id VARCHAR(255) NOT NULL,
    version_number INTEGER NOT NULL,
    content_text TEXT NOT NULL,
    model VARCHAR(255),
    temperature FLOAT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (content_id) REFERENCES content_inventory(content_id) ON DELETE CASCADE,
    UNIQUE (content_id, version_number)
);

-- Create index on content_id
CREATE INDEX idx_content_versions_content_id ON content_versions(content_id);
```

## Usage

### Import Content Inventory

```bash
python supabase_client.py
```

This will import the content inventory from `AI_Hub_Content_Inventory_Enhanced.csv` into the Supabase database. The script performs the following operations:

1. Connects to Supabase using the environment variables
2. Reads the CSV file and converts it to a list of dictionaries
3. Inserts or updates each row in the `content_inventory` table
4. Logs the results of the import operation

### List Content Inventory

```bash
python list_content_inventory.py [--section SECTION] [--status STATUS] [--format {table,csv,json}]
```

This will list content items from the inventory, with optional filtering by section and status. The output can be formatted as a table, CSV, or JSON.

Example:

```bash
# List all content items in the Learning Resources section
python list_content_inventory.py --section "Learning Resources"

# List all content items with status "In Progress" in JSON format
python list_content_inventory.py --status "In Progress" --format json
```

### Generate Content for a Content Item

```bash
python content_workflow_supabase.py --content-id LRN-BEG-001 [--model MODEL] [--temperature TEMPERATURE] [--output-dir OUTPUT_DIR] [--force] [--check-deps-only]
```

This will generate content for the specified content item, log the prompts and outputs to Supabase, and save the generated content to a file.

Options:

- `--force`: Force generation even if dependencies are not met or content is already completed
- `--check-deps-only`: Only check dependencies without generating content

Example:

```bash
# Generate content for LRN-BEG-001 using the gemini-2.5-pro-preview-03-25 model
python content_workflow_supabase.py --content-id LRN-BEG-001 --model "gemini-2.5-pro-preview-03-25" --temperature 0.7

# Check dependencies for LRN-BEG-002 without generating content
python content_workflow_supabase.py --content-id LRN-BEG-002 --check-deps-only
```

### Generate Content in Batch

```bash
python generate_content_batch.py [--section SECTION] [--status STATUS] [--model MODEL] [--temperature TEMPERATURE] [--output-dir OUTPUT_DIR] [--force] [--max-items MAX_ITEMS] [--delay DELAY] [--dry-run]
```

This will generate content for multiple items in the correct dependency order.

Options:

- `--section`: Filter by section
- `--status`: Filter by status (default: Not Started)
- `--force`: Force generation even if dependencies are not met or content is already completed
- `--max-items`: Maximum number of items to generate
- `--delay`: Delay in seconds between items (default: 5)
- `--dry-run`: Show what would be generated without actually generating

Example:

```bash
# Generate content for up to 5 items with status "Not Started"
python generate_content_batch.py --status "Not Started" --max-items 5 --model "gemini-2.5-pro-preview-03-25"

# Do a dry run to see what would be generated
python generate_content_batch.py --section "Learning Resources" --dry-run
```

### View Prompt Logs

```bash
python view_prompt_logs.py [--session-id SESSION_ID] [--content-id CONTENT_ID] [--limit LIMIT] [--show-content] [--output-id OUTPUT_ID]
```

This will display prompt logs from Supabase, with optional filtering by session ID and content ID.

Example:

```bash
# View the last 10 prompt logs
python view_prompt_logs.py --limit 10

# View prompt logs for a specific content item and show the generated content
python view_prompt_logs.py --content-id LRN-BEG-001 --show-content
```

### Web Interface

```bash
python web_view.py [--port PORT]
```

This will start the Flask web interface for viewing and managing content. The web interface provides:

- Dashboard with content statistics
- Content inventory browser with search and filtering
- Content editing with Markdown preview
- Workflow management interface
- Image attachment and management
- Version history and comparison

Example:

```bash
# Start the web interface on port 8081
python web_view.py --port 8081
```

Then open [http://127.0.0.1:8081](http://127.0.0.1:8081) in your browser.

## Workflow

### Content Generation Workflow

1. **Import Content Inventory**: Import the content inventory from CSV into Supabase
2. **List Content Inventory**: View the content items in the inventory
3. **Check Dependencies**: Check if dependencies for a content item are met
4. **Generate Content**: Generate content for a specific content item
5. **Generate Content in Batch**: Generate content for multiple items in the correct dependency order
6. **View Prompt Logs**: View the prompts and outputs for a specific content item or session

### Content Editing Workflow

1. **View Content**: View the generated content in the web interface
2. **Edit Content**: Edit the content using the Markdown editor
3. **Save Version**: Save a new version of the content
4. **Compare Versions**: Compare different versions of the content
5. **Attach Images**: Attach images to the content
6. **Manage Workflow**: Update the content status and assign users

## Content Dependencies

The system respects content dependencies defined in the `dependencies` field of the content inventory. Dependencies are comma-separated content IDs that must be completed before a content item can be generated.

For example, if content item `LRN-BEG-002` depends on `LRN-BEG-001`, then `LRN-BEG-001` must be completed before `LRN-BEG-002` can be generated.

The batch generation script automatically sorts content items in the correct dependency order using a topological sort algorithm. This ensures that dependencies are generated before the items that depend on them.

```python
def get_dependency_graph(content_items):
    """Build a dependency graph from content items."""
    graph = {}
    for item in content_items:
        content_id = item['content_id']
        dependencies = item.get('dependencies', '')
        if dependencies:
            deps = [dep.strip() for dep in dependencies.split(',') if dep.strip()]
        else:
            deps = []
        graph[content_id] = deps
    return graph

def topological_sort(graph):
    """Perform topological sort on a dependency graph."""
    visited = set()
    temp_visited = set()
    order = []

    def visit(node):
        if node in temp_visited:
            raise ValueError(f"Circular dependency detected: {node}")
        if node in visited:
            return
        temp_visited.add(node)
        for neighbor in graph.get(node, []):
            visit(neighbor)
        temp_visited.remove(node)
        visited.add(node)
        order.append(node)

    for node in graph:
        if node not in visited:
            visit(node)

    return order[::-1]  # Reverse to get correct order
```

## Performance Considerations

### Bulk Operations

For bulk operations, use the `upsert` method to insert or update multiple records at once:

```python
def bulk_update_content_status(content_items):
    """Bulk update content status in Supabase."""
    if not supabase or not content_items:
        return False

    try:
        update_data = []
        for item in content_items:
            update_data.append({
                'content_id': item['content_id'],
                'status': item['status'],
                'updated_at': datetime.datetime.now().isoformat()
            })

        result = supabase.table('content_inventory').upsert(update_data).execute()
        return bool(result.data)
    except Exception as e:
        print(f"Error bulk updating content status: {str(e)}")
        return False
```

### Query Optimization

Use selective queries to minimize data transfer:

```python
# Bad: Fetches all fields
result = supabase.table('content_inventory').select('*').execute()

# Good: Fetches only needed fields
result = supabase.table('content_inventory').select('content_id,title,status').execute()
```

## Benefits

1. **Traceability**: All prompts and outputs are logged, providing a complete history of content generation
2. **Reproducibility**: The exact prompts and parameters used to generate content are recorded
3. **Scalability**: The system can handle large amounts of content and prompts
4. **Monitoring**: The status of content generation can be monitored in real-time
5. **Analytics**: The data can be analyzed to improve content generation over time
6. **Version Control**: Content versions are tracked with metadata
7. **Workflow Management**: Content status and assignments are tracked
8. **Search and Filtering**: Content can be searched and filtered by various criteria
9. **Image Management**: Images can be attached to content with metadata
10. **Web Interface**: A user-friendly web interface for content management
