# Troubleshooting Guide

This document provides solutions for common issues you might encounter when using the AI Hub Content Creation System.

## Table of Contents

- [Supabase Connection Issues](#supabase-connection-issues)
- [Google AI API Issues](#google-ai-api-issues)
- [Content Generation Issues](#content-generation-issues)
- [Web Interface Issues](#web-interface-issues)
- [Database Schema Issues](#database-schema-issues)
- [Environment Variable Issues](#environment-variable-issues)
- [Performance Issues](#performance-issues)

## Supabase Connection Issues

### Connection Failures

**Symptoms:**
- Error message: "Supabase client not initialized"
- Error message: "Error connecting to Supabase"

**Possible Causes:**
1. Missing or incorrect environment variables
2. Network connectivity issues
3. Invalid API key or URL
4. Supabase service outage

**Solutions:**

1. **Check environment variables:**
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   print(f"SUPABASE_URL: {os.environ.get('SUPABASE_URL')}")
   print(f"SUPABASE_KEY (first 10 chars): {os.environ.get('SUPABASE_KEY')[:10]}...")
   ```

2. **Verify network connectivity:**
   ```python
   import requests
   
   try:
       response = requests.get(os.environ.get('SUPABASE_URL'))
       print(f"Status code: {response.status_code}")
   except Exception as e:
       print(f"Network error: {str(e)}")
   ```

3. **Check API key permissions:**
   - For read-only operations, use the `anon` key
   - For read-write operations, use the `service_role` key
   - Verify the key in the Supabase dashboard under Project Settings > API

4. **Check Supabase status:**
   - Visit [Supabase Status](https://status.supabase.com/) to check for service outages

### Authentication Errors

**Symptoms:**
- Error message: "JWT must be a string"
- Error message: "JWT signature does not match"

**Solutions:**

1. **Regenerate API key:**
   - Go to Supabase dashboard > Project Settings > API
   - Click "Regenerate" for the service_role key
   - Update your .env file with the new key

2. **Check JWT format:**
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   key = os.environ.get('SUPABASE_KEY')
   parts = key.split('.')
   if len(parts) != 3:
       print("Invalid JWT format - should have 3 parts separated by dots")
   else:
       print("JWT format appears valid")
   ```

## Google AI API Issues

### API Key Issues

**Symptoms:**
- Error message: "GOOGLE_GENAI_API_KEY environment variable not found"
- Error message: "Error generating content: Invalid API key"

**Solutions:**

1. **Check environment variable:**
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   key = os.environ.get('GOOGLE_GENAI_API_KEY')
   if not key:
       print("API key not found in environment variables")
   else:
       print(f"API key found: {key[:10]}...")
   ```

2. **Verify API key validity:**
   ```python
   import google.generativeai as genai
   
   try:
       genai.configure(api_key=os.environ.get('GOOGLE_GENAI_API_KEY'))
       models = genai.list_models()
       print(f"Available models: {[m.name for m in models]}")
   except Exception as e:
       print(f"API key validation error: {str(e)}")
   ```

3. **Regenerate API key:**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Update your .env file with the new key

### Model Availability Issues

**Symptoms:**
- Error message: "Model not found: gemini-2.5-pro-preview-03-25"
- Error message: "Error generating content: Model is not supported"

**Solutions:**

1. **Check available models:**
   ```python
   import google.generativeai as genai
   
   genai.configure(api_key=os.environ.get('GOOGLE_GENAI_API_KEY'))
   models = genai.list_models()
   for model in models:
       print(f"Model: {model.name}")
   ```

2. **Use a different model:**
   ```python
   # Try a different model
   from google_ai_client import generate_content
   
   content = generate_content(
       prompt="Write a short introduction to AI ethics.",
       model_name="gemini-1.5-flash"  # Use a more widely available model
   )
   print(content)
   ```

3. **Check model name spelling:**
   - Ensure the model name is spelled correctly
   - Common models: "gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"

## Content Generation Issues

### Dependency Resolution Failures

**Symptoms:**
- Error message: "Dependencies not met for content item"
- Error message: "Circular dependency detected"

**Solutions:**

1. **Check dependencies:**
   ```python
   from supabase_client import get_content_by_id
   
   content_item = get_content_by_id("LRN-BEG-002")
   if content_item:
       dependencies = content_item.get('dependencies', '')
       print(f"Dependencies: {dependencies}")
       
       # Check if dependencies exist and are completed
       if dependencies:
           for dep_id in dependencies.split(','):
               dep_id = dep_id.strip()
               dep_item = get_content_by_id(dep_id)
               if not dep_item:
                   print(f"Dependency {dep_id} not found")
               elif dep_item.get('status') != 'Completed':
                   print(f"Dependency {dep_id} not completed (status: {dep_item.get('status')})")
               else:
                   print(f"Dependency {dep_id} is completed")
   ```

2. **Force generation:**
   ```bash
   python content_workflow_supabase.py --content-id LRN-BEG-002 --force
   ```

3. **Visualize dependency graph:**
   ```python
   from supabase_client import get_content_inventory
   import networkx as nx
   import matplotlib.pyplot as plt
   
   # Get content inventory
   content_items = get_content_inventory()
   
   # Build dependency graph
   G = nx.DiGraph()
   for item in content_items:
       content_id = item['content_id']
       G.add_node(content_id)
       dependencies = item.get('dependencies', '')
       if dependencies:
           for dep_id in dependencies.split(','):
               dep_id = dep_id.strip()
               if dep_id:
                   G.add_edge(dep_id, content_id)
   
   # Check for cycles
   try:
       cycles = list(nx.simple_cycles(G))
       if cycles:
           print(f"Circular dependencies detected: {cycles}")
       else:
           print("No circular dependencies detected")
   except Exception as e:
       print(f"Error checking for cycles: {str(e)}")
   
   # Visualize graph
   plt.figure(figsize=(12, 8))
   pos = nx.spring_layout(G)
   nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, arrows=True)
   plt.title("Content Dependency Graph")
   plt.savefig("dependency_graph.png")
   plt.close()
   ```

### Content Quality Issues

**Symptoms:**
- Generated content is too short or lacks detail
- Generated content has factual errors
- Generated content is not properly formatted

**Solutions:**

1. **Adjust temperature:**
   ```bash
   # Lower temperature for more focused output
   python content_workflow_supabase.py --content-id LRN-BEG-001 --temperature 0.3
   
   # Higher temperature for more creative output
   python content_workflow_supabase.py --content-id LRN-BEG-001 --temperature 0.8
   ```

2. **Try a different model:**
   ```bash
   # Try a more powerful model
   python content_workflow_supabase.py --content-id LRN-BEG-001 --model "gemini-2.5-pro-preview-03-25"
   ```

3. **Improve the prompt:**
   - Edit the prompt template in `content_workflow_supabase.py`
   - Add more specific instructions
   - Include examples of desired output format

## Web Interface Issues

### Flask Server Won't Start

**Symptoms:**
- Error message: "Address already in use"
- Error message: "No module named 'flask'"

**Solutions:**

1. **Check if port is in use:**
   ```bash
   # Check if port 8081 is in use
   lsof -i :8081
   
   # Kill the process using the port
   kill -9 <PID>
   
   # Try a different port
   python web_view.py --port 8082
   ```

2. **Install Flask:**
   ```bash
   pip install flask
   ```

3. **Check for syntax errors:**
   ```bash
   python -m py_compile web_view.py
   ```

### Template Rendering Issues

**Symptoms:**
- Error message: "TemplateNotFound"
- Error message: "UndefinedError: 'function' is undefined"

**Solutions:**

1. **Check templates directory:**
   ```bash
   # Create templates directory if it doesn't exist
   mkdir -p templates
   
   # List templates
   ls -la templates/
   ```

2. **Check template functions:**
   ```python
   # In web_view.py
   
   # Register template filters
   app.jinja_env.filters['format_datetime'] = format_datetime
   app.jinja_env.globals['parse_metadata'] = parse_metadata
   app.jinja_env.globals['status_color'] = status_color
   ```

3. **Debug template rendering:**
   ```python
   # In web_view.py
   
   @app.route('/debug-template')
   def debug_template():
       """Debug template rendering."""
       return render_template(
           'debug.html',
           variables={
               'format_datetime': app.jinja_env.filters.get('format_datetime'),
               'parse_metadata': app.jinja_env.globals.get('parse_metadata'),
               'status_color': app.jinja_env.globals.get('status_color')
           }
       )
   ```

## Database Schema Issues

### Missing Tables

**Symptoms:**
- Error message: "relation 'content_inventory' does not exist"
- Error message: "Error getting content inventory: relation does not exist"

**Solutions:**

1. **Check if tables exist:**
   ```python
   from supabase_client import supabase
   
   # List tables
   result = supabase.rpc('get_tables').execute()
   print(f"Tables: {result.data}")
   ```

2. **Create tables:**
   ```bash
   # Run SQL scripts in Supabase SQL Editor
   # First create_tables.sql, then sql/create_content_versions_table.sql
   ```

3. **Check table structure:**
   ```python
   from supabase_client import supabase
   
   # List columns for a table
   result = supabase.rpc('get_columns', {'table_name': 'content_inventory'}).execute()
   print(f"Columns: {result.data}")
   ```

### Foreign Key Constraints

**Symptoms:**
- Error message: "insert or update on table violates foreign key constraint"
- Error message: "Error logging generation output: violates foreign key constraint"

**Solutions:**

1. **Check foreign key relationships:**
   ```sql
   -- In Supabase SQL Editor
   SELECT
       tc.table_schema, 
       tc.constraint_name, 
       tc.table_name, 
       kcu.column_name, 
       ccu.table_schema AS foreign_table_schema,
       ccu.table_name AS foreign_table_name,
       ccu.column_name AS foreign_column_name 
   FROM 
       information_schema.table_constraints AS tc 
       JOIN information_schema.key_column_usage AS kcu
         ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
       JOIN information_schema.constraint_column_usage AS ccu
         ON ccu.constraint_name = tc.constraint_name
         AND ccu.table_schema = tc.table_schema
   WHERE tc.constraint_type = 'FOREIGN KEY';
   ```

2. **Verify referenced values exist:**
   ```python
   from supabase_client import supabase
   
   # Check if content_id exists
   content_id = "LRN-BEG-001"
   result = supabase.table('content_inventory').select('count', count='exact').filter('content_id', 'eq', content_id).execute()
   print(f"Count: {result.count}")
   ```

3. **Temporarily disable foreign key constraints (use with caution):**
   ```sql
   -- In Supabase SQL Editor
   -- Disable foreign key checks
   SET session_replication_role = 'replica';
   
   -- Perform operations
   
   -- Re-enable foreign key checks
   SET session_replication_role = 'origin';
   ```

## Environment Variable Issues

### Missing Environment Variables

**Symptoms:**
- Error message: "SUPABASE_URL environment variable not found"
- Error message: "GOOGLE_GENAI_API_KEY environment variable not found"

**Solutions:**

1. **Check .env file:**
   ```bash
   # Check if .env file exists
   ls -la .env
   
   # Create .env file if it doesn't exist
   cp .env.example .env
   ```

2. **Check environment variables:**
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   required_vars = [
       'SUPABASE_URL',
       'SUPABASE_KEY',
       'GOOGLE_GENAI_API_KEY',
       'FLASK_SECRET_KEY'
   ]
   
   for var in required_vars:
       value = os.environ.get(var)
       if not value:
           print(f"Missing environment variable: {var}")
       else:
           print(f"{var}: {'*' * min(len(value), 10)}")
   ```

3. **Set environment variables manually:**
   ```bash
   # Linux/macOS
   export SUPABASE_URL="https://your-project-id.supabase.co"
   export SUPABASE_KEY="your-supabase-key"
   export GOOGLE_GENAI_API_KEY="your-google-genai-api-key"
   export FLASK_SECRET_KEY="your-flask-secret-key"
   
   # Windows
   set SUPABASE_URL=https://your-project-id.supabase.co
   set SUPABASE_KEY=your-supabase-key
   set GOOGLE_GENAI_API_KEY=your-google-genai-api-key
   set FLASK_SECRET_KEY=your-flask-secret-key
   ```

### Environment Variable Loading Issues

**Symptoms:**
- Environment variables are set but not being loaded
- Error message: "No module named 'dotenv'"

**Solutions:**

1. **Install python-dotenv:**
   ```bash
   pip install python-dotenv
   ```

2. **Check dotenv loading:**
   ```python
   import os
   from dotenv import load_dotenv
   
   # Print current working directory
   print(f"Current working directory: {os.getcwd()}")
   
   # Print .env file path
   env_path = os.path.join(os.getcwd(), '.env')
   print(f".env file path: {env_path}")
   print(f".env file exists: {os.path.exists(env_path)}")
   
   # Load .env file with verbose output
   load_dotenv(verbose=True)
   ```

3. **Use absolute path for .env file:**
   ```python
   import os
   from dotenv import load_dotenv
   
   # Use absolute path
   env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
   load_dotenv(dotenv_path=env_path)
   ```

## Performance Issues

### Slow Database Queries

**Symptoms:**
- Web interface is slow to load
- Content generation takes a long time
- Batch generation is very slow

**Solutions:**

1. **Use selective queries:**
   ```python
   # Bad: Fetches all fields
   result = supabase.table('content_inventory').select('*').execute()
   
   # Good: Fetches only needed fields
   result = supabase.table('content_inventory').select('content_id,title,status').execute()
   ```

2. **Use pagination:**
   ```python
   # Fetch results in pages
   page_size = 20
   page = 1
   
   result = supabase.table('content_inventory').select('*').range((page - 1) * page_size, page * page_size - 1).execute()
   ```

3. **Use indexes:**
   ```sql
   -- In Supabase SQL Editor
   -- Create index on frequently queried fields
   CREATE INDEX idx_content_inventory_status ON content_inventory(status);
   CREATE INDEX idx_content_inventory_section ON content_inventory(section);
   ```

### Memory Issues

**Symptoms:**
- Error message: "MemoryError"
- Process crashes with out of memory error

**Solutions:**

1. **Limit batch size:**
   ```bash
   # Process fewer items at a time
   python generate_content_batch.py --max-items 5
   ```

2. **Process large content in chunks:**
   ```python
   def process_large_content(content):
       """Process large content in chunks."""
       chunk_size = 10000
       chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
       
       for i, chunk in enumerate(chunks):
           print(f"Processing chunk {i+1}/{len(chunks)}")
           # Process chunk
           
       return "Processed content"
   ```

3. **Clean up resources:**
   ```python
   import gc
   
   # Force garbage collection
   gc.collect()
   ```

### Slow Content Generation

**Symptoms:**
- Content generation takes a long time
- API requests time out

**Solutions:**

1. **Use a faster model:**
   ```bash
   # Use a faster model
   python content_workflow_supabase.py --content-id LRN-BEG-001 --model "gemini-1.5-flash"
   ```

2. **Implement caching:**
   ```python
   import functools
   
   # Simple cache decorator
   def cache_result(func):
       cache = {}
       
       @functools.wraps(func)
       def wrapper(*args, **kwargs):
           key = str(args) + str(kwargs)
           if key not in cache:
               cache[key] = func(*args, **kwargs)
           return cache[key]
       
       return wrapper
   
   @cache_result
   def generate_content(prompt, model_name, temperature):
       # Generate content
       return "Generated content"
   ```

3. **Implement retries with exponential backoff:**
   ```python
   import time
   import random
   
   def retry_with_backoff(func, max_retries=5, initial_delay=1, max_delay=60):
       """Retry a function with exponential backoff."""
       retries = 0
       delay = initial_delay
       
       while retries < max_retries:
           try:
               return func()
           except Exception as e:
               retries += 1
               if retries >= max_retries:
                   raise e
               
               # Calculate delay with jitter
               delay = min(delay * 2, max_delay)
               jitter = random.uniform(0, 0.1 * delay)
               sleep_time = delay + jitter
               
               print(f"Retry {retries}/{max_retries} after {sleep_time:.2f}s: {str(e)}")
               time.sleep(sleep_time)
   ```
