# Compatibility module for generate_content_batch.py
# This file provides backward compatibility for imports after reorganization

from batch.generate_content_batch import *

# This file will be removed after all imports are updated
print("Warning: Using deprecated import path. Please update imports to use 'from batch.generate_content_batch import ...'")
