#!/usr/bin/env python3
"""
Supabase client module for the Agentic AI Content Creation System.
This module provides functions to interact with Supabase for content inventory and prompt logging.
"""

import os
import json
import csv
import datetime
import logging
from dotenv import load_dotenv
from supabase import create_client, Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

# Initialize Supabase client
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        # Print debug information
        logger.info(f"Supabase URL: {SUPABASE_URL}")
        logger.info(f"Supabase Key (first 10 chars): {SUPABASE_KEY[:10]}...")

        # Try to create the client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing Supabase client: {str(e)}")
else:
    logger.warning("Supabase URL or key not found in environment variables")

def is_connected():
    """Check if Supabase client is connected."""
    if not supabase:
        logger.error("Supabase client not initialized")
        return False

    try:
        # Try a simple query to check connection
        logger.info("Attempting to connect to Supabase...")
        response = supabase.table('content_inventory').select('count', count='exact').execute()
        logger.info(f"Connection successful. Response: {response}")
        return True
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error connecting to Supabase: {error_msg}")

        # Try to parse the error message if it's a JSON string
        if isinstance(error_msg, str) and '{' in error_msg:
            try:
                import json
                error_json = json.loads(error_msg)
                logger.error(f"Error details: {json.dumps(error_json, indent=2)}")
            except:
                pass

        return False

def create_tables():
    """Create necessary tables in Supabase if they don't exist."""
    if not supabase:
        logger.error("Supabase client not initialized")
        return False

    try:
        # This is a placeholder - in Supabase, tables are typically created through the web interface
        # or using SQL migrations. This function would be used to verify tables exist.
        tables = ['content_inventory', 'prompt_logs', 'generation_outputs', 'content_files']
        for table in tables:
            result = supabase.table(table).select('count', count='exact').execute()
            logger.info(f"Table {table} exists with {result.count} rows")
        return True
    except Exception as e:
        logger.error(f"Error checking tables: {str(e)}")
        return False

def import_content_inventory_from_csv(csv_file):
    """Import content inventory from CSV file to Supabase."""
    if not supabase:
        logger.error("Supabase client not initialized")
        return False

    try:
        # Read CSV file
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Process rows
        processed_rows = []
        for row in rows:
            # Skip empty rows or section headers
            if not row['Content ID'] or row['Content ID'].startswith('#'):
                continue

            # Process row
            processed_row = {
                'content_id': row['Content ID'],
                'section': row['Section'],
                'subsection': row['Subsection'],
                'title': row['Content Title'],
                'content_type': row['Content Type'],
                'status': row['Status'],
                'priority': row['Priority (H/M/L)'],
                'dependencies': row.get('Dependencies', ''),
                'audience_technical_level': row['Target Audience - Technical Level'],
                'audience_role': row['Target Audience - Role/Context'],
                'audience_constraints': row['Target Audience - Resource Constraints'],
                'primary_mission_pillar_1': row['Primary Mission Pillar 1'],
                'primary_mission_pillar_2': row['Primary Mission Pillar 2'],
                'secondary_mission_pillars': row['Secondary Mission Pillars'],
                'smart_objectives': row['SMART Objectives'],
                'practical_components': row['Practical Components'],
                'estimated_dev_time': row['Estimated Development Time (hours)'],
                'required_expertise': row['Required Expertise'],
                'assigned_creator': row['Assigned Creator'],
                'assigned_reviewers': row['Assigned Reviewers'],
                'review_status': row['Review Status'],
                'platform_requirements': row['Platform Requirements'],
                'notes': row['Notes'],
                'created_at': datetime.datetime.now().isoformat(),
                'updated_at': datetime.datetime.now().isoformat()
            }
            processed_rows.append(processed_row)

        # Insert rows into Supabase
        if processed_rows:
            result = supabase.table('content_inventory').upsert(processed_rows).execute()
            logger.info(f"Imported {len(processed_rows)} rows to content_inventory table")
            return True
        else:
            logger.warning("No valid rows found in CSV file")
            return False
    except Exception as e:
        logger.error(f"Error importing content inventory: {str(e)}")
        return False

def log_prompt(session_id, prompt_type, prompt_text, model, temperature, content_id=None, user_id=None):
    """Log a prompt to Supabase."""
    if not supabase:
        logger.error("Supabase client not initialized")
        return None

    try:
        prompt_data = {
            'session_id': session_id,
            'prompt_type': prompt_type,
            'prompt_text': prompt_text,
            'model': model,
            'temperature': temperature,
            'content_id': content_id,
            'user_id': user_id,
            'created_at': datetime.datetime.now().isoformat()
        }

        result = supabase.table('prompt_logs').insert(prompt_data).execute()
        prompt_id = result.data[0]['id'] if result.data else None
        logger.info(f"Logged prompt with ID: {prompt_id}")
        return prompt_id
    except Exception as e:
        logger.error(f"Error logging prompt: {str(e)}")
        return None

