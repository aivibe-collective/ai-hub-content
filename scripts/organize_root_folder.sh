#!/bin/bash
# Script to organize the root folder by moving files to appropriate directories
# Instead of removing files, we'll move them to an old_files directory

# Create the old_files directory if it doesn't exist
mkdir -p old_files
mkdir -p old_files/python_modules
mkdir -p old_files/compatibility
mkdir -p old_files/scripts
mkdir -p old_files/sql

echo "Created old_files directory structure"

# Function to safely move files
# Usage: safe_move <source_file> <destination_directory>
safe_move() {
    if [ -f "$1" ]; then
        echo "Moving $1 to $2"
        cp "$1" "$2"
        mv "$1" "old_files/$1"
    else
        echo "File $1 not found, skipping"
    fi
}

# Move Python modules to old_files/python_modules
echo "Moving Python modules to old_files/python_modules..."

# Core functionality
safe_move "google_ai_client.py" "old_files/python_modules"
safe_move "supabase_client.py" "old_files/python_modules"

# Workflow implementations
safe_move "content_workflow_supabase.py" "old_files/python_modules"
safe_move "content_workflow_with_references.py" "old_files/python_modules"
safe_move "content_workflow_with_ai_references.py" "old_files/python_modules"
safe_move "ai_reference_processor.py" "old_files/python_modules"
safe_move "improved_reference_extractor.py" "old_files/python_modules"
safe_move "reference_management.py" "old_files/python_modules"

# Web application
safe_move "web_view.py" "old_files/python_modules"
safe_move "app.py" "old_files/python_modules"
safe_move "main.py" "old_files/python_modules"
safe_move "dashboard.py" "old_files/python_modules"
safe_move "simple_dashboard.py" "old_files/python_modules"
safe_move "prompt_routes.py" "old_files/python_modules"
safe_move "reference_routes.py" "old_files/python_modules"
safe_move "prompt_management_routes.py" "old_files/python_modules"
safe_move "reference_management_routes.py" "old_files/python_modules"

# Prompt management
safe_move "prompt_importer.py" "old_files/python_modules"
safe_move "prompt_management.py" "old_files/python_modules"

# Quality control
safe_move "quality_control.py" "old_files/python_modules"
safe_move "content_evaluation.py" "old_files/python_modules"
safe_move "source_evaluation.py" "old_files/python_modules"
safe_move "ab_testing.py" "old_files/python_modules"

# Move compatibility files to old_files/compatibility
echo "Moving compatibility files to old_files/compatibility..."
for file in *_compat.py; do
    if [ -f "$file" ]; then
        echo "Moving $file to old_files/compatibility"
        cp "$file" "old_files/compatibility"
        mv "$file" "old_files/$file"
    fi
done

# Move script files to old_files/scripts
echo "Moving script files to old_files/scripts..."
safe_move "check_dashboard_data.py" "old_files/scripts"
safe_move "check_tables.py" "old_files/scripts"
safe_move "create_hub_repo.py" "old_files/scripts"
safe_move "generate_content_batch.py" "old_files/scripts"
safe_move "generate_content_batch_improved.py" "old_files/scripts"
safe_move "generate_references_for_content.py" "old_files/scripts"
safe_move "google_ai_test.py" "old_files/scripts"
safe_move "list_content_inventory.py" "old_files/scripts"
safe_move "process_all_content_references.py" "old_files/scripts"
safe_move "process_all_references.py" "old_files/scripts"
safe_move "reset_content_status.py" "old_files/scripts"
safe_move "test_ai_reference_processor.py" "old_files/scripts"
safe_move "test_supabase_connection.py" "old_files/scripts"
safe_move "test_compatibility.py" "old_files/scripts"

# Move SQL files to old_files/sql
echo "Moving SQL files to old_files/sql..."
safe_move "create_tables.sql" "old_files/sql"

echo "Root folder cleanup completed. All files have been moved to the old_files directory."
echo "You can review the files in the old_files directory and delete them if they are no longer needed."
