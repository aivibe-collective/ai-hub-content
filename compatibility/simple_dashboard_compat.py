# Compatibility module for simple_dashboard.py
# This file provides backward compatibility for imports after reorganization

from app.dashboard.simple_dashboard import *

# This file will be removed after all imports are updated
print("Warning: Using deprecated import path. Please update imports to use 'from app.dashboard.simple_dashboard import ...'")
