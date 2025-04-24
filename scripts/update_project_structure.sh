#!/bin/bash
# Script to update the PROJECT_STRUCTURE.md file to reflect the new organization

# Create a backup of the original file
cp PROJECT_STRUCTURE.md PROJECT_STRUCTURE.md.bak

# Create the new project structure file
cat > PROJECT_STRUCTURE.md << 'EOL'
# Project Structure

This document outlines the structure of the AI Hub Content Creation System.

## Directory Structure

```
.
├── app/                       # Web application
│   ├── dashboard/             # Dashboard components
│   ├── routes/                # Route handlers
│   ├── main.py                # Main application entry point
│   └── web_view.py            # Web view implementation
│
├── core/                      # Core functionality
│   ├── google_ai/             # Google AI integration
│   ├── supabase/              # Supabase integration
│   └── utils/                 # Utility functions
│
├── docs/                      # Documentation
│   ├── api/                   # API documentation
│   ├── architecture/          # Architecture documentation
│   ├── content/               # Content-related documentation
│   ├── implementation/        # Implementation plans
│   ├── reference/             # Reference documentation
│   ├── samples/               # Sample content
│   ├── security/              # Security documentation
│   ├── setup/                 # Setup documentation
│   ├── testing/               # Testing documentation
│   ├── ui/                    # UI documentation
│   └── workflows/             # Workflow documentation
│
├── prompt_management/         # Prompt management functionality
│
├── quality/                   # Quality control functionality
│
├── reference_management/      # Reference management functionality
│
├── scripts/                   # Utility scripts
│
├── sql/                       # SQL files
│
├── test/                      # Test files
│
├── workflows/                 # Workflow implementations
│   ├── content/               # Content generation workflows
│   └── reference/             # Reference management workflows
│
├── old_files/                 # Backup of old files (temporary)
│
├── .env                       # Environment variables
├── .env.example               # Example environment variables
├── .gitignore                 # Git ignore file
├── NEXT_STEPS.md              # Next steps for the project
├── PROJECT_STRUCTURE.md       # This file
├── README.md                  # Project README
└── requirements.txt           # Python dependencies
```

## Key Components

### Core Functionality

- **core/google_ai/**: Integration with Google's Generative AI API
- **core/supabase/**: Integration with Supabase for data storage

### Workflows

- **workflows/content/**: Content generation workflows
- **workflows/reference/**: Reference management workflows

### Web Application

- **app/**: Web application for interacting with the system
- **app/dashboard/**: Dashboard components
- **app/routes/**: Route handlers

### Documentation

- **docs/**: Documentation organized by topic

### Utility Scripts

- **scripts/**: Utility scripts for various tasks

### Tests

- **test/**: Test files for the system
EOL

echo "PROJECT_STRUCTURE.md has been updated to reflect the new organization."
echo "A backup of the original file has been saved as PROJECT_STRUCTURE.md.bak"
