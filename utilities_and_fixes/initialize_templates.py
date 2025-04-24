#!/usr/bin/env python3
"""
Initialize default prompt templates in the database.
"""

from prompt_management import initialize_default_templates

if __name__ == "__main__":
    print("Initializing default prompt templates...")
    success = initialize_default_templates()
    if success:
        print("Successfully initialized default prompt templates.")
    else:
        print("Failed to initialize default prompt templates.")
