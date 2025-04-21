# Agentic AI Content Creation System

This repository contains the implementation of an agentic AI content creation system for the AI Community & Sustainability Hub, built on Google Cloud Platform.

## System Overview

The system uses a combination of Google Cloud services to implement an agentic workflow for creating high-quality, well-sourced content. The workflow is based on the Enhanced Agentic AI Content Creation Workflow document and includes specialized modules for source collection and documentation.

### Architecture

The system architecture consists of the following components:

- **Cloud Functions**: Handle workflow orchestration and content generation
- **Vertex AI**: Provides foundation models for content generation
- **Cloud Storage**: Stores generated content and assets
- **Firestore**: Manages metadata and workflow state
- **Cloud Run**: Hosts specialized services for source research and citation management
- **Pub/Sub**: Enables asynchronous communication between components

For a detailed architecture diagram, see [architecture_diagram.md](architecture_diagram.md).

## Implementation

The system is implemented as a set of serverless components that work together to create content:

### Cloud Functions

- `initialize-content-creation`: Entry point for content creation
- `select-template`: Selects appropriate template based on content type
- `generate-content-plan`: Creates a detailed content plan
- `populate-sections`: Generates content for each section
- `integrate-sources`: Incorporates sources into content

### Cloud Run Services

- `research-service`: Handles source research, evaluation, and citation
  - `/identify-source-needs`: Identifies statements requiring citations
  - `/research-sources`: Finds potential sources for statements
  - `/evaluate-source`: Evaluates sources using CRAAP criteria
  - `/generate-citation`: Creates properly formatted citations
  - `/integrate-source`: Integrates sources into content

## Source Collection and Documentation Module

A key component of the system is the Source Collection and Documentation Module, which ensures content credibility through proper sourcing and citation. This module:

1. Automatically identifies statements requiring citation
2. Researches potential sources across academic and industry repositories
3. Evaluates sources using the CRAAP test (Currency, Relevance, Authority, Accuracy, Purpose)
4. Generates properly formatted citations in various styles (APA, MLA, Chicago, IEEE)
5. Integrates sources into content with appropriate in-text citations

## Getting Started

### Prerequisites

- Google Cloud Platform account
- Google Cloud CLI installed
- Python 3.9 or higher

### Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/aivibe-content-creation.git
   cd aivibe-content-creation
   ```

2. Set up Google Cloud project:
   ```
   gcloud projects create aivibe-content-creation
   gcloud config set project aivibe-content-creation
   ```

3. Enable required APIs:
   ```
   gcloud services enable cloudfunctions.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable firestore.googleapis.com
   gcloud services enable storage.googleapis.com
   gcloud services enable pubsub.googleapis.com
   gcloud services enable aiplatform.googleapis.com
   ```

4. Deploy the system:
   ```
   # Make deployment scripts executable
   chmod +x deployment/*.sh
   
   # Deploy Cloud Functions
   ./deployment/cloud_function_deploy.sh
   
   # Deploy Cloud Run services
   ./deployment/cloud_run_deploy.sh
   ```

### Usage

To create content, send a POST request to the initialize-content-creation Cloud Function:

```bash
curl -X POST https://REGION-PROJECT_ID.cloudfunctions.net/initialize-content-creation \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "LearningModule",
    "audience_level": "Beginner",
    "title": "Introduction to Generative AI",
    "mission_pillars": ["ResponsibleAI", "Sustainability"]
  }'
```

The system will return a content ID that can be used to track the content creation process.

## Implementation Plan

For a detailed implementation plan, see [implementation_plan.md](implementation_plan.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The AI Community & Sustainability Hub team
- Google Cloud Platform
- Vertex AI team
