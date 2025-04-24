#!/usr/bin/env python3
"""
Fix Reference Management Dashboard.

This script adds reference quality assessments and categories to make the
Reference Management dashboard display data correctly.
"""

import os
import uuid
import logging
import datetime
import random
from typing import Dict, List, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import our custom modules
from supabase_client import supabase, is_connected

def get_references(limit: int = 20) -> List[Dict[str, Any]]:
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

def create_reference_categories() -> List[str]:
    """Create reference categories if they don't exist.
    
    Returns:
        List of category IDs
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
    
    category_ids = []
    
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
            result = supabase.table('reference_categories').select('id').eq('name', category['name']).execute()
            
            if result.data:
                category_id = result.data[0]['id']
            else:
                # Create category
                category_data = {
                    "id": str(uuid.uuid4()),
                    "name": category['name'],
                    "description": category['description'],
                    "created_at": datetime.datetime.now().isoformat(),
                    "updated_at": datetime.datetime.now().isoformat()
                }
                
                result = supabase.table('reference_categories').insert(category_data).execute()
                
                if not result.data:
                    logger.error(f"Failed to create category: {category['name']}")
                    continue
                
                category_id = result.data[0]['id']
                logger.info(f"Created category: {category['name']} ({category_id})")
            
            category_ids.append(category_id)
        
        return category_ids
    
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
        # Check if table exists
        try:
            result = supabase.table('reference_to_category').select('count').execute()
        except Exception:
            # Create table if it doesn't exist
            logger.info("Creating reference_to_category table")
            query = """
            CREATE TABLE IF NOT EXISTS reference_to_category (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                reference_id UUID NOT NULL REFERENCES reference_sources(id) ON DELETE CASCADE,
                category_id UUID NOT NULL REFERENCES reference_categories(id) ON DELETE CASCADE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(reference_id, category_id)
            );
            """
            supabase.rpc('run_sql', {'query': query}).execute()
        
        return True
    
    except Exception as e:
        logger.error(f"Error creating reference_to_category table: {str(e)}")
        return False

def create_reference_quality_table() -> bool:
    """Create reference_quality table if it doesn't exist.
    
    Returns:
        True if successful, False otherwise
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return False
    
    try:
        # Check if table exists
        try:
            result = supabase.table('reference_quality').select('count').execute()
        except Exception:
            # Create table if it doesn't exist
            logger.info("Creating reference_quality table")
            query = """
            CREATE TABLE IF NOT EXISTS reference_quality (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                reference_id UUID NOT NULL REFERENCES reference_sources(id) ON DELETE CASCADE,
                currency_score INTEGER CHECK (currency_score BETWEEN 1 AND 5),
                relevance_score INTEGER CHECK (relevance_score BETWEEN 1 AND 5),
                authority_score INTEGER CHECK (authority_score BETWEEN 1 AND 5),
                accuracy_score INTEGER CHECK (accuracy_score BETWEEN 1 AND 5),
                purpose_score INTEGER CHECK (purpose_score BETWEEN 1 AND 5),
                overall_score INTEGER,
                assessment_notes TEXT,
                assessed_by TEXT,
                assessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
            supabase.rpc('run_sql', {'query': query}).execute()
        
        return True
    
    except Exception as e:
        logger.error(f"Error creating reference_quality table: {str(e)}")
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
        # Check if link already exists
        result = supabase.table('reference_to_category').select('id').eq('reference_id', reference_id).eq('category_id', category_id).execute()
        
        if result.data:
            logger.info(f"Reference {reference_id} already linked to category {category_id}")
            return True
        
        # Create link
        link_data = {
            "id": str(uuid.uuid4()),
            "reference_id": reference_id,
            "category_id": category_id,
            "created_at": datetime.datetime.now().isoformat()
        }
        
        result = supabase.table('reference_to_category').insert(link_data).execute()
        
        if not result.data:
            logger.error(f"Failed to link reference {reference_id} to category {category_id}")
            return False
        
        logger.info(f"Linked reference {reference_id} to category {category_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error linking reference to category: {str(e)}")
        return False

def create_reference_quality(reference_id: str) -> bool:
    """Create a quality assessment for a reference.
    
    Args:
        reference_id: Reference ID
        
    Returns:
        True if successful, False otherwise
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return False
    
    try:
        # Check if quality assessment already exists
        result = supabase.table('reference_quality').select('id').eq('reference_id', reference_id).execute()
        
        if result.data:
            logger.info(f"Quality assessment already exists for reference {reference_id}")
            return True
        
        # Create quality assessment
        quality_data = {
            "id": str(uuid.uuid4()),
            "reference_id": reference_id,
            "currency_score": random.randint(3, 5),
            "relevance_score": random.randint(3, 5),
            "authority_score": random.randint(3, 5),
            "accuracy_score": random.randint(3, 5),
            "purpose_score": random.randint(3, 5),
            "overall_score": random.randint(3, 5),
            "assessment_notes": "Automatically generated quality assessment.",
            "assessed_by": "system",
            "assessed_at": datetime.datetime.now().isoformat(),
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        }
        
        result = supabase.table('reference_quality').insert(quality_data).execute()
        
        if not result.data:
            logger.error(f"Failed to create quality assessment for reference {reference_id}")
            return False
        
        logger.info(f"Created quality assessment for reference {reference_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error creating reference quality: {str(e)}")
        return False

def fix_reference_management_dashboard():
    """Fix the reference management dashboard by adding sample data."""
    if not is_connected():
        logger.error("Not connected to Supabase")
        return False
    
    try:
        # Create reference categories
        category_ids = create_reference_categories()
        if not category_ids:
            logger.error("Failed to create reference categories")
            return False
        
        # Create reference_to_category table
        if not create_reference_to_category_table():
            logger.error("Failed to create reference_to_category table")
            return False
        
        # Create reference_quality table
        if not create_reference_quality_table():
            logger.error("Failed to create reference_quality table")
            return False
        
        # Get references
        references = get_references()
        if not references:
            logger.error("No references found")
            return False
        
        # Link references to categories and create quality assessments
        for reference in references:
            reference_id = reference['id']
            
            # Link to 1-3 random categories
            num_categories = random.randint(1, 3)
            selected_categories = random.sample(category_ids, min(num_categories, len(category_ids)))
            
            for category_id in selected_categories:
                link_reference_to_category(reference_id, category_id)
            
            # Create quality assessment
            create_reference_quality(reference_id)
        
        logger.info("Successfully fixed reference management dashboard")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing reference management dashboard: {str(e)}")
        return False

if __name__ == "__main__":
    success = fix_reference_management_dashboard()
    print(f"Reference Management Dashboard Fix: {'Success' if success else 'Failed'}")
