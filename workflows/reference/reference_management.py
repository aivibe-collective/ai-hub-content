#!/usr/bin/env python3
"""
Compatibility module for reference_management.py.
This module imports from the new location and provides warnings.
"""

import warnings

# Show deprecation warning
warnings.warn(
    "Importing from reference_management is deprecated. "
    "Please update your imports to use 'from reference_management.reference_management import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import from the new location
from reference_management.reference_management import *
