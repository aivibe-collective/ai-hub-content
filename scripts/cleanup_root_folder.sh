#!/bin/bash
# Master script to clean up the root folder and update the project structure

echo "Starting root folder cleanup..."

# Run the organize_root_folder.sh script
./scripts/organize_root_folder.sh

echo "Updating project structure documentation..."

# Run the update_project_structure.sh script
./scripts/update_project_structure.sh

echo "Root folder cleanup completed successfully!"
echo "Please review the changes and make any necessary adjustments."
