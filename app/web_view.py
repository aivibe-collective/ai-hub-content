#!/usr/bin/env python3
"""
Web interface for viewing Supabase tables.
"""

import os
import json
import datetime
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global dictionary to store generation progress
# This avoids the Flask session context issue in background threads
generation_progress_store = {}

# Helper functions for templates
def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    """Format a datetime string."""
    if not value:
        return ''
    try:
        if isinstance(value, str):
            # Try to parse ISO format
            dt = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
        else:
            dt = value
        return dt.strftime(format)
    except Exception as e:
        logger.error(f"Error formatting datetime: {str(e)}")
        return value

def parse_metadata(metadata_str):
    """Parse metadata JSON string."""
    if not metadata_str:
        return {}
    try:
        if isinstance(metadata_str, dict):
            return metadata_str
        return json.loads(metadata_str)
    except Exception as e:
        logger.error(f"Error parsing metadata: {str(e)}")
        return {}

def status_color(status):
    """Get Bootstrap color class for status."""
    status_colors = {
        'Not Started': 'secondary',
        'In Progress': 'warning',
        'Regenerating': 'info',
        'Edited': 'info',
        'Review Requested': 'primary',
        'In Review': 'primary',
        'Revision Needed': 'warning',
        'Approved': 'success',
        'Completed': 'success',
        'Published': 'success',
        'Archived': 'secondary',
        'Failed': 'danger'
    }
    return status_colors.get(status, 'secondary')

# Import our custom modules
from core.supabase_client import (
    is_connected, get_content_inventory, get_prompt_logs,
    get_generation_outputs, get_full_content, get_content_by_id,
    update_content_status, save_content_version, get_content_versions,
    get_available_models, update_content_item, log_generation_output
)
from workflows.content_workflow_with_references import generate_content_for_item
from core.google_ai_client import list_models as get_available_models
from app.routes.prompt_routes import init_app as init_prompt_management
from app.routes.reference_routes import init_app as init_reference_management

# Alias for get_content_by_id for clarity
def get_content_item(content_id):
    """Get content item by ID."""
    return get_content_by_id(content_id)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Register template filters
app.jinja_env.filters['format_datetime'] = format_datetime
app.jinja_env.globals['parse_metadata'] = parse_metadata
app.jinja_env.globals['status_color'] = status_color
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default-secret-key')

@app.route('/')
def index():
    """Home page."""
    # Check Supabase connection
    connected = is_connected()
    if not connected:
        flash('Not connected to Supabase. Using local mode.', 'warning')
        # Use mock data for demonstration
        total_items = 10
        completed_items = 5
        in_progress_items = 3
        not_started_items = 2
        total_prompts = 15
        total_outputs = 20
    else:
        # Get content inventory stats
        content_items = get_content_inventory()
        total_items = len(content_items)
        completed_items = len([item for item in content_items if item['status'] == 'Completed'])
        in_progress_items = len([item for item in content_items if item['status'] == 'In Progress'])
        not_started_items = len([item for item in content_items if item['status'] == 'Not Started'])

        # Get prompt logs stats
        prompt_logs = get_prompt_logs(limit=1000)
        total_prompts = len(prompt_logs)

        # Get generation outputs stats
        generation_outputs = get_generation_outputs(limit=1000)
        total_outputs = len(generation_outputs)

    return render_template(
        'index.html',
        connected=True,
        total_items=total_items,
        completed_items=completed_items,
        in_progress_items=in_progress_items,
        not_started_items=not_started_items,
        total_prompts=total_prompts,
        total_outputs=total_outputs
    )

@app.route('/content')
def content():
    """Content inventory page."""
    # Check Supabase connection
    connected = is_connected()
    if not connected:
        flash('Not connected to Supabase. Using local mode.', 'warning')
        # Use mock data for demonstration
        mock_content_items = [
            {
                'content_id': 'LRN-BEG-001',
                'title': 'Introduction to AI for SMEs',
                'section': 'Learning',
                'status': 'Completed',
                'model': 'gemini-1.5-flash',
                'temperature': 0.7
            },
            {
                'content_id': 'LRN-BEG-002',
                'title': 'AI Fundamentals for Business',
                'section': 'Learning',
                'status': 'In Progress',
                'model': 'gemini-1.5-flash',
                'temperature': 0.7
            },
            {
                'content_id': 'LRN-BEG-003',
                'title': 'Practical AI Applications for SMEs',
                'section': 'Learning',
                'status': 'Not Started',
                'model': 'gemini-1.5-flash',
                'temperature': 0.7
            }
        ]
        content_items = mock_content_items
        sections = ['Learning']
    else:
        # Get content inventory
        content_items = get_content_inventory()

        # Filter by status if provided
        status = request.args.get('status')
        if status:
            content_items = [item for item in content_items if item['status'] == status]

        # Filter by section if provided
        section = request.args.get('section')
        if section:
            content_items = [item for item in content_items if item['section'] == section]

        # Get unique sections for filter dropdown
        sections = sorted(list(set(item['section'] for item in get_content_inventory())))

    return render_template(
        'content.html',
        content_items=content_items,
        sections=sections,
        selected_status=status,
        selected_section=section
    )

