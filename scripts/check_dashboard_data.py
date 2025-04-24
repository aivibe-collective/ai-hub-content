#!/usr/bin/env python3
"""
Check Dashboard Data.

This script checks if the dashboard is displaying data correctly by making
direct API calls to the dashboard endpoints.
"""

import os
import json
import logging
import requests
from typing import Dict, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def check_references():
    """Check if references are being displayed correctly."""
    try:
        response = requests.get('http://localhost:8080/api/references')
        response.raise_for_status()
        
        references = response.json()
        logger.info(f"Found {len(references)} references")
        
        if len(references) > 0:
            logger.info(f"First reference: {json.dumps(references[0], indent=2)}")
        
        return len(references) > 0
    
    except Exception as e:
        logger.error(f"Error checking references: {str(e)}")
        return False

def check_prompts():
    """Check if prompts are being displayed correctly."""
    try:
        response = requests.get('http://localhost:8080/api/prompts')
        response.raise_for_status()
        
        data = response.json()
        
        templates = data.get('templates', [])
        usage = data.get('usage', [])
        logs = data.get('logs', [])
        
        logger.info(f"Found {len(templates)} prompt templates")
        logger.info(f"Found {len(usage)} prompt usage records")
        logger.info(f"Found {len(logs)} prompt logs")
        
        if len(templates) > 0:
            logger.info(f"First template: {json.dumps(templates[0], indent=2)}")
        
        if len(usage) > 0:
            logger.info(f"First usage: {json.dumps(usage[0], indent=2)}")
        
        if len(logs) > 0:
            logger.info(f"First log: {json.dumps(logs[0], indent=2)}")
        
        return len(templates) > 0 or len(usage) > 0 or len(logs) > 0
    
    except Exception as e:
        logger.error(f"Error checking prompts: {str(e)}")
        return False

def check_reference_quality():
    """Check if reference quality data is being displayed correctly."""
    try:
        response = requests.get('http://localhost:8080/api/reference_quality')
        response.raise_for_status()
        
        quality = response.json()
        logger.info(f"Found {len(quality)} reference quality records")
        
        if len(quality) > 0:
            logger.info(f"First quality record: {json.dumps(quality[0], indent=2)}")
        
        return len(quality) > 0
    
    except Exception as e:
        logger.error(f"Error checking reference quality: {str(e)}")
        return False

def check_reference_categories():
    """Check if reference categories are being displayed correctly."""
    try:
        response = requests.get('http://localhost:8080/api/reference_categories')
        response.raise_for_status()
        
        categories = response.json()
        logger.info(f"Found {len(categories)} reference categories")
        
        if len(categories) > 0:
            logger.info(f"First category: {json.dumps(categories[0], indent=2)}")
        
        return len(categories) > 0
    
    except Exception as e:
        logger.error(f"Error checking reference categories: {str(e)}")
        return False

if __name__ == '__main__':
    logger.info("Checking dashboard data...")
    
    references_ok = check_references()
    prompts_ok = check_prompts()
    quality_ok = check_reference_quality()
    categories_ok = check_reference_categories()
    
    logger.info("\nDashboard Data Check Results:")
    logger.info(f"References: {'OK' if references_ok else 'FAILED'}")
    logger.info(f"Prompts: {'OK' if prompts_ok else 'FAILED'}")
    logger.info(f"Reference Quality: {'OK' if quality_ok else 'FAILED'}")
    logger.info(f"Reference Categories: {'OK' if categories_ok else 'FAILED'}")
    
    if references_ok and prompts_ok and quality_ok and categories_ok:
        logger.info("\nAll dashboard data checks passed!")
    else:
        logger.error("\nSome dashboard data checks failed!")
