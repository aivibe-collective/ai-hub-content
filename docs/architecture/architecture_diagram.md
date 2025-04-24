# Agentic AI Content Creation System Architecture

```ascii
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│                        AI Hub Content Creation System                           │
│                                                                                 │
└───────────────────────────────────┬─────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│                             Core Components                                     │
│                                                                                 │
│  ┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐       │
│  │                   │    │                   │    │                   │       │
│  │  Content Workflow │    │  Google           │    │  Supabase         │       │
│  │  (Generation &    │    │  Generative AI    │    │  (Database &      │       │
│  │   Orchestration)  │    │  (Gemini Models)  │    │   Storage)        │       │
│  │                   │    │                   │    │                   │       │
│  └─────────┬─────────┘    └─────────┬─────────┘    └─────────┬─────────┘       │
│            │                        │                        │                 │
│            └────────────────────────┼────────────────────────┘                 │
│                                     │                                          │
│                                     ▼                                          │
│                        ┌───────────────────────────┐                           │
│                        │                           │                           │
│                        │  Web Interface            │                           │
│                        │  (Flask Application)      │                           │
│                        │                           │                           │
│                        └─────────────┬─────────────┘                           │
│                                      │                                         │
│            ┌────────────────────────┬┴┬────────────────────────┐              │
│            │                        │ │                        │              │
│            ▼                        ▼ │                        ▼              │
│  ┌───────────────────┐    ┌───────────┴───────┐    ┌───────────────────┐      │
│  │                   │    │                   │    │                   │      │
│  │  Content Editing  │    │  Workflow         │    │  Source Collection│      │
│  │  (Markdown Editor │    │  Management       │    │  & Documentation  │      │
│  │   & Version       │    │  (Status Tracking │    │  (CRAAP Test &    │      │
│  │   Control)        │    │   & Assignment)   │    │   Citation)       │      │
│  │                   │    │                   │    │                   │      │
│  └───────────────────┘    └───────────────────┘    └───────────────────┘      │
│                                                                                │
└────────────────────────────────────┬────────────────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                                                                                │
│                              User Interfaces                                   │
│                                                                                │
│  ┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐      │
│  │                   │    │                   │    │                   │      │
│  │  Dashboard        │    │  Content          │    │  Search &         │      │
│  │  (Statistics &    │    │  Management       │    │  Filtering        │      │
│  │   Overview)       │    │  (CRUD Operations)│    │  (Content Access) │      │
│  │                   │    │                   │    │                   │      │
│  └───────────────────┘    └───────────────────┘    └───────────────────┘      │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Content Workflow

- Manages the overall content creation process
- Coordinates content generation with dependency management
- Handles source collection and integration
- Implemented in `content_workflow_supabase.py` and `generate_content_batch.py`

### 2. Google Generative AI

- Provides foundation models for content generation (Gemini models)
- Supports multiple model variants (1.5-flash, 1.5-pro, 2.0-flash, 2.5-pro-preview)
- Handles structured JSON generation for source information
- Implemented in `google_ai_client.py`

### 3. Supabase Integration

- Stores content inventory, prompt logs, and generation outputs
- Manages content versions and metadata
- Provides API for content management and retrieval
- Implemented in `supabase_client.py`

### 4. Web Interface

- Flask-based web application for content management
- Provides dashboard, content inventory, and detailed views
- Enables content editing, workflow management, and image attachment
- Implemented in `web_view.py` with templates in `templates/`

### 5. Content Editing System

- Markdown editor with preview functionality
- Version control for content changes
- Edit history and comparison tools
- Implemented in the web interface

### 6. Workflow Management

- Tracks content through various stages (Not Started, In Progress, Edited, etc.)
- Assigns content to users
- Manages workflow transitions and notifications
- Implemented in the web interface

### 7. Source Collection & Documentation

- Analyzes content for source needs
- Generates and evaluates sources using CRAAP test
- Creates properly formatted citations
- Integrates sources into content

### 8. Search & Filtering

- Content search across multiple fields
- Filtering by status, section, and other attributes
- Quick access to relevant content items
- Implemented in the web interface

## Data Flow

1. User selects content item from inventory or creates new item
2. Content workflow orchestrates the generation process
3. Google Generative AI generates initial content
4. Source Collection module researches and verifies sources
5. Google Generative AI integrates sources into content
6. Content is saved to local file system and metadata to Supabase
7. User can view, edit, and manage content through web interface
8. Content versions are tracked and can be compared
9. Content can be regenerated with different models or parameters