@app.route('/content/<content_id>')
def content_detail(content_id):
    """Content detail page."""
    # Check Supabase connection
    connected = is_connected()
    if not connected:
        flash('Not connected to Supabase. Using local mode.', 'warning')
        # Use mock data for demonstration
        mock_content_items = {
            'LRN-BEG-001': {
                'content_id': 'LRN-BEG-001',
                'title': 'Introduction to AI for SMEs',
                'section': 'Learning',
                'status': 'Completed',
                'model': 'gemini-1.5-flash',
                'temperature': 0.7
            },
            'LRN-BEG-002': {
                'content_id': 'LRN-BEG-002',
                'title': 'AI Fundamentals for Business',
                'section': 'Learning',
                'status': 'In Progress',
                'model': 'gemini-1.5-flash',
                'temperature': 0.7
            },
            'LRN-BEG-003': {
                'content_id': 'LRN-BEG-003',
                'title': 'Practical AI Applications for SMEs',
                'section': 'Learning',
                'status': 'Not Started',
                'model': 'gemini-1.5-flash',
                'temperature': 0.7
            }
        }
        content_item = mock_content_items.get(content_id)
        prompt_logs = []
        generation_outputs = []
    else:
        # Get content item
        content_item = get_content_by_id(content_id)
        if not content_item:
            flash(f'Content item {content_id} not found', 'error')
            return redirect(url_for('content'))

        # Get prompt logs for this content item
        prompt_logs = get_prompt_logs(content_id=content_id)

        # Get generation outputs for this content item
        generation_outputs = get_generation_outputs(content_id=content_id)

    # Try to read the generated content file
    content_file_path = f'generated_content/{content_id}.md'
    content_file = None
    if os.path.exists(content_file_path):
        with open(content_file_path, 'r') as f:
            content_file = f.read()

    # If not connected and no content file, create a mock content file
    if not connected and not content_file and content_item:
        content_file = f"# {content_item['title']}\n\nThis is a mock content file for demonstration purposes.\n\n## Introduction\n\nThis content would normally be generated by the AI model.\n\n## Main Content\n\nThe content would include information about {content_item['title']}.\n\n## Conclusion\n\nThis is the end of the mock content.\n\n## Sources\n\n[SRC1] Mock Source 1. *Journal of AI*, 2023.\n\n[SRC2] Mock Source 2. *Business AI Review*, 2022.\n"

    return render_template(
        'content_detail.html',
        content_item=content_item,
        prompt_logs=prompt_logs,
        generation_outputs=generation_outputs,
        content_file=content_file
    )

@app.route('/prompts')
def prompts():
    """Prompt logs page."""
    # Get prompt logs
    prompt_logs = get_prompt_logs(limit=100)

    # Filter by content_id if provided
    content_id = request.args.get('content_id')
    if content_id:
        prompt_logs = [log for log in prompt_logs if log['content_id'] == content_id]

    # Filter by prompt_type if provided
    prompt_type = request.args.get('prompt_type')
    if prompt_type:
        prompt_logs = [log for log in prompt_logs if log['prompt_type'] == prompt_type]

    # Get unique prompt types for filter dropdown
    prompt_types = sorted(list(set(log['prompt_type'] for log in get_prompt_logs(limit=1000) if log['prompt_type'])))

    return render_template(
        'prompts.html',
        prompt_logs=prompt_logs,
        prompt_types=prompt_types,
        selected_content_id=content_id,
        selected_prompt_type=prompt_type
    )

@app.route('/prompts/<prompt_id>')
def prompt_detail(prompt_id):
    """Prompt detail page."""
    # Get prompt logs
    prompt_logs = get_prompt_logs(limit=1000)
    prompt_log = next((log for log in prompt_logs if log['id'] == prompt_id), None)

    if not prompt_log:
        flash(f'Prompt log {prompt_id} not found', 'error')
        return redirect(url_for('prompts'))

    # Get generation outputs for this prompt
    generation_outputs = get_generation_outputs(prompt_id=prompt_id)

    return render_template(
        'prompt_detail.html',
        prompt_log=prompt_log,
        generation_outputs=generation_outputs
    )

@app.route('/outputs')
def outputs():
    """Generation outputs page."""
    # Get generation outputs
    generation_outputs = get_generation_outputs(limit=100)

    # Filter by content_id if provided
    content_id = request.args.get('content_id')
    if content_id:
        generation_outputs = [output for output in generation_outputs if output['content_id'] == content_id]

    return render_template(
        'outputs.html',
        generation_outputs=generation_outputs,
        selected_content_id=content_id
    )

