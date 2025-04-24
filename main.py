#!/usr/bin/env python3
"""
Compatibility script for running main.py from the root directory.
This script imports and runs the main.py file from the app directory.
"""

import os
import sys
import warnings

# Show a deprecation warning
warnings.warn(
    "Running main.py from the root directory is deprecated. "
    "Please use 'python3 app/main.py' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create compatibility imports
sys.modules['google_ai_client'] = __import__('core.google_ai_client', fromlist=['*'])
sys.modules['supabase_client'] = __import__('core.supabase_client', fromlist=['*'])
sys.modules['content_workflow_supabase'] = __import__('workflows.content.content_workflow_supabase', fromlist=['*'])
sys.modules['content_workflow_with_references'] = __import__('workflows.content.content_workflow_with_references', fromlist=['*'])
sys.modules['content_workflow_with_ai_references'] = __import__('workflows.content.content_workflow_with_ai_references', fromlist=['*'])
sys.modules['ai_reference_processor'] = __import__('workflows.reference.ai_reference_processor', fromlist=['*'])
sys.modules['improved_reference_extractor'] = __import__('workflows.reference.improved_reference_extractor', fromlist=['*'])
sys.modules['reference_management'] = __import__('workflows.reference.reference_management', fromlist=['*'])

# Import and run the main.py file from the app directory
from app.main import main

if __name__ == "__main__":
    main()
