#!/usr/bin/env python3
"""
Enhanced content workflow with AI-based reference management.

This module extends the content generation workflow to use AI for generating,
structuring, and validating references for content.
"""

import os
import re
import json
import logging
import datetime
import argparse
from typing import Dict, List, Tuple, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import our custom modules
from workflows.content_workflow_supabase import generate_content_for_item as original_generate_content
from workflows.content_workflow_supabase import create_prompt, clean_generated_content, update_content_status
from reference_management.ai_reference_processor import (
    process_reference_with_ai, process_references_batch,
    store_processed_references, generate_references_for_content,
    format_references_as_markdown
)
from reference_management.reference_management import get_content_references
from core.supabase_client import (
    is_connected, get_content_inventory, log_prompt,
    log_generation_output, get_generation_outputs
)

def create_content_with_references_prompt(content_item: Dict[str, Any]) -> str:
    """
    Create a prompt for generating content with structured references.

    Args:
        content_item: Content item dictionary

    Returns:
        Prompt text
    """
    # Get the base prompt
    base_prompt = create_prompt(content_item)

    # Add instructions for structured references
    references_instructions = """
    IMPORTANT: At the end of your response, include a section titled "REFERENCES_JSON" that contains
    all references used in a JSON array format. Each reference should have the following structure:

    {
        "title": "The full title of the work",
        "authors": "Author names in the format 'Last, First M.; Last, First M.'",
        "publication_date": "YYYY-MM-DD",
        "publication_name": "Name of journal/book/website",
        "url": "Full URL if available",
        "doi": "DOI if available (just the DOI, not the URL)",
        "reference_type": "One of: Journal Article, Book, Book Chapter, Conference Paper, Report, Thesis, Website, Encyclopedia, Other",
        "citation_context": "Brief description of how this reference was used in the content",
        "apa_citation": "The reference formatted in APA 7th edition style"
    }

    Make sure all references are real, verifiable sources. Do not make up references.
    Ensure each reference is properly formatted according to APA 7th edition style.
    """

    # Combine prompts
    full_prompt = f"{base_prompt}\n\n{references_instructions}"

    return full_prompt

