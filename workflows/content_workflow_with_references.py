#!/usr/bin/env python3
"""
Enhanced content workflow with automatic reference management.

This module extends the content generation workflow to automatically extract
references from generated content and store them in the reference management system.
"""

import os
import re
import logging
import datetime
from typing import List, Dict, Tuple, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import our custom modules
from workflows.content_workflow_supabase import generate_content_for_item as original_generate_content
from reference_management.reference_management import (
    Reference, ReferenceQuality, create_reference, link_reference_to_content,
    get_references, get_content_references
)

def extract_reference_from_text(text: str) -> Dict[str, Any]:
    """Extract reference information from text.

    Args:
        text: Reference text to parse

    Returns:
        Dictionary with extracted reference information
    """
    # This is a simplified example - adapt to your reference format
    # Example format: Author(s). (Year). Title. Publication. URL/DOI

    # Try to extract author
    author_match = re.search(r'^([^\.]+)\.', text)
    authors = author_match.group(1).strip() if author_match else "Unknown"

    # Try to extract year
    year_match = re.search(r'\((\d{4})\)', text)
    year = year_match.group(1) if year_match else None

    # Try to extract title
    title_match = re.search(r'\(\d{4}\)\.\s+([^\.]+)\.', text)
    if title_match:
        title = title_match.group(1).strip()
    else:
        # If no year or standard format, just use the first sentence or part of text
        title_alt_match = re.search(r'^[^\.]+\.\s+([^\.]+)\.', text)
        title = title_alt_match.group(1).strip() if title_alt_match else text[:100]

    # Try to extract publication
    pub_match = re.search(r'\.\s+([^\.]+)\.\s+(?:https?|doi|Retrieved)', text, re.IGNORECASE)
    publication = pub_match.group(1).strip() if pub_match else "Unknown"

    # Try to extract URL/DOI
    url_match = re.search(r'(https?://[^\s]+|doi:[^\s]+)', text, re.IGNORECASE)
    url = url_match.group(1) if url_match else None

    # Try to extract DOI separately
    doi_match = re.search(r'doi:([^\s]+)', text, re.IGNORECASE) or re.search(r'https?://doi.org/([^\s]+)', text, re.IGNORECASE)
    doi = doi_match.group(1) if doi_match else None

    return {
        'authors': authors,
        'publication_date': f"{year}-01-01" if year else None,
        'title': title,
        'publication_name': publication,
        'url': url,
        'doi': doi,
        'reference_type': 'Article',  # Default type
        'content': text,  # Store original text
        'abstract': "Automatically extracted from generated content",
        'is_active': True
    }

def extract_references_from_content(content_text: str) -> List[str]:
    """Extract references from content text.

    Args:
        content_text: Content text to extract references from

    Returns:
        List of reference text strings
    """
    # Look for references section
    references_section_match = re.search(
        r'(?:References|Sources|Bibliography|Works Cited)[\s\n]*:?([\s\S]+)$',
        content_text,
        re.IGNORECASE
    )

    if not references_section_match:
        return []

    references_text = references_section_match.group(1).strip()

    # Split into individual references
    # This regex looks for patterns like [1], [SRC1], etc. or numbered items
    reference_items = re.split(r'\n\s*(?:\[\w+\]|\d+\.)\s+', references_text)
    # Remove empty items and the first item if it's empty (from the split)
    reference_items = [item.strip() for item in reference_items if item.strip()]

    return reference_items

