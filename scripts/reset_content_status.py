#!/usr/bin/env python3
"""
Script to reset content status to 'Not Started'.
"""

import argparse
import logging
import datetime
from dotenv import load_dotenv

# Import our custom modules
from supabase_client import is_connected, update_content_status, get_content_inventory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def reset_content_status(content_ids=None):
    """Reset content status to 'Not Started'.
    
    Args:
        content_ids (list, optional): List of content IDs to reset. If None, all content items will be reset.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    # Check Supabase connection
    if not is_connected():
        logger.error("Not connected to Supabase")
        return False
    
    try:
        # Get all content items if no IDs provided
        if not content_ids:
            content_items = get_content_inventory()
            content_ids = [item['content_id'] for item in content_items]
        
        # Reset status for each content item
        for content_id in content_ids:
            update_content_status(content_id, "Not Started", {
                "reset_time": datetime.datetime.now().isoformat()
            })
            logger.info(f"Reset status for content ID {content_id} to Not Started")
        
        return True
    except Exception as e:
        logger.error(f"Error resetting content status: {str(e)}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Reset content status to 'Not Started'")
    parser.add_argument("--content-ids", help="Comma-separated list of content IDs to reset")
    parser.add_argument("--section", help="Reset all content items in a specific section")
    parser.add_argument("--all", action="store_true", help="Reset all content items")
    
    args = parser.parse_args()
    
    if args.content_ids:
        content_ids = args.content_ids.split(",")
        logger.info(f"Resetting status for {len(content_ids)} content items: {', '.join(content_ids)}")
        success = reset_content_status(content_ids)
    elif args.section:
        content_items = get_content_inventory(section=args.section)
        content_ids = [item['content_id'] for item in content_items]
        logger.info(f"Resetting status for {len(content_ids)} content items in section {args.section}")
        success = reset_content_status(content_ids)
    elif args.all:
        logger.info("Resetting status for all content items")
        success = reset_content_status()
    else:
        logger.error("No content items specified. Use --content-ids, --section, or --all")
        return False
    
    # Exit with appropriate status code
    import sys
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
