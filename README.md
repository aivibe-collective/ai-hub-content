# AI Hub Content Creation System

This repository contains the implementation of an agentic AI content creation system for the AI Community & Sustainability Hub, using Google Generative AI (Gemini) models.

## System Overview

The system implements an agentic workflow for creating high-quality, well-sourced content. The workflow includes specialized modules for source collection and documentation, ensuring all content is properly cited and referenced.

### Architecture

The system architecture consists of the following components:

- **Content Workflow**: Core content generation process with dependency management
- **Google Generative AI**: Integration with Gemini models for content generation
- **Supabase**: Database for content inventory, prompt logs, and generation outputs
- **Web Interface**: Flask-based UI for viewing and managing content
- **Source Collection Module**: Ensures proper citation and referencing

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
- Support for different Gemini models (1.5-flash, 2.5-pro, etc.)
- JSON generation capabilities for structured data
- Fallback to Node.js implementation if needed

### Supabase Integration

The Supabase integration is implemented in `supabase_client.py`, which provides:

- Content inventory management
- Prompt and output logging
- Content file storage
- Status tracking

### Web Interface

The web interface is implemented in `web_view.py`, which provides:

- Dashboard with content statistics
- Content inventory browser
- Prompt log viewer
- Generation output viewer
- Detailed views of content items

## Source Collection and Documentation Module

A key component of the system is the Source Collection and Documentation Module, which ensures content credibility through proper sourcing and citation. This module:

1. Analyzes generated content to identify source needs
2. Generates high-quality academic sources relevant to the content
3. Creates properly formatted citations in APA format
4. Integrates sources into content with appropriate metadata

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Supabase account and project
- Google AI API key (for Gemini models)

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

4. Import content inventory:

   ```bash
   python supabase_client.py
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

#### View Content

To view generated content through the web interface:

```bash
python web_view.py
```

Then open [http://127.0.0.1:8081](http://127.0.0.1:8081) in your browser.

## Testing

The system includes comprehensive test coverage:

```bash
python -m unittest discover test
```

For more detailed test information, see [test/README.md](test/README.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The AI Community & Sustainability Hub team
- Google Generative AI team
- Supabase team
