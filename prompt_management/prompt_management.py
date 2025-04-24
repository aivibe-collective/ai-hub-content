#!/usr/bin/env python3
"""
Prompt Management System for AI Hub Content Creation.

This module provides functions for managing prompt templates, variables,
and tracking prompt usage and effectiveness.
"""

import os
import json
import logging
import datetime
import uuid
import re
from typing import Dict, List, Optional, Any, Union

from dotenv import load_dotenv
from core.supabase_client import supabase, is_connected

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class PromptTemplate:
    """Class representing a prompt template with variables."""

    def __init__(self, template_id=None, name=None, description=None, template_text=None,
                 category=None, tags=None, version=1, parent_id=None, variables=None):
        """Initialize a prompt template."""
        self.template_id = template_id or str(uuid.uuid4())
        self.name = name or ""
        self.description = description or ""
        self.template_text = template_text or ""
        self.category = category or "Content Generation"
        self.tags = tags or {}
        self.version = version
        self.parent_id = parent_id
        self.variables = variables or []
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = self.created_at
        self.created_by = "system"
        self.is_active = True
        self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert the template to a dictionary."""
        return {
            "id": self.template_id,
            "name": self.name,
            "description": self.description,
            "template_text": self.template_text,
            "category": self.category,
            "tags": json.dumps(self.tags) if isinstance(self.tags, dict) else self.tags,
            "version": self.version,
            "parent_id": self.parent_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "is_active": self.is_active,
            "metadata": json.dumps(self.metadata) if isinstance(self.metadata, dict) else self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTemplate':
        """Create a template from a dictionary."""
        template = cls()
        template.template_id = data.get("id") or data.get("template_id")
        template.name = data.get("name", "")
        template.description = data.get("description", "")
        template.template_text = data.get("template_text", "")
        template.category = data.get("category", "Content Generation")

        # Handle tags
        tags = data.get("tags", {})
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except:
                tags = {}
        template.tags = tags

        template.version = data.get("version", 1)
        template.parent_id = data.get("parent_id")
        template.created_at = data.get("created_at", template.created_at)
        template.updated_at = data.get("updated_at", template.updated_at)
        template.created_by = data.get("created_by", "system")
        template.is_active = data.get("is_active", True)

        # Handle metadata
        metadata = data.get("metadata", {})
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        template.metadata = metadata

        return template

    def extract_variables(self) -> List[str]:
        """Extract variable names from the template text."""
        # Find all occurrences of {{variable_name}}
        pattern = r'\{\{([^}]+)\}\}'
        matches = re.findall(pattern, self.template_text)
        return list(set(matches))  # Remove duplicates

    def render(self, variables: Dict[str, str]) -> str:
        """Render the template with the provided variables."""
        rendered_text = self.template_text

        # Replace each variable
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            rendered_text = rendered_text.replace(placeholder, str(var_value))

        return rendered_text


def create_prompt_template(template: PromptTemplate) -> Optional[str]:
    """Create a new prompt template in the database.

    Args:
        template: The prompt template to create

    Returns:
        The template ID if successful, None otherwise
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return None

    try:
        # Insert the template
        template_data = template.to_dict()
        result = supabase.table('prompt_templates').insert(template_data).execute()

        if not result.data:
            logger.error("Failed to create prompt template")
            return None

        template_id = result.data[0]['id']

        # Extract and create variables
        variable_names = template.extract_variables()
        for var_name in variable_names:
            variable_data = {
                "template_id": template_id,
                "name": var_name,
                "description": f"Variable {var_name}",
                "required": True,
                "variable_type": "string"
            }
            supabase.table('prompt_variables').insert(variable_data).execute()

        logger.info(f"Created prompt template: {template.name} (ID: {template_id})")
        return template_id

    except Exception as e:
        logger.error(f"Error creating prompt template: {str(e)}")
        return None


