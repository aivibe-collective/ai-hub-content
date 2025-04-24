# Compatibility module for process_all_content_references.py
# This file provides backward compatibility for imports after reorganization

from batch.process_all_content_references import *

# This file will be removed after all imports are updated
print("Warning: Using deprecated import path. Please update imports to use 'from batch.process_all_content_references import ...'")
