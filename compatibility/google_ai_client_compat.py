# Compatibility module for google_ai_client.py
# This file provides backward compatibility for imports after reorganization

from core.google_ai_client import *

# This file will be removed after all imports are updated
print("Warning: Using deprecated import path. Please update imports to use 'from core.google_ai_client import ...'")
