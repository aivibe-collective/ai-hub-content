#!/usr/bin/env python3
"""
Test script to verify that the compatibility modules are working correctly.
"""

import sys
import warnings

# Capture warnings
warnings.filterwarnings('always')
import io
captured_warnings = io.StringIO()
sys.stderr = captured_warnings

# Import from compatibility modules
print("Testing compatibility modules...")

# Test supabase_client.py
print("\nTesting supabase_client.py:")
import supabase_client
print("✓ Successfully imported supabase_client")

# Test google_ai_client.py
print("\nTesting google_ai_client.py:")
import google_ai_client
print("✓ Successfully imported google_ai_client")

# Test prompt_management.py
print("\nTesting prompt_management.py:")
import prompt_management
print("✓ Successfully imported prompt_management")

# Test reference_management.py
print("\nTesting reference_management.py:")
import reference_management
print("✓ Successfully imported reference_management")

# Test content_workflow_supabase.py
print("\nTesting content_workflow_supabase.py:")
import content_workflow_supabase
print("✓ Successfully imported content_workflow_supabase")

# Test content_workflow_with_references.py
print("\nTesting content_workflow_with_references.py:")
import content_workflow_with_references
print("✓ Successfully imported content_workflow_with_references")

# Test content_workflow_with_ai_references.py
print("\nTesting content_workflow_with_ai_references.py:")
import content_workflow_with_ai_references
print("✓ Successfully imported content_workflow_with_ai_references")

# Test ai_reference_processor.py
print("\nTesting ai_reference_processor.py:")
import ai_reference_processor
print("✓ Successfully imported ai_reference_processor")

# Test source_evaluation.py
print("\nTesting source_evaluation.py:")
import source_evaluation
print("✓ Successfully imported source_evaluation")

# Test prompt_routes.py
print("\nTesting prompt_routes.py:")
import prompt_routes
print("✓ Successfully imported prompt_routes")

# Test reference_routes.py
print("\nTesting reference_routes.py:")
import reference_routes
print("✓ Successfully imported reference_routes")

# Print captured warnings
sys.stderr = sys.__stderr__
print("\nWarnings captured:")
warnings_text = captured_warnings.getvalue()
print(warnings_text if warnings_text else "No warnings captured")

print("\nAll compatibility modules tested successfully!")