@app.route('/outputs/<output_id>')
def output_detail(output_id):
    """Output detail page."""
    # Get generation outputs
    generation_outputs = get_generation_outputs(limit=1000)
    generation_output = next((output for output in generation_outputs if output['id'] == output_id), None)

    if not generation_output:
        flash(f'Generation output {output_id} not found', 'error')
        return redirect(url_for('outputs'))

    # Get full content if available
    full_content = get_full_content(output_id)
    if full_content:
        generation_output['output_text'] = full_content

    # Get prompt log for this output
    prompt_logs = get_prompt_logs(limit=1000)
    prompt_log = next((log for log in prompt_logs if log['id'] == generation_output['prompt_id']), None)

    return render_template(
        'output_detail.html',
        generation_output=generation_output,
        prompt_log=prompt_log
    )

@app.route('/api/content')
def api_content():
    """API endpoint for content inventory."""
    content_items = get_content_inventory()
    return jsonify(content_items)

@app.route('/api/prompts')
def api_prompts():
    """API endpoint for prompt logs."""
    prompt_logs = get_prompt_logs(limit=100)
    return jsonify(prompt_logs)

@app.route('/api/outputs')
def api_outputs():
    """API endpoint for generation outputs."""
    generation_outputs = get_generation_outputs(limit=100)
    return jsonify(generation_outputs)

@app.route('/api/models')
def api_models():
    """API endpoint for available models."""
    models = get_available_models()
    return jsonify(models)

@app.route('/models')
def models_page():
    """Page displaying available models."""
    models = get_available_models()
    return render_template('models.html', models=models)

@app.route('/content/<content_id>/regenerate', methods=['GET', 'POST'])
def regenerate_content(content_id):
    """Regenerate content page."""
    # Check Supabase connection
    connected = is_connected()
    if not connected:
        flash('Not connected to Supabase. Using local mode.', 'warning')
        # Use mock data for demonstration
        mock_content_items = {
            'LRN-BEG-001': {
                'content_id': 'LRN-BEG-001',
                'title': 'Introduction to AI for SMEs',
                'section': 'Learning',
                'status': 'Completed',
                'model': 'gemini-1.5-flash',
                'temperature': 0.7
            },
            'LRN-BEG-002': {
                'content_id': 'LRN-BEG-002',
                'title': 'AI Fundamentals for Business',
                'section': 'Learning',
                'status': 'In Progress',
                'model': 'gemini-1.5-flash',
                'temperature': 0.7
            },
            'LRN-BEG-003': {
                'content_id': 'LRN-BEG-003',
                'title': 'Practical AI Applications for SMEs',
                'section': 'Learning',
                'status': 'Not Started',
                'model': 'gemini-1.5-flash',
                'temperature': 0.7
            }
        }
        content_item = mock_content_items.get(content_id)
        if not content_item:
            flash(f'Content item {content_id} not found', 'error')
            return redirect(url_for('content'))
    else:
        # Get content item
        content_item = get_content_by_id(content_id)
        if not content_item:
            flash(f'Content item {content_id} not found', 'error')
            return redirect(url_for('content'))

    # Get available models
    models = get_available_models()

    if request.method == 'POST':
        # Get form data
        model = request.form.get('model')
        temperature = float(request.form.get('temperature', 0.7))
        force = 'force' in request.form
        include_references = 'include_references' in request.form

        if not connected:
            # In local mode, just create a mock content file
            content_file_path = f'generated_content/{content_id}.md'
            os.makedirs('generated_content', exist_ok=True)

            # Create a mock content file
            mock_content = f"# {content_item['title']}\n\nThis content was regenerated in local mode with model {model} at temperature {temperature}.\n\n## Introduction\n\nThis content would normally be generated by the AI model.\n\n## Main Content\n\nThe content would include information about {content_item['title']}.\n\n## Conclusion\n\nThis is the end of the mock content.\n\n## Sources\n\n[SRC1] Mock Source 1. *Journal of AI*, 2023.\n\n[SRC2] Mock Source 2. *Business AI Review*, 2022.\n"

            with open(content_file_path, 'w') as f:
                f.write(mock_content)

            flash(f'Mock content regenerated with model {model} (local mode)', 'success')
            return redirect(url_for('content_detail', content_id=content_id))
        else:
            # Save current version if it exists
            content_file_path = f'generated_content/{content_id}.md'
            if os.path.exists(content_file_path):
                with open(content_file_path, 'r') as f:
                    current_content = f.read()

                # Save current version
                current_model = content_item.get('model', 'unknown')
                current_temp = content_item.get('temperature', 0.7)

                try:
                    # Try to save to Supabase
                    version_number = save_content_version(content_id, current_content, current_model, current_temp)
                    if version_number:
                        flash(f'Saved version {version_number} to Supabase', 'success')
                except Exception as e:
                    # If Supabase fails, save locally
                    os.makedirs('content_versions', exist_ok=True)
                    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                    local_file = f'content_versions/{content_id}_{timestamp}.md'
                    with open(local_file, 'w') as f:
                        f.write(current_content)
                    flash(f'Saved version to local file: {local_file}', 'info')

            # Update content status
            update_content_status(content_id, 'Regenerating')

            # Set up global progress tracking
            global generation_progress_store
            generation_progress_store[content_id] = {
                'content_id': content_id,
                'steps': [
                    {'name': 'Preparing', 'status': 'pending', 'description': 'Setting up generation parameters'},
                    {'name': 'Generating Content', 'status': 'pending', 'description': 'Creating content with AI model'},
                    {'name': 'Collecting Sources', 'status': 'pending', 'description': 'Finding and evaluating sources'},
                    {'name': 'Formatting', 'status': 'pending', 'description': 'Formatting content with sources'},
                    {'name': 'Saving', 'status': 'pending', 'description': 'Saving content to database'}
                ],
                'current_step': 0,
                'start_time': datetime.datetime.now().isoformat(),
                'model': model,
                'temperature': temperature,
                'force': 'force' in request.form,
                'include_references': include_references
            }

            # Update first step to in-progress
            generation_progress_store[content_id]['steps'][0]['status'] = 'in-progress'

            # Redirect to progress page
            return render_template(
                'generation_progress.html',
                content_item=content_item,
                model=model,
                temperature=temperature,
                start_time=datetime.datetime.now().strftime('%H:%M:%S')
            )

            # Note: The actual generation will be started by a background process
            # or when the progress page is loaded and makes API calls



    return render_template(
        'regenerate.html',
        content_item=content_item,
        models=models,
        include_references_default=True
    )

