# Agentic AI Content Creation System UI

This is a web-based user interface for the Agentic AI Content Creation System. It allows you to generate content step by step, displaying inputs and outputs at each stage.

## Features

- Step-by-step content generation workflow
- Input form for content specifications
- Real-time preview of generated content
- Source generation and integration
- Export functionality

## Installation

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Make sure you have set up your Google Generative AI API key in the `.env` file:

```
GOOGLE_GENAI_API_KEY="your-api-key-here"
FLASK_SECRET_KEY="your-secret-key-here"  # For session management
```

## Usage

1. Run the Flask application:

```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Follow the step-by-step workflow:
   - Step 1: Initialize Content Creation
   - Step 2: Generate Content
   - Step 3: Add Sources
   - Step 4: Review & Export

## Workflow Steps

### Step 1: Initialize Content Creation

In this step, you specify the parameters for your content:

- **Title**: The title of your content
- **Content Type**: The type of content (Learning Module, Blog Post, Case Study)
- **Audience Level**: The target audience level (Beginner, Intermediate, Expert)
- **Mission Pillars**: The mission pillars to integrate (Responsible AI, Inclusion, Sustainability)
- **Model**: The Google Generative AI model to use
- **Temperature**: Controls the randomness of the generation (0.0 - 1.0)

### Step 2: Generate Content

This step generates the content based on your specifications. The generated content is displayed in a preview panel.

### Step 3: Add Sources

This step adds academic sources to your content. The generated sources are displayed in a preview panel.

### Step 4: Review & Export

This step allows you to review the final content with sources and export it to a file.

## Additional Features

- **Reset**: Resets the session and clears all generated content
- **Start Over**: Resets the UI without clearing the session

## Technical Details

- The UI is built with Bootstrap 5 and vanilla JavaScript
- The backend is built with Flask
- The content generation uses Google Generative AI API
- The content is formatted with Markdown and rendered with the marked.js library