def log_generation_output(prompt_id, output_text, content_id=None, status='completed', metadata=None):
    """Log a generation output to Supabase."""
    if not supabase:
        logger.error("Supabase client not initialized")
        return False

    try:
        # Limit text size for database storage
        truncated_text = output_text[:10000] if len(output_text) > 10000 else output_text

        output_data = {
            'prompt_id': prompt_id,
            'output_text': truncated_text,
            'content_id': content_id,
            'status': status,
            'metadata': json.dumps(metadata) if metadata else None,
            'created_at': datetime.datetime.now().isoformat()
        }

        result = supabase.table('generation_outputs').insert(output_data).execute()
        output_id = result.data[0]['id'] if result.data else None
        logger.info(f"Logged generation output with ID: {output_id}")

        # If output text is very large, store it in a separate content_files table
        if len(output_text) > 10000 and output_id:
            file_data = {
                'output_id': output_id,
                'content_type': 'text/markdown',
                'file_content': output_text,
                'created_at': datetime.datetime.now().isoformat()
            }
            file_result = supabase.table('content_files').insert(file_data).execute()
            file_id = file_result.data[0]['id'] if file_result.data else None
            logger.info(f"Stored full content in content_files with ID: {file_id}")

        return output_id
    except Exception as e:
        logger.error(f"Error logging generation output: {str(e)}")
        return None

def get_content_inventory(content_id=None, section=None, status=None):
    """Get content inventory from Supabase."""
    if not supabase:
        logger.error("Supabase client not initialized")
        return []

    try:
        # Start with a base query
        query = supabase.table('content_inventory').select('*')

        # Apply filters
        if content_id:
            query = query.filter('content_id', 'eq', content_id)

        if section:
            query = query.filter('section', 'eq', section)

        if status:
            query = query.filter('status', 'eq', status)

        # Execute the query
        result = query.execute()
        return result.data
    except Exception as e:
        logger.error(f"Error getting content inventory: {str(e)}")
        return []

def update_content_status(content_id, status, metadata=None):
    """Update content status in Supabase."""
    if not supabase:
        logger.error("Supabase client not initialized")
        return False

    try:
        update_data = {
            'status': status,
            'updated_at': datetime.datetime.now().isoformat()
        }

        if metadata:
            update_data['metadata'] = json.dumps(metadata)

        result = supabase.table('content_inventory').update(update_data).filter('content_id', 'eq', content_id).execute()

        logger.info(f"Updated status for content ID {content_id} to {status}")
        return True
    except Exception as e:
        logger.error(f"Error updating content status: {str(e)}")
        return False

def get_prompt_logs(session_id=None, content_id=None, limit=100):
    """Get prompt logs from Supabase."""
    if not supabase:
        logger.error("Supabase client not initialized")
        return []

    try:
        query = supabase.table('prompt_logs').select('*')

        if session_id:
            query = query.filter('session_id', 'eq', session_id)

        if content_id:
            query = query.filter('content_id', 'eq', content_id)

        result = query.order('created_at', desc=True).limit(limit).execute()
        return result.data
    except Exception as e:
        logger.error(f"Error getting prompt logs: {str(e)}")
        return []

def get_generation_outputs(prompt_id=None, content_id=None, limit=100):
    """Get generation outputs from Supabase."""
    if not supabase:
        logger.error("Supabase client not initialized")
        return []

    try:
        query = supabase.table('generation_outputs').select('*')

        if prompt_id:
            query = query.filter('prompt_id', 'eq', prompt_id)

        if content_id:
            query = query.filter('content_id', 'eq', content_id)

        result = query.order('created_at', desc=True).limit(limit).execute()
        return result.data
    except Exception as e:
        logger.error(f"Error getting generation outputs: {str(e)}")
        return []

def get_full_content(output_id):
    """Get full content from content_files table."""
    if not supabase:
        logger.error("Supabase client not initialized")
        return None

    try:
        result = supabase.table('content_files').select('file_content').filter('output_id', 'eq', output_id).execute()
        if result.data:
            return result.data[0]['file_content']
        return None
    except Exception as e:
        logger.error(f"Error getting full content: {str(e)}")
        return None

