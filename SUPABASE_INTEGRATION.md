# Supabase Integration for AI Hub Content Creation

This document explains the Supabase integration for the AI Hub Content Creation system, which provides database storage for content inventory, prompt logging, and generation outputs.

## Overview

The Supabase integration consists of the following components:

1. **Content Inventory**: Stores metadata about content items from the AI Hub Content Inventory
2. **Prompt Logging**: Logs prompts sent to the AI model
3. **Generation Outputs**: Stores the generated content
4. **Content Files**: Stores large content that exceeds database size limits

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file with the following variables:

```
SUPABASE_URL="your-supabase-url"
SUPABASE_KEY="your-supabase-key"
GOOGLE_GENAI_API_KEY="your-google-genai-api-key"
```

### 3. Create Supabase Tables

Create the following tables in your Supabase project:

#### content_inventory

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| content_id | text | Content ID from inventory (e.g., LRN-BEG-001) |
| section | text | Section name |
| subsection | text | Subsection name |
| title | text | Content title |
| content_type | text | Type of content |
| status | text | Status (Not Started, In Progress, Completed, Failed) |
| priority | text | Priority (H, M, L) |
| dependencies | text | Dependencies on other content items |
| audience_technical_level | text | Technical level of target audience |
| audience_role | text | Role/context of target audience |
| audience_constraints | text | Resource constraints of target audience |
| primary_mission_pillar_1 | text | Primary mission pillar 1 |
| primary_mission_pillar_2 | text | Primary mission pillar 2 |
| secondary_mission_pillars | text | Secondary mission pillars |
| smart_objectives | text | SMART objectives |
| practical_components | text | Practical components |
| estimated_dev_time | text | Estimated development time |
| required_expertise | text | Required expertise |
| assigned_creator | text | Assigned creator |
| assigned_reviewers | text | Assigned reviewers |
| review_status | text | Review status |
| platform_requirements | text | Platform requirements |
| notes | text | Notes |
| metadata | jsonb | Additional metadata |
| created_at | timestamp | Creation timestamp |
| updated_at | timestamp | Update timestamp |

#### prompt_logs

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| session_id | text | Session ID |
| prompt_type | text | Type of prompt (content_generation, sources_generation, etc.) |
| prompt_text | text | The prompt text |
| model | text | Model name |
| temperature | float | Temperature setting |
| content_id | text | Content ID from inventory |
| user_id | text | User ID |
| created_at | timestamp | Creation timestamp |

#### generation_outputs

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| prompt_id | uuid | Reference to prompt_logs.id |
| output_text | text | Generated text (truncated if too large) |
| content_id | text | Content ID from inventory |
| status | text | Status (completed, failed) |
| metadata | jsonb | Additional metadata |
| created_at | timestamp | Creation timestamp |

#### content_files

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| output_id | uuid | Reference to generation_outputs.id |
| content_type | text | Content type (e.g., text/markdown) |
| file_content | text | Full content text |
| created_at | timestamp | Creation timestamp |

## Usage

### Import Content Inventory

```bash
python supabase_client.py
```

This will import the content inventory from `AI_Hub_Content_Inventory_Enhanced.csv` into the Supabase database.

### List Content Inventory

```bash
python list_content_inventory.py [--section SECTION] [--status STATUS] [--format {table,csv,json}]
```

This will list content items from the inventory, with optional filtering by section and status.

### Generate Content for a Content Item

```bash
python content_workflow_supabase.py --content-id LRN-BEG-001 [--model MODEL] [--temperature TEMPERATURE] [--output-dir OUTPUT_DIR] [--force] [--check-deps-only]
```

This will generate content for the specified content item, log the prompts and outputs to Supabase, and save the generated content to a file.

Options:
- `--force`: Force generation even if dependencies are not met or content is already completed
- `--check-deps-only`: Only check dependencies without generating content

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

### View Prompt Logs

```bash
python view_prompt_logs.py [--session-id SESSION_ID] [--content-id CONTENT_ID] [--limit LIMIT] [--show-content] [--output-id OUTPUT_ID]
```

This will display prompt logs from Supabase, with optional filtering by session ID and content ID.

## Workflow

1. **Import Content Inventory**: Import the content inventory from CSV into Supabase
2. **List Content Inventory**: View the content items in the inventory
3. **Check Dependencies**: Check if dependencies for a content item are met
4. **Generate Content**: Generate content for a specific content item
5. **Generate Content in Batch**: Generate content for multiple items in the correct dependency order
6. **View Prompt Logs**: View the prompts and outputs for a specific content item or session

## Content Dependencies

The system respects content dependencies defined in the `dependencies` field of the content inventory. Dependencies are comma-separated content IDs that must be completed before a content item can be generated.

For example, if content item `LRN-BEG-002` depends on `LRN-BEG-001`, then `LRN-BEG-001` must be completed before `LRN-BEG-002` can be generated.

The batch generation script automatically sorts content items in the correct dependency order using a topological sort algorithm. This ensures that dependencies are generated before the items that depend on them.

## Benefits

1. **Traceability**: All prompts and outputs are logged, providing a complete history of content generation
2. **Reproducibility**: The exact prompts and parameters used to generate content are recorded
3. **Scalability**: The system can handle large amounts of content and prompts
4. **Monitoring**: The status of content generation can be monitored in real-time
5. **Analytics**: The data can be analyzed to improve content generation over time
