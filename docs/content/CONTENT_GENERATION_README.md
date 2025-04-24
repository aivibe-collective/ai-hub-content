# Agentic AI Content Creation System

This repository contains scripts for generating content using the Agentic AI Content Creation System. The system is designed to create high-quality educational content with a focus on responsible AI and inclusion.

## Google Generative AI Integration

The system now integrates with Google's Generative AI API to generate content and sources. This integration provides more accurate, relevant, and up-to-date content and sources.

## Overview

The Agentic AI Content Creation System follows a structured workflow:

1. **Content Initialization**: Define the content type, audience level, title, and mission pillars.
2. **Template Selection**: Select an appropriate template based on content type and audience level.
3. **Content Planning**: Generate a detailed content plan with learning objectives, key concepts, and structure.
4. **Section Population**: Generate content for each section based on the content plan.
5. **Source Collection**: Identify source needs and collect appropriate sources.
6. **Mission Pillar Integration**: Integrate mission pillars (e.g., ResponsibleAI, Inclusion) into the content.
7. **Review**: Review the content for quality, accuracy, and alignment with mission pillars.

## Scripts

The repository includes the following scripts:

### Content Generation

- `generate_content_local.py`: Generate content locally without using Google Cloud services.
- `generate_content_google_ai.py`: Generate content using Google Generative AI API.
- `generate_content.py`: Generate content using the full Agentic AI Content Creation System (requires Google Cloud setup).

### Source Documentation

- `add_sources.py`: Add hardcoded source documentation to generated content.
- `add_sources_google_ai.py`: Add source documentation using Google Generative AI API.

### Combined Workflows

- `generate_content_with_sources.py`: Generate content with sources using Google Generative AI API.
- `run_content_generation.py`: Run the content generation process with the simulated API server.

### Utilities

- `simulate_api.py`: Simulate the API server for testing content generation.
- `google-ai-test.js`: Test the Google Generative AI API using Node.js.

## Usage

### Generating Content with Google Generative AI

To generate content using Google Generative AI API:

```bash
python3 generate_content_google_ai.py --title "Introduction to Generative AI" --type "LearningModule" --audience "Beginner" --pillars "ResponsibleAI" "Inclusion" --output "generative_ai_intro.md" --model "gemini-1.5-flash"
```

### Adding Sources with Google Generative AI

To add source documentation using Google Generative AI API:

```bash
python3 add_sources_google_ai.py --input "generative_ai_intro.md" --output "generative_ai_intro_with_sources.md" --model "gemini-1.5-flash"
```

### Complete Workflow with Google Generative AI

To generate content with sources using Google Generative AI API in a single step:

```bash
python3 generate_content_with_sources.py --title "Introduction to Generative AI" --type "LearningModule" --audience "Beginner" --pillars "ResponsibleAI" "Inclusion" --output "generative_ai_intro_with_sources.md" --model "gemini-1.5-flash"
```

### Generating Content Locally (Without API)

To generate content locally without using Google Cloud services or Google Generative AI API:

```bash
python3 generate_content_local.py --title "Introduction to Generative AI" --type "LearningModule" --audience "Beginner" --pillars "ResponsibleAI" "Inclusion" --output "generative_ai_intro.md"
```

### Adding Hardcoded Sources (Without API)

To add hardcoded source documentation to generated content:

```bash
python3 add_sources.py --input "generative_ai_intro.md" --output "generative_ai_intro_with_sources.md"
```

### Full Content Generation Process (Requires Google Cloud Setup)

To run the full content generation process with the simulated API server:

```bash
python3 run_content_generation.py --title "Introduction to Generative AI" --type "LearningModule" --audience "Beginner" --pillars "ResponsibleAI" "Inclusion" --output "generative_ai_intro.md"
```

## Parameters

The content generation scripts accept the following parameters:

- `--title`: Title of the content (e.g., "Introduction to Generative AI")
- `--type`: Type of content (options: "LearningModule", "BlogPost", "CaseStudy")
- `--audience`: Audience level (options: "Beginner", "Intermediate", "Expert")
- `--pillars`: Mission pillars to integrate (e.g., "ResponsibleAI", "Inclusion")
- `--output`: Output file path
- `--model`: Google Generative AI model to use (e.g., "gemini-1.5-flash", "gemini-1.5-pro")
- `--input`: Input file path (for source addition scripts)

## Example Content

The system can generate various types of content, including:

1. **Learning Modules**: Educational content with learning objectives, key concepts, and practical examples.
2. **Blog Posts**: Informative articles on specific topics with a clear structure and engaging style.
3. **Case Studies**: In-depth analyses of real-world examples with lessons learned and best practices.

Each content piece includes:

- Clear structure with introduction, main content, and conclusion
- Integration of mission pillars (e.g., ResponsibleAI, Inclusion)
- Source documentation with proper citations
- Metadata about the content creation process

## Source Collection and Documentation

The Source Collection and Documentation Module ensures that all content includes proper citations and references. The module:

1. Identifies source needs based on the content
2. Collects appropriate sources from academic papers, industry reports, and technical documentation
3. Evaluates sources based on relevance, authority, recency, and accuracy
4. Adds source documentation to the content with proper citations

## Mission Pillar Integration

The Mission Pillar Integration Module ensures that content aligns with the organization's mission pillars:

1. **ResponsibleAI**: Addresses ethical considerations, bias mitigation, transparency, and privacy
2. **Inclusion**: Ensures content is accessible, multilingual, representative, and designed with diverse stakeholders

## Testing

The repository includes comprehensive tests for the content generation system:

- Unit tests for individual components
- Integration tests for the end-to-end workflow
- Performance tests for measuring system performance

## Requirements

- Python 3.7+
- Node.js 14+
- Required Python packages: `python-dotenv`, `requests`
- Required Node.js packages: `@google/generative-ai`, `dotenv`
- Google Generative AI API key (set in `.env` file as `GOOGLE_GENAI_API_KEY`)

## Setup

1. Clone the repository
2. Install required Python packages: `pip install python-dotenv requests`
3. Install required Node.js packages: `npm install @google/generative-ai dotenv`
4. Create a `.env` file with your Google Generative AI API key:

   ```env
   GOOGLE_GENAI_API_KEY="your-api-key-here"
   ```

5. Run the content generation scripts as described above

## Contributing

Contributions to the Agentic AI Content Creation System are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
