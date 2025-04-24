#!/usr/bin/env python3
"""
Routes for the Prompt Management System.

This module provides Flask routes for managing prompt templates,
variables, and tracking prompt usage and effectiveness.
"""

import json
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

from prompt_management import (
    get_prompt_templates, get_prompt_template, create_prompt_template,
    update_prompt_template, create_new_version, log_prompt_usage,
    add_prompt_feedback, get_prompt_categories, get_prompt_performance_metrics,
    PromptTemplate, initialize_default_templates
)
from google_ai_client import list_models, generate_content

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
prompt_bp = Blueprint('prompt_management', __name__)

@prompt_bp.route('/prompt-templates')
def prompt_templates():
    """Prompt templates listing page."""
    # Get query parameters
    category = request.args.get('category')
    active_param = request.args.get('active')
    is_active = None if active_param is None else (active_param.lower() == 'true')

    # Get templates
    template_list = get_prompt_templates(category, is_active)

    # Get categories
    categories = get_prompt_categories()

    # Get performance metrics
    metrics = get_prompt_performance_metrics(category=category)

    return render_template(
        'prompt_templates_list.html',
        items=template_list,
        categories=categories,
        metrics=metrics,
        selected_category=category,
        show_active_only=is_active if is_active is not None else True
    )

@prompt_bp.route('/prompt-templates/<template_id>')
def prompt_template_detail(template_id):
    """Prompt template detail page."""
    # Get template
    template = get_prompt_template(template_id)
    if not template:
        flash(f'Prompt template not found: {template_id}', 'error')
        return redirect(url_for('prompt_management.prompt_templates'))

    # Get usage history
    metrics = get_prompt_performance_metrics(template_id=template_id)
    usage_history = None
    if metrics:
        metric = metrics[0]
        usage_history = {
            'total_count': metric.get('usage_count', 0),
            'success_rate': metric.get('success_count', 0) / metric.get('usage_count', 1) if metric.get('usage_count', 0) > 0 else 0,
            'avg_rating': metric.get('avg_rating', 0),
            'last_used': metric.get('last_used', 'Never')
        }

    # Get recent usage
    # This would require a new function to get recent usage for a template
    recent_usage = []  # Placeholder

    return render_template(
        'prompt_template_detail.html',
        template=template,
        usage_history=usage_history,
        recent_usage=recent_usage
    )

@prompt_bp.route('/prompt-templates/new', methods=['GET', 'POST'])
def new_prompt_template():
    """Create a new prompt template."""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            description = request.form.get('description', '')
            category = request.form.get('category')
            template_text = request.form.get('template_text')
            tags_json = request.form.get('tags', '{}')
            is_active = 'is_active' in request.form

            # Parse tags
            try:
                tags = json.loads(tags_json) if tags_json.strip() else {}
            except json.JSONDecodeError:
                flash('Invalid JSON in tags field', 'error')
                categories = get_prompt_categories()
                return render_template(
                    'prompt_template_form.html',
                    template=PromptTemplate(
                        name=name,
                        description=description,
                        category=category,
                        template_text=template_text,
                        is_active=is_active
                    ),
                    categories=categories
                )

            # Create template
            template = PromptTemplate(
                name=name,
                description=description,
                category=category,
                template_text=template_text,
                tags=tags,
                is_active=is_active
            )

            template_id = create_prompt_template(template)
            if not template_id:
                flash('Failed to create prompt template', 'error')
                categories = get_prompt_categories()
                return render_template('prompt_template_form.html', template=template, categories=categories)

            flash(f'Prompt template created: {name}', 'success')
            return redirect(url_for('prompt_management.prompt_template_detail', template_id=template_id))

        except Exception as e:
            logger.error(f"Error creating prompt template: {str(e)}")
            flash(f'Error creating prompt template: {str(e)}', 'error')
            categories = get_prompt_categories()
            return render_template('prompt_template_form.html', template=PromptTemplate(), categories=categories)

    # GET request
    categories = get_prompt_categories()
    return render_template('prompt_template_form.html', template=PromptTemplate(), categories=categories)

@prompt_bp.route('/prompt-templates/<template_id>/edit', methods=['GET', 'POST'])
def edit_prompt_template(template_id):
    """Edit an existing prompt template."""
    # Get template
    template = get_prompt_template(template_id)
    if not template:
        flash(f'Prompt template not found: {template_id}', 'error')
        return redirect(url_for('prompt_management.prompt_templates'))

    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            description = request.form.get('description', '')
            category = request.form.get('category')
            template_text = request.form.get('template_text')
            tags_json = request.form.get('tags', '{}')
            is_active = 'is_active' in request.form

            # Parse tags
            try:
                tags = json.loads(tags_json) if tags_json.strip() else {}
            except json.JSONDecodeError:
                flash('Invalid JSON in tags field', 'error')
                categories = get_prompt_categories()
                return render_template('prompt_template_form.html', template=template, categories=categories)

            # Update template
            template.name = name
            template.description = description
            template.category = category
            template.template_text = template_text
            template.tags = tags
            template.is_active = is_active

            success = update_prompt_template(template)
            if not success:
                flash('Failed to update prompt template', 'error')
                categories = get_prompt_categories()
                return render_template('prompt_template_form.html', template=template, categories=categories)

            flash(f'Prompt template updated: {name}', 'success')
            return redirect(url_for('prompt_management.prompt_template_detail', template_id=template_id))

        except Exception as e:
            logger.error(f"Error updating prompt template: {str(e)}")
            flash(f'Error updating prompt template: {str(e)}', 'error')
            categories = get_prompt_categories()
            return render_template('prompt_template_form.html', template=template, categories=categories)

    # GET request
    categories = get_prompt_categories()
    return render_template('prompt_template_form.html', template=template, categories=categories)