@app.route('/content/<content_id>/versions')
def content_versions(content_id):
    """Content versions page."""
    # Check Supabase connection
    connected = is_connected()
    if not connected:
        flash('Not connected to Supabase. Using local mode.', 'warning')
        # Use mock data for demonstration
        mock_content_items = {
            'LRN-BEG-001': {
                'content_id': 'LRN-BEG-001',
                'title': 'Introduction to AI for SMEs',
                'section': 'Learning',
                'status': 'Completed',
                'model': 'gemini-1.5-flash',
                'temperature': 0.7
            },
            'LRN-BEG-002': {
                'content_id': 'LRN-BEG-002',
                'title': 'AI Fundamentals for Business',
                'section': 'Learning',
                'status': 'In Progress',
                'model': 'gemini-1.5-flash',
                'temperature': 0.7
            },
            'LRN-BEG-003': {
                'content_id': 'LRN-BEG-003',
                'title': 'Practical AI Applications for SMEs',
                'section': 'Learning',
                'status': 'Not Started',
                'model': 'gemini-1.5-flash',
                'temperature': 0.7
            }
        }
        content_item = mock_content_items.get(content_id)
        if not content_item:
            flash(f'Content item {content_id} not found', 'error')
            return redirect(url_for('content'))

        # Create mock versions
        versions = [
            {
                'version_number': 2,
                'content_id': content_id,
                'model': 'gemini-1.5-flash',
                'temperature': 0.7,
                'created_at': '2023-06-15T10:30:00',
                'content_text': f"# {content_item['title']} (Version 2)\n\nThis is a mock version 2 for demonstration purposes.\n\n## Introduction\n\nThis content would normally be generated by the AI model.\n\n## Main Content\n\nThe content would include information about {content_item['title']}.\n\n## Conclusion\n\nThis is the end of the mock content.\n\n## Sources\n\n[SRC1] Mock Source 1. *Journal of AI*, 2023.\n\n[SRC2] Mock Source 2. *Business AI Review*, 2022.\n"
            },
            {
                'version_number': 1,
                'content_id': content_id,
                'model': 'gemini-1.5-pro',
                'temperature': 0.5,
                'created_at': '2023-06-10T14:20:00',
                'content_text': f"# {content_item['title']} (Version 1)\n\nThis is a mock version 1 for demonstration purposes.\n\n## Introduction\n\nThis content would normally be generated by the AI model.\n\n## Main Content\n\nThe content would include information about {content_item['title']}.\n\n## Conclusion\n\nThis is the end of the mock content.\n\n## Sources\n\n[SRC1] Mock Source 1. *Journal of AI*, 2023.\n"
            }
        ]
    else:
        # Get content item
        content_item = get_content_by_id(content_id)
        if not content_item:
            flash(f'Content item {content_id} not found', 'error')
            return redirect(url_for('content'))

        # Get versions
        versions = get_content_versions(content_id)

    return render_template(
        'versions.html',
        content_item=content_item,
        versions=versions
    )

