# Core module for AI Hub Content System

# Import key components for easier access
from core.supabase_client import (
    supabase, is_connected, get_content_inventory, update_content_status,
    get_content_by_id, update_content_item
)

from core.google_ai_client import (
    generate_content, list_models
)
