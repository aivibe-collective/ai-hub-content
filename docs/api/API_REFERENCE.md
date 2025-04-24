# API Reference

This document provides a comprehensive reference for the API functions in the AI Hub Content Creation System.

## Table of Contents

- [Supabase Client API](#supabase-client-api)
- [Google AI Client API](#google-ai-client-api)
- [Content Workflow API](#content-workflow-api)
- [Web Interface API](#web-interface-api)

## Supabase Client API

The Supabase Client API provides functions to interact with Supabase for content inventory, prompt logging, and generation outputs.

### Connection Management

#### `is_connected()`

Checks if the Supabase client is connected.

```python
from supabase_client import is_connected

# Check connection
if is_connected():
    print("Connected to Supabase")
else:
    print("Not connected to Supabase")
```

**Returns:**
- `bool`: True if connected, False otherwise

### Content Inventory Management

#### `get_content_inventory(section=None, status=None)`

Gets content inventory from Supabase with optional filtering.

```python
from supabase_client import get_content_inventory

# Get all content items
all_items = get_content_inventory()

# Get content items in a specific section
section_items = get_content_inventory(section="Learning Resources")

# Get content items with a specific status
status_items = get_content_inventory(status="In Progress")

# Get content items with both filters
filtered_items = get_content_inventory(section="Learning Resources", status="In Progress")
```

**Parameters:**
- `section` (str, optional): Filter by section
- `status` (str, optional): Filter by status

**Returns:**
- `list`: List of content items

#### `get_content_by_id(content_id)`

Gets content details by ID.

```python
from supabase_client import get_content_by_id

# Get content item by ID
content_item = get_content_by_id("LRN-BEG-001")
if content_item:
    print(f"Title: {content_item['title']}")
else:
    print("Content item not found")
```

**Parameters:**
- `content_id` (str): Content ID

**Returns:**
- `dict`: Content item details or None if not found

#### `update_content_status(content_id, status, metadata=None)`

Updates content status in Supabase.

```python
from supabase_client import update_content_status

# Update content status
success = update_content_status("LRN-BEG-001", "In Progress", {"started_at": "2023-06-01T12:00:00Z"})
if success:
    print("Status updated successfully")
else:
    print("Failed to update status")
```

**Parameters:**
- `content_id` (str): Content ID
- `status` (str): New status
- `metadata` (dict, optional): Additional metadata

**Returns:**
- `bool`: True if successful, False otherwise

#### `update_content_item(content_id, update_data)`

Updates content item in Supabase.

```python
from supabase_client import update_content_item

# Update content item
update_data = {
    "title": "Updated Title",
    "status": "In Progress",
    "assigned_creator": "John Doe"
}
success = update_content_item("LRN-BEG-001", update_data)
if success:
    print("Content item updated successfully")
else:
    print("Failed to update content item")
```

**Parameters:**
- `content_id` (str): Content ID
- `update_data` (dict): Data to update

**Returns:**
- `bool`: True if successful, False otherwise

### Prompt Logging

#### `log_prompt(session_id, prompt_type, prompt_text, model, temperature, content_id=None, user_id=None)`

Logs a prompt to Supabase.

```python
from supabase_client import log_prompt
import uuid

# Generate a session ID
session_id = str(uuid.uuid4())

# Log a prompt
prompt_id = log_prompt(
    session_id=session_id,
    prompt_type="content_generation",
    prompt_text="Write an introduction to AI ethics.",
    model="gemini-1.5-flash",
    temperature=0.7,
    content_id="LRN-BEG-001"
)
if prompt_id:
    print(f"Prompt logged with ID: {prompt_id}")
else:
    print("Failed to log prompt")
```

**Parameters:**
- `session_id` (str): Session identifier
- `prompt_type` (str): Type of prompt
- `prompt_text` (str): Prompt text
- `model` (str): Model used
- `temperature` (float): Temperature used
- `content_id` (str, optional): Associated content ID
- `user_id` (str, optional): User ID

**Returns:**
- `str`: Prompt ID or None if failed

#### `log_generation_output(prompt_id, output_text, content_id=None, status='completed', metadata=None)`

Logs a generation output to Supabase.

```python
from supabase_client import log_generation_output

# Log a generation output
success = log_generation_output(
    prompt_id="123e4567-e89b-12d3-a456-426614174000",
    output_text="# Introduction to AI Ethics\n\nAI ethics is a field...",
    content_id="LRN-BEG-001",
    status="completed",
    metadata={"generation_time": 3.5}
)
if success:
    print("Generation output logged successfully")
else:
    print("Failed to log generation output")
```

**Parameters:**
- `prompt_id` (str): Associated prompt ID
- `output_text` (str): Generated text
- `content_id` (str, optional): Associated content ID
- `status` (str, optional): Status of the generation (completed, failed)
- `metadata` (dict, optional): Additional metadata

**Returns:**
- `bool`: True if successful, False otherwise

### Content Version Management

#### `save_content_version(content_id, content_text, model, temperature, metadata=None)`

Saves a new content version.

```python
from supabase_client import save_content_version

# Save a content version
version_number = save_content_version(
    content_id="LRN-BEG-001",
    content_text="# Introduction to AI Ethics\n\nAI ethics is a field...",
    model="gemini-1.5-flash",
    temperature=0.7,
    metadata={"edited_by": "John Doe"}
)
if version_number:
    print(f"Content version {version_number} saved successfully")
else:
    print("Failed to save content version")
```

**Parameters:**
- `content_id` (str): Content ID
- `content_text` (str): Content text
- `model` (str): Model used to generate content
- `temperature` (float): Temperature used to generate content
- `metadata` (dict, optional): Additional metadata

**Returns:**
- `int`: Version number or None if failed

#### `get_content_versions(content_id)`

Gets content versions for a specific content ID.

```python
from supabase_client import get_content_versions

# Get content versions
versions = get_content_versions("LRN-BEG-001")
if versions:
    for version in versions:
        print(f"Version {version['version_number']} created at {version['created_at']}")
else:
    print("No versions found")
```

**Parameters:**
- `content_id` (str): Content ID

**Returns:**
- `list`: List of content versions

## Google AI Client API

The Google AI Client API provides functions to interact with Google's Generative AI API.

### Content Generation

#### `generate_content(prompt, model_name="gemini-1.5-flash", temperature=0.7, max_tokens=None)`

Generates content using Google Generative AI.

```python
from google_ai_client import generate_content

# Generate content with default parameters
content = generate_content("Write an introduction to AI ethics.")
print(content)

# Generate content with custom parameters
content = generate_content(
    prompt="Write an introduction to AI ethics.",
    model_name="gemini-2.5-pro-preview-03-25",
    temperature=0.5,
    max_tokens=1000
)
print(content)
```

**Parameters:**
- `prompt` (str): The prompt for content generation
- `model_name` (str, optional): Model name to use. Defaults to "gemini-1.5-flash"
- `temperature` (float, optional): Temperature for generation. Defaults to 0.7
- `max_tokens` (int, optional): Maximum number of tokens to generate. Defaults to None

**Returns:**
- `str`: The generated content

### JSON Generation

#### `generate_json(prompt, schema=None, model_name="gemini-1.5-flash", temperature=0.2)`

Generates JSON content using Google Generative AI.

```python
from google_ai_client import generate_json

# Define a schema
schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "description": {"type": "string"},
        "sources": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "author": {"type": "string"},
                    "year": {"type": "integer"},
                    "url": {"type": "string"}
                },
                "required": ["title", "author", "year"]
            }
        }
    },
    "required": ["title", "description", "sources"]
}

# Generate JSON
json_content = generate_json(
    prompt="Provide information about AI ethics with academic sources.",
    schema=schema,
    model_name="gemini-1.5-flash",
    temperature=0.2
)
print(json_content)
```

**Parameters:**
- `prompt` (str): The prompt for content generation
- `schema` (dict, optional): JSON schema to validate against. Defaults to None
- `model_name` (str, optional): Model name to use. Defaults to "gemini-1.5-flash"
- `temperature` (float, optional): Temperature for generation. Defaults to 0.2

**Returns:**
- `dict`: The generated JSON content

## Content Workflow API

The Content Workflow API provides functions to generate content for specific items.

### Content Generation

#### `generate_content_for_item(content_id, model_name=None, temperature=None, output_dir=None, force=False, check_deps_only=False)`

Generates content for a specific item.

```python
from content_workflow_supabase import generate_content_for_item

# Generate content for an item
success, output_file = generate_content_for_item(
    content_id="LRN-BEG-001",
    model_name="gemini-2.5-pro-preview-03-25",
    temperature=0.7,
    output_dir="generated_content",
    force=False,
    check_deps_only=False
)
if success:
    print(f"Content generated successfully: {output_file}")
else:
    print("Failed to generate content")
```

**Parameters:**
- `content_id` (str): Content ID
- `model_name` (str, optional): Model name to use. Defaults to None (uses DEFAULT_MODEL)
- `temperature` (float, optional): Temperature for generation. Defaults to None (uses DEFAULT_TEMPERATURE)
- `output_dir` (str, optional): Output directory. Defaults to None (uses "generated_content")
- `force` (bool, optional): Force regeneration even if content exists. Defaults to False
- `check_deps_only` (bool, optional): Only check dependencies without generating content. Defaults to False

**Returns:**
- `tuple`: (success, output_file) where success is a boolean and output_file is the path to the generated file

### Batch Content Generation

#### `generate_content_batch(status=None, max_items=None, model_name=None, temperature=None, output_dir=None, force=False, reset_all=False)`

Generates content in batch, respecting dependencies.

```python
from generate_content_batch import generate_content_batch

# Generate content for items with status "Not Started"
results = generate_content_batch(
    status="Not Started",
    max_items=10,
    model_name="gemini-2.5-pro-preview-03-25",
    temperature=0.7,
    output_dir="generated_content",
    force=False,
    reset_all=False
)
print(f"Generated {len(results)} items")
```

**Parameters:**
- `status` (str, optional): Filter by status. Defaults to None
- `max_items` (int, optional): Maximum number of items to generate. Defaults to None
- `model_name` (str, optional): Model name to use. Defaults to None (uses DEFAULT_MODEL)
- `temperature` (float, optional): Temperature for generation. Defaults to None (uses DEFAULT_TEMPERATURE)
- `output_dir` (str, optional): Output directory. Defaults to None (uses "generated_content")
- `force` (bool, optional): Force regeneration even if content exists. Defaults to False
- `reset_all` (bool, optional): Reset all content and regenerate. Defaults to False

**Returns:**
- `list`: List of (content_id, success, output_file) tuples

## Web Interface API

The Web Interface API provides Flask routes for viewing and managing content.

### Dashboard

#### `GET /`

Displays the dashboard with content statistics.

```http
GET / HTTP/1.1
Host: localhost:8081
```

### Content Inventory

#### `GET /content`

Displays the content inventory with optional filtering.

```http
GET /content?section=Learning%20Resources&status=In%20Progress HTTP/1.1
Host: localhost:8081
```

**Query Parameters:**
- `section` (str, optional): Filter by section
- `status` (str, optional): Filter by status

### Content Detail

#### `GET /content/<content_id>`

Displays the content detail page.

```http
GET /content/LRN-BEG-001 HTTP/1.1
Host: localhost:8081
```

**URL Parameters:**
- `content_id` (str): Content ID

### Content Editing

#### `GET /content/<content_id>/edit`

Displays the content editing page.

```http
GET /content/LRN-BEG-001/edit HTTP/1.1
Host: localhost:8081
```

**URL Parameters:**
- `content_id` (str): Content ID

#### `POST /content/<content_id>/edit`

Updates the content.

```http
POST /content/LRN-BEG-001/edit HTTP/1.1
Host: localhost:8081
Content-Type: application/x-www-form-urlencoded

content_text=# Introduction to AI Ethics%0A%0AAI ethics is a field...&edit_notes=Updated introduction
```

**URL Parameters:**
- `content_id` (str): Content ID

**Form Parameters:**
- `content_text` (str): Content text
- `edit_notes` (str, optional): Edit notes

### Workflow Management

#### `GET /content/<content_id>/workflow`

Displays the workflow management page.

```http
GET /content/LRN-BEG-001/workflow HTTP/1.1
Host: localhost:8081
```

**URL Parameters:**
- `content_id` (str): Content ID

#### `POST /content/<content_id>/workflow`

Updates the workflow status.

```http
POST /content/LRN-BEG-001/workflow HTTP/1.1
Host: localhost:8081
Content-Type: application/x-www-form-urlencoded

status=In%20Progress&assigned_to=John%20Doe&workflow_notes=Started working on this
```

**URL Parameters:**
- `content_id` (str): Content ID

**Form Parameters:**
- `status` (str): New status
- `assigned_to` (str, optional): Assigned user
- `workflow_notes` (str, optional): Workflow notes

### Image Attachment

#### `GET /content/<content_id>/attach-image`

Displays the image attachment page.

```http
GET /content/LRN-BEG-001/attach-image HTTP/1.1
Host: localhost:8081
```

**URL Parameters:**
- `content_id` (str): Content ID

#### `POST /content/<content_id>/attach-image`

Uploads an image.

```http
POST /content/LRN-BEG-001/attach-image HTTP/1.1
Host: localhost:8081
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="image"; filename="example.jpg"
Content-Type: image/jpeg

(binary data)
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="image_description"

Example image for AI ethics
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

**URL Parameters:**
- `content_id` (str): Content ID

**Form Parameters:**
- `image` (file): Image file
- `image_description` (str, optional): Image description

### Content Search

#### `GET /search`

Searches content inventory.

```http
GET /search?q=ethics&status=In%20Progress&section=Learning%20Resources HTTP/1.1
Host: localhost:8081
```

**Query Parameters:**
- `q` (str, optional): Search query
- `status` (str, optional): Filter by status
- `section` (str, optional): Filter by section

### Content Regeneration

#### `GET /content/<content_id>/regenerate`

Displays the content regeneration page.

```http
GET /content/LRN-BEG-001/regenerate HTTP/1.1
Host: localhost:8081
```

**URL Parameters:**
- `content_id` (str): Content ID

#### `POST /content/<content_id>/regenerate`

Regenerates the content.

```http
POST /content/LRN-BEG-001/regenerate HTTP/1.1
Host: localhost:8081
Content-Type: application/x-www-form-urlencoded

model=gemini-2.5-pro-preview-03-25&temperature=0.7
```

**URL Parameters:**
- `content_id` (str): Content ID

**Form Parameters:**
- `model` (str): Model name
- `temperature` (float): Temperature for generation
