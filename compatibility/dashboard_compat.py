# Compatibility module for dashboard.py
# This file provides backward compatibility for imports after reorganization

from app.dashboard.dashboard import *

# This file will be removed after all imports are updated
print("Warning: Using deprecated import path. Please update imports to use 'from app.dashboard.dashboard import ...'")
