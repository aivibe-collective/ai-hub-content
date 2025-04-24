# Compatibility module for content_evaluation.py
# This file provides backward compatibility for imports after reorganization

from quality.content_evaluation import *

# This file will be removed after all imports are updated
print("Warning: Using deprecated import path. Please update imports to use 'from quality.content_evaluation import ...'")
