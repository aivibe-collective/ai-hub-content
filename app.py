#!/usr/bin/env python3
"""
Compatibility script for running app.py from the root directory.
This script imports and runs the app.py file from the app directory.
"""

import os
import sys
import warnings

# Show a deprecation warning
warnings.warn(
    "Running app.py from the root directory is deprecated. "
    "Please use 'python3 app/app.py' instead.",
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

# Import the Flask app from app/app.py
import os
from flask import Flask

# Create a new Flask app that uses templates from the root directory
app = Flask(__name__, template_folder=os.path.abspath('templates'))

# Import the routes from app/app.py and register them with our app
from app.app import register_routes
register_routes(app)

if __name__ == "__main__":
    # Get command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Flask application for the Agentic AI Content Creation System.")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the web interface on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to run the web interface on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    args = parser.parse_args()

    # Run the app
    app.run(host=args.host, port=args.port, debug=args.debug)
