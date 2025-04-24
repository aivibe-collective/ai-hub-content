# Reference Management module for AI Hub Content System

# Import key components for easier access
from reference_management.reference_management import (
    Reference, ReferenceQuality, ContentReference,
    get_references, get_reference, create_reference, update_reference,
    create_quality_assessment, update_quality_assessment,
    link_reference_to_content, get_content_references,
    get_reference_categories, get_reference_types,
    search_references, get_reference_statistics
)

from reference_management.ai_reference_processor import (
    process_reference_with_ai, process_references_batch
)
