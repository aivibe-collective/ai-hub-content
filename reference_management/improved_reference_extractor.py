#!/usr/bin/env python3
"""
Improved reference extraction for AI Hub Content Creation.

This module provides improved functions for extracting reference information
from text, handling various citation formats more accurately.
"""

import re
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    # This regex looks for patterns like [1], [SRC1], etc. or numbered items
    reference_items = re.split(r'\n\s*(?:\[\w+\]|\d+\.|\*)\s+', references_text)
    # Remove empty items and the first item if it's empty (from the split)
    reference_items = [item.strip() for item in reference_items if item.strip()]

    return reference_items

# Test function
def test_extraction():
    """Test the reference extraction with various formats."""
    test_references = [
        "Smith, J. (2020). The impact of AI on society. Journal of Technology, 45(2), 123-145. https://doi.org/10.1234/jtech.2020.45.2.123",
        "Johnson, A. B., & Williams, C. D. (2019). Machine learning applications. In Advanced Computing (pp. 78-92). Springer.",
        "Brown et al. The future of robotics. IEEE Conference on Robotics, 2021.",
        "Wikipedia. (2022). Artificial intelligence. Retrieved from https://en.wikipedia.org/wiki/Artificial_intelligence",
        "This is just a text snippet without any structured citation format."
    ]

    for ref in test_references:
        print("\nOriginal:", ref)
        extracted = extract_reference_from_text(ref)
        print("Extracted:")
        for key, value in extracted.items():
            if key != 'content':  # Skip the full content for brevity
                print(f"  {key}: {value}")

if __name__ == "__main__":
    test_extraction()
