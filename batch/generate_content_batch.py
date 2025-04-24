#!/usr/bin/env python3
"""
Script to generate content for multiple items in the correct dependency order.
"""

import os
import argparse
import logging
import time
import datetime
from dotenv import load_dotenv

# Import our custom modules
from supabase_client import is_connected, get_content_inventory, get_content_by_id, update_content_status
from content_workflow_supabase import generate_content_for_item, check_dependencies

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def build_dependency_graph(content_items):
    """Build a dependency graph from content items."""
    graph = {}

    for item in content_items:
        content_id = item['content_id']
        dependencies_str = item.get('dependencies', '')

        if not dependencies_str or dependencies_str.lower() == 'none':
            dependencies = []
        else:
            dependencies = [dep.strip() for dep in dependencies_str.split(',')]

        graph[content_id] = dependencies

    return graph

def topological_sort(graph):
    """Perform a topological sort on the dependency graph."""
    # Initialize variables
    visited = set()
    temp_visited = set()
    order = []

    def visit(node):
        """Visit a node in the graph."""
        if node in temp_visited:
            # Cycle detected
            logger.error(f"Cycle detected in dependencies involving {node}")
            return False

        if node in visited:
            return True

        temp_visited.add(node)

        # Visit dependencies
        for dependency in graph.get(node, []):
            if dependency not in graph:
                logger.warning(f"Dependency {dependency} not found in inventory")
                continue

            if not visit(dependency):
                return False

        temp_visited.remove(node)
        visited.add(node)
        order.append(node)
        return True

    # Visit all nodes
    for node in graph:
        if node not in visited:
            if not visit(node):
                return None

    # Reverse the order to get the correct dependency order
    return list(reversed(order))

def reset_content_status(content_ids=None):
    """Reset content status to 'Not Started'."""
    # Check Supabase connection
    if not is_connected():
        logger.error("Not connected to Supabase")
        return False

    try:
        # Get all content items if no IDs provided
        if not content_ids:
            content_items = get_content_inventory()
            content_ids = [item['content_id'] for item in content_items]

        # Reset status for each content item
        for content_id in content_ids:
            update_content_status(content_id, "Not Started", {
                "reset_time": datetime.datetime.now().isoformat()
            })
            logger.info(f"Reset status for content ID {content_id} to Not Started")

        return True
    except Exception as e:
        logger.error(f"Error resetting content status: {str(e)}")
        return False

