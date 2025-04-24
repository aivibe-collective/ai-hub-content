#!/usr/bin/env python3
"""
Fix Reference Categories.

This script creates a reference_to_category table and links references to categories.
"""

import os
import uuid
import logging
import random
from typing import Dict, Any, List
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import our custom modules
from supabase_client import supabase, is_connected

def get_references(limit: int = 20) -> list:
    """Get references from the database.
    
    Args:
        limit: Maximum number of references to retrieve
        
    Returns:
        List of references
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return []
    
    try:
        result = supabase.table('reference_sources').select('*').limit(limit).execute()
        return result.data if result.data else []
    
    except Exception as e:
        logger.error(f"Error getting references: {str(e)}")
        return []

def create_reference_categories() -> List[Dict[str, str]]:
    """Create reference categories if they don't exist.
    
    Returns:
        List of category dictionaries
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return []
    
    categories = [
        {"name": "AI Technology", "description": "References about AI technology, algorithms, and implementations"},
        {"name": "Business", "description": "References about business applications, strategy, and management"},
        {"name": "Ethics", "description": "References about ethical considerations, guidelines, and frameworks"},
        {"name": "Sustainability", "description": "References about environmental sustainability and responsible practices"},
        {"name": "Inclusion", "description": "References about diversity, equity, and inclusion"},
        {"name": "Policy", "description": "References about policy, regulation, and governance"},
        {"name": "Education", "description": "References about education, training, and learning"},
        {"name": "Research", "description": "References about academic and scientific research"}
    ]
    
    created_categories = []
    
    try:
        # Check if categories table exists
        try:
            result = supabase.table('reference_categories').select('count').execute()
        except Exception:
            # Create categories table if it doesn't exist
            logger.info("Creating reference_categories table")
            query = """
            CREATE TABLE IF NOT EXISTS reference_categories (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                parent_id UUID REFERENCES reference_categories(id),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
            supabase.rpc('run_sql', {'query': query}).execute()
        
        # Create categories
        for category in categories:
            # Check if category exists
            result = supabase.table('reference_categories').select('id,name,description').eq('name', category['name']).execute()
            
            if result.data:
                created_categories.append(result.data[0])
                logger.info(f"Category already exists: {category['name']}")
            else:
                # Create category
                category_data = {
                    "id": str(uuid.uuid4()),
                    "name": category['name'],
                    "description": category['description'],
                    "created_at": "now()",
                    "updated_at": "now()"
                }
                
                result = supabase.table('reference_categories').insert(category_data).execute()
                
                if not result.data:
                    logger.error(f"Failed to create category: {category['name']}")
                    continue
                
                created_categories.append(result.data[0])
                logger.info(f"Created category: {category['name']}")
        
        return created_categories
    
    except Exception as e:
        logger.error(f"Error creating reference categories: {str(e)}")
        return []

def create_reference_to_category_table() -> bool:
    """Create reference_to_category table if it doesn't exist.
    
    Returns:
        True if successful, False otherwise
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return False
    
    try:
        # Create table if it doesn't exist
        logger.info("Creating reference_to_category table")
        query = """
        CREATE TABLE IF NOT EXISTS reference_to_category (
            reference_id UUID NOT NULL REFERENCES reference_sources(id) ON DELETE CASCADE,
            category_id UUID NOT NULL REFERENCES reference_categories(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            PRIMARY KEY (reference_id, category_id)
        );
        """
        supabase.rpc('run_sql', {'query': query}).execute()
        
        return True
    
    except Exception as e:
        logger.error(f"Error creating reference_to_category table: {str(e)}")
        return False

def link_reference_to_category(reference_id: str, category_id: str) -> bool:
    """Link a reference to a category.
    
    Args:
        reference_id: Reference ID
        category_id: Category ID
        
    Returns:
        True if successful, False otherwise
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return False
    
    try:
        # Create link
        link_data = {
            "reference_id": reference_id,
            "category_id": category_id,
            "created_at": "now()"
        }
        
        # Use raw SQL to insert the link
        query = f"""
        INSERT INTO reference_to_category (reference_id, category_id, created_at)
        VALUES ('{reference_id}', '{category_id}', NOW())
        ON CONFLICT (reference_id, category_id) DO NOTHING;
        """
        
        supabase.rpc('run_sql', {'query': query}).execute()
        
        logger.info(f"Linked reference {reference_id} to category {category_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error linking reference to category: {str(e)}")
        return False

def fix_reference_categories():
    """Fix reference categories by creating categories and linking references."""
    if not is_connected():
        logger.error("Not connected to Supabase")
        return False
    
    try:
        # Create reference categories
        categories = create_reference_categories()
        if not categories:
            logger.error("Failed to create reference categories")
            return False
        
        # Create reference_to_category table
        if not create_reference_to_category_table():
            logger.error("Failed to create reference_to_category table")
            return False
        
        # Get references
        references = get_references()
        if not references:
            logger.error("No references found")
            return False
        
        # Link references to categories
        for reference in references:
            reference_id = reference['id']
            
            # Link to 1-3 random categories
            num_categories = random.randint(1, 3)
            selected_categories = random.sample(categories, min(num_categories, len(categories)))
            
            for category in selected_categories:
                link_reference_to_category(reference_id, category['id'])
        
        logger.info("Successfully fixed reference categories")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing reference categories: {str(e)}")
        return False

if __name__ == "__main__":
    success = fix_reference_categories()
    print(f"Reference Categories Fix: {'Success' if success else 'Failed'}")