def get_prompt_template(template_id: str) -> Optional[PromptTemplate]:
    """Get a prompt template by ID.

    Args:
        template_id: The ID of the template to retrieve

    Returns:
        The prompt template if found, None otherwise
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return None

    try:
        # Get the template
        result = supabase.table('prompt_templates').select('*').eq('id', template_id).execute()

        if not result.data:
            logger.warning(f"Prompt template not found: {template_id}")
            return None

        template_data = result.data[0]
        template = PromptTemplate.from_dict(template_data)

        # Get the variables
        var_result = supabase.table('prompt_variables').select('*').eq('template_id', template_id).execute()
        template.variables = var_result.data if var_result.data else []

        return template

    except Exception as e:
        logger.error(f"Error getting prompt template: {str(e)}")
        return None


def get_prompt_templates(category: Optional[str] = None, is_active: bool = True) -> List[Dict[str, Any]]:
    """Get prompt templates, optionally filtered by category and active status.

    Args:
        category: Optional category to filter by
        is_active: Whether to return only active templates

    Returns:
        List of prompt templates
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return []

    try:
        # Start the query
        query = supabase.table('prompt_templates').select('*')

        # Apply filters
        if category:
            query = query.eq('category', category)

        if is_active is not None:
            query = query.eq('is_active', is_active)

        # Execute the query
        result = query.order('name').execute()

        return result.data if result.data else []

    except Exception as e:
        logger.error(f"Error getting prompt templates: {str(e)}")
        return []


def update_prompt_template(template: PromptTemplate) -> bool:
    """Update an existing prompt template.

    Args:
        template: The prompt template to update

    Returns:
        True if successful, False otherwise
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return False

    if not template.template_id:
        logger.error("Template ID is required for update")
        return False

    try:
        # Check if the template exists
        existing = get_prompt_template(template.template_id)
        if not existing:
            logger.error(f"Template not found: {template.template_id}")
            return False

        # Update the template
        template.updated_at = datetime.datetime.now().isoformat()
        template_data = template.to_dict()

        result = supabase.table('prompt_templates').update(template_data).eq('id', template.template_id).execute()

        if not result.data:
            logger.error("Failed to update prompt template")
            return False

        # Update variables
        # First, get existing variables
        var_result = supabase.table('prompt_variables').select('*').eq('template_id', template.template_id).execute()
        existing_vars = {v['name']: v for v in var_result.data} if var_result.data else {}

        # Extract new variables
        new_vars = template.extract_variables()

        # Add new variables
        for var_name in new_vars:
            if var_name not in existing_vars:
                variable_data = {
                    "template_id": template.template_id,
                    "name": var_name,
                    "description": f"Variable {var_name}",
                    "required": True,
                    "variable_type": "string"
                }
                supabase.table('prompt_variables').insert(variable_data).execute()

        # Remove variables that are no longer used
        for var_name, var_data in existing_vars.items():
            if var_name not in new_vars:
                supabase.table('prompt_variables').delete().eq('id', var_data['id']).execute()

        logger.info(f"Updated prompt template: {template.name} (ID: {template.template_id})")
        return True

    except Exception as e:
        logger.error(f"Error updating prompt template: {str(e)}")
        return False


def create_new_version(template_id: str, new_template_text: str,
                       new_name: Optional[str] = None,
                       new_description: Optional[str] = None) -> Optional[str]:
    """Create a new version of an existing prompt template.

    Args:
        template_id: The ID of the template to version
        new_template_text: The new template text
        new_name: Optional new name for the template
        new_description: Optional new description for the template

    Returns:
        The new template ID if successful, None otherwise
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return None

    try:
        # Get the existing template
        existing = get_prompt_template(template_id)
        if not existing:
            logger.error(f"Template not found: {template_id}")
            return None

        # Create a new template based on the existing one
        new_template = PromptTemplate(
            name=new_name or f"{existing.name} (v{existing.version + 1})",
            description=new_description or existing.description,
            template_text=new_template_text,
            category=existing.category,
            tags=existing.tags,
            version=existing.version + 1,
            parent_id=template_id
        )

        # Create the new template
        new_id = create_prompt_template(new_template)
        if not new_id:
            logger.error("Failed to create new version of prompt template")
            return None

        logger.info(f"Created new version of prompt template: {new_template.name} (ID: {new_id})")
        return new_id

    except Exception as e:
        logger.error(f"Error creating new version of prompt template: {str(e)}")
        return None


