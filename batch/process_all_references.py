#!/usr/bin/env python3
"""
Process all existing references in the database using AI.

This script retrieves all references from the database and processes them
using AI to improve their structure, validation, and formatting.
"""

import os
import logging
import argparse
import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import our custom modules
from supabase_client import supabase, is_connected
from ai_reference_processor import process_reference_with_ai
from reference_management import Reference, update_reference

def get_all_references(limit: int = 0, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get all references from the database.
    
    Args:
        limit: Maximum number of references to retrieve (0 for all)
        offset: Offset for pagination
        
    Returns:
        List of reference dictionaries
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return []
    
    try:
        query = supabase.table('reference_sources').select('*')
        
        if limit > 0:
            query = query.limit(limit)
        
        if offset > 0:
            query = query.offset(offset)
        
        result = query.execute()
        
        return result.data if result.data else []
    
    except Exception as e:
        logger.error(f"Error getting references: {str(e)}")
        return []

def process_reference(reference: Dict[str, Any], model_name: str = "gemini-1.5-flash") -> bool:
    """
    Process a reference using AI and update it in the database.
    
    Args:
        reference: Reference dictionary
        model_name: Model name to use for processing
        
    Returns:
        True if successful, False otherwise
    """
    reference_id = reference.get('id')
    if not reference_id:
        logger.error("Reference ID is required")
        return False
    
    # Get the reference text to process
    reference_text = reference.get('content', '')
    if not reference_text:
        # If no content, try to construct a reference text from the available fields
        title = reference.get('title', '')
        authors = reference.get('authors', '')
        publication_date = reference.get('publication_date', '')
        publication_name = reference.get('publication_name', '')
        url = reference.get('url', '')
        doi = reference.get('doi', '')
        
        if publication_date and isinstance(publication_date, str):
            # Try to extract year from ISO date
            try:
                year = datetime.datetime.fromisoformat(publication_date).year
            except (ValueError, TypeError):
                year = publication_date[:4] if len(publication_date) >= 4 else ''
        else:
            year = ''
        
        # Construct a reference text
        reference_text = f"{authors}"
        if year:
            reference_text += f" ({year})."
        else:
            reference_text += "."
        
        reference_text += f" {title}."
        if publication_name:
            reference_text += f" {publication_name}."
        if doi:
            reference_text += f" doi:{doi}"
        elif url:
            reference_text += f" {url}"
    
    if not reference_text:
        logger.error(f"No reference text available for reference {reference_id}")
        return False
    
    try:
        # Process the reference with AI
        processed = process_reference_with_ai(reference_text, model_name)
        
        if not processed.get('is_valid_reference', False):
            logger.warning(f"AI determined reference {reference_id} is not valid: {processed.get('title', '')}")
            return False
        
        # Create a Reference object with the processed data
        ref = Reference(
            reference_id=reference_id,
            title=processed.get('title', reference.get('title', '')),
            authors=processed.get('authors', reference.get('authors', '')),
            publication_date=processed.get('publication_date', reference.get('publication_date')),
            publication_name=processed.get('publication_name', reference.get('publication_name', '')),
            url=processed.get('url', reference.get('url', '')),
            doi=processed.get('doi', reference.get('doi', '')),
            reference_type=processed.get('reference_type', reference.get('reference_type', 'Other')),
            content=processed.get('apa_citation', reference_text),
            abstract=reference.get('abstract', ''),
            keywords=reference.get('keywords', []),
            is_active=reference.get('is_active', True),
            created_by=reference.get('created_by', 'system')
        )
        
        # Update metadata
        metadata = reference.get('metadata', {})
        if isinstance(metadata, str):
            import json
            try:
                metadata = json.loads(metadata)
            except json.JSONDecodeError:
                metadata = {}
        
        # Add AI processing metadata
        ai_metadata = {
            'ai_processed': True,
            'processing_date': datetime.datetime.now().isoformat(),
            'model_used': model_name,
            'confidence_score': processed.get('confidence_score', 0),
            'verification': processed.get('verification', {})
        }
        
        # Merge metadata
        if isinstance(metadata, dict):
            metadata.update(ai_metadata)
        else:
            metadata = ai_metadata
        
        ref.metadata = metadata
        
        # Update the reference in the database
        success = update_reference(ref)
        
        if success:
            logger.info(f"Successfully processed and updated reference {reference_id}")
        else:
            logger.error(f"Failed to update reference {reference_id}")
        
        return success
    
    except Exception as e:
        logger.error(f"Error processing reference {reference_id}: {str(e)}")
        return False

def process_all_references(model_name: str = "gemini-1.5-flash", batch_size: int = 10, max_references: int = 0) -> Dict[str, int]:
    """
    Process all references in the database using AI.
    
    Args:
        model_name: Model name to use for processing
        batch_size: Number of references to process in each batch
        max_references: Maximum number of references to process (0 for all)
        
    Returns:
        Dictionary with processing statistics
    """
    stats = {
        'total': 0,
        'processed': 0,
        'failed': 0,
        'skipped': 0
    }
    
    # Get total count of references
    total_references = len(get_all_references())
    stats['total'] = total_references
    
    logger.info(f"Found {total_references} references in the database")
    
    if max_references > 0 and max_references < total_references:
        logger.info(f"Processing only {max_references} references")
        total_references = max_references
    
    # Process references in batches
    offset = 0
    while offset < total_references:
        # Calculate batch size
        current_batch_size = min(batch_size, total_references - offset)
        
        # Get batch of references
        references = get_all_references(limit=current_batch_size, offset=offset)
        
        if not references:
            break
        
        logger.info(f"Processing batch of {len(references)} references (offset: {offset})")
        
        # Process each reference in the batch
        for reference in references:
            reference_id = reference.get('id', 'Unknown')
            logger.info(f"Processing reference {reference_id}")
            
            # Check if reference has already been processed
            metadata = reference.get('metadata', {})
            if isinstance(metadata, str):
                import json
                try:
                    metadata = json.loads(metadata)
                except json.JSONDecodeError:
                    metadata = {}
            
            if isinstance(metadata, dict) and metadata.get('ai_processed', False):
                logger.info(f"Skipping already processed reference {reference_id}")
                stats['skipped'] += 1
                continue
            
            # Process the reference
            success = process_reference(reference, model_name)
            
            if success:
                stats['processed'] += 1
            else:
                stats['failed'] += 1
        
        # Update offset for next batch
        offset += len(references)
        
        logger.info(f"Processed {offset}/{total_references} references")
    
    logger.info(f"Finished processing references: {stats['processed']} processed, {stats['failed']} failed, {stats['skipped']} skipped")
    
    return stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process all references in the database using AI.")
    parser.add_argument("--model", default="gemini-1.5-flash", help="Model name")
    parser.add_argument("--batch-size", type=int, default=10, help="Number of references to process in each batch")
    parser.add_argument("--max-references", type=int, default=0, help="Maximum number of references to process (0 for all)")
    
    args = parser.parse_args()
    
    stats = process_all_references(
        model_name=args.model,
        batch_size=args.batch_size,
        max_references=args.max_references
    )
    
    # Print statistics
    print("\nProcessing Statistics:")
    print(f"Total references: {stats['total']}")
    print(f"Successfully processed: {stats['processed']}")
    print(f"Failed to process: {stats['failed']}")
    print(f"Skipped (already processed): {stats['skipped']}")
    
    # Exit with appropriate status code
    import sys
    sys.exit(0 if stats['failed'] == 0 else 1)
