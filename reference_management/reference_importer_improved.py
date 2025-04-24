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
    """Extract reference information from text with improved accuracy."""
    # Clean up the text
    text = text.strip()
    
    # If the text is very short, just use it as the title
    if len(text) < 50:
        return {
            'authors': 'Unknown',
            'publication_date': None,
            'title': text,
            'publication_name': 'Unknown',
            'url': None,
            'reference_type': 'Article'
        }
    
    # Try to determine if this is a structured reference or just a text snippet
    is_structured = bool(re.search(r'\((\d{4})\)|doi:|https?://|Retrieved from', text, re.IGNORECASE))
    
    if is_structured:
        # Try to extract author - look for patterns like "Author, A. B." or "Author et al."
        author_match = re.search(r'^([^\(\.]+?(et al\.)?)[,\.]', text)
        authors = author_match.group(1).strip() if author_match else "Unknown"
        
        # Try to extract year
        year_match = re.search(r'\((\d{4}[a-z]?)\)', text)
        year = year_match.group(1) if year_match else None
        publication_date = f"{year}-01-01" if year and len(year) == 4 else None
        
        # Try to extract title - different patterns for different citation styles
        # APA style: Author. (Year). Title. Publication.
        title_apa_match = re.search(r'\(\d{4}[a-z]?\)\.?\s+([^\.]+(\.[^\.]*)?)\.', text)
        # Other style: Author. Title. Publication, Year.
        title_other_match = re.search(r'^[^\.]+?(et al\.)?\.\s+([^\.]+(\.[^\.]*)?)\.', text)
        
        if title_apa_match:
            title = title_apa_match.group(1).strip()
        elif title_other_match:
            title = title_other_match.group(2).strip()
        else:
            # If no standard format, use a portion of text that's likely to be the title
            title = text[:100].split('. ')[1] if '. ' in text[:100] else text[:100]
        
        # Try to extract publication name
        pub_match = None
        if year_match:
            # Try after the year and title
            pub_match = re.search(r'\(\d{4}[a-z]?\)\.?\s+[^\.]+(\.[^\.]*)?\.\s+([^\.]+(\.[^\.]*)?)[\.,\s]', text)
        
        if not pub_match:
            # Try before a URL or DOI
            pub_match = re.search(r'\. ([^\.]+(\.[^\.]*)?)[\.,] (?:https?://|doi:|Retrieved)', text, re.IGNORECASE)
        
        publication = "Unknown"
        if pub_match and pub_match.lastindex > 1:
            try:
                publication = pub_match.group(pub_match.lastindex - 1).strip()
            except (IndexError, AttributeError):
                pass
        
        # Try to extract URL/DOI
        url_match = re.search(r'(https?://[^\s\)]+|doi:[^\s\)]+)', text, re.IGNORECASE)
        url = url_match.group(1) if url_match else None
        
        # Try to determine reference type
        ref_type = 'Article'  # Default
        if 'journal' in text.lower() or 'proceedings' in text.lower():
            ref_type = 'Journal Article'
        elif 'book' in text.lower() or 'chapter' in text.lower():
            ref_type = 'Book'
        elif 'conference' in text.lower():
            ref_type = 'Conference Paper'
        elif 'thesis' in text.lower() or 'dissertation' in text.lower():
            ref_type = 'Thesis'
        elif 'report' in text.lower() or 'technical' in text.lower():
            ref_type = 'Report'
        elif url and ('wikipedia' in url.lower() or 'wiki' in url.lower()):
            ref_type = 'Encyclopedia'
        elif url:
            ref_type = 'Website'
    else:
        # For unstructured text, use simpler extraction
        # Use the first sentence or phrase as title
        title_match = re.search(r'^([^\.]+(\.[^\.]*)?)[\s\.]', text)
        title = title_match.group(1).strip() if title_match else text[:100]
        
        # Check if there's any name-like pattern at the beginning
        author_match = re.search(r'^([A-Z][a-z]+(\s[A-Z][a-z]+)+)', text)
        authors = author_match.group(1) if author_match else "Unknown"
        
        publication_date = None
        publication = "Unknown"
        url = None
        ref_type = 'Article'
    
    # Clean up the title - remove quotes if they wrap the entire title
    title = re.sub(r'^["\'](.+)["\']$', r'\1', title)
    
    # Ensure title isn't too long
    if len(title) > 255:
        title = title[:252] + '...'
    
    return {
        'authors': authors,
        'publication_date': publication_date,
        'title': title,
        'publication_name': publication,
        'url': url,
        'reference_type': ref_type,
        'content': text  # Store the original text for reference
    }

def extract_references_from_content(content_text):
    """Extract references from content text with improved accuracy."""
    # Look for references section
    references_section_match = re.search(
        r'(?:References|Sources|Bibliography|Works Cited|Citations)[\s\n]*:?([\s\S]+)$', 
        content_text, 
        re.IGNORECASE
    )
    
    if not references_section_match:
        return []
    
    references_text = references_section_match.group(1).strip()
    
    # Split into individual references
    # This regex looks for patterns like [1], [SRC1], etc. or numbered items or bullet points
    reference_items = re.split(r'\n\s*(?:\[\w+\]|\d+\.|\*)\s+', references_text)
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
    existing_titles = [ref.get('title', '').lower() if isinstance(ref, dict) else 
                       (ref.title.lower() if hasattr(ref, 'title') and ref.title else "") 
                       for ref in existing_references]
    
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
            # Skip duplicate references in the same content
            if any(ref_text.strip() == item.strip() for item in reference_items[:i]):
                logger.info(f"Skipping duplicate reference in content {content_id}")
                continue
                
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
