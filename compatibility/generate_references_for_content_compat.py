# Compatibility module for generate_references_for_content.py
# This file provides backward compatibility for imports after reorganization

from batch.generate_references_for_content import *

# This file will be removed after all imports are updated
print("Warning: Using deprecated import path. Please update imports to use 'from batch.generate_references_for_content import ...'")