@app.route('/content/<content_id>/versions/<int:version_number>')
def version_detail(content_id, version_number):
    """Version detail page."""
    # Check Supabase connection
    connected = is_connected()
    if not connected:
        flash('Not connected to Supabase. Using local mode.', 'warning')
        # Use mock data for demonstration
        mock_content_items = {
            'LRN-BEG-001': {
                'content_id': 'LRN-BEG-001',
                'title': 'Introduction to AI for SMEs',
                'section': 'Learning',
                'status': 'Completed',
                'model': 'gemini-1.5-flash',
                'temperature': 0.7
            },
            'LRN-BEG-002': {
                'content_id': 'LRN-BEG-002',
                'title': 'AI Fundamentals for Business',
                'section': 'Learning',
                'status': 'In Progress',
                'model': 'gemini-1.5-flash',
                'temperature': 0.7
            },
            'LRN-BEG-003': {
                'content_id': 'LRN-BEG-003',
                'title': 'Practical AI Applications for SMEs',
                'section': 'Learning',
                'status': 'Not Started',
                'model': 'gemini-1.5-flash',
                'temperature': 0.7
            }
        }
        content_item = mock_content_items.get(content_id)
        if not content_item:
            flash(f'Content item {content_id} not found', 'error')
            return redirect(url_for('content'))

        # Create mock versions
        mock_versions = [
            {
                'version_number': 2,
                'content_id': content_id,
                'model': 'gemini-1.5-flash',
                'temperature': 0.7,
                'created_at': '2023-06-15T10:30:00',
                'content_text': f"# {content_item['title']} (Version 2)\n\nThis is a mock version 2 for demonstration purposes.\n\n## Introduction\n\nThis content would normally be generated by the AI model.\n\n## Main Content\n\nThe content would include information about {content_item['title']}.\n\n## Conclusion\n\nThis is the end of the mock content.\n\n## Sources\n\n[SRC1] Mock Source 1. *Journal of AI*, 2023.\n\n[SRC2] Mock Source 2. *Business AI Review*, 2022.\n"
            },
            {
                'version_number': 1,
                'content_id': content_id,
                'model': 'gemini-1.5-pro',
                'temperature': 0.5,
                'created_at': '2023-06-10T14:20:00',
                'content_text': f"# {content_item['title']} (Version 1)\n\nThis is a mock version 1 for demonstration purposes.\n\n## Introduction\n\nThis content would normally be generated by the AI model.\n\n## Main Content\n\nThe content would include information about {content_item['title']}.\n\n## Conclusion\n\nThis is the end of the mock content.\n\n## Sources\n\n[SRC1] Mock Source 1. *Journal of AI*, 2023.\n"
            }
        ]
        version = next((v for v in mock_versions if v['version_number'] == version_number), None)

        if not version:
            flash(f'Version {version_number} not found for content {content_id}', 'error')
            return redirect(url_for('content_versions', content_id=content_id))
    else:
        # Get content item
        content_item = get_content_by_id(content_id)
        if not content_item:
            flash(f'Content item {content_id} not found', 'error')
            return redirect(url_for('content'))

        # Get versions
        versions = get_content_versions(content_id)
        version = next((v for v in versions if v['version_number'] == version_number), None)

        if not version:
            flash(f'Version {version_number} not found for content {content_id}', 'error')
            return redirect(url_for('content_versions', content_id=content_id))

    return render_template(
        'version_detail.html',
        content_item=content_item,
        version=version,
        versions=versions
    )

