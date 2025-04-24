#!/usr/bin/env python3
"""
Routes for the Reference Management System.

This module provides Flask routes for managing references,
quality assessments, and linking references to content items.
"""

import json
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

from reference_management import (
    Reference, ReferenceQuality, ContentReference,
    get_reference, get_references, create_reference, update_reference,
    create_quality_assessment, update_quality_assessment,
    link_reference_to_content, get_content_references,
    get_reference_categories, get_reference_types,
    search_references, get_reference_statistics
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
reference_bp = Blueprint('reference_management', __name__)

@reference_bp.route('/references')
def references():
    """References listing page."""
    # Get query parameters
    reference_type = request.args.get('type')
    category_id = request.args.get('category')
    active_param = request.args.get('active')
    is_active = None if active_param is None else (active_param.lower() == 'true')
    search_term = request.args.get('search')
    min_quality = request.args.get('min_quality')
    
    if min_quality:
        try:
            min_quality = int(min_quality)
        except ValueError:
            min_quality = None
    
    # Get references
    references_list = get_references(
        reference_type=reference_type,
        category_id=category_id,
        is_active=is_active,
        search_term=search_term,
        min_quality=min_quality
    )
    
    # Get categories and types
    categories = get_reference_categories()
    types = get_reference_types()
    
    # Get statistics
    statistics = get_reference_statistics()
    
    return render_template(
        'reference_management.html',
        references=references_list,
        categories=categories,
        types=types,
        statistics=statistics,
        selected_type=reference_type,
        selected_category=category_id,
        search_term=search_term,
        min_quality=min_quality,
        show_active_only=is_active if is_active is not None else True
    )

@reference_bp.route('/references/<reference_id>')
def reference_detail(reference_id):
    """Reference detail page."""
    # Get reference
    reference = get_reference(reference_id)
    if not reference:
        flash(f'Reference not found: {reference_id}', 'error')
        return redirect(url_for('reference_management.references'))
    
    # Get categories and types
    categories = get_reference_categories()
    types = get_reference_types()
    
    # Get linked content
    # This would require a new function to get content items linked to a reference
    linked_content = []  # Placeholder
    
    return render_template(
        'reference_detail.html',
        reference=reference,
        categories=categories,
        types=types,
        linked_content=linked_content
    )

@reference_bp.route('/references/new', methods=['GET', 'POST'])
def new_reference():
    """Create a new reference."""
    if request.method == 'POST':
        try:
            # Get form data
            title = request.form.get('title')
            authors = request.form.get('authors', '')
            publication_date_str = request.form.get('publication_date', '')
            url = request.form.get('url', '')
            doi = request.form.get('doi', '')
            publication_name = request.form.get('publication_name', '')
            reference_type = request.form.get('reference_type')
            content = request.form.get('content', '')
            abstract = request.form.get('abstract', '')
            keywords_str = request.form.get('keywords', '')
            is_active = 'is_active' in request.form
            
            # Parse publication date
            publication_date = None
            if publication_date_str:
                try:
                    publication_date = datetime.strptime(publication_date_str, '%Y-%m-%d').isoformat()
                except ValueError:
                    flash('Invalid publication date format. Use YYYY-MM-DD.', 'error')
                    categories = get_reference_categories()
                    types = get_reference_types()
                    return render_template('reference_form.html', reference=None, categories=categories, types=types)
            
            # Parse keywords
            keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
            
            # Parse categories
            categories = request.form.getlist('categories')
            
            # Create reference
            reference = Reference(
                title=title,
                authors=authors,
                publication_date=publication_date,
                url=url,
                doi=doi,
                publication_name=publication_name,
                reference_type=reference_type,
                content=content,
                abstract=abstract,
                keywords=keywords
            )
            reference.is_active = is_active
            reference.categories = categories
            
            # Create quality assessment if scores are provided
            currency_score = request.form.get('currency_score')
            relevance_score = request.form.get('relevance_score')
            authority_score = request.form.get('authority_score')
            accuracy_score = request.form.get('accuracy_score')
            purpose_score = request.form.get('purpose_score')
            assessment_notes = request.form.get('assessment_notes', '')
            
            if any(score for score in [currency_score, relevance_score, authority_score, accuracy_score, purpose_score]):
                assessment = ReferenceQuality(
                    currency_score=int(currency_score) if currency_score else None,
                    relevance_score=int(relevance_score) if relevance_score else None,
                    authority_score=int(authority_score) if authority_score else None,
                    accuracy_score=int(accuracy_score) if accuracy_score else None,
                    purpose_score=int(purpose_score) if purpose_score else None,
                    assessment_notes=assessment_notes
                )
                reference.quality_assessment = assessment
            
            reference_id = create_reference(reference)
            if not reference_id:
                flash('Failed to create reference', 'error')
                categories = get_reference_categories()
                types = get_reference_types()
                return render_template('reference_form.html', reference=reference, categories=categories, types=types)
            
            flash(f'Reference created: {title}', 'success')
            return redirect(url_for('reference_management.reference_detail', reference_id=reference_id))
            
        except Exception as e:
            logger.error(f"Error creating reference: {str(e)}")
            flash(f'Error creating reference: {str(e)}', 'error')
            categories = get_reference_categories()
            types = get_reference_types()
            return render_template('reference_form.html', reference=None, categories=categories, types=types)
    
    # GET request
    categories = get_reference_categories()
    types = get_reference_types()
    return render_template('reference_form.html', reference=None, categories=categories, types=types)

@reference_bp.route('/references/<reference_id>/edit', methods=['GET', 'POST'])
def edit_reference(reference_id):
    """Edit an existing reference."""
    # Get reference
    reference = get_reference(reference_id)
    if not reference:
        flash(f'Reference not found: {reference_id}', 'error')
        return redirect(url_for('reference_management.references'))
    
    if request.method == 'POST':
        try:
            # Get form data
            title = request.form.get('title')
            authors = request.form.get('authors', '')
            publication_date_str = request.form.get('publication_date', '')
            url = request.form.get('url', '')
            doi = request.form.get('doi', '')
            publication_name = request.form.get('publication_name', '')
            reference_type = request.form.get('reference_type')
            content = request.form.get('content', '')
            abstract = request.form.get('abstract', '')
            keywords_str = request.form.get('keywords', '')
            is_active = 'is_active' in request.form
            
            # Parse publication date
            publication_date = None
            if publication_date_str:
                try:
                    publication_date = datetime.strptime(publication_date_str, '%Y-%m-%d').isoformat()
                except ValueError:
                    flash('Invalid publication date format. Use YYYY-MM-DD.', 'error')
                    categories = get_reference_categories()
                    types = get_reference_types()
                    return render_template('reference_form.html', reference=reference, categories=categories, types=types)
            
            # Parse keywords
            keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
            
            # Parse categories
            categories = request.form.getlist('categories')
            
            # Update reference
            reference.title = title
            reference.authors = authors
            reference.publication_date = publication_date
            reference.url = url
            reference.doi = doi
            reference.publication_name = publication_name
            reference.reference_type = reference_type
            reference.content = content
            reference.abstract = abstract
            reference.keywords = keywords
            reference.is_active = is_active
            reference.categories = categories
            
            # Update quality assessment if scores are provided
            currency_score = request.form.get('currency_score')
            relevance_score = request.form.get('relevance_score')
            authority_score = request.form.get('authority_score')
            accuracy_score = request.form.get('accuracy_score')
            purpose_score = request.form.get('purpose_score')
            assessment_notes = request.form.get('assessment_notes', '')
            
            if any(score for score in [currency_score, relevance_score, authority_score, accuracy_score, purpose_score]):
                if not reference.quality_assessment:
                    reference.quality_assessment = ReferenceQuality(reference_id=reference_id)
                
                reference.quality_assessment.currency_score = int(currency_score) if currency_score else None
                reference.quality_assessment.relevance_score = int(relevance_score) if relevance_score else None
                reference.quality_assessment.authority_score = int(authority_score) if authority_score else None
                reference.quality_assessment.accuracy_score = int(accuracy_score) if accuracy_score else None
                reference.quality_assessment.purpose_score = int(purpose_score) if purpose_score else None
                reference.quality_assessment.assessment_notes = assessment_notes
            
            success = update_reference(reference)
            if not success:
                flash('Failed to update reference', 'error')
                categories = get_reference_categories()
                types = get_reference_types()
                return render_template('reference_form.html', reference=reference, categories=categories, types=types)
            
            flash(f'Reference updated: {title}', 'success')
            return redirect(url_for('reference_management.reference_detail', reference_id=reference_id))
            
        except Exception as e:
            logger.error(f"Error updating reference: {str(e)}")
            flash(f'Error updating reference: {str(e)}', 'error')
            categories = get_reference_categories()
            types = get_reference_types()
            return render_template('reference_form.html', reference=reference, categories=categories, types=types)
    
    # GET request
    categories = get_reference_categories()
    types = get_reference_types()
    return render_template('reference_form.html', reference=reference, categories=categories, types=types)

@reference_bp.route('/content/<content_id>/references')
def content_references(content_id):
    """References for a content item."""
    # Get references for the content item
    references_list = get_content_references(content_id)
    
    # Get all references for adding
    all_references = get_references(is_active=True)
    
    return render_template(
        'content_references.html',
        content_id=content_id,
        references=references_list,
        all_references=all_references
    )

@reference_bp.route('/api/content/<content_id>/references', methods=['POST'])
def add_content_reference(content_id):
    """Add a reference to a content item."""
    try:
        # Get data from request
        data = request.get_json()
        reference_id = data.get('reference_id')
        citation_key = data.get('citation_key', '')
        citation_context = data.get('citation_context', '')
        relevance_score = data.get('relevance_score')
        
        if relevance_score:
            try:
                relevance_score = int(relevance_score)
                if not 1 <= relevance_score <= 5:
                    return jsonify({'success': False, 'error': 'Relevance score must be between 1 and 5'})
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid relevance score'})
        
        # Link reference to content
        link_id = link_reference_to_content(
            content_id=content_id,
            reference_id=reference_id,
            citation_key=citation_key,
            citation_context=citation_context,
            relevance_score=relevance_score
        )
        
        if not link_id:
            return jsonify({'success': False, 'error': 'Failed to link reference to content'})
        
        return jsonify({'success': True, 'link_id': link_id})
        
    except Exception as e:
        logger.error(f"Error adding content reference: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@reference_bp.route('/api/references/search', methods=['GET'])
def api_search_references():
    """API endpoint for searching references."""
    try:
        # Get query parameters
        query = request.args.get('q', '')
        limit = request.args.get('limit', 10)
        
        try:
            limit = int(limit)
        except ValueError:
            limit = 10
        
        # Search references
        results = search_references(query, limit)
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error searching references: {str(e)}")
        return jsonify([])

@reference_bp.route('/api/references/<reference_id>/status', methods=['POST'])
def update_reference_status(reference_id):
    """Update the active status of a reference."""
    # Get reference
    reference = get_reference(reference_id)
    if not reference:
        return jsonify({'success': False, 'error': 'Reference not found'})
    
    try:
        # Get status from request
        data = request.get_json()
        is_active = data.get('is_active', True)
        
        # Update reference
        reference.is_active = is_active
        success = update_reference(reference)
        
        if not success:
            return jsonify({'success': False, 'error': 'Failed to update reference status'})
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error updating reference status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

def init_app(app):
    """Initialize the reference management routes with the Flask app."""
    app.register_blueprint(reference_bp)
