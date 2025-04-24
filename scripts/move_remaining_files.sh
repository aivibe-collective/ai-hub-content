#!/bin/bash
# Script to move remaining files from the root directory to their appropriate directories
# This script will only move files if they're not already in their destination directories

# Create old_files directory for backup
mkdir -p old_files
mkdir -p old_files/python_modules
mkdir -p old_files/compatibility

echo "Moving remaining files from root directory..."

# Function to safely move a file if it exists in the root directory
# Usage: move_if_exists <file_name> <destination_directory>
move_if_exists() {
    if [ -f "$1" ] && [ ! -f "$2/$1" ]; then
        echo "Moving $1 to $2/"
        cp "$1" "$2/"
        mv "$1" "old_files/python_modules/$1"
    elif [ -f "$1" ] && [ -f "$2/$1" ]; then
        echo "$1 already exists in $2/, moving original to old_files/"
        mv "$1" "old_files/python_modules/$1"
    else
        echo "$1 not found in root directory, skipping"
    fi
}

# Function to safely move compatibility files
# Usage: move_compat <file_name>
move_compat() {
    if [ -f "$1" ]; then
        echo "Moving $1 to old_files/compatibility/"
        cp "$1" "compatibility/"
        mv "$1" "old_files/compatibility/$1"
    else
        echo "$1 not found in root directory, skipping"
    fi
}

# Make sure destination directories exist
mkdir -p scripts
mkdir -p test
mkdir -p sql
mkdir -p compatibility
mkdir -p core/google_ai
mkdir -p core/supabase
mkdir -p workflows/content
mkdir -p workflows/reference
mkdir -p app
mkdir -p app/dashboard
mkdir -p app/routes
mkdir -p prompt_management
mkdir -p reference_management
mkdir -p quality

# Move script files to scripts/ directory
echo "Moving script files to scripts/ directory..."
move_if_exists "check_dashboard_data.py" "scripts"
move_if_exists "check_tables.py" "scripts"
move_if_exists "create_hub_repo.py" "scripts"
move_if_exists "generate_content_batch.py" "scripts"
move_if_exists "generate_content_batch_improved.py" "scripts"
move_if_exists "generate_references_for_content.py" "scripts"
move_if_exists "google_ai_test.py" "scripts"
move_if_exists "list_content_inventory.py" "scripts"
move_if_exists "process_all_content_references.py" "scripts"
move_if_exists "process_all_references.py" "scripts"
move_if_exists "reset_content_status.py" "scripts"
move_if_exists "test_ai_reference_processor.py" "scripts"
move_if_exists "test_supabase_connection.py" "scripts"

# Move test files to test/ directory
echo "Moving test files to test/ directory..."
move_if_exists "test_compatibility.py" "test"

# Move SQL files to sql/ directory
echo "Moving SQL files to sql/ directory..."
move_if_exists "create_tables.sql" "sql"

# Move core functionality files
echo "Moving core functionality files..."
move_if_exists "google_ai_client.py" "core/google_ai"
move_if_exists "supabase_client.py" "core/supabase"

# Move workflow implementation files
echo "Moving workflow implementation files..."
move_if_exists "content_workflow_supabase.py" "workflows/content"
move_if_exists "content_workflow_with_references.py" "workflows/content"
move_if_exists "content_workflow_with_ai_references.py" "workflows/content"
move_if_exists "ai_reference_processor.py" "workflows/reference"
move_if_exists "improved_reference_extractor.py" "workflows/reference"
move_if_exists "reference_management.py" "workflows/reference"

# Move web application files
echo "Moving web application files..."
move_if_exists "web_view.py" "app"
move_if_exists "app.py" "app"
move_if_exists "main.py" "app"
move_if_exists "dashboard.py" "app/dashboard"
move_if_exists "simple_dashboard.py" "app/dashboard"
move_if_exists "prompt_routes.py" "app/routes"
move_if_exists "reference_routes.py" "app/routes"
move_if_exists "prompt_management_routes.py" "app/routes"
move_if_exists "reference_management_routes.py" "app/routes"

# Move prompt management files
echo "Moving prompt management files..."
move_if_exists "prompt_importer.py" "prompt_management"
move_if_exists "prompt_management.py" "prompt_management"

# Move reference management files
echo "Moving reference management files..."
move_if_exists "reference_importer.py" "reference_management"
move_if_exists "reference_importer_improved.py" "reference_management"

# Move quality control files
echo "Moving quality control files..."
move_if_exists "quality_control.py" "quality"
move_if_exists "content_evaluation.py" "quality"
move_if_exists "source_evaluation.py" "quality"
move_if_exists "ab_testing.py" "quality"

# Move compatibility files
echo "Moving compatibility files..."
for file in *_compat.py; do
    move_compat "$file"
done

echo "File movement completed."
echo "Original files have been backed up to the old_files directory."
echo "Please review the changes and test the application to ensure everything works correctly."