@app.route('/content/<content_id>/progress')
def generation_progress(content_id):
    """Get the progress of content generation."""
    global generation_progress_store
    progress = generation_progress_store.get(content_id, {})

    # If this is the first request and we're in the first step, start the generation process
    if (progress and progress.get('current_step') == 0 and
            progress['steps'][0]['status'] == 'in-progress' and
            not progress.get('generation_started')):

        # Mark that we've started generation to avoid duplicate starts
        progress['generation_started'] = True

        # Get generation parameters
        model = progress.get('model', 'gemini-1.5-flash')
        temperature = progress.get('temperature', 0.7)
        force = progress.get('force', False)

        # Start generation in a background thread
        import threading
        def generate_in_background():
            try:
                # Make sure the progress dictionary exists and has the expected structure
                if not progress or 'steps' not in progress or len(progress['steps']) < 2:
                    logger.error(f"Progress dictionary is missing or has invalid structure")
                    return

                # Update step 0 to complete and step 1 to in-progress
                progress['steps'][0]['status'] = 'complete'
                progress['steps'][1]['status'] = 'in-progress'
                progress['current_step'] = 1

                # Generate content with debug enabled
                include_references = progress.get('include_references', True)
                success, _ = generate_content_for_item(content_id, model_name=model, temperature=temperature, force=force, debug=True, include_references=include_references)

                # Make sure the progress dictionary still exists and has the expected structure after generation
                if not progress or 'steps' not in progress:
                    logger.error(f"Progress dictionary is missing or has invalid structure after generation")
                    return

                # Update progress based on result
                if success:
                    for step in progress['steps']:
                        step['status'] = 'complete'
                    progress['current_step'] = len(progress['steps'])
                else:
                    # Make sure current_step is valid
                    if 'current_step' in progress and 0 <= progress['current_step'] < len(progress['steps']):
                        # Mark current step as error
                        progress['steps'][progress['current_step']]['status'] = 'error'
                        progress['steps'][progress['current_step']]['error'] = 'Generation failed'

            except Exception as e:
                # Handle exceptions
                error_msg = str(e)
                logger.error(f"Error in background generation: {error_msg}")

                # Make sure the progress dictionary still exists and has the expected structure
                if progress and 'steps' in progress and 'current_step' in progress:
                    # Update progress with error
                    current_step = progress.get('current_step', 0)
                    if 0 <= current_step < len(progress['steps']):
                        progress['steps'][current_step]['status'] = 'error'
                        progress['steps'][current_step]['error'] = error_msg

        # Start the background thread
        thread = threading.Thread(target=generate_in_background)
        thread.daemon = True
        thread.start()

    return jsonify(progress)

@app.route('/content/<content_id>/start-generation', methods=['POST'])
def start_generation(content_id):
    """Start the content generation process."""
    # Get parameters from request
    data = request.get_json()
    model = data.get('model', 'gemini-1.5-flash')
    temperature = float(data.get('temperature', 0.7))
    force = data.get('force', False)
    include_references = data.get('include_references', True)

    # Get content item
    content_item = get_content_item(content_id)
    if not content_item:
        return jsonify({'success': False, 'error': 'Content item not found'})



    # Update content status
    update_content_status(content_id, 'Regenerating')

    # Set up global progress tracking
    global generation_progress_store
    generation_progress_store[content_id] = {
        'content_id': content_id,
        'steps': [
            {'name': 'Preparing', 'status': 'complete', 'description': 'Setting up generation parameters'},
            {'name': 'Generating Content', 'status': 'in-progress', 'description': 'Creating content with AI model'},
            {'name': 'Collecting Sources', 'status': 'pending', 'description': 'Finding and evaluating sources'},
            {'name': 'Formatting', 'status': 'pending', 'description': 'Formatting content with sources'},
            {'name': 'Saving', 'status': 'pending', 'description': 'Saving content to database'}
        ],
        'current_step': 1,
        'start_time': datetime.datetime.now().isoformat(),
        'model': model,
        'temperature': temperature,
        'force': force,
        'include_references': include_references,
        'generation_started': True
    }

    try:
        # Start generation in a background thread
        import threading
        def generate_in_background():
            try:
                # Make sure the content_id still exists in the progress store
                if content_id not in generation_progress_store:
                    logger.error(f"Content ID {content_id} not found in generation_progress_store")
                    return

                # Generate content with debug enabled
                include_references = generation_progress_store[content_id].get('include_references', True)
                success, _ = generate_content_for_item(content_id, model_name=model, temperature=temperature, force=force, debug=True, include_references=include_references)

                # Make sure the content_id still exists in the progress store after generation
                if content_id not in generation_progress_store:
                    logger.error(f"Content ID {content_id} not found in generation_progress_store after generation")
                    return

                # Update progress based on result
                if success:
                    # Make sure the steps key exists
                    if 'steps' in generation_progress_store[content_id]:
                        for step in generation_progress_store[content_id]['steps']:
                            step['status'] = 'complete'
                        generation_progress_store[content_id]['current_step'] = len(generation_progress_store[content_id]['steps'])
                else:
                    # Make sure the steps key exists and has at least 2 elements
                    if 'steps' in generation_progress_store[content_id] and len(generation_progress_store[content_id]['steps']) > 1:
                        # Mark current step as error
                        generation_progress_store[content_id]['steps'][1]['status'] = 'error'
                        generation_progress_store[content_id]['steps'][1]['error'] = 'Generation failed'
            except Exception as e:
                # Handle exceptions
                error_msg = str(e)
                logger.error(f"Error in background generation: {error_msg}")

                # Make sure the progress store still exists for this content_id
                if content_id in generation_progress_store:
                    # Make sure the steps key exists and has at least 2 elements
                    if 'steps' in generation_progress_store[content_id] and len(generation_progress_store[content_id]['steps']) > 1:
                        # Update progress with error
                        generation_progress_store[content_id]['steps'][1]['status'] = 'error'
                        generation_progress_store[content_id]['steps'][1]['error'] = error_msg

        # Start the background thread
        thread = threading.Thread(target=generate_in_background)
        thread.daemon = True
        thread.start()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/content/<content_id>/edit', methods=['GET', 'POST'])
