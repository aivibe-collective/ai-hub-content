#!/usr/bin/env python3
"""
Web interface for viewing Supabase tables.
"""

import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from dotenv import load_dotenv

# Import our custom modules
from supabase_client import (
    is_connected, get_content_inventory, get_prompt_logs,
    get_generation_outputs, get_full_content, get_content_by_id
)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default-secret-key')

@app.route('/')
def index():
    """Home page."""
    # Check Supabase connection
    if not is_connected():
        flash('Not connected to Supabase', 'error')
        return render_template('index.html', connected=False)

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

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)

    import argparse
    parser = argparse.ArgumentParser(description="Run the web interface.")
    parser.add_argument("--port", type=int, default=8081, help="Port to run the server on")
    args = parser.parse_args()

    # Run the app
    app.run(debug=True, port=args.port)