def log_prompt_usage(template_id: str, variables: Dict[str, str],
                     rendered_prompt: str, prompt_id: Optional[str] = None,
                     model: Optional[str] = None, temperature: Optional[float] = None,
                     content_id: Optional[str] = None, success: bool = True,
                     metrics: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Log the usage of a prompt template.

    Args:
        template_id: The ID of the template used
        variables: The variables used to render the template
        rendered_prompt: The rendered prompt text
        prompt_id: Optional ID of the prompt in prompt_logs
        model: Optional model used for generation
        temperature: Optional temperature used for generation
        content_id: Optional content ID
        success: Whether the prompt was successful
        metrics: Optional metrics about the prompt usage

    Returns:
        The usage ID if successful, None otherwise
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return None

    try:
        # Create the usage record
        usage_data = {
            "template_id": template_id,
            "prompt_id": prompt_id,
            "variables": json.dumps(variables),
            "rendered_prompt": rendered_prompt,
            "model": model,
            "temperature": temperature,
            "content_id": content_id,
            "success": success,
            "metrics": json.dumps(metrics) if metrics else None,
            "created_at": datetime.datetime.now().isoformat()
        }

        result = supabase.table('prompt_usage').insert(usage_data).execute()

        if not result.data:
            logger.error("Failed to log prompt usage")
            return None

        usage_id = result.data[0]['id']
        logger.info(f"Logged prompt usage: {usage_id}")
        return usage_id

    except Exception as e:
        logger.error(f"Error logging prompt usage: {str(e)}")
        return None


def add_prompt_feedback(usage_id: str, rating: int, feedback_text: Optional[str] = None,
                       feedback_type: Optional[str] = None) -> bool:
    """Add feedback for a prompt usage.

    Args:
        usage_id: The ID of the prompt usage
        rating: Rating from 1 to 5
        feedback_text: Optional feedback text
        feedback_type: Optional feedback type

    Returns:
        True if successful, False otherwise
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return False

    try:
        # Validate rating
        if not 1 <= rating <= 5:
            logger.error(f"Invalid rating: {rating}. Must be between 1 and 5.")
            return False

        # Create the feedback record
        feedback_data = {
            "usage_id": usage_id,
            "rating": rating,
            "feedback_text": feedback_text,
            "feedback_type": feedback_type,
            "created_at": datetime.datetime.now().isoformat()
        }

        result = supabase.table('prompt_feedback').insert(feedback_data).execute()

        if not result.data:
            logger.error("Failed to add prompt feedback")
            return False

        logger.info(f"Added feedback for prompt usage: {usage_id}")
        return True

    except Exception as e:
        logger.error(f"Error adding prompt feedback: {str(e)}")
        return False


def get_prompt_categories() -> List[Dict[str, Any]]:
    """Get all prompt categories.

    Returns:
        List of prompt categories
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return []

    try:
        result = supabase.table('prompt_categories').select('*').order('name').execute()
        return result.data if result.data else []

    except Exception as e:
        logger.error(f"Error getting prompt categories: {str(e)}")
        return []


def get_prompt_performance_metrics(template_id: Optional[str] = None,
                                  category: Optional[str] = None,
                                  days: int = 30) -> List[Dict[str, Any]]:
    """Get performance metrics for prompts.

    Args:
        template_id: Optional template ID to filter by
        category: Optional category to filter by
        days: Number of days to look back

    Returns:
        List of prompt performance metrics
    """
    if not is_connected():
        logger.error("Not connected to Supabase")
        return []

    try:
        # Calculate the date range
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)

        # Build the query
        query = f"""
        SELECT
            pt.id as template_id,
            pt.name as template_name,
            pt.category,
            COUNT(pu.id) as usage_count,
            SUM(CASE WHEN pu.success = true THEN 1 ELSE 0 END) as success_count,
            AVG(COALESCE(pf.rating, 0)) as avg_rating,
            COUNT(pf.id) as feedback_count
        FROM
            prompt_templates pt
        LEFT JOIN
            prompt_usage pu ON pt.id = pu.template_id
        LEFT JOIN
            prompt_feedback pf ON pu.id = pf.usage_id
        WHERE
            pu.created_at >= '{start_date.isoformat()}'
        """

        # Add filters
        if template_id:
            query += f" AND pt.id = '{template_id}'"

        if category:
            query += f" AND pt.category = '{category}'"

        # Group and order
        query += """
        GROUP BY
            pt.id, pt.name, pt.category
        ORDER BY
            usage_count DESC
        """

        # Execute the query
        result = supabase.rpc('run_sql', {'query': query}).execute()

        return result.data if result.data else []

    except Exception as e:
        logger.error(f"Error getting prompt performance metrics: {str(e)}")
        return []


