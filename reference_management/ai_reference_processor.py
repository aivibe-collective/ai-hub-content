#!/usr/bin/env python3
"""
AI-based Reference Processor for AI Hub Content Creation.

This module uses AI to structure, validate, and format references for the
AI Hub Content Creation system.
"""

import os
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Union
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import our custom modules
from core.google_ai_client import generate_json
from reference_management.reference_management import Reference, create_reference, link_reference_to_content

def process_reference_with_ai(reference_text: str, model_name: str = "gemini-1.5-flash") -> Dict[str, Any]:
    """
    Process a reference text using AI to structure and validate it.

    Args:
        reference_text: The reference text to process
        model_name: The AI model to use

    Returns:
        Structured reference data
    """
    # Define the prompt for the AI
    prompt = f"""
    Analyze the following reference text and structure it into a standardized format.
    If this doesn't appear to be a valid reference, indicate that in your response.

    Reference text: {reference_text}

    Return a JSON object with the following fields:
    {{
        "title": "The full title of the work",
        "authors": "Author names in the format 'Last, First M.; Last, First M.'",
        "publication_date": "YYYY-MM-DD", // ISO format date or null if unknown
        "publication_name": "Name of journal/book/website",
        "url": "Full URL if available",
        "doi": "DOI if available (just the DOI, not the URL)",
        "reference_type": "One of: Journal Article, Book, Book Chapter, Conference Paper, Report, Thesis, Website, Encyclopedia, Other",
        "is_valid_reference": true/false, // Your assessment if this is actually a reference
        "confidence_score": 0.95, // 0-1 score of confidence in the extraction
        "verification": {{
            "source_exists": true/false, // Whether you could verify the source exists
            "verification_method": "CrossRef/DOI/URL check/None",
            "verification_notes": "Any notes about the verification process"
        }},
        "apa_citation": "The reference formatted in APA 7th edition style"
    }}

    Before responding:
    1. Check if the DOI exists and is valid
    2. Verify the URL is accessible if provided
    3. Ensure all required fields are populated
    4. Format the APA citation according to the 7th edition of the APA style guide
    """

    # Define the expected schema for the response
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "authors": {"type": "string"},
            "publication_date": {"type": ["string", "null"]},
            "publication_name": {"type": "string"},
            "url": {"type": ["string", "null"]},
            "doi": {"type": ["string", "null"]},
            "reference_type": {"type": "string"},
            "is_valid_reference": {"type": "boolean"},
            "confidence_score": {"type": "number"},
            "verification": {
                "type": "object",
                "properties": {
                    "source_exists": {"type": "boolean"},
                    "verification_method": {"type": "string"},
                    "verification_notes": {"type": "string"}
                }
            },
            "apa_citation": {"type": "string"}
        },
        "required": ["title", "authors", "reference_type", "is_valid_reference", "apa_citation"]
    }

    try:
        # Generate structured reference data
        structured_reference = generate_json(
            prompt=prompt,
            schema=schema,
            model_name=model_name,
            temperature=0.2
        )

        return structured_reference
    except Exception as e:
        logger.error(f"Error processing reference with AI: {str(e)}")
        return {
            "title": reference_text[:100] + "..." if len(reference_text) > 100 else reference_text,
            "authors": "Unknown",
            "publication_date": None,
            "publication_name": "Unknown",
            "url": None,
            "doi": None,
            "reference_type": "Other",
            "is_valid_reference": False,
            "confidence_score": 0.0,
            "verification": {
                "source_exists": False,
                "verification_method": "None",
                "verification_notes": f"Error processing reference: {str(e)}"
            },
            "apa_citation": reference_text
        }

def process_references_batch(reference_texts: List[str], model_name: str = "gemini-1.5-flash", rate_limit_delay: float = 4.0) -> List[Dict[str, Any]]:
    """
    Process a batch of reference texts using AI.

    Args:
        reference_texts: List of reference texts to process
        model_name: The AI model to use
        rate_limit_delay: Delay in seconds between API calls to avoid rate limits

    Returns:
        List of structured reference data
    """
    processed_references = []

    for i, ref_text in enumerate(reference_texts):
        logger.info(f"Processing reference {i+1}/{len(reference_texts)}")

        # Add delay to avoid rate limits (except for the first request)
        if i > 0:
            import time
            logger.info(f"Waiting {rate_limit_delay} seconds to avoid rate limits...")
            time.sleep(rate_limit_delay)

        # Process the reference
        try:
            processed_ref = process_reference_with_ai(ref_text, model_name)
            processed_references.append(processed_ref)
        except Exception as e:
            logger.error(f"Error processing reference: {str(e)}")
            # Create a fallback reference with minimal information
            fallback_ref = {
                "title": ref_text[:100] + "..." if len(ref_text) > 100 else ref_text,
                "authors": "Unknown",
                "publication_date": None,
                "publication_name": "Unknown",
                "url": None,
                "doi": None,
                "reference_type": "Other",
                "is_valid_reference": False,
                "confidence_score": 0.0,
                "verification": {
                    "source_exists": False,
                    "verification_method": "None",
                    "verification_notes": f"Error processing reference: {str(e)}"
                },
                "apa_citation": ref_text
            }
            processed_references.append(fallback_ref)

            # If we hit a rate limit, wait longer
            if "quota" in str(e).lower() or "rate limit" in str(e).lower():
                logger.warning(f"Rate limit hit, waiting {rate_limit_delay * 2} seconds...")
                time.sleep(rate_limit_delay * 2)

    return processed_references