def extract_references_json(content: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Extract JSON references from content and remove the JSON section.

    Args:
        content: Content text with JSON references

    Returns:
        Tuple of (content without JSON section, list of reference dictionaries)
    """
    # Split content at the REFERENCES_JSON marker
    parts = content.split("REFERENCES_JSON")

    if len(parts) < 2:
        return content, []

    # Clean content is the first part
    clean_content = parts[0].strip()

    # Try to extract JSON from the second part
    references_text = parts[1].strip()

    try:
        # Find JSON array in the text
        json_match = re.search(r'\[(.*?)\]', references_text, re.DOTALL)
        if json_match:
            references_json = json_match.group(0)
            references = json.loads(references_json)
        else:
            # Try to parse the entire text as JSON
            references = json.loads(references_text)
            if not isinstance(references, list):
                references = [references]
    except (json.JSONDecodeError, ValueError):
        # If JSON parsing fails, return empty list
        references = []

    return clean_content, references

def generate_content_for_item(content_id: str, model_name: str = "gemini-1.5-flash",
                             temperature: float = 0.7, output_dir: str = "generated_content",
                             force: bool = False, debug: bool = False,
                             use_ai_references: bool = True) -> Tuple[bool, Optional[str]]:
    """
    Generate content for a specific content item with AI-based reference management.

    Args:
        content_id: Content ID
        model_name: Model name to use for generation
        temperature: Temperature for generation
        output_dir: Directory to save generated content
        force: Whether to force regeneration even if dependencies are not met
        debug: Whether to print debug information
        use_ai_references: Whether to use AI for reference generation

    Returns:
        Tuple of (success, content_text)
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return False, None

    # Get content item
    content_items = get_content_inventory(content_id=content_id)
    if not content_items:
        logger.error(f"Content item with ID {content_id} not found")
        return False, None

    content_item = content_items[0]
    logger.info(f"Generating content with AI references for: {content_item['title']} ({content_id})")

    # If use_ai_references is False, use the original function
    if not use_ai_references:
        success = original_generate_content(
            content_id=content_id,
            model_name=model_name,
            temperature=temperature,
            output_dir=output_dir,
            force=force,
            debug=debug
        )
        return success, None

    # Create session ID for tracking
    import uuid
    session_id = str(uuid.uuid4())

    # Update content status
    update_content_status(content_id, "In Progress", {
        "session_id": session_id,
        "start_time": datetime.datetime.now().isoformat()
    })

    try:
        # Step 1: Create prompt with reference instructions
        prompt = create_content_with_references_prompt(content_item)

        # Log prompt
        prompt_id = log_prompt(
            session_id=session_id,
            prompt_type="content_generation_with_references",
            prompt_text=prompt,
            model=model_name,
            temperature=temperature,
            content_id=content_id
        )

        if not prompt_id:
            logger.error("Failed to log prompt")
            update_content_status(content_id, "Failed", {
                "session_id": session_id,
                "error": "Failed to log prompt"
            })
            return False, None

        # Step 2: Generate content with references
        logger.info(f"Generating content with references using model: {model_name}")

        from core.google_ai_client import generate_content as generate_ai_content

        raw_content = generate_ai_content(
            prompt=prompt,
            model_name=model_name,
            temperature=temperature
        )

        # Clean the generated content and extract references
        content_with_refs = clean_generated_content(raw_content)
        content, references = extract_references_json(content_with_refs)

        # Log generation output
        output_id = log_generation_output(
            prompt_id=prompt_id,
            output_text=content,
            content_id=content_id,
            status="completed",
            metadata={
                "model": model_name,
                "temperature": temperature,
                "type": "content_with_ai_references"
            }
        )

        # Step 3: Process and store references
        if references:
            logger.info(f"Found {len(references)} references in AI response")

            # Store references in database
            reference_ids = store_processed_references(content_id, references)
            logger.info(f"Stored {len(reference_ids)} references for content {content_id}")

            # Format references as Markdown
            references_markdown = format_references_as_markdown(references)

            # Add references to content
            content_with_references = f"{content}\n{references_markdown}"
        else:
            # If no references in AI response, generate them separately
            logger.info("No references found in AI response, generating separately")

            # Generate references based on content
            generated_references = generate_references_for_content(
                content_text=content,
                topic=content_item['title'],
                model_name=model_name
            )

            if generated_references:
                logger.info(f"Generated {len(generated_references)} references")

                # Store references in database
                reference_ids = store_processed_references(content_id, generated_references)
                logger.info(f"Stored {len(reference_ids)} references for content {content_id}")

                # Format references as Markdown
                references_markdown = format_references_as_markdown(generated_references)

                # Add references to content
                content_with_references = f"{content}\n{references_markdown}"
            else:
                logger.warning("Failed to generate references")
                content_with_references = content

        # Log final content with references
        final_output_id = log_generation_output(
            prompt_id=prompt_id,
            output_text=content_with_references,
            content_id=content_id,
            status="completed",
            metadata={
                "model": model_name,
                "temperature": temperature,
                "type": "content_with_formatted_references"
            }
        )

        # Save content to file
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{content_id}.md")
        with open(output_file, 'w') as f:
            f.write(content_with_references)

        logger.info(f"Content with AI references saved to {output_file}")

        # Update content status
        update_content_status(content_id, "Completed", {
            "session_id": session_id,
            "end_time": datetime.datetime.now().isoformat(),
            "output_file": output_file,
            "output_id": final_output_id
        })

        return True, content_with_references

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error generating content with AI references: {error_msg}")

        if debug:
            print(f"ERROR: Failed in content generation workflow: {error_msg}")
            print(f"DEBUG: Content ID: {content_id}")
            print(f"DEBUG: Model: {model_name}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")

        update_content_status(content_id, "Failed", {
            "session_id": session_id,
            "error": error_msg,
            "error_type": type(e).__name__
        })
        return False, None

def process_existing_references(content_id: str, model_name: str = "gemini-1.5-flash", batch_size: int = 10, rate_limit_delay: float = 4.0) -> bool:
    """
    Process existing references for a content item using AI.

    Args:
        content_id: Content ID
        model_name: Model name to use for processing

    Returns:
        True if successful, False otherwise
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return False

    try:
        # Get content item
        content_items = get_content_inventory(content_id=content_id)
        if not content_items:
            logger.error(f"Content item with ID {content_id} not found")
            return False

        content_item = content_items[0]

        # Get generation outputs for the content
        outputs = get_generation_outputs(content_id=content_id, limit=1)
        if not outputs:
            logger.error(f"No generation outputs found for content {content_id}")
            return False

        output = outputs[0]
        content_text = output.get('output_text', '')

        if not content_text:
            logger.error(f"No content text found for output {output.get('id')}")
            return False

        # Extract references section
        references_section_match = re.search(
            r'(?:References|Sources|Bibliography|Works Cited)[\s\n]*:?([\s\S]+)$',
            content_text,
            re.IGNORECASE
        )

        if not references_section_match:
            logger.warning(f"No references section found in content {content_id}")
            return False

        references_text = references_section_match.group(1).strip()

        # Split into individual references
        reference_items = re.split(r'\n\s*(?:\[\w+\]|\d+\.|\*)\s+', references_text)
        reference_items = [item.strip() for item in reference_items if item.strip()]

        if not reference_items:
            logger.warning(f"No reference items found in content {content_id}")
            return False

        logger.info(f"Found {len(reference_items)} reference items in content {content_id}")

        # Process references in batches to avoid overwhelming the API
        all_processed_references = []
        for i in range(0, len(reference_items), batch_size):
            batch = reference_items[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(reference_items) + batch_size - 1)//batch_size}")
            processed_batch = process_references_batch(batch, model_name, rate_limit_delay)
            all_processed_references.extend(processed_batch)

            # Add a delay between batches
            if i + batch_size < len(reference_items):
                import time
                logger.info(f"Waiting 10 seconds between batches...")
                time.sleep(10)

        processed_references = all_processed_references

        # Store processed references
        reference_ids = store_processed_references(content_id, processed_references)

        logger.info(f"Processed and stored {len(reference_ids)} references for content {content_id}")

        return True

    except Exception as e:
        logger.error(f"Error processing existing references: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate content with AI-based reference management.")
    parser.add_argument("--content-id", required=True, help="Content ID to generate content for")
    parser.add_argument("--model", default="gemini-1.5-flash", help="Model name")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature for generation")
    parser.add_argument("--output-dir", default="generated_content", help="Output directory")
    parser.add_argument("--force", action="store_true", help="Force generation even if dependencies are not met or content is already completed")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--process-existing", action="store_true", help="Process existing references instead of generating new content")

    args = parser.parse_args()

    if args.process_existing:
        success = process_existing_references(
            content_id=args.content_id,
            model_name=args.model
        )
    else:
        success, _ = generate_content_for_item(
            content_id=args.content_id,
            model_name=args.model,
            temperature=args.temperature,
            output_dir=args.output_dir,
            force=args.force,
            debug=args.debug,
            use_ai_references=True
        )

    # Exit with appropriate status code
    import sys
    sys.exit(0 if success else 1)