def edit_content(content_id):
    """Edit content page."""
    # Check Supabase connection
    connected = is_connected()
    if not connected:
        flash('Not connected to Supabase. Cannot edit content.', 'error')
        return redirect(url_for('content_detail', content_id=content_id))

    # Get content item
    content_item = get_content_by_id(content_id)
    if not content_item:
        flash(f'Content item {content_id} not found', 'error')
        return redirect(url_for('content'))

    # Try to read the generated content file
    content_file_path = f'generated_content/{content_id}.md'
    content_text = ''
    if os.path.exists(content_file_path):
        with open(content_file_path, 'r') as f:
            content_text = f.read()

    if request.method == 'POST':
        # Get form data
        edited_content = request.form.get('content_text')
        edit_notes = request.form.get('edit_notes', '')

        # Save current version before updating
        current_model = content_item.get('model', 'manual-edit')
        current_temp = content_item.get('temperature', 0.0)

        try:
            # Save version to Supabase
            metadata = {
                'edit_notes': edit_notes,
                'edited_by': 'user',  # Could be replaced with actual user ID
                'edit_type': 'manual'
            }
            version_number = save_content_version(content_id, content_text, current_model, current_temp, metadata)

            if version_number:
                flash(f'Saved previous version {version_number} to Supabase', 'success')

            # Update the content file
            with open(content_file_path, 'w') as f:
                f.write(edited_content)

            # Log the edit as a generation output
            prompt_id = None  # No prompt for manual edits
            log_generation_output(
                prompt_id=prompt_id,
                output_text=edited_content,
                content_id=content_id,
                status='completed',
                metadata={
                    'edit_notes': edit_notes,
                    'edited_by': 'user',
                    'edit_type': 'manual',
                    'edit_date': datetime.datetime.now().isoformat()
                }
            )

            # Update content status
            update_content_status(content_id, 'Edited', {
                'last_edit': datetime.datetime.now().isoformat(),
                'edit_notes': edit_notes
            })

            flash('Content updated successfully', 'success')
            return redirect(url_for('content_detail', content_id=content_id))

        except Exception as e:
            flash(f'Error updating content: {str(e)}', 'error')
            # Continue to show the edit form with the current content

    return render_template(
        'edit_content.html',
        content_item=content_item,
        content_text=content_text
    )

@app.route('/content/<content_id>/workflow', methods=['GET', 'POST'])
def content_workflow(content_id):
    """Content workflow management page."""
    # Check Supabase connection
    connected = is_connected()
    if not connected:
        flash('Not connected to Supabase. Cannot manage workflow.', 'error')
        return redirect(url_for('content_detail', content_id=content_id))

    # Get content item
    content_item = get_content_by_id(content_id)
    if not content_item:
        flash(f'Content item {content_id} not found', 'error')
        return redirect(url_for('content'))

    # Define workflow statuses and their descriptions
    workflow_statuses = [
        {'value': 'Not Started', 'description': 'Content creation has not begun'},
        {'value': 'In Progress', 'description': 'Content is being generated or edited'},
        {'value': 'Regenerating', 'description': 'Content is being regenerated'},
        {'value': 'Edited', 'description': 'Content has been manually edited'},
        {'value': 'Review Requested', 'description': 'Content is ready for review'},
        {'value': 'In Review', 'description': 'Content is being reviewed'},
        {'value': 'Revision Needed', 'description': 'Content needs revisions based on review'},
        {'value': 'Approved', 'description': 'Content has been approved'},
        {'value': 'Published', 'description': 'Content has been published'},
        {'value': 'Archived', 'description': 'Content is no longer active'},
        {'value': 'Failed', 'description': 'Content generation failed'}
    ]

    if request.method == 'POST':
        # Get form data
        new_status = request.form.get('status')
        workflow_notes = request.form.get('workflow_notes', '')
        assigned_to = request.form.get('assigned_to', '')

        # Update content status
        try:
            metadata = {
                'workflow_notes': workflow_notes,
                'status_changed_by': 'user',  # Could be replaced with actual user ID
                'status_changed_at': datetime.datetime.now().isoformat()
            }

            # Update content item with workflow information
            update_data = {
                'status': new_status,
                'assigned_creator': assigned_to,
                'metadata': json.dumps(metadata)
            }

            success = update_content_item(content_id, update_data)

            if success:
                flash(f'Workflow status updated to {new_status}', 'success')
                return redirect(url_for('content_detail', content_id=content_id))
            else:
                flash('Failed to update workflow status', 'error')
        except Exception as e:
            flash(f'Error updating workflow status: {str(e)}', 'error')

    return render_template(
        'content_workflow.html',
        content_item=content_item,
        workflow_statuses=workflow_statuses
    )

