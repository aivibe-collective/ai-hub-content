# Compatibility module for prompt_management.py
# This file provides backward compatibility for imports after reorganization

from prompt_management.prompt_management import *

# This file will be removed after all imports are updated
print("Warning: Using deprecated import path. Please update imports to use 'from prompt_management.prompt_management import ...'")
