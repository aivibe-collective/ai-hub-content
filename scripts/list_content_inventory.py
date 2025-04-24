#!/usr/bin/env python3
"""
Script to list content items from the inventory.
"""

import os
import argparse
import pandas as pd
from dotenv import load_dotenv

# Import our custom modules
from supabase_client import is_connected, get_content_inventory

# Load environment variables
load_dotenv()

def list_content_inventory(section=None, status=None, output_format="table"):
    """List content items from the inventory."""
    # Check Supabase connection
    if not is_connected():
        print("Not connected to Supabase")
        return False
    
    # Get content items
    content_items = get_content_inventory(section=section, status=status)
    if not content_items:
        print("No content items found")
        return False
    
    # Convert to DataFrame for easier display
    df = pd.DataFrame(content_items)
    
    # Select columns to display
    display_columns = [
        'content_id', 'section', 'subsection', 'title', 'content_type', 
        'status', 'priority', 'audience_technical_level'
    ]
    
    # Filter columns that exist in the DataFrame
    display_columns = [col for col in display_columns if col in df.columns]
    
    # Display content items
    if output_format == "table":
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        print(df[display_columns].to_string(index=False))
    elif output_format == "csv":
        print(df[display_columns].to_csv(index=False))
    elif output_format == "json":
        print(df[display_columns].to_json(orient="records", indent=2))
    
    print(f"\nTotal: {len(content_items)} items")
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="List content items from the inventory.")
    parser.add_argument("--section", help="Filter by section")
    parser.add_argument("--status", help="Filter by status")
    parser.add_argument("--format", choices=["table", "csv", "json"], default="table", help="Output format")
    
    args = parser.parse_args()
    
    # List content items
    success = list_content_inventory(
        section=args.section,
        status=args.status,
        output_format=args.format
    )
    
    # Exit with appropriate status code
    import sys
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