@app.route('/search', methods=['GET'])
def search_content():
    """Search content inventory."""
    # Get search parameters
    query = request.args.get('q', '')
    status = request.args.get('status', '')
    section = request.args.get('section', '')

    # Get all content items
    content_items = get_content_inventory()

    # Filter by search query
    if query:
        query = query.lower()
        filtered_items = []
        for item in content_items:
            # Search in content_id, title, and other relevant fields
            content_id = item.get('content_id', '') or ''
            title = item.get('title', '') or ''
            section = item.get('section', '') or ''
            subsection = item.get('subsection', '') or ''
            audience_role = item.get('audience_role', '') or ''
            primary_mission_pillar = item.get('primary_mission_pillar_1', '') or ''

            if (query in content_id.lower() or
                query in title.lower() or
                query in section.lower() or
                query in subsection.lower() or
                query in audience_role.lower() or
                query in primary_mission_pillar.lower()):
                filtered_items.append(item)
        content_items = filtered_items

    # Filter by status
    if status:
        content_items = [item for item in content_items if item.get('status') == status]

    # Filter by section
    if section:
        content_items = [item for item in content_items if item.get('section') == section]

    # Get unique sections for filter dropdown
    sections = sorted(list(set(item.get('section') for item in get_content_inventory() if item.get('section'))))

    # Get unique statuses for filter dropdown
    statuses = sorted(list(set(item.get('status') for item in get_content_inventory() if item.get('status'))))

    return render_template(
        'search_results.html',
        content_items=content_items,
        query=query,
        sections=sections,
        statuses=statuses,
        selected_status=status,
        selected_section=section,
        result_count=len(content_items)
    )

@app.route('/content/<content_id>/attach-image', methods=['GET', 'POST'])
def attach_image(content_id):
    """Attach image to content."""
    # Check Supabase connection
    connected = is_connected()
    if not connected:
        flash('Not connected to Supabase. Cannot attach images.', 'error')
        return redirect(url_for('content_detail', content_id=content_id))

    # Get content item
    content_item = get_content_by_id(content_id)
    if not content_item:
        flash(f'Content item {content_id} not found', 'error')
        return redirect(url_for('content'))

    if request.method == 'POST':
        # Check if the post request has the file part
        if 'image' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['image']

        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        # Check if the file is an allowed image type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            flash('Invalid file type. Only PNG, JPG, JPEG, and GIF are allowed.', 'error')
            return redirect(request.url)

        try:
            # Create images directory if it doesn't exist
            os.makedirs(f'generated_content/images/{content_id}', exist_ok=True)

            # Save the file
            filename = file.filename
            file_path = f'generated_content/images/{content_id}/{filename}'
            file.save(file_path)

            # Get image description
            image_description = request.form.get('image_description', '')

            # Update content metadata to include the image
            metadata = content_item.get('metadata', '{}')
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}

            if not isinstance(metadata, dict):
                metadata = {}

            # Add image to metadata
            if 'images' not in metadata:
                metadata['images'] = []

            metadata['images'].append({
                'filename': filename,
                'path': file_path,
                'description': image_description,
                'uploaded_at': datetime.datetime.now().isoformat()
            })

            # Update content item
            update_data = {
                'metadata': json.dumps(metadata)
            }

            success = update_content_item(content_id, update_data)

            if success:
                flash(f'Image {filename} attached successfully', 'success')
                return redirect(url_for('content_detail', content_id=content_id))
            else:
                flash('Failed to update content metadata', 'error')
        except Exception as e:
            flash(f'Error attaching image: {str(e)}', 'error')

    # Get existing images
    metadata = content_item.get('metadata', '{}')
    if isinstance(metadata, str):
        try:
            metadata = json.loads(metadata)
        except:
            metadata = {}

    images = metadata.get('images', []) if isinstance(metadata, dict) else []

    return render_template(
        'attach_image.html',
        content_item=content_item,
        images=images
    )

# Initialize prompt management routes
init_prompt_management(app)

# Initialize reference management routes
init_reference_management(app)

@app.route('/content/<content_id>/references')
def content_references_page(content_id):
    """Page for managing references for a content item."""
    # Get content item
    content_item = get_content_by_id(content_id)
    if not content_item:
        flash(f'Content item {content_id} not found', 'error')
        return redirect(url_for('content'))

    # Get references for this content item
    from reference_management import get_content_references
    references = get_content_references(content_id)

    return render_template(
        'content_references.html',
        content_id=content_id,
        content_item=content_item,
        references=references
    )

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)

    import argparse
    parser = argparse.ArgumentParser(description="Run the web interface.")
    parser.add_argument("--port", type=int, default=8081, help="Port to run the server on")
    args = parser.parse_args()

    # Run the app
    app.run(debug=True, port=args.port)
