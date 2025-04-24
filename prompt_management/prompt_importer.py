#!/usr/bin/env python3
"""
Import prompts from existing prompt logs in the database.

This script extracts unique prompts from the prompt logs table and imports them
into the prompt management system.
"""

import logging
import os
import sys
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from supabase_client import get_prompt_logs
from prompt_management import PromptTemplate, create_prompt_template, get_prompt_templates

def extract_variables_from_prompt(prompt_text):
    """Extract variables from a prompt text using {{variable}} pattern."""
    import re
    variables = []
    # Find all occurrences of {{variable_name}}
    matches = re.finditer(r'{{(.*?)}}', prompt_text)
    for match in matches:
        variable_name = match.group(1).strip()
        if variable_name and variable_name not in [v['name'] for v in variables]:
            variables.append({
                'name': variable_name,
                'description': f'Variable for {variable_name}',
                'type': 'string'
            })
    return variables

def import_prompts_from_database():
    """Import prompts from existing prompt logs in the database."""
    logger.info("Starting prompt import from database...")

    # Get all unique prompts from the database
    prompt_logs = get_prompt_logs(limit=1000)
    logger.info(f"Retrieved {len(prompt_logs)} prompt logs from database")

    # Get existing prompt templates to avoid duplicates
    existing_templates = get_prompt_templates()
    existing_texts = [template.get('template_text', '') for template in existing_templates]

    # Create a dictionary to deduplicate prompts by their text
    unique_prompts = {}
    for log in prompt_logs:
        prompt_text = log.get('prompt_text', '')
        prompt_type = log.get('prompt_type', 'General')

        if not prompt_text or len(prompt_text) < 10:
            continue

        if prompt_text in existing_texts:
            logger.info(f"Skipping already imported prompt: {prompt_text[:50]}...")
            continue

        if prompt_text not in unique_prompts:
            unique_prompts[prompt_text] = {
                'text': prompt_text,
                'type': prompt_type,
                'content_id': log.get('content_id'),
                'model': log.get('model'),
                'created_at': log.get('created_at')
            }

    logger.info(f"Found {len(unique_prompts)} unique prompts to import")

    # Import unique prompts into the prompt management system
    imported_count = 0
    for prompt_data in unique_prompts.values():
        # Try to extract a name from the first line of the prompt
        first_line = prompt_data['text'].split('\n')[0].strip()
        # If first line is empty or just whitespace, try the second line
        if not first_line and len(prompt_data['text'].split('\n')) > 1:
            first_line = prompt_data['text'].split('\n')[1].strip()
        # If still empty, use the prompt type and content ID
        if not first_line:
            first_line = f"{prompt_data['type']} prompt for {prompt_data['content_id']}"
        name = first_line[:50] if len(first_line) <= 50 else first_line[:47] + '...'

        # Extract variables from the prompt
        variables = extract_variables_from_prompt(prompt_data['text'])

        template = PromptTemplate(
            name=name,
            description=f"Prompt used for {prompt_data['content_id']} with {prompt_data['model']}",
            category=prompt_data['type'],
            template_text=prompt_data['text'],
            tags={
                'content_id': prompt_data['content_id'],
                'model': prompt_data['model'],
                'imported_from': 'prompt_logs'
            },
            variables=variables
        )
        template.is_active = True

        template_id = create_prompt_template(template)
        if template_id:
            logger.info(f"Imported prompt: {name}")
            imported_count += 1
        else:
            logger.error(f"Failed to import prompt: {name}")

    logger.info(f"Imported {imported_count} prompts successfully.")
    return imported_count

if __name__ == "__main__":
    import_prompts_from_database()
