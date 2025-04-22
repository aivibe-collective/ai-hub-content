# Project Structure

This document outlines the structure of the AI Hub Content Creation System, explaining the purpose of each directory and key files.

## Directory Structure

```
.
├── README.md                      # Project overview and setup instructions
├── architecture_diagram.md        # System architecture visualization
├── ENVIRONMENT_VARIABLES.md       # Environment variable documentation
├── NEXT_STEPS.md                  # Future development roadmap
├── PROJECT_STRUCTURE.md           # This file - project structure documentation
├── .env.example                   # Example environment variables file
├── requirements.txt               # Python dependencies
│
├── content_workflow_supabase.py   # Content generation workflow implementation
├── generate_content_batch.py      # Batch content generation script
├── google_ai_client.py            # Google Generative AI integration
├── supabase_client.py             # Supabase database integration
├── web_view.py                    # Flask web interface
│
├── create_tables.sql              # Main database schema for Supabase
├── sql/                           # Additional SQL scripts
│   └── create_content_versions_table.sql  # Schema for content versions table
│
├── generated_content/             # Generated content files
│   └── images/                    # Attached images for content
│
├── content_versions/              # Content version history
│
├── templates/                     # HTML templates for web interface
│   ├── base.html                  # Base template with common elements
│   ├── content.html               # Content inventory page
│   ├── content_detail.html        # Content detail page
│   ├── edit_content.html          # Content editing page
│   ├── content_workflow.html      # Workflow management page
│   ├── attach_image.html          # Image attachment page
│   └── search_results.html        # Search results page
│
└── test/                          # Test files
    └── README.md                  # Testing documentation
```

## Key Components

### Core Modules

#### content_workflow_supabase.py

This module implements the core content generation workflow with Supabase integration. It handles:

- Content generation based on inventory items
- Dependency management between content items
- Source collection and integration
- Logging of prompts and outputs to Supabase

Key functions:
- `generate_content_for_item()`: Main function to generate content for a specific item
- `create_prompt()`: Creates a prompt for the Google Generative AI API
- `create_sources_prompt()`: Creates a prompt for generating sources
- `add_sources_to_content()`: Integrates sources into the generated content

#### google_ai_client.py

This module provides a unified interface for interacting with Google's Generative AI API. It supports:

- Multiple Gemini models (1.5-flash, 1.5-pro, 2.0-flash, 2.5-pro-preview-03-25)
- Text generation with temperature control
- JSON generation with schema validation
- Fallback to Node.js implementation if Python package is not available

Key classes and functions:
- `GoogleAIClient`: Main client class for interacting with the API
- `generate_content()`: Function to generate text content
- `generate_json()`: Function to generate JSON content

#### supabase_client.py

This module provides functions to interact with Supabase for content inventory, prompt logging, and generation outputs. It handles:

- Content inventory management
- Prompt and output logging
- Content file storage
- Status tracking and workflow management

Key functions:
- `is_connected()`: Checks if Supabase client is connected
- `get_content_inventory()`: Gets content inventory from Supabase
- `get_content_by_id()`: Gets content details by ID
- `update_content_status()`: Updates content status in Supabase
- `log_prompt()`: Logs a prompt to Supabase
- `log_generation_output()`: Logs a generation output to Supabase
- `save_content_version()`: Saves a new content version

#### web_view.py

This module implements a Flask web interface for viewing and managing content. It provides:

- Dashboard with content statistics
- Content inventory browser with search and filtering
- Content editing with Markdown preview
- Workflow management interface
- Image attachment and management

Key routes:
- `/`: Dashboard
- `/content`: Content inventory
- `/content/<content_id>`: Content detail
- `/content/<content_id>/edit`: Content editing
- `/content/<content_id>/workflow`: Workflow management
- `/content/<content_id>/attach-image`: Image attachment
- `/search`: Content search

### Database Schema

The system uses Supabase as its database backend with the following tables:

