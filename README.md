# AI Hub Content Creation System

This repository contains the implementation of an agentic AI content creation system for the AI Community & Sustainability Hub, using Google Generative AI (Gemini) models.

## System Overview

The system implements an agentic workflow for creating high-quality, well-sourced content. The workflow includes specialized modules for source collection and documentation, ensuring all content is properly cited and referenced.

### Architecture

The system architecture consists of the following components:

- **Content Workflow**: Core content generation process with dependency management
- **Google Generative AI**: Integration with Gemini models for content generation
- **Supabase**: Database for content inventory, prompt logs, and generation outputs
- **Web Interface**: Flask-based UI for viewing, managing, and editing content
- **Source Collection Module**: Ensures proper citation and referencing
- **Content Editing System**: Allows for manual editing with version control
- **Workflow Management**: Tracks content through various stages of development
- **Image Attachment**: Supports adding images to content with metadata

## Core Components

### Content Workflow

The content workflow is implemented in `content_workflow_supabase.py` and `generate_content_batch.py`. These files handle:

- Content generation based on inventory items
- Dependency management between content items
- Source collection and integration
- Logging of prompts and outputs

### Google AI Integration

The Google AI integration is implemented in `google_ai_client.py`, which provides:

- A unified interface for interacting with Google's Generative AI API
- Support for different Gemini models (1.5-flash, 1.5-pro, 2.0-flash, 2.5-pro-preview-03-25)
- JSON generation capabilities for structured data
- Fallback to Node.js implementation if needed

### Supabase Integration

The Supabase integration is implemented in `supabase_client.py`, which provides:

- Content inventory management
- Prompt and output logging
- Content file storage and version control
- Status tracking and workflow management
- User assignment and metadata storage

### Web Interface

The web interface is implemented in `web_view.py`, which provides:

- Dashboard with content statistics
- Content inventory browser with search and filtering
- Prompt log viewer
- Generation output viewer
- Detailed views of content items
- Content editing with Markdown preview
- Workflow management interface
- Image attachment and management
- Version history and comparison

## Source Collection and Documentation Module

A key component of the system is the Source Collection and Documentation Module, which ensures content credibility through proper sourcing and citation. This module:

1. Analyzes generated content to identify source needs
2. Generates high-quality academic sources relevant to the content
3. Creates properly formatted citations in APA format
4. Integrates sources into content with appropriate metadata
5. Evaluates sources using the CRAAP test (Currency, Relevance, Authority, Accuracy, Purpose)

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Supabase account and project
- Google AI API key (for Gemini models)
- Node.js (optional, for fallback implementation)

### Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/aivibe-collective/ai-hub-content.git
   cd ai-hub-content
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your Supabase and Google AI credentials
   ```

   Required environment variables:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase API key
   - `GOOGLE_GENAI_API_KEY`: Your Google Generative AI API key
   - `FLASK_SECRET_KEY`: Secret key for Flask sessions

4. Create database tables:

   ```bash
   # Run the SQL scripts in your Supabase SQL editor
   # First create_tables.sql, then sql/create_content_versions_table.sql
   ```

5. Import content inventory:

   ```bash
   python supabase_client.py
   ```

6. Create necessary directories:

   ```bash
   mkdir -p generated_content/images
   mkdir -p content_versions
   mkdir -p templates
   ```

### Usage

#### Generate Content

To generate content for a specific item:

```bash
python content_workflow_supabase.py --content-id LRN-BEG-001 --model "gemini-2.5-pro-preview-03-25"
```

To generate content in batch, respecting dependencies:

```bash
python generate_content_batch.py --status "Not Started" --model "gemini-2.5-pro-preview-03-25" --max-items 10
```

To reset all content and regenerate with a different model:

```bash
python generate_content_batch.py --reset-all --model "gemini-2.5-pro-preview-03-25" --force
```

#### Web Interface

To run the web interface:

```bash
python web_view.py --port 8081
```

Then open [http://127.0.0.1:8081](http://127.0.0.1:8081) in your browser.

The web interface provides:

- **Dashboard**: Overview of content statistics
- **Content Inventory**: Browse and search all content items
- **Content Detail**: View, edit, and manage individual content items
- **Content Editing**: Edit content with Markdown preview
- **Workflow Management**: Update content status and assign users
- **Image Attachment**: Add images to content
- **Version History**: View and compare content versions

## Testing

The system includes test coverage for core components:

```bash
python -m unittest discover test
```

Recommended tests to implement:

- Unit tests for utility functions
- Integration tests for Supabase client
- Integration tests for Google AI client
- End-to-end tests for content generation workflow
- UI tests for web interface

## Project Structure

The project has been reorganized into a more modular structure:

```bash
ai-hub-content/
├── app/                      # Core application code
│   ├── __init__.py           # Make it a proper package
│   ├── main.py               # Main entry point (renamed from app.py)
│   ├── web_view.py           # Web interface
│   ├── routes/               # Route definitions
│   │   ├── __init__.py
│   │   ├── prompt_routes.py
│   │   ├── reference_routes.py
│   │   └── ...
│   └── dashboard/            # Dashboard implementations
│       ├── __init__.py
│       ├── dashboard.py
│       └── simple_dashboard.py
├── core/                     # Core functionality
│   ├── __init__.py
│   ├── supabase_client.py    # Database client
│   ├── google_ai_client.py   # AI client
│   └── ...
├── workflows/                # Content generation workflows
│   ├── __init__.py
│   ├── content_workflow_supabase.py
│   ├── content_workflow_with_references.py
│   └── ...
├── reference_management/     # Reference management
│   ├── __init__.py
│   ├── reference_management.py
│   ├── ai_reference_processor.py
│   └── ...
├── prompt_management/        # Prompt management
│   ├── __init__.py
│   ├── prompt_management.py
│   └── ...
├── quality/                  # Quality control and evaluation
│   ├── __init__.py
│   ├── content_evaluation.py
│   ├── source_evaluation.py
│   └── ...
├── batch/                    # Batch processing tools
│   ├── __init__.py
│   ├── generate_content_batch.py
│   └── ...
├── cloud_function/           # Cloud functions
│   ├── __init__.py
│   ├── main.py
│   └── utils.py
├── cloud_run/                # Cloud Run services
│   └── ...
├── utilities_and_fixes/      # Utilities and fixes
│   └── ...
├── test/                     # Tests
│   └── ...
├── scripts/                  # Standalone scripts
│   ├── check_dashboard_data.py
│   ├── check_tables.py
│   └── ...
├── generated_content/        # Generated content files
│   └── images/               # Attached images
├── content_versions/         # Content version history
├── sql/                      # SQL scripts
├── templates/                # HTML templates
├── main.py                   # Main entry point
├── setup.py                  # Package setup
└── README.md                 # This file
```

## Reorganization and Compatibility

The project has been reorganized to improve modularity and maintainability. For backward compatibility, the old import paths are still supported through compatibility modules. However, you should update your imports to use the new structure.

Old import:

```python
from supabase_client import is_connected
```

New import:

```python
from core.supabase_client import is_connected
```

### Running with the New Structure

```bash
# Install in development mode
pip install -e .

# Run the main application
python main.py

# Or use the console script
ai-hub
```

### Development Guidelines

When adding new functionality, please follow the modular structure:

1. Core functionality goes in the appropriate module
2. Web routes go in app/routes/
3. Batch processing tools go in batch/
4. Scripts go in scripts/

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The AI Community & Sustainability Hub team
- Google Generative AI team
- Supabase team
- Flask and Bootstrap contributors
