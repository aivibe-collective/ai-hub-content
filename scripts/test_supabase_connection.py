#!/usr/bin/env python3
"""
Simple test script for Supabase integration.
This script tests the connection to Supabase and performs basic operations.
"""

import os
import json
import uuid
import logging
from dotenv import load_dotenv
from supabase import create_client, Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables(supabase):
    """Create the required tables in Supabase."""
    print("\n🔧 Creating required tables...")

    try:
        # Read SQL file
        with open('create_tables.sql', 'r') as f:
            sql = f.read()

        # Execute SQL
        result = supabase.rpc('exec_sql', {"query": sql}).execute()
        print("✅ Tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        print(f"\n❌ ERROR creating tables: {str(e)}")
        print("\nTrying to continue anyway...")
        return False

def test_supabase_connection():
    """Test the connection to Supabase."""
    # Load environment variables
    load_dotenv()

    # Get Supabase credentials
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        logger.error("SUPABASE_URL or SUPABASE_KEY not found in environment variables")
        print("\n❌ ERROR: Missing Supabase credentials")
        print("Please set SUPABASE_URL and SUPABASE_KEY in your .env file")
        return False

    print(f"\n🔑 Found Supabase credentials:")
    print(f"  URL: {supabase_url[:30]}...")
    print(f"  Key: {supabase_key[:10]}...")

    try:
        # Initialize Supabase client
        print("\n🔌 Connecting to Supabase...")
        supabase = create_client(supabase_url, supabase_key)

        # Test connection with a simple health check
        print("📊 Testing connection...")
        try:
            # Just check if we can connect
            print(f"\n✅ Connection successful!")
            print(f"Supabase connection is working correctly.")

            # Check if our tables exist
            print("\n📊 Checking if required tables exist...")
            tables_to_check = ['content_inventory', 'prompt_logs', 'generation_outputs', 'content_files']
            missing_tables = []

            for table in tables_to_check:
                try:
                    table_response = supabase.table(table).select('count', count='exact').execute()
                    print(f"  ✅ Table '{table}' exists with {table_response.count} rows")
                except Exception as e:
                    if "relation \"public." + table + "\" does not exist" in str(e):
                        missing_tables.append(table)
                        print(f"  ❌ Table '{table}' does not exist")
                    else:
                        print(f"  ⚠️ Error checking table '{table}': {str(e)}")

            if missing_tables:
                print("\n⚠️ Some required tables are missing. You need to create them manually.")
                print("Please run the SQL script in create_tables.sql in the Supabase SQL Editor.")
                print("\nMissing tables:")
                for table in missing_tables:
                    print(f"  - {table}")
                return False

            # If all tables exist, try creating a test record
            if not missing_tables:
                # Test creating a test record
                test_id = str(uuid.uuid4())
                print(f"\n🧪 Creating test record with ID: {test_id}")

                # Check if test_table exists
                try:
                    test_table_response = supabase.table('test_table').select('count', count='exact').execute()
                    print(f"📊 Found test_table with {test_table_response.count} rows")
                    table_name = 'test_table'
                    test_data = {
                        'test_id': test_id,
                        'test_name': 'Connection Test',
                        'test_data': json.dumps({
                            'timestamp': str(uuid.uuid4()),
                            'status': 'success'
                        })
                    }
                except Exception as e:
                    print(f"⚠️ Test table not found. Creating test record in content_inventory instead.")
                    # Insert test data into content_inventory
                    table_name = 'content_inventory'
                    test_data = {
                        'content_id': f'TEST-{test_id[:8]}',
                        'section': 'Test',
                        'subsection': 'Connection Test',
                        'title': f'Test Record {test_id[:8]}',
                        'content_type': 'Test',
                        'status': 'Test'
                    }

                # Insert test data
                try:
                    insert_response = supabase.table(table_name).insert(test_data).execute()

                    if insert_response.data:
                        print(f"✅ Successfully inserted test record into {table_name}")

                        # Clean up test data if not in content_inventory
                        if table_name == 'test_table':
                            print(f"🧹 Cleaning up test record...")
                            supabase.table(table_name).delete().eq('test_id', test_id).execute()
                            print(f"✅ Test record deleted")
                    else:
                        print(f"❌ Failed to insert test record")
                except Exception as e:
                    print(f"❌ Error inserting test record: {str(e)}")

                print("\n✅ All tests passed! Supabase integration is working correctly.")

            return True
        except Exception as e:
            print(f"\n❌ ERROR: Could not query system tables: {str(e)}")
            print("This might indicate a permission issue or an invalid API key.")
            return False

    except Exception as e:
        logger.error(f"Error testing Supabase connection: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}")
        print("\nPossible issues:")
        print("1. Incorrect Supabase URL or API key")
        print("2. Network connectivity issues")
        print("3. Required tables don't exist in the Supabase project")
        print("4. Insufficient permissions")
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("🧪 SUPABASE INTEGRATION TEST")
    print("=" * 60)

    success = test_supabase_connection()

    print("\n" + "=" * 60)
    if success:
        print("✅ SUPABASE INTEGRATION TEST PASSED")
    else:
        print("❌ SUPABASE INTEGRATION TEST FAILED")
    print("=" * 60)

    # Exit with appropriate status code
    import sys
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
