# Compatibility module for reference_management.py
# This file provides backward compatibility for imports after reorganization

from reference_management.reference_management import *

# This file will be removed after all imports are updated
print("Warning: Using deprecated import path. Please update imports to use 'from reference_management.reference_management import ...'")
