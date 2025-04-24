#!/usr/bin/env python3
"""
Compatibility module for content_workflow_with_references.py.
This module imports from the new location and provides warnings.
"""

import warnings

# Show deprecation warning
warnings.warn(
    "Importing from content_workflow_with_references is deprecated. "
    "Please update your imports to use 'from workflows.content_workflow_with_references import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import from the new location
from workflows.content_workflow_with_references import *