def get_content_by_id(content_id):
    """Get content details by ID."""
    if not supabase:
        logger.error("Supabase client not initialized")
        return None

    try:
        result = supabase.table('content_inventory').select('*').filter('content_id', 'eq', content_id).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        logger.error(f"Error getting content by ID: {str(e)}")
        return None

def update_content_item(content_id, data):
    """Update content item in Supabase.

    Args:
        content_id: Content ID to update
        data: Dictionary of fields to update

    Returns:
        Boolean indicating success
    """
    if not supabase:
        logger.error("Supabase client not initialized")
        return False

    try:
        # Add updated_at timestamp
        update_data = data.copy()
        update_data['updated_at'] = datetime.datetime.now().isoformat()

        # Update in Supabase
        result = supabase.table('content_inventory').update(update_data).filter('content_id', 'eq', content_id).execute()

        if not result.data:
            logger.error(f"Failed to update content item {content_id}")
            return False

        logger.info(f"Updated content item {content_id}")
        return True
    except Exception as e:
        logger.error(f"Error updating content item: {str(e)}")
        return False

def get_content_versions(content_id):
    """Get content versions from Supabase.

    Args:
        content_id: Content ID to get versions for

    Returns:
        List of content versions
    """
    if not supabase:
        logger.error("Supabase client not initialized")
        return []

    try:
        # Check if content_versions table exists
        try:
            # Query content_versions table
            result = supabase.table('content_versions').select('*').filter('content_id', 'eq', content_id).order('version_number', desc=True).execute()

            if not result.data:
                logger.info(f"No content versions found for {content_id}")
                return []

            return result.data
        except Exception as table_error:
            if "relation \"public.content_versions\" does not exist" in str(table_error):
                logger.warning("content_versions table does not exist. Please create it using the SQL script.")
                return []
            else:
                # Re-raise if it's a different error
                raise
    except Exception as e:
        logger.error(f"Error getting content versions: {str(e)}")
        return []

def save_content_version(content_id, content_text, model=None, temperature=None, metadata=None):
    """Save a new content version.

    Args:
        content_id: Content ID
        content_text: Content text
        model: Model used to generate content
        temperature: Temperature used to generate content
        metadata: Additional metadata

    Returns:
        Version number if successful, None otherwise
    """
    if not supabase:
        logger.error("Supabase client not initialized")
        return None

    try:
        # Get latest version number
        versions = get_content_versions(content_id)
        version_number = 1
        if versions:
            version_number = versions[0]['version_number'] + 1

        # Prepare data
        data = {
            'content_id': content_id,
            'version_number': version_number,
            'content_text': content_text,
            'created_at': datetime.datetime.now().isoformat()
        }

        if model:
            data['model'] = model

        if temperature:
            data['temperature'] = float(temperature)

        if metadata:
            data['metadata'] = json.dumps(metadata) if isinstance(metadata, dict) else metadata

        try:
            # Insert into Supabase
            result = supabase.table('content_versions').insert(data).execute()

            if not result.data:
                logger.error(f"Failed to save content version for {content_id}")
                return None

            logger.info(f"Saved content version {version_number} for {content_id}")
            return version_number
        except Exception as table_error:
            if "relation \"public.content_versions\" does not exist" in str(table_error):
                logger.warning("content_versions table does not exist. Please create it using the SQL script.")
                # Save to local file as fallback
                os.makedirs('content_versions', exist_ok=True)
                file_path = f'content_versions/{content_id}_v{version_number}.md'
                with open(file_path, 'w') as f:
                    f.write(content_text)
                logger.info(f"Saved content version {version_number} for {content_id} to local file {file_path}")
                return version_number
            else:
                # Re-raise if it's a different error
                raise
    except Exception as e:
        logger.error(f"Error saving content version: {str(e)}")
        return None

def get_available_models():
    """Get list of available models.

    Returns:
        List of model names
    """
    # This could be fetched from a database or API in the future
    return [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-2.0-flash",
        "gemini-2.5-pro-exp-03-25"  # Use the experimental version that has a free tier
    ]

if __name__ == '__main__':
    # Test connection
    if is_connected():
        print("Connected to Supabase")

        # Create tables
        create_tables()

        # Import content inventory
        if os.path.exists('AI_Hub_Content_Inventory_Enhanced.csv'):
            print("Importing content inventory from AI_Hub_Content_Inventory_Enhanced.csv...")
            import_content_inventory_from_csv('AI_Hub_Content_Inventory_Enhanced.csv')
        else:
            print("AI_Hub_Content_Inventory_Enhanced.csv not found")
    else:
        print("Not connected to Supabase")
