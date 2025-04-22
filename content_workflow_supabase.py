#!/usr/bin/env python3
"""
Content workflow script with Supabase integration.
This script integrates the content generation workflow with Supabase for content inventory and prompt logging.
"""

import os
import json
import uuid
import argparse
import datetime
import logging
import re
from dotenv import load_dotenv

# Import our custom modules
from google_ai_client import generate_content, generate_json
from supabase_client import (
    is_connected, get_content_inventory, update_content_status,
    log_prompt, log_generation_output, get_prompt_logs, get_generation_outputs
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_prompt(content_item):
    """Create a prompt for the Google Generative AI API based on content item."""
    content_id = content_item['content_id']
    title = content_item['title']
    content_type = content_item['content_type']
    audience_level = content_item['audience_technical_level']
    audience_role = content_item['audience_role']
    audience_constraints = content_item['audience_constraints']
    primary_mission_pillar_1 = content_item['primary_mission_pillar_1']
    primary_mission_pillar_2 = content_item.get('primary_mission_pillar_2', '')
    secondary_mission_pillars = content_item.get('secondary_mission_pillars', '')
    smart_objectives = content_item['smart_objectives']
    practical_components = content_item['practical_components']

    # Create a list of mission pillars
    mission_pillars = [p for p in [primary_mission_pillar_1, primary_mission_pillar_2] if p]
    if secondary_mission_pillars:
        secondary_pillars = [p.strip() for p in secondary_mission_pillars.split(',')]
        mission_pillars.extend(secondary_pillars)

    # Create the prompt
    prompt = f"""
    Create a comprehensive {content_type} on "{title}" for a {audience_level} audience.

    Content ID: {content_id}

    Target Audience:
    - Technical Level: {audience_level}
    - Role/Context: {audience_role}
    - Resource Constraints: {audience_constraints}

    The content should integrate the following mission pillars:
    {', '.join(mission_pillars)}

    SMART Objectives:
    {smart_objectives}

    Practical Components to include:
    {practical_components}

    The content should include:
    1. An introduction that explains the topic and its importance
    2. Main content sections that cover key concepts, how it works, applications, and limitations
    3. For each mission pillar, include a dedicated section that discusses how the topic relates to that pillar
    4. A conclusion that summarizes key points and provides next steps

    Format the content in Markdown with clear headings, bullet points, and numbered lists where appropriate.

    The content should be educational, informative, and engaging for the specified audience.

    IMPORTANT: Start directly with the content. Do not include any introductory phrases like "Here is..." or "I've created..." or "Okay, here is...". The content should begin immediately with the title or first section.
    """

    return prompt

def create_sources_prompt(content):
    """Create a prompt for generating sources."""
    # Limit content to first 2000 chars to avoid token limits
    content_excerpt = content[:2000]

    prompt = f"""
    Based on the following content, recommend 5 high-quality academic sources that would be relevant for citation.

    Content:
    {content_excerpt}

    For each source, provide:
    1. A unique ID (e.g., "author2023title")
    2. The full title
    3. The authors (full names)
    4. The publication year
    5. The venue (journal, conference, etc.)
    6. A URL if available
    7. The full citation in APA format

    Make sure the sources are:
    - Recent (within the last 5 years when possible)
    - Relevant to the content
    - From reputable venues
    - Properly formatted
    - Diverse (from different authors/institutions)

    IMPORTANT: Provide the sources directly in JSON format. Do not include any introductory phrases like "Here are the sources..." or "I've found these sources...". Just return the JSON array of sources.
    """

    return prompt

def clean_generated_content(content):
    """Remove meta-commentary from the beginning of generated content."""
    # Common patterns to remove
    patterns = [
        r"^Okay, here is a comprehensive .+?\n\n",
        r"^Here is the .+?\n\n",
        r"^I've created a .+?\n\n",
        r"^Below is a .+?\n\n",
        r"^As requested, here is .+?\n\n",
        r"^This is a .+?\n\n"
    ]

    for pattern in patterns:
        content = re.sub(pattern, "", content, flags=re.DOTALL)

    return content

def add_sources_to_content(content, sources):
    """Add sources to content."""
    # Add sources section to content
    content_with_sources = content + "\n\n## Sources\n\n"

    for source in sources:
        content_with_sources += f"[{source['id']}] {source['citation']}\n\n"

    # Add source collection metadata
    content_with_sources += "\n## Source Collection Metadata\n\n"
    content_with_sources += "This content includes sources collected through the Source Collection and Documentation Module of the Agentic AI Content Creation System.\n\n"
    content_with_sources += f"**Collection Date**: {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n"
    content_with_sources += "**Source Types**:\n"
    content_with_sources += "- Academic papers\n"
    content_with_sources += "- Industry reports\n"
    content_with_sources += "- Technical documentation\n\n"
    content_with_sources += "**Source Evaluation Criteria**:\n"
    content_with_sources += "- Relevance to the topic\n"
    content_with_sources += "- Authority of the source\n"
    content_with_sources += "- Recency of the information\n"
    content_with_sources += "- Accuracy and reliability\n"

    return content_with_sources

def check_dependencies(content_id):
    """Check if all dependencies for a content item are completed."""
    # Get content item
    content_items = get_content_inventory(content_id=content_id)
    if not content_items:
        logger.error(f"Content item with ID {content_id} not found")
        return False, []

    content_item = content_items[0]

    # Check if there are dependencies
    dependencies_str = content_item.get('dependencies', '')
    if not dependencies_str or dependencies_str.lower() == 'none':
        return True, []  # No dependencies

    # Parse dependencies
    dependencies = [dep.strip() for dep in dependencies_str.split(',')]

    # Check status of each dependency
    incomplete_deps = []
    for dep_id in dependencies:
        dep_items = get_content_inventory(content_id=dep_id)
        if not dep_items:
            logger.warning(f"Dependency {dep_id} not found in inventory")
            incomplete_deps.append(f"{dep_id} (Not Found)")
            continue

        dep_item = dep_items[0]
        if dep_item['status'] != 'Completed':
            incomplete_deps.append(f"{dep_id} ({dep_item['status']})")

    if incomplete_deps:
        return False, incomplete_deps

    return True, []

def generate_content_for_item(content_id, model_name="gemini-1.5-flash", temperature=0.7, output_dir="generated_content", force=False):
    """Generate content for a specific content item."""
    # Check Supabase connection
    if not is_connected():
        logger.error("Not connected to Supabase")
        return False

    # Get content item
    content_items = get_content_inventory(content_id=content_id)
    if not content_items:
        logger.error(f"Content item with ID {content_id} not found")
        return False

    content_item = content_items[0]
    logger.info(f"Generating content for: {content_item['title']} ({content_id})")

    # Check if content is already completed
    if content_item['status'] == 'Completed':
        logger.warning(f"Content item {content_id} is already completed")
        if not force:
            logger.info("Use --force to regenerate completed content")
            return False
        logger.info("Forcing regeneration of completed content")

    # Check dependencies
    if not force:
        deps_met, incomplete_deps = check_dependencies(content_id)
        if not deps_met:
            logger.error(f"Dependencies not met for {content_id}:")
            for dep in incomplete_deps:
                logger.error(f"  - {dep}")
            logger.info("Use --force to ignore dependencies")
            return False

    # Create session ID
    session_id = str(uuid.uuid4())

    # Update content status
    update_content_status(content_id, "In Progress", {
        "session_id": session_id,
        "start_time": datetime.datetime.now().isoformat()
    })

    try:
        # Step 1: Create prompt
        prompt = create_prompt(content_item)

        # Log prompt
        prompt_id = log_prompt(
            session_id=session_id,
            prompt_type="content_generation",
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
            return False

        # Step 2: Generate content
        logger.info(f"Generating content using model: {model_name}")
        raw_content = generate_content(
            prompt=prompt,
            model_name=model_name,
            temperature=temperature
        )

        # Clean the generated content
        content = clean_generated_content(raw_content)

        # Log generation output
        output_id = log_generation_output(
            prompt_id=prompt_id,
            output_text=content,
            content_id=content_id,
            status="completed",
            metadata={
                "model": model_name,
                "temperature": temperature,
                "type": "content"
            }
        )

        if not output_id:
            logger.error("Failed to log generation output")
            update_content_status(content_id, "Failed", {
                "session_id": session_id,
                "error": "Failed to log generation output"
            })
            return False

        # Step 3: Generate sources
        logger.info("Generating sources")
        sources_prompt = create_sources_prompt(content)

        # Log sources prompt
        sources_prompt_id = log_prompt(
            session_id=session_id,
            prompt_type="sources_generation",
            prompt_text=sources_prompt,
            model=model_name,
            temperature=0.2,
            content_id=content_id
        )

        # Define the expected schema for the sources
        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "title": {"type": "string"},
                    "authors": {"type": "array", "items": {"type": "string"}},
                    "year": {"type": ["number", "string"]},
                    "venue": {"type": "string"},
                    "url": {"type": "string"},
                    "citation": {"type": "string"}
                },
                "required": ["id", "title", "authors", "year", "venue", "citation"]
            }
        }

        # Generate sources
        sources = generate_json(
            prompt=sources_prompt,
            schema=schema,
            model_name=model_name,
            temperature=0.2
        )

        # Log sources output
        sources_output_id = log_generation_output(
            prompt_id=sources_prompt_id,
            output_text=json.dumps(sources, indent=2),
            content_id=content_id,
            status="completed",
            metadata={
                "model": model_name,
                "temperature": 0.2,
                "type": "sources"
            }
        )

        # Step 4: Add sources to content
        logger.info("Adding sources to content")
        content_with_sources = add_sources_to_content(content, sources)

        # Log final content
        final_output_id = log_generation_output(
            prompt_id=prompt_id,
            output_text=content_with_sources,
            content_id=content_id,
            status="completed",
            metadata={
                "model": model_name,
                "temperature": temperature,
                "type": "content_with_sources"
            }
        )

        # Save content to file
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{content_id}.md")
        with open(output_file, 'w') as f:
            f.write(content_with_sources)

        logger.info(f"Content saved to {output_file}")

        # Update content status
        update_content_status(content_id, "Completed", {
            "session_id": session_id,
            "end_time": datetime.datetime.now().isoformat(),
            "output_file": output_file,
            "output_id": final_output_id
        })

        return True
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        update_content_status(content_id, "Failed", {
            "session_id": session_id,
            "error": str(e)
        })
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate content for a specific content item.")
    parser.add_argument("--content-id", required=True, help="Content ID to generate content for")
    parser.add_argument("--model", default="gemini-1.5-flash", help="Model name")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature for generation")
    parser.add_argument("--output-dir", default="generated_content", help="Output directory")
    parser.add_argument("--force", action="store_true", help="Force generation even if dependencies are not met or content is already completed")
    parser.add_argument("--check-deps-only", action="store_true", help="Only check dependencies without generating content")

    args = parser.parse_args()

    # Check dependencies only
    if args.check_deps_only:
        deps_met, incomplete_deps = check_dependencies(args.content_id)
        if deps_met:
            print(f"All dependencies for {args.content_id} are met.")
            return True
        else:
            print(f"Dependencies not met for {args.content_id}:")
            for dep in incomplete_deps:
                print(f"  - {dep}")
            return False

    # Generate content
    success = generate_content_for_item(
        content_id=args.content_id,
        model_name=args.model,
        temperature=args.temperature,
        output_dir=args.output_dir,
        force=args.force
    )

    # Exit with appropriate status code
    import sys
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
