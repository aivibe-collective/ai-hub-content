# Compatibility module for reference_management_routes.py
# This file provides backward compatibility for imports after reorganization

from app.routes.reference_management_routes import *

# This file will be removed after all imports are updated
print("Warning: Using deprecated import path. Please update imports to use 'from app.routes.reference_management_routes import ...'")
