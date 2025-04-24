#!/usr/bin/env python3
"""
Process references for all completed content items.

This script processes references for all completed content items in the database,
extracting references from the content, processing them with AI, and storing them
in the database.
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
from content_workflow_with_ai_references import process_existing_references

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

def process_all_content_references(model_name: str = "gemini-1.5-flash", max_items: int = 0, batch_size: int = 5, rate_limit_delay: float = 4.0) -> Dict[str, int]:
    """
    Process references for all completed content items.

    Args:
        model_name: Model name to use for processing
        max_items: Maximum number of content items to process (0 for all)

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

        # Process references for the content item
        success = process_existing_references(
            content_id=content_id,
            model_name=model_name,
            batch_size=batch_size,
            rate_limit_delay=rate_limit_delay
        )

        if success:
            logger.info(f"Successfully processed references for content {content_id}")
            stats['processed'] += 1
        else:
            logger.error(f"Failed to process references for content {content_id}")
            stats['failed'] += 1

    logger.info(f"Finished processing references for all content items: {stats['processed']} processed, {stats['failed']} failed, {stats['skipped']} skipped")

    return stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process references for all completed content items.")
    parser.add_argument("--model", default="gemini-1.5-flash", help="Model name")
    parser.add_argument("--max-items", type=int, default=0, help="Maximum number of content items to process (0 for all)")
    parser.add_argument("--batch-size", type=int, default=5, help="Number of references to process in each batch")
    parser.add_argument("--rate-limit-delay", type=float, default=4.0, help="Delay in seconds between API calls to avoid rate limits")

    args = parser.parse_args()

    stats = process_all_content_references(
        model_name=args.model,
        max_items=args.max_items,
        batch_size=args.batch_size,
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