def generate_content_batch(section=None, status=None, content_id=None, model_name=None, temperature=0.7, output_dir="generated_content", force=False, max_items=None, delay=5, reset_all=False):
    """Generate content for multiple items in the correct dependency order."""
    # Check Supabase connection
    if not is_connected():
        logger.error("Not connected to Supabase")
        return False

    # Get default model from environment variable if not specified
    if model_name is None:
        model_name = os.environ.get('DEFAULT_MODEL', 'gemini-1.5-flash')
        logger.info(f"Using default model: {model_name}")

    # Check if model is a preview model and warn the user
    if 'preview' in model_name:
        logger.warning(f"Model {model_name} is a preview model and may not have a free quota tier.")
        logger.warning(f"Consider using an experimental model (e.g., gemini-2.5-pro-exp-03-25) instead.")
        # Give the user a chance to abort
        time.sleep(2)

    # Reset all content status if requested
    if reset_all:
        logger.info("Resetting all content status to 'Not Started'")
        if not reset_content_status():
            logger.error("Failed to reset content status")
            return False

    # Get content items
    if content_id:
        # If specific content IDs are provided, get those items
        content_ids = [id.strip() for id in content_id.split(',')]
        content_items = []
        for id in content_ids:
            item = get_content_by_id(id)
            if item:
                content_items.append(item)
            else:
                logger.warning(f"Content item {id} not found")
    else:
        # Otherwise, get items based on section and status
        content_items = get_content_inventory(section=section, status=status)

    if not content_items:
        logger.error("No content items found")
        return False

    logger.info(f"Found {len(content_items)} content items")

    # Build dependency graph
    graph = build_dependency_graph(content_items)

    # Perform topological sort
    sorted_ids = topological_sort(graph)
    if sorted_ids is None:
        logger.error("Could not determine dependency order due to cycles")
        return False

    # Create a map of content items by ID
    content_map = {item['content_id']: item for item in content_items}

    # Filter sorted IDs to only include items from our query
    sorted_ids = [content_id for content_id in sorted_ids if content_id in content_map]

    # Limit the number of items if specified
    if max_items and len(sorted_ids) > max_items:
        logger.info(f"Limiting to {max_items} items")
        sorted_ids = sorted_ids[:max_items]

    logger.info(f"Generating content for {len(sorted_ids)} items in dependency order")

    # Generate content for each item
    successful = 0
    failed = 0
    skipped = 0

    for i, content_id in enumerate(sorted_ids):
        item = content_map[content_id]
        logger.info(f"[{i+1}/{len(sorted_ids)}] Processing {content_id}: {item['title']}")

        # Skip completed items unless forced
        if item['status'] == 'Completed' and not force:
            logger.info(f"Skipping {content_id} (already completed)")
            skipped += 1
            continue

        # Generate content
        success = generate_content_for_item(
            content_id=content_id,
            model_name=model_name,
            temperature=temperature,
            output_dir=output_dir,
            force=force
        )

        if success:
            logger.info(f"Successfully generated content for {content_id}")
            successful += 1
        else:
            logger.error(f"Failed to generate content for {content_id}")
            failed += 1

        # Add delay between items
        if i < len(sorted_ids) - 1 and delay > 0:
            logger.info(f"Waiting {delay} seconds before next item...")
            time.sleep(delay)

    logger.info(f"Batch generation complete: {successful} successful, {failed} failed, {skipped} skipped")
    return failed == 0

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate content for multiple items in the correct dependency order.")
    parser.add_argument("--section", help="Filter by section")
    parser.add_argument("--status", default="Not Started", help="Filter by status (default: Not Started)")
    parser.add_argument("--content-id", help="Specific content ID(s) to generate (comma-separated)")

    parser.add_argument("--model", help="Model name (default: from DEFAULT_MODEL env var or gemini-1.5-flash)")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature for generation")
    parser.add_argument("--output-dir", default="generated_content", help="Output directory")
    parser.add_argument("--force", action="store_true", help="Force generation even if dependencies are not met or content is already completed")
    parser.add_argument("--max-items", type=int, help="Maximum number of items to generate")
    parser.add_argument("--delay", type=int, default=5, help="Delay in seconds between items (default: 5)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated without actually generating")
    parser.add_argument("--reset-all", action="store_true", help="Reset all content status to 'Not Started' before generating")

    args = parser.parse_args()

    if args.dry_run:
        # Get content items
        content_items = get_content_inventory(section=args.section, status=args.status)
        if not content_items:
            logger.error("No content items found")
            return False

        # Build dependency graph
        graph = build_dependency_graph(content_items)

        # Perform topological sort
        sorted_ids = topological_sort(graph)
        if sorted_ids is None:
            logger.error("Could not determine dependency order due to cycles")
            return False

        # Create a map of content items by ID
        content_map = {item['content_id']: item for item in content_items}

        # Filter sorted IDs to only include items from our query
        sorted_ids = [content_id for content_id in sorted_ids if content_id in content_map]

        # Limit the number of items if specified
        if args.max_items and len(sorted_ids) > args.max_items:
            logger.info(f"Limiting to {args.max_items} items")
            sorted_ids = sorted_ids[:args.max_items]

        print(f"\nDry run: Would generate content for {len(sorted_ids)} items in this order:")
        for i, content_id in enumerate(sorted_ids):
            item = content_map[content_id]
            deps = graph.get(content_id, [])
            deps_str = f" (depends on: {', '.join(deps)})" if deps else ""
            print(f"{i+1}. {content_id}: {item['title']}{deps_str}")

        return True
    else:
        # Generate content
        success = generate_content_batch(
            section=args.section,
            status=args.status,
            content_id=args.content_id,
            model_name=args.model,
            temperature=args.temperature,
            output_dir=args.output_dir,
            force=args.force,
            max_items=args.max_items,
            delay=args.delay,
            reset_all=args.reset_all
        )

        # Exit with appropriate status code
        import sys
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
