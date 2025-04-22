"""
Configuration for the test environment.
"""

import os
from enum import Enum

# Project configuration
TEST_PROJECT_ID = os.environ.get("TEST_PROJECT_ID", "test-project")
TEST_REGION = os.environ.get("TEST_REGION", "us-central1")

# Firestore configuration
FIRESTORE_EMULATOR_HOST = os.environ.get("FIRESTORE_EMULATOR_HOST", "localhost:8080")
CONTENT_COLLECTION = os.environ.get("TEST_CONTENT_COLLECTION", "test_content-items")
TEMPLATES_COLLECTION = os.environ.get("TEST_TEMPLATES_COLLECTION", "test_templates")
USERS_COLLECTION = os.environ.get("TEST_USERS_COLLECTION", "test_users")
SOURCE_COLLECTION = os.environ.get("TEST_SOURCE_COLLECTION", "test_sources")
FEEDBACK_COLLECTION = os.environ.get("TEST_FEEDBACK_COLLECTION", "test_feedback")

# Pub/Sub configuration
PUBSUB_EMULATOR_HOST = os.environ.get("PUBSUB_EMULATOR_HOST", "localhost:8085")
CONTENT_CREATION_TOPIC = os.environ.get("TEST_CONTENT_CREATION_TOPIC", "test_content-creation-events")
SOURCE_COLLECTION_TOPIC = os.environ.get("TEST_SOURCE_COLLECTION_TOPIC", "test_source-collection-events")
REVIEW_TOPIC = os.environ.get("TEST_REVIEW_TOPIC", "test_review-events")

# Storage configuration
TEST_CONTENT_BUCKET = os.environ.get("TEST_CONTENT_BUCKET", "test-content-bucket")

# Vertex AI configuration
VERTEX_AI_LOCATION = os.environ.get("TEST_VERTEX_AI_LOCATION", "us-central1")
VERTEX_AI_MODEL = os.environ.get("TEST_VERTEX_AI_MODEL", "text-bison@002")

# Test data directories
TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CONTENT_PLANS_DIR = os.path.join(TEST_DATA_DIR, "content_plans")
SOURCE_DATA_DIR = os.path.join(TEST_DATA_DIR, "sources")
TEMPLATES_DIR = os.path.join(TEST_DATA_DIR, "templates")
USER_FEEDBACK_DIR = os.path.join(TEST_DATA_DIR, "feedback")

# API configuration
TEST_API_URL = os.environ.get("TEST_API_URL", "http://localhost:8080")

# Enums for test data
class ContentTypes(str, Enum):
    """Content types for testing."""
    LEARNING_MODULE = "LearningModule"
    CASE_STUDY = "CaseStudy"
    BLOG_POST = "BlogPost"
    TOOL_GUIDE = "ToolGuide"
    SECTOR_PLAYBOOK = "SectorPlaybook"

class AudienceLevels(str, Enum):
    """Audience levels for testing."""
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    EXPERT = "Expert"
    GENERAL = "General"

class MissionPillars(str, Enum):
    """Mission pillars for testing."""
    RESPONSIBLE_AI = "ResponsibleAI"
    INCLUSION = "Inclusion"
    EXPERTISE = "Expertise"
    SUSTAINABILITY = "Sustainability"

class UserRoles(str, Enum):
    """User roles for testing."""
    CONTENT_CREATOR = "ContentCreator"
    TECHNICAL_REVIEWER = "TechnicalReviewer"
    MISSION_PILLAR_REVIEWER = "MissionPillarReviewer"
    AUDIENCE_REVIEWER = "AudienceReviewer"
    SOURCE_REVIEWER = "SourceReviewer"
    EDITOR = "Editor"
    ADMIN = "Admin"
