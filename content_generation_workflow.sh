#!/bin/bash

# Script to set up the basic infrastructure for an agentic AI content creation system.

# Create the 'sources' directory to store raw source data.
mkdir -p sources
echo "Created 'sources' directory."

# Create the 'content' directory to store generated content.
mkdir -p content
echo "Created 'content' directory."

# Create the 'metadata' directory to store source and content metadata.
mkdir -p metadata
echo "Created 'metadata' directory."

# Display a completion message.
echo "Infrastructure setup complete."