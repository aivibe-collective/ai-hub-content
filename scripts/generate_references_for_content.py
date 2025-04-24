#!/usr/bin/env python3
"""
Generate references for existing content.

This script generates new references for existing content items using AI,
rather than trying to extract them from the content.
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
from supabase_client import supabase, is_connected, get_content_inventory, get_generation_outputs
from ai_reference_processor import generate_references_for_content, store_processed_references

def get_completed_content_ids() -> List[str]:
    """
    Get IDs of all completed content items.
    
    Returns:
        List of content IDs
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return []
    
    try:
        result = supabase.table('content_inventory').select('content_id').eq('status', 'Completed').execute()
        
        if not result.data:
            return []
        
        return [item['content_id'] for item in result.data]
    
    except Exception as e:
        logger.error(f"Error getting completed content IDs: {str(e)}")
        return []

def generate_references_for_all_content(model_name: str = "gemini-1.5-flash", max_items: int = 0, rate_limit_delay: float = 10.0) -> Dict[str, int]:
    """
    Generate references for all completed content items.
    
    Args:
        model_name: Model name to use for generation
        max_items: Maximum number of content items to process (0 for all)
        rate_limit_delay: Delay in seconds between API calls to avoid rate limits
        
    Returns:
        Dictionary with processing statistics
    """
    stats = {
        'total': 0,
        'processed': 0,
        'failed': 0,
        'skipped': 0
    }
    
    # Get all completed content IDs
    content_ids = get_completed_content_ids()
    stats['total'] = len(content_ids)
    
    logger.info(f"Found {len(content_ids)} completed content items")
    
    if max_items > 0 and max_items < len(content_ids):
        logger.info(f"Processing only {max_items} content items")
        content_ids = content_ids[:max_items]
    
    # Process each content item
    for i, content_id in enumerate(content_ids):
        logger.info(f"Processing content item {i+1}/{len(content_ids)}: {content_id}")
        
        # Check if content item has generation outputs
        outputs = get_generation_outputs(content_id=content_id, limit=1)
        if not outputs:
            logger.warning(f"No generation outputs found for content {content_id}, skipping")
            stats['skipped'] += 1
            continue
        
        # Get content item details
        content_items = get_content_inventory(content_id=content_id)
        if not content_items:
            logger.error(f"Content item with ID {content_id} not found")
            stats['failed'] += 1
            continue
        
        content_item = content_items[0]
        content_title = content_item.get('title', '')
        
        # Get content text
        content_text = outputs[0].get('output_text', '')
        if not content_text:
            logger.error(f"No content text found for output {outputs[0].get('id')}")
            stats['failed'] += 1
            continue
        
        try:
            # Add delay to avoid rate limits (except for the first item)
            if i > 0:
                import time
                logger.info(f"Waiting {rate_limit_delay} seconds to avoid rate limits...")
                time.sleep(rate_limit_delay)
            
            # Generate references for the content
            logger.info(f"Generating references for content: {content_title}")
            references = generate_references_for_content(
                content_text=content_text[:5000],  # Use first 5000 chars to avoid token limits
                topic=content_title,
                model_name=model_name
            )
            
            if not references:
                logger.warning(f"No references generated for content {content_id}")
                stats['failed'] += 1
                continue
            
            logger.info(f"Generated {len(references)} references for content {content_id}")
            
            # Store references in database
            reference_ids = store_processed_references(content_id, references)
            
            if reference_ids:
                logger.info(f"Stored {len(reference_ids)} references for content {content_id}")
                stats['processed'] += 1
            else:
                logger.error(f"Failed to store references for content {content_id}")
                stats['failed'] += 1
        
        except Exception as e:
            logger.error(f"Error generating references for content {content_id}: {str(e)}")
            stats['failed'] += 1
    
    logger.info(f"Finished generating references for all content items: {stats['processed']} processed, {stats['failed']} failed, {stats['skipped']} skipped")
    
    return stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate references for all completed content items.")
    parser.add_argument("--model", default="gemini-1.5-flash", help="Model name")
    parser.add_argument("--max-items", type=int, default=0, help="Maximum number of content items to process (0 for all)")
    parser.add_argument("--rate-limit-delay", type=float, default=10.0, help="Delay in seconds between API calls to avoid rate limits")
    
    args = parser.parse_args()
    
    stats = generate_references_for_all_content(
        model_name=args.model,
        max_items=args.max_items,
        rate_limit_delay=args.rate_limit_delay
    )
    
    # Print statistics
    print("\nProcessing Statistics:")
    print(f"Total content items: {stats['total']}")
    print(f"Successfully processed: {stats['processed']}")
    print(f"Failed to process: {stats['failed']}")
    print(f"Skipped: {stats['skipped']}")
    
    # Exit with appropriate status code
    import sys
    sys.exit(0 if stats['failed'] == 0 else 1)
