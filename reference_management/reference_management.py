#!/usr/bin/env python3
"""
Reference Management System for AI Hub Content Creation.

This module provides functions for managing references, quality assessments,
and linking references to content items.
"""

import os
import json
import logging
import datetime
import uuid
from typing import Dict, List, Optional, Any, Union

from dotenv import load_dotenv
from core.supabase_client import supabase, is_connected

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class Reference:
    """Class representing a reference source."""

    def __init__(self, reference_id=None, title=None, authors=None, publication_date=None,
                 url=None, doi=None, publication_name=None, reference_type=None,
                 content=None, abstract=None, keywords=None, is_active=True, created_by=None,
                 metadata=None, categories=None, quality_assessment=None):
        """Initialize a reference."""
        self.reference_id = reference_id or str(uuid.uuid4())
        self.title = title or ""
        self.authors = authors or ""
        self.publication_date = publication_date
        self.url = url or ""
        self.doi = doi or ""
        self.publication_name = publication_name or ""
        self.reference_type = reference_type or "Website"
        self.content = content or ""
        self.abstract = abstract or ""
        self.keywords = keywords or []
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = self.created_at
        self.created_by = created_by or "system"
        self.is_active = is_active
        self.metadata = metadata or {}
        self.categories = categories or []
        self.quality_assessment = quality_assessment

    def to_dict(self) -> Dict[str, Any]:
        """Convert the reference to a dictionary."""
        return {
            "id": self.reference_id,
            "title": self.title,
            "authors": self.authors,
            "publication_date": self.publication_date,
            "url": self.url,
            "doi": self.doi,
            "publication_name": self.publication_name,
            "reference_type": self.reference_type,
            "content": self.content,
            "abstract": self.abstract,
            "keywords": self.keywords,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "is_active": self.is_active,
            "metadata": json.dumps(self.metadata) if isinstance(self.metadata, dict) else self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reference':
        """Create a reference from a dictionary."""
        reference = cls()
        reference.reference_id = data.get("id") or data.get("reference_id")
        reference.title = data.get("title", "")
        reference.authors = data.get("authors", "")
        reference.publication_date = data.get("publication_date")
        reference.url = data.get("url", "")
        reference.doi = data.get("doi", "")
        reference.publication_name = data.get("publication_name", "")
        reference.reference_type = data.get("reference_type", "Website")
        reference.content = data.get("content", "")
        reference.abstract = data.get("abstract", "")
        reference.keywords = data.get("keywords", [])
        reference.created_at = data.get("created_at", reference.created_at)
        reference.updated_at = data.get("updated_at", reference.updated_at)
        reference.created_by = data.get("created_by", "system")
        reference.is_active = data.get("is_active", True)

        # Handle metadata
        metadata = data.get("metadata", {})
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        reference.metadata = metadata

        return reference


class ReferenceQuality:
    """Class representing a quality assessment for a reference."""

    def __init__(self, assessment_id=None, reference_id=None, currency_score=None,
                 relevance_score=None, authority_score=None, accuracy_score=None,
                 purpose_score=None, overall_score=None, assessment_notes=None):
        """Initialize a quality assessment."""
        self.assessment_id = assessment_id or str(uuid.uuid4())
        self.reference_id = reference_id
        self.currency_score = currency_score
        self.relevance_score = relevance_score
        self.authority_score = authority_score
        self.accuracy_score = accuracy_score
        self.purpose_score = purpose_score
        self.overall_score = overall_score
        self.assessment_notes = assessment_notes or ""
        self.assessed_by = "system"
        self.assessed_at = datetime.datetime.now().isoformat()
        self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert the quality assessment to a dictionary."""
        return {
            "id": self.assessment_id,
            "reference_id": self.reference_id,
            "currency_score": self.currency_score,
            "relevance_score": self.relevance_score,
            "authority_score": self.authority_score,
            "accuracy_score": self.accuracy_score,
            "purpose_score": self.purpose_score,
            "overall_score": self.overall_score,
            "assessment_notes": self.assessment_notes,
            "assessed_by": self.assessed_by,
            "assessed_at": self.assessed_at,
            "metadata": json.dumps(self.metadata) if isinstance(self.metadata, dict) else self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReferenceQuality':
        """Create a quality assessment from a dictionary."""
        assessment = cls()
        assessment.assessment_id = data.get("id") or data.get("assessment_id")
        assessment.reference_id = data.get("reference_id")
        assessment.currency_score = data.get("currency_score")
        assessment.relevance_score = data.get("relevance_score")
        assessment.authority_score = data.get("authority_score")
        assessment.accuracy_score = data.get("accuracy_score")
        assessment.purpose_score = data.get("purpose_score")
        assessment.overall_score = data.get("overall_score")
        assessment.assessment_notes = data.get("assessment_notes", "")
        assessment.assessed_by = data.get("assessed_by", "system")
        assessment.assessed_at = data.get("assessed_at", assessment.assessed_at)

        # Handle metadata
        metadata = data.get("metadata", {})
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        assessment.metadata = metadata

        return assessment


class ContentReference:
    """Class representing a link between a content item and a reference."""

    def __init__(self, link_id=None, content_id=None, reference_id=None, citation_key=None,
                 citation_context=None, relevance_score=None):
        """Initialize a content reference link."""
        self.link_id = link_id or str(uuid.uuid4())
        self.content_id = content_id
        self.reference_id = reference_id
        self.citation_key = citation_key or ""
        self.citation_context = citation_context or ""
        self.relevance_score = relevance_score
        self.created_at = datetime.datetime.now().isoformat()
        self.created_by = "system"
        self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert the content reference link to a dictionary."""
        return {
            "id": self.link_id,
            "content_id": self.content_id,
            "reference_id": self.reference_id,
            "citation_key": self.citation_key,
            "citation_context": self.citation_context,
            "relevance_score": self.relevance_score,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "metadata": json.dumps(self.metadata) if isinstance(self.metadata, dict) else self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentReference':
        """Create a content reference link from a dictionary."""
        link = cls()
        link.link_id = data.get("id") or data.get("link_id")
        link.content_id = data.get("content_id")
        link.reference_id = data.get("reference_id")
        link.citation_key = data.get("citation_key", "")
        link.citation_context = data.get("citation_context", "")
        link.relevance_score = data.get("relevance_score")
        link.created_at = data.get("created_at", link.created_at)
        link.created_by = data.get("created_by", "system")

        # Handle metadata
        metadata = data.get("metadata", {})
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        link.metadata = metadata

        return link


def create_reference(reference: Reference) -> Optional[str]:
    """Create a new reference in the database.

    Args:
        reference: The reference to create

    Returns:
        The reference ID if successful, None otherwise
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return None

    try:
        # Insert the reference
        reference_data = reference.to_dict()
        result = supabase.table('reference_sources').insert(reference_data).execute()

        if not result.data:
            logger.error("Failed to create reference")
            return None

        reference_id = result.data[0]['id']

        # Add categories if provided
        if reference.categories:
            for category_id in reference.categories:
                category_data = {
                    "reference_id": reference_id,
                    "category_id": category_id
                }
                supabase.table('reference_to_category').insert(category_data).execute()

        # Add quality assessment if provided
        if reference.quality_assessment:
            assessment = reference.quality_assessment
            assessment.reference_id = reference_id
            create_quality_assessment(assessment)

        logger.info(f"Created reference: {reference.title} (ID: {reference_id})")
        return reference_id

    except Exception as e:
        logger.error(f"Error creating reference: {str(e)}")
        return None


def get_reference(reference_id: str) -> Optional[Reference]:
    """Get a reference by ID.

    Args:
        reference_id: The ID of the reference to retrieve

    Returns:
        The reference if found, None otherwise
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return None

    try:
        # Get the reference
        result = supabase.table('reference_sources').select('*').eq('id', reference_id).execute()

        if not result.data:
            logger.warning(f"Reference not found: {reference_id}")
            return None

        reference_data = result.data[0]
        reference = Reference.from_dict(reference_data)

        # Get categories
        cat_result = supabase.table('reference_to_category').select('category_id').eq('reference_id', reference_id).execute()
        if cat_result.data:
            reference.categories = [item['category_id'] for item in cat_result.data]

        # Get quality assessment
        quality_result = supabase.table('reference_quality').select('*').eq('reference_id', reference_id).execute()
        if quality_result.data:
            reference.quality_assessment = ReferenceQuality.from_dict(quality_result.data[0])

        return reference

    except Exception as e:
        logger.error(f"Error getting reference: {str(e)}")
        return None


def get_references(reference_type: Optional[str] = None, category_id: Optional[str] = None,
                  is_active: bool = True, search_term: Optional[str] = None,
                  min_quality: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get references, optionally filtered by type, category, active status, and quality.

    Args:
        reference_type: Optional reference type to filter by
        category_id: Optional category ID to filter by
        is_active: Whether to return only active references
        search_term: Optional search term to filter by title or authors
        min_quality: Optional minimum overall quality score

    Returns:
        List of references
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return []

    try:
        # Start with a basic query on reference_sources
        query = supabase.table('reference_sources').select('*')

        # Apply filters
        if reference_type:
            query = query.eq('reference_type', reference_type)

        if is_active is not None:
            query = query.eq('is_active', is_active)

        if search_term:
            query = query.or_(f"title.ilike.%{search_term}%,authors.ilike.%{search_term}%")

        # Execute the query
        result = query.execute()
        references = result.data if result.data else []

        if not references:
            return []

        # Get all reference IDs
        reference_ids = [ref['id'] for ref in references]

        # Get all quality scores in one query
        quality_result = supabase.table('reference_quality').select('reference_id, overall_score').in_('reference_id', reference_ids).execute()
        quality_scores = {item['reference_id']: item['overall_score'] for item in quality_result.data} if quality_result.data else {}

        # Get all category mappings in one query
        cat_result = supabase.table('reference_to_category').select('reference_id, category_id').in_('reference_id', reference_ids).execute()
        category_mappings = {}
        for item in cat_result.data if cat_result.data else []:
            if item['reference_id'] not in category_mappings:
                category_mappings[item['reference_id']] = []
            category_mappings[item['reference_id']].append(item['category_id'])

        # Get all category names in one query
        all_category_ids = []
        for cat_ids in category_mappings.values():
            all_category_ids.extend(cat_ids)
        all_category_ids = list(set(all_category_ids))  # Remove duplicates

        category_names = {}
        if all_category_ids:
            cat_names_result = supabase.table('reference_categories').select('id, name').in_('id', all_category_ids).execute()
            category_names = {item['id']: item['name'] for item in cat_names_result.data} if cat_names_result.data else {}

        # Process each reference to add categories and quality score
        for ref in references:
            ref_id = ref['id']
            # Add quality score
            ref['quality_score'] = quality_scores.get(ref_id, 0)

            # Add categories
            ref_category_ids = category_mappings.get(ref_id, [])
            ref['categories'] = [category_names.get(cat_id, '') for cat_id in ref_category_ids if cat_id in category_names]

        # Filter by category if needed
        if category_id:
            references = [ref for ref in references if category_id in category_mappings.get(ref['id'], [])]

        # Filter by quality score if needed
        if min_quality is not None and min_quality > 0:
            try:
                min_quality_int = int(min_quality)
                references = [ref for ref in references if ref.get('quality_score', 0) >= min_quality_int]
            except ValueError:
                # If min_quality is not a valid integer, ignore this filter
                pass

        # Sort by title
        references.sort(key=lambda x: x.get('title', ''))

        return references

    except Exception as e:
        logger.error(f"Error getting references: {str(e)}")
        return []


def update_reference(reference: Reference) -> bool:
    """Update an existing reference.

    Args:
        reference: The reference to update

    Returns:
        True if successful, False otherwise
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return False

    if not reference.reference_id:
        logger.error("Reference ID is required for update")
        return False

    try:
        # Check if the reference exists
        existing = get_reference(reference.reference_id)
        if not existing:
            logger.error(f"Reference not found: {reference.reference_id}")
            return False

        # Update the reference
        reference.updated_at = datetime.datetime.now().isoformat()
        reference_data = reference.to_dict()

        result = supabase.table('reference_sources').update(reference_data).eq('id', reference.reference_id).execute()

        if not result.data:
            logger.error("Failed to update reference")
            return False

        # Update categories
        # First, delete existing categories
        supabase.table('reference_to_category').delete().eq('reference_id', reference.reference_id).execute()

        # Then, add new categories
        if reference.categories:
            for category_id in reference.categories:
                category_data = {
                    "reference_id": reference.reference_id,
                    "category_id": category_id
                }
                supabase.table('reference_to_category').insert(category_data).execute()

        # Update quality assessment if provided
        if reference.quality_assessment:
            assessment = reference.quality_assessment
            assessment.reference_id = reference.reference_id

            # Check if assessment exists
            quality_result = supabase.table('reference_quality').select('id').eq('reference_id', reference.reference_id).execute()

            if quality_result.data:
                # Update existing assessment
                assessment.assessment_id = quality_result.data[0]['id']
                update_quality_assessment(assessment)
            else:
                # Create new assessment
                create_quality_assessment(assessment)

        logger.info(f"Updated reference: {reference.title} (ID: {reference.reference_id})")
        return True

    except Exception as e:
        logger.error(f"Error updating reference: {str(e)}")
        return False


def create_quality_assessment(assessment: ReferenceQuality) -> Optional[str]:
    """Create a new quality assessment for a reference.

    Args:
        assessment: The quality assessment to create

    Returns:
        The assessment ID if successful, None otherwise
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return None

    if not assessment.reference_id:
        logger.error("Reference ID is required for quality assessment")
        return None

    try:
        # Calculate overall score if not provided
        if assessment.overall_score is None and all(score is not None for score in [
            assessment.currency_score, assessment.relevance_score,
            assessment.authority_score, assessment.accuracy_score,
            assessment.purpose_score
        ]):
            scores = [
                assessment.currency_score, assessment.relevance_score,
                assessment.authority_score, assessment.accuracy_score,
                assessment.purpose_score
            ]
            assessment.overall_score = round(sum(scores) / len(scores))

        # Insert the assessment
        assessment_data = assessment.to_dict()
        result = supabase.table('reference_quality').insert(assessment_data).execute()

        if not result.data:
            logger.error("Failed to create quality assessment")
            return None

        assessment_id = result.data[0]['id']
        logger.info(f"Created quality assessment for reference: {assessment.reference_id}")
        return assessment_id

    except Exception as e:
        logger.error(f"Error creating quality assessment: {str(e)}")
        return None


def update_quality_assessment(assessment: ReferenceQuality) -> bool:
    """Update an existing quality assessment.

    Args:
        assessment: The quality assessment to update

    Returns:
        True if successful, False otherwise
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return False

    if not assessment.assessment_id:
        logger.error("Assessment ID is required for update")
        return False

    try:
        # Calculate overall score if not provided
        if assessment.overall_score is None and all(score is not None for score in [
            assessment.currency_score, assessment.relevance_score,
            assessment.authority_score, assessment.accuracy_score,
            assessment.purpose_score
        ]):
            scores = [
                assessment.currency_score, assessment.relevance_score,
                assessment.authority_score, assessment.accuracy_score,
                assessment.purpose_score
            ]
            assessment.overall_score = round(sum(scores) / len(scores))

        # Update the assessment
        assessment.assessed_at = datetime.datetime.now().isoformat()
        assessment_data = assessment.to_dict()

        result = supabase.table('reference_quality').update(assessment_data).eq('id', assessment.assessment_id).execute()

        if not result.data:
            logger.error("Failed to update quality assessment")
            return False

        logger.info(f"Updated quality assessment: {assessment.assessment_id}")
        return True

    except Exception as e:
        logger.error(f"Error updating quality assessment: {str(e)}")
        return False


def link_reference_to_content(content_id: str, reference_id: str, citation_key: Optional[str] = None,
                             citation_context: Optional[str] = None, relevance_score: Optional[int] = None) -> Optional[str]:
    """Link a reference to a content item.

    Args:
        content_id: The ID of the content item
        reference_id: The ID of the reference
        citation_key: Optional citation key
        citation_context: Optional citation context
        relevance_score: Optional relevance score (1-5)

    Returns:
        The link ID if successful, None otherwise
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return None

    try:
        # Check if the link already exists
        existing = supabase.table('content_references').select('id').eq('content_id', content_id).eq('reference_id', reference_id).execute()

        if existing.data:
            logger.info(f"Reference {reference_id} is already linked to content {content_id}")
            return existing.data[0]['id']

        # Create the link
        link = ContentReference(
            content_id=content_id,
            reference_id=reference_id,
            citation_key=citation_key,
            citation_context=citation_context,
            relevance_score=relevance_score
        )

        # Create a simplified data structure that matches the database table
        link_data = {
            'id': link.link_id,
            'content_id': link.content_id,
            'reference_id': link.reference_id,
            'citation_key': link.citation_key,
            'citation_context': link.citation_context,
            'relevance_score': link.relevance_score,
            'created_at': link.created_at,
            'updated_at': link.created_at
        }
        result = supabase.table('content_references').insert(link_data).execute()

        if not result.data:
            logger.error("Failed to link reference to content")
            return None

        link_id = result.data[0]['id']
        logger.info(f"Linked reference {reference_id} to content {content_id}")
        return link_id

    except Exception as e:
        logger.error(f"Error linking reference to content: {str(e)}")
        return None


def get_content_references(content_id: str) -> List[Dict[str, Any]]:
    """Get references linked to a content item.

    Args:
        content_id: The ID of the content item

    Returns:
        List of references linked to the content item
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return []

    try:
        # Get content references for this content ID
        content_refs_result = supabase.table('content_references').select('*').eq('content_id', content_id).execute()
        content_refs = content_refs_result.data if content_refs_result.data else []

        if not content_refs:
            return []

        # Get reference IDs
        reference_ids = [ref['reference_id'] for ref in content_refs]

        # Get reference details
        refs_result = supabase.table('reference_sources').select('*').in_('id', reference_ids).execute()
        references = refs_result.data if refs_result.data else []

        if not references:
            return []

        # Get quality scores
        quality_result = supabase.table('reference_quality').select('reference_id,overall_score').in_('reference_id', reference_ids).execute()
        quality_scores = {item['reference_id']: item['overall_score'] for item in quality_result.data} if quality_result.data else {}

        # Get category mappings
        cat_result = supabase.table('reference_to_category').select('reference_id,category_id').in_('reference_id', reference_ids).execute()
        category_mappings = {}
        for item in cat_result.data if cat_result.data else []:
            if item['reference_id'] not in category_mappings:
                category_mappings[item['reference_id']] = []
            category_mappings[item['reference_id']].append(item['category_id'])

        # Get category names
        all_category_ids = []
        for cat_ids in category_mappings.values():
            all_category_ids.extend(cat_ids)
        all_category_ids = list(set(all_category_ids))  # Remove duplicates

        category_names = {}
        if all_category_ids:
            cat_names_result = supabase.table('reference_categories').select('id,name').in_('id', all_category_ids).execute()
            category_names = {item['id']: item['name'] for item in cat_names_result.data} if cat_names_result.data else {}

        # Create a citation key mapping
        citation_mapping = {ref['reference_id']: ref for ref in content_refs}

        # Combine all the data
        result = []
        for ref in references:
            ref_id = ref['id']
            citation_data = citation_mapping.get(ref_id, {})

            # Add citation information
            ref['citation_key'] = citation_data.get('citation_key', '')
            ref['citation_context'] = citation_data.get('citation_context', '')
            ref['relevance_score'] = citation_data.get('relevance_score')

            # Add quality score
            ref['quality_score'] = quality_scores.get(ref_id, 0)

            # Add categories
            ref_category_ids = category_mappings.get(ref_id, [])
            ref['categories'] = [category_names.get(cat_id, '') for cat_id in ref_category_ids if cat_id in category_names]

            result.append(ref)

        # Sort by relevance score (descending) and then by title
        result.sort(key=lambda x: (-1 * (x.get('relevance_score') or 0), x.get('title', '')))

        return result

    except Exception as e:
        logger.error(f"Error getting content references: {str(e)}")
        return []


def get_reference_categories() -> List[Dict[str, Any]]:
    """Get all reference categories.

    Returns:
        List of reference categories
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return []

    try:
        result = supabase.table('reference_categories').select('*').order('name').execute()
        return result.data if result.data else []

    except Exception as e:
        logger.error(f"Error getting reference categories: {str(e)}")
        return []


def get_reference_types() -> List[Dict[str, Any]]:
    """Get all reference types.

    Returns:
        List of reference types
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return []

    try:
        result = supabase.table('reference_types').select('*').order('name').execute()
        return result.data if result.data else []

    except Exception as e:
        logger.error(f"Error getting reference types: {str(e)}")
        return []


def search_references(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search for references by title, authors, or content.

    Args:
        query: The search query
        limit: Maximum number of results to return

    Returns:
        List of matching references
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return []

    try:
        # Create a filter for the search query
        like_query = f"%{query}%"

        # Get references matching the search query
        result = supabase.table('reference_sources')\
            .select('*')\
            .eq('is_active', True)\
            .or_(f"title.ilike.{like_query},authors.ilike.{like_query},abstract.ilike.{like_query},content.ilike.{like_query}")\
            .limit(limit)\
            .order('title')\
            .execute()

        references = result.data if result.data else []

        if not references:
            return []

        # Get reference IDs
        reference_ids = [ref['id'] for ref in references]

        # Get quality scores
        quality_result = supabase.table('reference_quality').select('reference_id,overall_score').in_('reference_id', reference_ids).execute()
        quality_scores = {item['reference_id']: item['overall_score'] for item in quality_result.data} if quality_result.data else {}

        # Add quality scores to references
        for ref in references:
            ref['quality_score'] = quality_scores.get(ref['id'], 0)

        # Sort by relevance (simple implementation - in a real system, we would use a more sophisticated ranking algorithm)
        # For now, we'll sort by how closely the title matches the query, then by quality score
        def rank_reference(ref):
            title = ref.get('title', '').lower()
            query_lower = query.lower()

            # Exact match gets highest score
            if title == query_lower:
                title_score = 100
            # Title starts with query gets high score
            elif title.startswith(query_lower):
                title_score = 75
            # Title contains query gets medium score
            elif query_lower in title:
                title_score = 50
            # Otherwise, low score
            else:
                title_score = 25

            # Quality score is a secondary factor
            quality_score = ref.get('quality_score', 0)

            return (title_score, quality_score)

        references.sort(key=rank_reference, reverse=True)

        return references

    except Exception as e:
        logger.error(f"Error searching references: {str(e)}")
        return []


def get_reference_statistics() -> Dict[str, Any]:
    """Get statistics about references.

    Returns:
        Dictionary with reference statistics
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return {}

    try:
        # Get all active references in one query
        refs_result = supabase.table('reference_sources').select('id, reference_type').eq('is_active', True).execute()
        references = refs_result.data if refs_result.data else []
        total_references = len(references)

        if total_references == 0:
            return {
                'total_references': 0,
                'unique_types': 0,
                'avg_quality': 0,
                'linked_content_count': 0,
                'type_breakdown': [],
                'category_breakdown': []
            }

        # Get unique types
        reference_types = [ref.get('reference_type') for ref in references if ref.get('reference_type')]
        unique_types = len(set(reference_types))

        # Get all reference IDs
        reference_ids = [ref['id'] for ref in references]

        # Get all quality scores in one query
        quality_result = supabase.table('reference_quality').select('reference_id, overall_score').in_('reference_id', reference_ids).execute()
        quality_scores = [item['overall_score'] for item in quality_result.data if item.get('overall_score') is not None] if quality_result.data else []
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0

        # Get linked content count
        content_refs_result = supabase.table('content_references').select('content_id').execute()
        linked_content_ids = set(item['content_id'] for item in content_refs_result.data) if content_refs_result.data else set()
        linked_content_count = len(linked_content_ids)

        # Get type breakdown
        type_breakdown = {}
        for ref_type in reference_types:
            type_breakdown[ref_type] = type_breakdown.get(ref_type, 0) + 1

        type_breakdown_list = [{'reference_type': t, 'count': c} for t, c in type_breakdown.items()]
        type_breakdown_list.sort(key=lambda x: x['count'], reverse=True)

        # Get all category mappings in one query
        cat_result = supabase.table('reference_to_category').select('reference_id, category_id').in_('reference_id', reference_ids).execute()
        category_ids = [item['category_id'] for item in cat_result.data] if cat_result.data else []

        # Get all category names in one query
        if category_ids:
            cat_names_result = supabase.table('reference_categories').select('id, name').in_('id', list(set(category_ids))).execute()
            category_names = {item['id']: item['name'] for item in cat_names_result.data} if cat_names_result.data else {}

            # Get category breakdown
            category_breakdown = {}
            for cat_id in category_ids:
                if cat_id in category_names:
                    cat_name = category_names[cat_id]
                    category_breakdown[cat_name] = category_breakdown.get(cat_name, 0) + 1

            category_breakdown_list = [{'name': c, 'count': n} for c, n in category_breakdown.items()]
            category_breakdown_list.sort(key=lambda x: x['count'], reverse=True)
        else:
            category_breakdown_list = []

        # Combine results
        stats = {
            'total_references': total_references,
            'unique_types': unique_types,
            'avg_quality': avg_quality,
            'linked_content_count': linked_content_count,
            'type_breakdown': type_breakdown_list,
            'category_breakdown': category_breakdown_list
        }

        return stats

    except Exception as e:
        logger.error(f"Error getting reference statistics: {str(e)}")
        return {
            'total_references': 0,
            'unique_types': 0,
            'avg_quality': 0,
            'linked_content_count': 0,
            'type_breakdown': [],
            'category_breakdown': []
        }


if __name__ == "__main__":
    # Test the module
    print("Reference Management Module")
