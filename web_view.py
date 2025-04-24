#!/usr/bin/env python3
"""
Compatibility script for running web_view.py from the root directory.
This script imports and runs the web_view.py file from the app directory.
"""

import os
import sys
import warnings

# Show a deprecation warning
warnings.warn(
    "Running web_view.py from the root directory is deprecated. "
    "Please use 'python3 app/web_view.py' instead.",
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

# Import the Flask app from app/web_view.py
import os
from flask import Flask

# Create a new Flask app that uses templates from the root directory
app = Flask(__name__, template_folder=os.path.abspath('templates'))

# Import the routes from app/web_view.py
from app.web_view import index, content, content_detail, prompts, prompt_detail, outputs, output_detail, api_content, api_prompts, api_outputs, api_models, models_page, regenerate_content

# Register the routes with our app
app.route('/')(index)
app.route('/content')(content)
app.route('/content/<content_id>')(content_detail)
app.route('/prompts')(prompts)
app.route('/prompts/<prompt_id>')(prompt_detail)
app.route('/outputs')(outputs)
app.route('/outputs/<output_id>')(output_detail)
app.route('/api/content')(api_content)
app.route('/api/prompts')(api_prompts)
app.route('/api/outputs')(api_outputs)
app.route('/api/models')(api_models)
app.route('/models')(models_page)
app.route('/content/<content_id>/regenerate', methods=['GET', 'POST'])(regenerate_content)

# Import additional routes from app/web_view.py
from app.web_view import content_versions, version_detail, generation_progress, start_generation, edit_content, content_workflow, search_content, attach_image, content_references_page

# Register additional routes
app.route('/content/<content_id>/versions')(content_versions)
app.route('/content/<content_id>/versions/<int:version_number>')(version_detail)
app.route('/content/<content_id>/progress')(generation_progress)
app.route('/content/<content_id>/start-generation', methods=['POST'])(start_generation)
app.route('/content/<content_id>/edit', methods=['GET', 'POST'])(edit_content)
app.route('/content/<content_id>/workflow', methods=['GET', 'POST'])(content_workflow)
app.route('/search', methods=['GET'])(search_content)
app.route('/content/<content_id>/attach-image', methods=['GET', 'POST'])(attach_image)
app.route('/content/<content_id>/references')(content_references_page)

# Initialize prompt management and reference management routes
from app.routes.prompt_routes import init_app as init_prompt_management
from app.routes.reference_routes import init_app as init_reference_management
init_prompt_management(app)
init_reference_management(app)

# Set up template filters
from app.web_view import format_datetime, parse_metadata, status_color
app.jinja_env.filters['format_datetime'] = format_datetime
app.jinja_env.globals['parse_metadata'] = parse_metadata
app.jinja_env.globals['status_color'] = status_color

# Add the get filter for dictionaries
app.jinja_env.filters['get'] = lambda d, k: d.get(k, '') if d else ''

# Add the progress endpoint
@app.route('/content/<content_id>/progress')
def content_progress(content_id):
    """Get the progress of content generation."""
    from flask import jsonify

    # Get the content from Supabase
    try:
        # Import the functions from the supabase_client
        from core.supabase_client import get_content_by_id as get_content
        from core.supabase_client import get_prompt_logs_for_content as get_prompts
        from core.supabase_client import get_generation_outputs_for_content as get_outputs

        content = get_content(content_id)
        if not content:
            return jsonify({})

        # Get the latest prompt and output
        prompts = get_prompts(content_id, limit=10)
        outputs = get_outputs(content_id, limit=10)

        # If there are no prompts or outputs, return empty progress
        if not prompts or not outputs:
            return jsonify({})
    except Exception as e:
        print(f"Error getting content progress: {e}")
        return jsonify({})

    # Get the latest prompt and output
    latest_prompt = prompts[0] if prompts else None
    latest_output = outputs[0] if outputs else None

    # Get the model and temperature from the latest prompt
    model = latest_prompt.get('metadata', {}).get('model', 'Unknown')
    temperature = latest_prompt.get('metadata', {}).get('temperature', 0.7)

    # Get the start time from the latest prompt
    start_time = latest_prompt.get('created_at')

    # Define the steps
    steps = [
        {
            'name': 'Content Generation',
            'description': 'Generating main content',
            'status': 'pending'
        },
        {
            'name': 'Source Generation',
            'description': 'Generating sources',
            'status': 'pending'
        },
        {
            'name': 'Content Integration',
            'description': 'Integrating sources into content',
            'status': 'pending'
        },
        {
            'name': 'Content Storage',
            'description': 'Storing content in database',
            'status': 'pending'
        }
    ]

    # Update the steps based on the content status
    if content.get('status') == 'In Progress':
        steps[0]['status'] = 'in-progress'
    elif content.get('status') == 'Completed':
        for step in steps:
            step['status'] = 'complete'
    elif content.get('status') == 'Failed':
        # Find the step that failed
        error_message = latest_output.get('metadata', {}).get('error')
        if 'source' in error_message.lower() if error_message else False:
            steps[0]['status'] = 'complete'
            steps[1]['status'] = 'error'
            steps[1]['error'] = error_message
        else:
            steps[0]['status'] = 'error'
            steps[0]['error'] = error_message

    # Return the progress
    return jsonify({
        'content_id': content_id,
        'status': content.get('status'),
        'model': model,
        'temperature': temperature,
        'start_time': start_time,
        'steps': steps
    })

app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default-secret-key')

if __name__ == "__main__":
    # Get command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Web interface for viewing Supabase tables.")
    parser.add_argument("--port", type=int, default=8081, help="Port to run the web interface on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to run the web interface on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    args = parser.parse_args()

    # Run the app
    app.run(host=args.host, port=args.port, debug=args.debug)
