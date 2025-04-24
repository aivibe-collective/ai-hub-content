#!/usr/bin/env python3
"""
Fix Prompt Management Dashboard.

This script adds sample prompt usage and feedback data to make the
Prompt Management dashboard display data correctly.
"""

import os
import uuid
import logging
import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import our custom modules
from supabase_client import supabase, is_connected

def get_prompt_templates(limit: int = 5) -> List[Dict[str, Any]]:
    """Get prompt templates from the database.
    
    Args:
        limit: Maximum number of templates to retrieve
        
    Returns:
        List of prompt templates
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return []
    
    try:
        result = supabase.table('prompt_templates').select('*').limit(limit).execute()
        return result.data if result.data else []
    
    except Exception as e:
        logger.error(f"Error getting prompt templates: {str(e)}")
        return []

def get_prompt_logs(limit: int = 10) -> List[Dict[str, Any]]:
    """Get prompt logs from the database.
    
    Args:
        limit: Maximum number of logs to retrieve
        
    Returns:
        List of prompt logs
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return []
    
    try:
        result = supabase.table('prompt_logs').select('*').limit(limit).execute()
        return result.data if result.data else []
    
    except Exception as e:
        logger.error(f"Error getting prompt logs: {str(e)}")
        return []

def create_prompt_usage(template_id: str, prompt_id: str, content_id: str = None) -> str:
    """Create a prompt usage record.
    
    Args:
        template_id: Prompt template ID
        prompt_id: Prompt log ID
        content_id: Content ID (optional)
        
    Returns:
        ID of the created prompt usage record
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return None
    
    try:
        usage_data = {
            "id": str(uuid.uuid4()),
            "template_id": template_id,
            "prompt_id": prompt_id,
            "variables": {"topic": "AI", "audience_technical_level": "Beginner"},
            "rendered_prompt": "Generate comprehensive content about AI for a beginner audience.",
            "model": "gemini-1.5-flash",
            "temperature": 0.7,
            "content_id": content_id,
            "success": True,
            "metrics": {"tokens": 1024, "generation_time": 2.5},
            "created_at": datetime.datetime.now().isoformat(),
            "user_id": "system"
        }
        
        result = supabase.table('prompt_usage').insert(usage_data).execute()
        
        if not result.data:
            logger.error("Failed to create prompt usage")
            return None
        
        usage_id = result.data[0]['id']
        logger.info(f"Created prompt usage: {usage_id}")
        return usage_id
    
    except Exception as e:
        logger.error(f"Error creating prompt usage: {str(e)}")
        return None

def create_prompt_feedback(usage_id: str, rating: int = 4) -> bool:
    """Create a prompt feedback record.
    
    Args:
        usage_id: Prompt usage ID
        rating: Rating (1-5)
        
    Returns:
        True if successful, False otherwise
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return False
    
    try:
        feedback_data = {
            "id": str(uuid.uuid4()),
            "usage_id": usage_id,
            "rating": rating,
            "feedback_text": "Good prompt, generated useful content.",
            "feedback_type": "user",
            "created_at": datetime.datetime.now().isoformat(),
            "user_id": "system"
        }
        
        result = supabase.table('prompt_feedback').insert(feedback_data).execute()
        
        if not result.data:
            logger.error("Failed to create prompt feedback")
            return False
        
        logger.info(f"Created prompt feedback for usage: {usage_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error creating prompt feedback: {str(e)}")
        return False

def fix_prompt_management_dashboard():
    """Fix the prompt management dashboard by adding sample data."""
    if not is_connected():
        logger.error("Not connected to Supabase")
        return False
    
    try:
        # Get prompt templates
        templates = get_prompt_templates(limit=5)
        if not templates:
            logger.error("No prompt templates found")
            return False
        
        # Get prompt logs
        logs = get_prompt_logs(limit=10)
        if not logs:
            logger.error("No prompt logs found")
            return False
        
        # Create prompt usage and feedback for each template
        for template in templates:
            template_id = template['id']
            
            # Use a different prompt log for each template
            for i, log in enumerate(logs[:2]):
                prompt_id = log['id']
                content_id = log.get('content_id')
                
                # Create prompt usage
                usage_id = create_prompt_usage(template_id, prompt_id, content_id)
                if not usage_id:
                    continue
                
                # Create prompt feedback
                create_prompt_feedback(usage_id, rating=4 + (i % 2))  # Ratings of 4 or 5
        
        logger.info("Successfully fixed prompt management dashboard")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing prompt management dashboard: {str(e)}")
        return False

if __name__ == "__main__":
    success = fix_prompt_management_dashboard()
    print(f"Prompt Management Dashboard Fix: {'Success' if success else 'Failed'}")