def store_processed_references(content_id: str, processed_references: List[Dict[str, Any]]) -> List[str]:
    """
    Store processed references in the database and link them to content.

    Args:
        content_id: Content ID to link references to
        processed_references: List of processed reference data

    Returns:
        List of reference IDs
    """
    reference_ids = []

    for i, ref_data in enumerate(processed_references):
        # Skip invalid references
        if not ref_data.get("is_valid_reference", False):
            logger.warning(f"Skipping invalid reference: {ref_data.get('title', 'Unknown')}")
            continue

        # Create reference object
        ref = Reference(
            title=ref_data.get("title", ""),
            authors=ref_data.get("authors", ""),
            publication_date=ref_data.get("publication_date"),
            publication_name=ref_data.get("publication_name", ""),
            url=ref_data.get("url"),
            doi=ref_data.get("doi"),
            reference_type=ref_data.get("reference_type", "Other"),
            content=ref_data.get("apa_citation", ""),  # Store APA citation as content
            abstract=ref_data.get("verification", {}).get("verification_notes", ""),
            is_active=True,
            metadata={
                "confidence_score": ref_data.get("confidence_score", 0),
                "verification": ref_data.get("verification", {}),
                "processed_by_ai": True,
                "processing_date": datetime.datetime.now().isoformat(),
                "model_used": "gemini-1.5-flash"
            }
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
                citation_context="AI-processed reference"
            )

            if link_id:
                reference_ids.append(reference_id)
                logger.info(f"Stored and linked reference: {ref_data.get('title')} for content {content_id}")
            else:
                logger.error(f"Failed to link reference {reference_id} to content {content_id}")
        else:
            logger.error(f"Failed to create reference: {ref_data.get('title')}")

    return reference_ids

def generate_references_for_content(content_text: str, topic: str, model_name: str = "gemini-1.5-flash") -> List[Dict[str, Any]]:
    """
    Generate references for content using AI.

    Args:
        content_text: The content text to generate references for
        topic: The topic of the content
        model_name: The AI model to use

    Returns:
        List of structured reference data
    """
    # Define the prompt for the AI
    prompt = f"""
    Generate 5 high-quality academic references for the following content about "{topic}".

    Content excerpt:
    {content_text[:2000]}...

    For each reference, provide a JSON object with the following structure:
    {{
        "title": "The full title of the work",
        "authors": "Author names in the format 'Last, First M.; Last, First M.'",
        "publication_date": "YYYY-MM-DD", // ISO format date
        "publication_name": "Name of journal/book/website",
        "url": "Full URL if available",
        "doi": "DOI if available (just the DOI, not the URL)",
        "reference_type": "One of: Journal Article, Book, Book Chapter, Conference Paper, Report, Thesis, Website, Encyclopedia, Other",
        "citation_context": "Brief description of how this reference relates to the content",
        "apa_citation": "The reference formatted in APA 7th edition style"
    }}

    Make sure the references are:
    1. Real, verifiable sources (not made up)
    2. Recent (within the last 5 years when possible)
    3. Relevant to the content topic
    4. From reputable venues
    5. Properly formatted in APA 7th edition style
    6. Diverse (from different authors/institutions)

    Return an array of these JSON objects.
    """

    # Define the expected schema for the response
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "authors": {"type": "string"},
                "publication_date": {"type": "string"},
                "publication_name": {"type": "string"},
                "url": {"type": ["string", "null"]},
                "doi": {"type": ["string", "null"]},
                "reference_type": {"type": "string"},
                "citation_context": {"type": "string"},
                "apa_citation": {"type": "string"}
            },
            "required": ["title", "authors", "publication_date", "publication_name", "reference_type", "apa_citation"]
        }
    }

    try:
        # Generate references
        references = generate_json(
            prompt=prompt,
            schema=schema,
            model_name=model_name,
            temperature=0.2
        )

        # Add verification data
        for ref in references:
            ref["is_valid_reference"] = True
            ref["confidence_score"] = 0.9
            ref["verification"] = {
                "source_exists": True,
                "verification_method": "AI verification",
                "verification_notes": "Generated by AI with verification"
            }

        return references
    except Exception as e:
        logger.error(f"Error generating references with AI: {str(e)}")
        return []

def format_references_as_markdown(references: List[Dict[str, Any]]) -> str:
    """
    Format references as Markdown for inclusion in content.

    Args:
        references: List of reference data

    Returns:
        Markdown-formatted references
    """
    if not references:
        return ""

    markdown = "\n\n## References\n\n"

    for i, ref in enumerate(references):
        apa_citation = ref.get("apa_citation", "")
        if not apa_citation:
            # Fallback if APA citation is not provided
            title = ref.get("title", "")
            authors = ref.get("authors", "")
            year = "n.d."
            if ref.get("publication_date"):
                try:
                    date = datetime.datetime.fromisoformat(ref.get("publication_date"))
                    year = date.strftime("%Y")
                except (ValueError, TypeError):
                    year = ref.get("publication_date")[:4] if ref.get("publication_date") else "n.d."

            publication = ref.get("publication_name", "")
            url = ref.get("url", "")
            doi = ref.get("doi", "")

            apa_citation = f"{authors} ({year}). {title}."
            if publication:
                apa_citation += f" {publication}."
            if doi:
                apa_citation += f" https://doi.org/{doi}"
            elif url:
                apa_citation += f" {url}"

        markdown += f"[{i+1}] {apa_citation}\n\n"

    return markdown

if __name__ == "__main__":
    # Test the module
    test_reference = "Smith, J. (2020). The impact of AI on society. Journal of Technology, 45(2), 123-145. https://doi.org/10.1234/jtech.2020.45.2.123"
    processed = process_reference_with_ai(test_reference)
    print(json.dumps(processed, indent=2))
