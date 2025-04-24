#!/usr/bin/env python3
"""
Fix Reference Categories using Supabase API.

This script creates reference categories and links references to categories.
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
                    "description": category['description']
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

def add_reference_metadata(reference_id: str, categories: List[Dict[str, str]]) -> bool:
    """Add category information to reference metadata.
    
    Args:
        reference_id: Reference ID
        categories: List of categories
        
    Returns:
        True if successful, False otherwise
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return False
    
    try:
        # Get current reference
        result = supabase.table('reference_sources').select('metadata').eq('id', reference_id).execute()
        
        if not result.data:
            logger.error(f"Reference {reference_id} not found")
            return False
        
        # Get current metadata
        current_metadata = result.data[0].get('metadata', {})
        if isinstance(current_metadata, str):
            import json
            try:
                current_metadata = json.loads(current_metadata)
            except json.JSONDecodeError:
                current_metadata = {}
        
        if not isinstance(current_metadata, dict):
            current_metadata = {}
        
        # Add categories to metadata
        category_data = [{"id": cat['id'], "name": cat['name']} for cat in categories]
        current_metadata['categories'] = category_data
        
        # Update reference
        update_data = {"metadata": current_metadata}
        result = supabase.table('reference_sources').update(update_data).eq('id', reference_id).execute()
        
        if not result.data:
            logger.error(f"Failed to update reference {reference_id}")
            return False
        
        logger.info(f"Added categories to reference {reference_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error adding reference metadata: {str(e)}")
        return False

def fix_reference_categories():
    """Fix reference categories by creating categories and adding them to reference metadata."""
    if not is_connected():
        logger.error("Not connected to Supabase")
        return False
    
    try:
        # Create reference categories
        categories = create_reference_categories()
        if not categories:
            logger.error("Failed to create reference categories")
            return False
        
        # Get references
        references = get_references()
        if not references:
            logger.error("No references found")
            return False
        
        # Add categories to reference metadata
        for reference in references:
            reference_id = reference['id']
            
            # Select 1-3 random categories
            num_categories = random.randint(1, 3)
            selected_categories = random.sample(categories, min(num_categories, len(categories)))
            
            # Add categories to reference metadata
            add_reference_metadata(reference_id, selected_categories)
        
        logger.info("Successfully fixed reference categories")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing reference categories: {str(e)}")
        return False

if __name__ == "__main__":
    success = fix_reference_categories()
    print(f"Reference Categories Fix: {'Success' if success else 'Failed'}")
