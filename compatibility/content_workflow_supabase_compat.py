# Compatibility module for content_workflow_supabase.py
# This file provides backward compatibility for imports after reorganization

from workflows.content_workflow_supabase import *

# This file will be removed after all imports are updated
print("Warning: Using deprecated import path. Please update imports to use 'from workflows.content_workflow_supabase import ...'")