def store_references_in_database(content_id: str, reference_items: List[str]) -> List[str]:
    """Store references in the database and link them to content.

    Args:
        content_id: Content ID to link references to
        reference_items: List of reference text strings

    Returns:
        List of reference IDs
    """
    # Get existing references to avoid duplicates
    existing_references = get_references()
    existing_titles = [ref.get('title', '').lower() for ref in existing_references]

    reference_ids = []
    for i, ref_text in enumerate(reference_items):
        # Extract reference data
        ref_data = extract_reference_from_text(ref_text)

        # Skip if title already exists
        if ref_data['title'].lower() in existing_titles:
            logger.info(f"Skipping duplicate reference: {ref_data['title']}")

            # Find the existing reference ID
            for ref in existing_references:
                if ref.get('title') and ref.get('title').lower() == ref_data['title'].lower():
                    # Link existing reference to content
                    citation_key = f"REF{i+1}"
                    link_id = link_reference_to_content(
                        content_id=content_id,
                        reference_id=ref.get('id'),
                        citation_key=citation_key,
                        citation_context="Extracted from generated content"
                    )

                    if link_id:
                        reference_ids.append(ref.get('id'))
                        logger.info(f"Linked existing reference: {ref_data['title']} to content {content_id}")
                    else:
                        logger.error(f"Failed to link existing reference {ref.get('id')} to content {content_id}")

                    break

            continue

        # Create reference object
        ref = Reference(
            title=ref_data['title'],
            authors=ref_data['authors'],
            publication_date=ref_data['publication_date'],
            publication_name=ref_data['publication_name'],
            url=ref_data['url'],
            doi=ref_data['doi'],
            reference_type=ref_data['reference_type'],
            content=ref_data['content'],
            abstract=ref_data['abstract'],
            is_active=ref_data['is_active']
        )

        # Create quality assessment
        quality = ReferenceQuality(
            currency_score=4,  # Default values
            relevance_score=5,
            authority_score=4,
            accuracy_score=4,
            purpose_score=4,
            assessment_notes="Automatically assessed during content generation"
        )
        ref.quality_assessment = quality

        # Store reference in database
        reference_id = create_reference(ref)
        if reference_id:
            # Link reference to content
            citation_key = f"REF{i+1}"
            link_id = link_reference_to_content(
                content_id=content_id,
                reference_id=reference_id,
                citation_key=citation_key,
                citation_context="Extracted from generated content"
            )

            if link_id:
                reference_ids.append(reference_id)
                existing_titles.append(ref_data['title'].lower())
                logger.info(f"Imported reference: {ref_data['title']} for content {content_id}")
            else:
                logger.error(f"Failed to link reference {reference_id} to content {content_id}")
        else:
            logger.error(f"Failed to create reference: {ref_data['title']}")

    return reference_ids

def generate_content_for_item(content_id: str, model_name: str = "gemini-1.5-flash",
                             temperature: float = 0.7, output_dir: str = "generated_content",
                             force: bool = False, debug: bool = False,
                             include_references: bool = True) -> Tuple[bool, Optional[str]]:
    """Generate content for a specific content item with automatic reference management.

    Args:
        content_id: Content ID
        model_name: Model name to use for generation
        temperature: Temperature for generation
        output_dir: Directory to save generated content
        force: Whether to force regeneration even if dependencies are not met
        debug: Whether to print debug information
        include_references: Whether to extract and store references

    Returns:
        Tuple of (success, content_text)
    """
    # Generate content using the original function
    try:
        # Try to call with the new signature that returns (success, content_text)
        success, content_text = original_generate_content(
            content_id=content_id,
            model_name=model_name,
            temperature=temperature,
            output_dir=output_dir,
            force=force,
            debug=debug,
            include_references=include_references
        )
    except ValueError:
        # Fall back to the old signature that only returns success
        success = original_generate_content(
            content_id=content_id,
            model_name=model_name,
            temperature=temperature,
            output_dir=output_dir,
            force=force,
            debug=debug
        )
        content_text = None

    if not success:
        logger.error(f"Failed to generate content for {content_id}")
        return False, None

    # If include_references is False, we're done
    if not include_references:
        logger.info(f"Skipping reference extraction for {content_id}")
        return True, None

    # Read the generated content file
    content_file_path = os.path.join(output_dir, f"{content_id}.md")
    if not os.path.exists(content_file_path):
        logger.error(f"Generated content file not found: {content_file_path}")
        return True, None

    with open(content_file_path, 'r') as f:
        content_text = f.read()

    # Extract references from content
    reference_items = extract_references_from_content(content_text)
    if not reference_items:
        logger.warning(f"No references found in content {content_id}")
        return True, content_text

    logger.info(f"Found {len(reference_items)} references in content {content_id}")

    # Store references in database
    reference_ids = store_references_in_database(content_id, reference_items)
    logger.info(f"Stored {len(reference_ids)} references for content {content_id}")

    return True, content_text

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate content with automatic reference management.")
    parser.add_argument("--content-id", required=True, help="Content ID to generate content for")
    parser.add_argument("--model", default="gemini-1.5-flash", help="Model name")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature for generation")
    parser.add_argument("--output-dir", default="generated_content", help="Output directory")
    parser.add_argument("--force", action="store_true", help="Force generation even if dependencies are not met or content is already completed")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--no-references", action="store_true", help="Skip reference extraction and storage")

    args = parser.parse_args()

    success, _ = generate_content_for_item(
        content_id=args.content_id,
        model_name=args.model,
        temperature=args.temperature,
        output_dir=args.output_dir,
        force=args.force,
        debug=args.debug,
        include_references=not args.no_references
    )

    # Exit with appropriate status code
    import sys
    sys.exit(0 if success else 1)
