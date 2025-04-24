# Compatibility module for ab_testing.py
# This file provides backward compatibility for imports after reorganization

from quality.ab_testing import *

# This file will be removed after all imports are updated
print("Warning: Using deprecated import path. Please update imports to use 'from quality.ab_testing import ...'")
