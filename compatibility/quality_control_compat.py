# Compatibility module for quality_control.py
# This file provides backward compatibility for imports after reorganization

from quality.quality_control import *

# This file will be removed after all imports are updated
print("Warning: Using deprecated import path. Please update imports to use 'from quality.quality_control import ...'")
