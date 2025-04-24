#!/usr/bin/env python3
"""
Import references from existing generation outputs in the database.

This script extracts references from the generation outputs and imports them
into the reference management system.
"""

import logging
import os
import re
import sys
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from supabase_client import get_generation_outputs, get_full_content
from reference_management import (
    Reference, create_reference, link_reference_to_content,
    get_references, get_content_references
)

def extract_reference_from_text(text):
    """Extract reference information from text."""
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
    
    return {
        'authors': authors,
        'publication_date': f"{year}-01-01" if year else None,
        'title': title,
        'publication_name': publication,
        'url': url,
        'reference_type': 'Article'  # Default type
    }

def extract_references_from_content(content_text):
    """Extract references from content text."""
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

def import_references_from_database():
    """Import references from existing generation outputs in the database."""
    logger.info("Starting reference import from database...")
    
    # Get all generation outputs
    outputs = get_generation_outputs(limit=1000)
    logger.info(f"Retrieved {len(outputs)} generation outputs from database")
    
    # Get existing references to avoid duplicates
    existing_references = get_references()
    existing_titles = [ref.title.lower() if ref.title else "" for ref in existing_references]
    
    imported_count = 0
    for output in outputs:
        content_id = output.get('content_id')
        if not content_id:
            continue
        
        # Check if we already have references for this content
        content_refs = get_content_references(content_id)
        if content_refs:
            logger.info(f"Skipping content {content_id} - already has {len(content_refs)} references")
            continue
        
        # Get full content text
        content_text = get_full_content(output.get('id'))
        if not content_text:
            logger.warning(f"No content found for output {output.get('id')}")
            continue
        
        # Extract references
        reference_items = extract_references_from_content(content_text)
        if not reference_items:
            logger.warning(f"No references found in content {content_id}")
            continue
        
        logger.info(f"Found {len(reference_items)} references in content {content_id}")
        
        # Process each reference
        for i, ref_text in enumerate(reference_items):
            # Extract reference data
            ref_data = extract_reference_from_text(ref_text)
            
            # Skip if title already exists
            if ref_data['title'].lower() in existing_titles:
                logger.info(f"Skipping duplicate reference: {ref_data['title']}")
                continue
            
            # Create reference object
            ref = Reference(
                title=ref_data['title'],
                authors=ref_data['authors'],
                publication_date=ref_data['publication_date'],
                publication_name=ref_data['publication_name'],
                url=ref_data['url'],
                reference_type=ref_data['reference_type'],
                content=ref_text,  # Store original text
                abstract="Automatically extracted from generated content",
                is_active=True
            )
            
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
                    imported_count += 1
                    existing_titles.append(ref_data['title'].lower())
                    logger.info(f"Imported reference: {ref_data['title']} for content {content_id}")
                else:
                    logger.error(f"Failed to link reference {reference_id} to content {content_id}")
            else:
                logger.error(f"Failed to create reference: {ref_data['title']}")
    
    logger.info(f"Imported {imported_count} references successfully.")
    return imported_count

if __name__ == "__main__":
    import_references_from_database()
