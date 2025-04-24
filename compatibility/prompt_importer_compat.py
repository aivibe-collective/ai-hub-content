# Compatibility module for prompt_importer.py
# This file provides backward compatibility for imports after reorganization

from prompt_management.prompt_importer import *

# This file will be removed after all imports are updated
print("Warning: Using deprecated import path. Please update imports to use 'from prompt_management.prompt_importer import ...'")
