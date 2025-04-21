"""
Test environment configuration for the Agentic AI Content Creation System.
"""

import os
from pathlib import Path

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    # Find .env file in the test directory
    env_path = Path(os.path.dirname(os.path.abspath(__file__))) / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"Loaded environment variables from {env_path}")
    else:
        print("No .env file found. Using default or system environment variables.")
except ImportError:
    print("python-dotenv not installed. Using default or system environment variables.")
    # Continue without dotenv

# Test environment configuration
TEST_PROJECT_ID = os.environ.get("TEST_PROJECT_ID", "aivibe-content-creation-test")
TEST_REGION = os.environ.get("TEST_REGION", "us-central1")
TEST_CONTENT_BUCKET = os.environ.get("TEST_CONTENT_BUCKET", "aivibe-content-test")

# Vertex AI configuration
TEST_MODEL = os.environ.get("TEST_MODEL", "text-bison@002")

# Firestore collections
CONTENT_ITEMS_COLLECTION = "content-items-test"
TEMPLATES_COLLECTION = "templates-test"
SOURCES_COLLECTION = "sources-test"
USERS_COLLECTION = "users-test"

# Pub/Sub topics
CONTENT_CREATION_TOPIC = "content-creation-events-test"
SOURCE_COLLECTION_TOPIC = "source-collection-events-test"
REVIEW_TOPIC = "review-events-test"

# Cloud Run services
RESEARCH_SERVICE_URL = os.environ.get(
    "RESEARCH_SERVICE_URL",
    f"https://research-service-test-{TEST_PROJECT_ID}.a.run.app"
)

# Test data paths
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CONTENT_PLANS_DIR = os.path.join(TEST_DATA_DIR, "content_plans")
SOURCE_DATA_DIR = os.path.join(TEST_DATA_DIR, "sources")
TEMPLATES_DIR = os.path.join(TEST_DATA_DIR, "templates")
USER_FEEDBACK_DIR = os.path.join(TEST_DATA_DIR, "feedback")

# Test user roles
class UserRoles:
    CONTENT_CREATOR = "content_creator"
    TECHNICAL_REVIEWER = "technical_reviewer"
    MISSION_PILLAR_REVIEWER = "mission_pillar_reviewer"
    AUDIENCE_REVIEWER = "audience_reviewer"
    SOURCE_REVIEWER = "source_reviewer"
    EDITOR = "editor"
    ADMIN = "admin"

# Content types
class ContentTypes:
    LEARNING_MODULE = "LearningModule"
    CASE_STUDY = "CaseStudy"
    BLOG_POST = "BlogPost"
    TOOL_GUIDE = "ToolGuide"
    SECTOR_PLAYBOOK = "SectorPlaybook"

# Audience levels
class AudienceLevels:
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    EXPERT = "Expert"
    GENERAL = "General"

# Mission pillars
class MissionPillars:
    RESPONSIBLE_AI = "ResponsibleAI"
    SUSTAINABILITY = "Sustainability"
    INCLUSION = "Inclusion"
    EXPERTISE = "Expertise"