#### content_inventory

Stores content items with metadata:

- `content_id`: Unique identifier for the content item
- `title`: Content title
- `section`: Content section
- `subsection`: Content subsection
- `content_type`: Type of content (Article, Tutorial, etc.)
- `status`: Current status (Not Started, In Progress, Completed, etc.)
- `priority`: Priority level (High, Medium, Low)
- `dependencies`: Comma-separated list of content IDs that this content depends on
- `audience_technical_level`: Target audience technical level
- `audience_role`: Target audience role/context
- `audience_constraints`: Target audience resource constraints
- `primary_mission_pillar_1`: Primary mission pillar 1
- `primary_mission_pillar_2`: Primary mission pillar 2
- `secondary_mission_pillars`: Secondary mission pillars
- `smart_objectives`: SMART objectives for the content
- `practical_components`: Practical components to include
- `estimated_dev_time`: Estimated development time in hours
- `required_expertise`: Required expertise for development
- `assigned_creator`: Assigned creator
- `assigned_reviewers`: Assigned reviewers
- `review_status`: Review status
- `platform_requirements`: Platform requirements
- `notes`: Additional notes
- `metadata`: JSON metadata
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

#### prompt_logs

Stores prompts sent to the AI model:

- `id`: Unique identifier for the prompt
- `session_id`: Session identifier
- `prompt_type`: Type of prompt
- `prompt_text`: Prompt text
- `model`: Model used
- `temperature`: Temperature used
- `content_id`: Associated content ID
- `user_id`: User ID
- `created_at`: Creation timestamp

#### generation_outputs

Stores generated content outputs:

- `id`: Unique identifier for the output
- `prompt_id`: Associated prompt ID
- `output_text`: Generated text (truncated if too large)
- `content_id`: Associated content ID
- `status`: Status of the generation (completed, failed)
- `metadata`: JSON metadata
- `created_at`: Creation timestamp

#### content_files

Stores full content when it exceeds database limits:

- `id`: Unique identifier for the file
- `output_id`: Associated output ID
- `content_type`: Content type (text/markdown)
- `file_content`: Full content text
- `created_at`: Creation timestamp

#### content_versions

Stores version history of content:

- `id`: Unique identifier for the version
- `content_id`: Associated content ID
- `version_number`: Version number
- `content_text`: Content text
- `model`: Model used to generate content
- `temperature`: Temperature used to generate content
- `metadata`: JSON metadata
- `created_at`: Creation timestamp

## File Storage

The system uses the local file system for storing generated content and images:

- `generated_content/`: Directory for generated content files
  - `<content_id>.md`: Markdown file for each content item
  - `images/`: Directory for attached images
    - `<content_id>/`: Directory for images attached to a specific content item
      - `<filename>`: Image file

- `content_versions/`: Directory for content version history
  - `<content_id>_v<version_number>.md`: Markdown file for each content version
  - `<content_id>_<timestamp>.md`: Markdown file for local version backup

## Web Interface

The web interface is implemented using Flask with the following templates:

- `base.html`: Base template with common elements (navigation, styles, scripts)
- `content.html`: Content inventory page with filtering and sorting
- `content_detail.html`: Content detail page with metadata and generated content
- `edit_content.html`: Content editing page with Markdown preview
- `content_workflow.html`: Workflow management page with status tracking
- `attach_image.html`: Image attachment page with upload and management
- `search_results.html`: Search results page with filtering options

## Environment Variables

The system uses the following environment variables:

- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase API key
- `GOOGLE_GENAI_API_KEY`: Google Generative AI API key
- `FLASK_SECRET_KEY`: Secret key for Flask sessions
- `WEB_PORT`: Port for the web interface (default: 8081)
- `DEBUG_MODE`: Enable debug mode (default: False)
- `DEFAULT_MODEL`: Default model for content generation
- `DEFAULT_TEMPERATURE`: Default temperature for content generation

See [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md) for more details.
