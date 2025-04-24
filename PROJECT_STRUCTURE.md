# Project Structure

This document outlines the structure of the AI Hub Content Creation System, explaining the purpose of each directory and key files.

## Directory Structure

```bash
.
├── app/                           # Web application
│   ├── dashboard/                 # Dashboard components
│   ├── routes/                    # Route handlers
│   ├── main.py                    # Main application entry point
│   └── web_view.py                # Web view implementation
│
├── core/                          # Core functionality
│   ├── google_ai/                 # Google AI integration
│   ├── supabase/                  # Supabase integration
│   └── utils/                     # Utility functions
│
├── docs/                          # Documentation
│   ├── api/                       # API documentation
│   ├── architecture/              # Architecture documentation
│   ├── content/                   # Content-related documentation
│   ├── implementation/            # Implementation plans
│   ├── reference/                 # Reference documentation
│   ├── samples/                   # Sample content
│   ├── security/                  # Security documentation
│   ├── setup/                     # Setup documentation
│   ├── testing/                   # Testing documentation
│   ├── ui/                        # UI documentation
│   └── workflows/                 # Workflow documentation
│
├── prompt_management/             # Prompt management functionality
│
├── quality/                       # Quality control functionality
│
├── reference_management/          # Reference management functionality
│
├── scripts/                       # Utility scripts
│
├── sql/                           # SQL files
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
├── test/                          # Test files
│
├── workflows/                     # Workflow implementations
│   ├── content/                   # Content generation workflows
│   └── reference/                 # Reference management workflows
│
├── generated_content/             # Generated content files
│   └── images/                    # Attached images for content
│
├── content_versions/              # Content version history
│
├── compatibility/                 # Compatibility modules
│
├── NEXT_STEPS.md                  # Future development roadmap
├── PROJECT_STRUCTURE.md           # This file - project structure documentation
├── README.md                      # Project overview and setup instructions
├── .env.example                   # Example environment variables file
├── requirements.txt               # Python dependencies
└── setup.py                       # Python package setup file
```

## Key Components

### Core Functionality

#### core/google_ai/

This directory contains modules for interacting with Google's Generative AI API. It supports:

- Multiple Gemini models (1.5-flash, 1.5-pro, 2.0-flash, 2.5-pro-preview-03-25)
- Text generation with temperature control
- JSON generation with schema validation
- Fallback to Node.js implementation if Python package is not available

Key functions:

- `generate_content()`: Function to generate text content
- `generate_json()`: Function to generate JSON content
- `list_models()`: Function to list available models

#### core/supabase/

This directory contains modules for interacting with Supabase for content inventory, prompt logging, and generation outputs. It handles:

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

### Workflow Implementations

#### workflows/content/

This directory contains modules for content generation workflows. It handles:

- Content generation based on inventory items
- Dependency management between content items
- Source collection and integration
- Logging of prompts and outputs to Supabase

Key functions:

- `generate_content_for_item()`: Main function to generate content for a specific item
- `create_prompt()`: Creates a prompt for the Google Generative AI API
- `create_sources_prompt()`: Creates a prompt for generating sources
- `add_sources_to_content()`: Integrates sources into the generated content

#### workflows/reference/

This directory contains modules for reference management workflows. It handles:

- Reference extraction from content
- Reference validation and formatting
- Reference storage and retrieval

### Web Application

#### app/

This directory contains the web application for viewing and managing content. It provides:

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

### Prompt Management

#### prompt_management/

This directory contains modules for managing prompts. It handles:

- Prompt template management
- Prompt versioning
- Prompt import and export

### Reference Management

#### reference_management/

This directory contains modules for managing references. It handles:

- Reference source management
- Reference extraction and validation
- Reference import and export

### Quality Control

#### quality/

This directory contains modules for quality control. It handles:

- Content evaluation
- Source evaluation
- A/B testing

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