# Default prompt templates
DEFAULT_TEMPLATES = [
    {
        "name": "Content Generation",
        "description": "Generate content for a specific topic with structured sections",
        "template_text": """Generate comprehensive content about {{topic}} for an audience with {{audience_technical_level}} technical level.

The content should include the following sections:
1. Introduction
2. {{section1}}
3. {{section2}}
4. {{section3}}
5. Conclusion

Focus on {{focus_area}} and ensure the content aligns with these mission pillars:
- {{mission_pillar1}}
- {{mission_pillar2}}

Include practical examples and applications where appropriate.
""",
        "category": "Content Generation",
        "tags": {"purpose": "main_content", "complexity": "medium"}
    },
    {
        "name": "Source Collection",
        "description": "Find and evaluate sources for a specific topic",
        "template_text": """Find 5 high-quality sources about {{topic}} that would be valuable for creating educational content.

For each source, provide:
1. Title
2. Author(s)
3. Publication date
4. URL or DOI
5. Brief summary (2-3 sentences)
6. CRAAP evaluation (Currency, Relevance, Authority, Accuracy, Purpose)
7. Key insights relevant to {{focus_area}}

Prioritize sources that address {{specific_aspect}} and are accessible to readers with {{audience_technical_level}} technical knowledge.
""",
        "category": "Source Collection",
        "tags": {"purpose": "research", "complexity": "high"}
    },
    {
        "name": "Content Structuring",
        "description": "Create a detailed outline for content",
        "template_text": """Create a detailed outline for content about {{topic}} aimed at {{audience}} with {{audience_technical_level}} technical level.

The outline should include:

1. Introduction
   - Hook to engage the reader
   - Brief overview of {{topic}}
   - Why this topic matters to the audience

2. Background
   - Key concepts and terminology
   - Historical context or development
   - Current state of {{topic}}

3. Main Sections
   {{main_sections}}

4. Practical Applications
   - Real-world examples
   - Hands-on activities or exercises
   - Implementation guidelines

5. Challenges and Considerations
   - Common pitfalls
   - Ethical considerations
   - Future developments

6. Conclusion
   - Summary of key points
   - Call to action
   - Additional resources

Ensure the outline incorporates these mission pillars:
- {{mission_pillar1}}
- {{mission_pillar2}}
""",
        "category": "Content Structuring",
        "tags": {"purpose": "outlining", "complexity": "medium"}
    },
    {
        "name": "Content Review",
        "description": "Review and provide feedback on content",
        "template_text": """Review the following content about {{topic}} and provide detailed feedback:

Content to review:
{{content_text}}

Please evaluate the content on these dimensions:

1. Technical Accuracy
   - Are all facts and concepts correct?
   - Are there any technical errors or misconceptions?
   - Are explanations clear and precise?

2. Completeness
   - Does it cover all essential aspects of {{topic}}?
   - Are there any significant gaps in the content?
   - Is the depth appropriate for {{audience_technical_level}} technical level?

3. Structure and Flow
   - Is the content well-organized?
   - Does it flow logically from one section to another?
   - Are transitions smooth and effective?

4. Alignment with Mission Pillars
   - How well does it address {{mission_pillar1}}?
   - How well does it address {{mission_pillar2}}?
   - Are there opportunities to better integrate these pillars?

5. Practical Value
   - Does it include useful examples and applications?
   - Is it actionable for the target audience?
   - Does it provide sufficient guidance for implementation?

6. Accessibility
   - Is the language appropriate for the audience?
   - Are complex concepts explained clearly?
   - Are there terms or concepts that need better explanation?

7. Specific Improvement Suggestions
   - What sections need the most improvement?
   - What content should be added?
   - What content could be removed or condensed?

Please be specific and constructive in your feedback.
""",
        "category": "Content Review",
        "tags": {"purpose": "quality_assurance", "complexity": "high"}
    }
]


def initialize_default_templates():
    """Initialize the database with default prompt templates."""
    if not is_connected():
        logger.error("Not connected to Supabase")
        return False

    try:
        # Check if we already have templates
        existing = get_prompt_templates()
        if existing:
            logger.info(f"Found {len(existing)} existing templates. Skipping initialization.")
            return True

        # Create default templates
        for template_data in DEFAULT_TEMPLATES:
            template = PromptTemplate(
                name=template_data["name"],
                description=template_data["description"],
                template_text=template_data["template_text"],
                category=template_data["category"],
                tags=template_data["tags"]
            )
            create_prompt_template(template)

        logger.info(f"Initialized {len(DEFAULT_TEMPLATES)} default prompt templates")
        return True

    except Exception as e:
        logger.error(f"Error initializing default templates: {str(e)}")
        return False


if __name__ == "__main__":
    # Initialize default templates when run directly
    initialize_default_templates()
