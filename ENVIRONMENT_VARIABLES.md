# Required Environment Variables

## Core Configuration

```env
# Supabase Configuration (Required)
SUPABASE_URL="https://your-project-id.supabase.co"  # Your Supabase project URL
SUPABASE_KEY="your-supabase-api-key"                # Your Supabase API key

# Google Generative AI Configuration (Required)
GOOGLE_GENAI_API_KEY="your-google-genai-api-key"    # Your Google Generative AI API key

# Flask Configuration (Required)
FLASK_SECRET_KEY="your-flask-secret-key"            # Secret key for Flask sessions
```

## Optional Configuration

```env
# Web Interface Configuration
WEB_PORT=8081                                      # Port for the web interface (default: 8081)
DEBUG_MODE=True                                    # Enable debug mode (default: False)

# Content Generation Configuration
DEFAULT_MODEL="gemini-2.5-pro-preview-03-25"       # Default model for content generation
DEFAULT_TEMPERATURE=0.7                            # Default temperature for content generation

# File Storage Configuration
CONTENT_DIR="generated_content"                     # Directory for generated content
VERSION_DIR="content_versions"                      # Directory for content versions
IMAGE_DIR="generated_content/images"                # Directory for attached images
```

## Example .env File

```env
# Supabase Configuration
SUPABASE_URL="https://abcdefghijklmnopqrst.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Google Generative AI Configuration
GOOGLE_GENAI_API_KEY="AIzaSyAqd-nLSm6dLyxgrzSt50hlQ9aQcO7t6hE"

# Flask Configuration
FLASK_SECRET_KEY="your-secret-key-here"

# Web Interface Configuration
WEB_PORT=8081
DEBUG_MODE=True

# Content Generation Configuration
DEFAULT_MODEL="gemini-2.5-pro-preview-03-25"
DEFAULT_TEMPERATURE=0.7
```

## Usage in Code

```python
# In supabase_client.py
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

# In google_ai_client.py
api_key = api_key or os.environ.get('GOOGLE_GENAI_API_KEY')

# In web_view.py
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default-secret-key')
```

## Verification

```bash
# Command to test the configuration
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(f'SUPABASE_URL: {os.environ.get(\"SUPABASE_URL\")}\nGOOGLE_GENAI_API_KEY: {os.environ.get(\"GOOGLE_GENAI_API_KEY\")[0:10]}...')"
```
