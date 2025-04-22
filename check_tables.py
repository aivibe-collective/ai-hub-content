#!/usr/bin/env python3
"""
Check if tables exist in Supabase.
"""

from supabase_client import supabase, is_connected

def check_table(table_name):
    """Check if a table exists in Supabase."""
    try:
        result = supabase.table(table_name).select('count', count='exact').execute()
        print(f"Table {table_name} exists with {result.count} rows")
        return True
    except Exception as e:
        print(f"Error checking table {table_name}: {str(e)}")
        return False

def main():
    """Main function."""
    if not is_connected():
        print("Not connected to Supabase")
        return

    # Check tables
    tables = [
        'content_inventory',
        'prompt_logs',
        'generation_outputs',
        'content_files',
        'content_versions'
    ]

    for table in tables:
        check_table(table)

if __name__ == '__main__':
    main()