@prompt_bp.route('/prompt-templates/<template_id>/new-version', methods=['GET', 'POST'])
def new_version(template_id):
    """Create a new version of a prompt template."""
    # Get template
    template = get_prompt_template(template_id)
    if not template:
        flash(f'Prompt template not found: {template_id}', 'error')
        return redirect(url_for('prompt_management.prompt_templates'))

    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            description = request.form.get('description', '')
            template_text = request.form.get('template_text')

            # Create new version
            new_id = create_new_version(template_id, template_text, name, description)
            if not new_id:
                flash('Failed to create new version', 'error')
                categories = get_prompt_categories()
                return render_template('prompt_template_form.html', template=template, categories=categories, is_new_version=True)

            flash(f'New version created: {name}', 'success')
            return redirect(url_for('prompt_management.prompt_template_detail', template_id=new_id))

        except Exception as e:
            logger.error(f"Error creating new version: {str(e)}")
            flash(f'Error creating new version: {str(e)}', 'error')
            categories = get_prompt_categories()
            return render_template('prompt_template_form.html', template=template, categories=categories, is_new_version=True)

    # GET request - Pre-fill form with current template data but suggest a new name
    new_template = PromptTemplate.from_dict(template.to_dict())
    new_template.name = f"{template.name} (v{template.version + 1})"

    categories = get_prompt_categories()
    return render_template('prompt_template_form.html', template=new_template, categories=categories, is_new_version=True)

@prompt_bp.route('/prompt-templates/<template_id>/test')
def test_prompt_template(template_id):
    """Test a prompt template."""
    # Get template
    template = get_prompt_template(template_id)
    if not template:
        flash(f'Prompt template not found: {template_id}', 'error')
        return redirect(url_for('prompt_management.prompt_templates'))

    # Get available models
    models = list_models()

    return render_template('prompt_template_test.html', template=template, models=models)

@prompt_bp.route('/api/prompt-templates/<template_id>/status', methods=['POST'])
def update_template_status(template_id):
    """Update the active status of a prompt template."""
    # Get template
    template = get_prompt_template(template_id)
    if not template:
        return jsonify({'success': False, 'error': 'Template not found'})

    try:
        # Get status from request
        data = request.get_json()
        is_active = data.get('is_active', True)

        # Update template
        template.is_active = is_active
        success = update_prompt_template(template)

        if not success:
            return jsonify({'success': False, 'error': 'Failed to update template status'})

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Error updating template status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@prompt_bp.route('/api/prompt-templates/<template_id>/render', methods=['POST'])
def render_template(template_id):
    """Render a prompt template with variables."""
    # Get template
    template = get_prompt_template(template_id)
    if not template:
        return jsonify({'success': False, 'error': 'Template not found'})

    try:
        # Get variables from request
        data = request.get_json()
        variables = data.get('variables', {})

        # Render template
        rendered_prompt = template.render(variables)

        return jsonify({
            'success': True,
            'rendered_prompt': rendered_prompt
        })

    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@prompt_bp.route('/api/prompt-templates/<template_id>/generate', methods=['POST'])
def generate_from_template(template_id):
    """Generate content using a prompt template."""
    # Get template
    template = get_prompt_template(template_id)
    if not template:
        return jsonify({'success': False, 'error': 'Template not found'})

    try:
        # Get data from request
        data = request.get_json()
        variables = data.get('variables', {})
        model = data.get('model', 'gemini-1.5-flash')
        temperature = data.get('temperature', 0.7)

        # Render template
        rendered_prompt = template.render(variables)

        # Generate content
        content = generate_content(rendered_prompt, model, temperature)

        # Log usage
        usage_id = log_prompt_usage(
            template_id=template_id,
            variables=variables,
            rendered_prompt=rendered_prompt,
            model=model,
            temperature=temperature,
            success=True
        )

        return jsonify({
            'success': True,
            'content': content,
            'usage_id': usage_id
        })

    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@prompt_bp.route('/api/prompt-usage/<usage_id>/feedback', methods=['POST'])
def add_usage_feedback(usage_id):
    """Add feedback for a prompt usage."""
    try:
        # Get data from request
        data = request.get_json()
        rating = data.get('rating')
        feedback_text = data.get('feedback_text', '')
        feedback_type = data.get('feedback_type', 'user')

        # Validate rating
        if not rating or not isinstance(rating, int) or not (1 <= rating <= 5):
            return jsonify({'success': False, 'error': 'Invalid rating'})

        # Add feedback
        success = add_prompt_feedback(usage_id, rating, feedback_text, feedback_type)

        if not success:
            return jsonify({'success': False, 'error': 'Failed to add feedback'})

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Error adding feedback: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

def init_app(app):
    """Initialize the prompt management routes with the Flask app."""
    app.register_blueprint(prompt_bp)

    # Initialize default templates
    initialize_default_templates()
