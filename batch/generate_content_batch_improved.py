#!/usr/bin/env python3
"""
Improved batch content generation script with better dependency handling.
"""

import os
import sys
import argparse
import logging
import time
import json
from typing import List, Dict, Set, Optional, Tuple
import networkx as nx
from datetime import datetime

# Import our custom modules
from supabase_client import (
    is_connected, get_content_inventory, update_content_status
)
from content_workflow_supabase import generate_content_for_id

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_dependencies(dependency_str: str) -> List[str]:
    """Parse dependency string into a list of content IDs.
    
    Args:
        dependency_str: Semicolon-separated list of content IDs
        
    Returns:
        List of content IDs
    """
    if not dependency_str or dependency_str.strip() == '':
        return []
    
    # Split by semicolon and remove any whitespace
    return [dep.strip() for dep in dependency_str.split(';') if dep.strip()]

def build_dependency_graph(content_items: List[Dict]) -> nx.DiGraph:
    """Build a directed graph of content dependencies.
    
    Args:
        content_items: List of content inventory items
        
    Returns:
        NetworkX DiGraph where nodes are content IDs and edges represent dependencies
    """
    G = nx.DiGraph()
    
    # Add all content items as nodes
    for item in content_items:
        content_id = item['content_id']
        G.add_node(content_id, data=item)
    
    # Add dependency edges
    for item in content_items:
        content_id = item['content_id']
        dependencies = parse_dependencies(item.get('dependencies', ''))
        
        for dep in dependencies:
            if dep in G:
                # Add edge from dependency to the item (item depends on dep)
                G.add_edge(dep, content_id)
            else:
                logger.warning(f"Dependency {dep} for {content_id} not found in inventory")
    
    return G

def get_generation_order(G: nx.DiGraph) -> List[str]:
    """Determine the order in which content should be generated based on dependencies.
    
    Args:
        G: Dependency graph
        
    Returns:
        List of content IDs in generation order
    """
    try:
        # Try to get a topological sort (respects dependencies)
        return list(nx.topological_sort(G))
    except nx.NetworkXUnfeasible:
        # If there's a cycle, log a warning and return nodes in arbitrary order
        logger.warning("Dependency cycle detected! Using arbitrary order.")
        return list(G.nodes())

def filter_content_items(content_items: List[Dict], 
                        status: Optional[str] = None,
                        content_ids: Optional[List[str]] = None,
                        section: Optional[str] = None) -> List[Dict]:
    """Filter content items based on criteria.
    
    Args:
        content_items: List of content inventory items
        status: Filter by status (e.g., "Not Started")
        content_ids: Filter by specific content IDs
        section: Filter by section
        
    Returns:
        Filtered list of content items
    """
    filtered_items = content_items
    
    if status:
        filtered_items = [item for item in filtered_items if item.get('status') == status]
    
    if content_ids:
        filtered_items = [item for item in filtered_items if item.get('content_id') in content_ids]
    
    if section:
        filtered_items = [item for item in filtered_items if item.get('section') == section]
    
    return filtered_items

def generate_content_batch(status: Optional[str] = None,
                          content_ids: Optional[List[str]] = None,
                          section: Optional[str] = None,
                          model: str = "gemini-1.5-flash",
                          temperature: float = 0.7,
                          max_items: int = None,
                          force: bool = False,
                          retry_failed: bool = False,
                          delay: int = 0) -> Tuple[int, int]:
    """Generate content for multiple items in dependency order.
    
    Args:
        status: Filter by status (e.g., "Not Started")
        content_ids: Filter by specific content IDs
        section: Filter by section
        model: Model to use for generation
        temperature: Temperature for generation
        max_items: Maximum number of items to generate
        force: Whether to force generation even if dependencies aren't met
        retry_failed: Whether to retry previously failed items
        delay: Delay between generations in seconds
        
    Returns:
        Tuple of (success_count, failure_count)
    """
    # Check Supabase connection
    if not is_connected():
        logger.error("Not connected to Supabase")
        return 0, 0
    
    # Get all content items
    all_content_items = get_content_inventory()
    if not all_content_items:
        logger.error("No content items found in inventory")
        return 0, 0
    
    # Apply filters
    statuses = ["Not Started"]
    if retry_failed:
        statuses.append("Failed")
    
    if status:
        statuses = [status]
    
    filtered_items = []
    for s in statuses:
        filtered_items.extend(filter_content_items(all_content_items, s, content_ids, section))
    
    if not filtered_items:
        logger.info(f"No content items match the criteria (status={status}, content_ids={content_ids}, section={section})")
        return 0, 0
    
    # Build dependency graph
    G = build_dependency_graph(all_content_items)
    
    # Get subgraph of only the filtered items
    filtered_ids = [item['content_id'] for item in filtered_items]
    subgraph = G.subgraph(filtered_ids)
    
    # Determine generation order
    generation_order = get_generation_order(subgraph)
    
    # Limit to max_items if specified
    if max_items and len(generation_order) > max_items:
        generation_order = generation_order[:max_items]
    
    logger.info(f"Will generate {len(generation_order)} items in dependency order")
    
    # Generate content for each item in order
    success_count = 0
    failure_count = 0
    
    for i, content_id in enumerate(generation_order):
        logger.info(f"Generating item {i+1}/{len(generation_order)}: {content_id}")
        
        # Check if dependencies are met
        dependencies_met = True
        if not force:
            for pred in G.predecessors(content_id):
                pred_data = G.nodes[pred]['data']
                if pred_data.get('status') != 'Completed':
                    logger.warning(f"Dependency {pred} for {content_id} is not completed (status: {pred_data.get('status')})")
                    dependencies_met = False
        
        if not dependencies_met:
            logger.error(f"Dependencies not met for {content_id}. Use --force to ignore dependencies.")
            failure_count += 1
            continue
        
        try:
            # Generate content
            result = generate_content_for_id(content_id, model, temperature, force=True)
            
            if result:
                success_count += 1
                logger.info(f"Successfully generated content for {content_id}")
            else:
                failure_count += 1
                logger.error(f"Failed to generate content for {content_id}")
            
            # Add delay if specified
            if delay > 0 and i < len(generation_order) - 1:
                logger.info(f"Waiting {delay} seconds before next generation...")
                time.sleep(delay)
                
        except Exception as e:
            failure_count += 1
            logger.error(f"Error generating content for {content_id}: {str(e)}")
    
    return success_count, failure_count

def reset_content_status(content_ids: Optional[List[str]] = None,
                        section: Optional[str] = None,
                        all_items: bool = False) -> int:
    """Reset content status to 'Not Started'.
    
    Args:
        content_ids: List of content IDs to reset
        section: Reset all content in a section
        all_items: Reset all content items
        
    Returns:
        Number of items reset
    """
    # Check Supabase connection
    if not is_connected():
        logger.error("Not connected to Supabase")
        return 0
    
    # Get content items
    content_items = get_content_inventory()
    if not content_items:
        logger.error("No content items found in inventory")
        return 0
    
    # Apply filters
    filtered_items = content_items
    
    if content_ids:
        filtered_items = [item for item in filtered_items if item.get('content_id') in content_ids]
    
    if section:
        filtered_items = [item for item in filtered_items if item.get('section') == section]
    
    if not all_items and not content_ids and not section:
        logger.error("No filter specified. Use --content-ids, --section, or --all")
        return 0
    
    # Reset status for each item
    reset_count = 0
    for item in filtered_items:
        content_id = item['content_id']
        update_content_status(content_id, "Not Started", {
            "reset_time": datetime.now().isoformat()
        })
        logger.info(f"Reset status for content ID {content_id} to Not Started")
        reset_count += 1
    
    return reset_count

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate content in batch with improved dependency handling")
    
    # Content selection options
    selection_group = parser.add_argument_group("Content Selection")
    selection_group.add_argument("--status", help="Filter by status (e.g., 'Not Started', 'Failed')")
    selection_group.add_argument("--content-ids", help="Comma-separated list of content IDs")
    selection_group.add_argument("--section", help="Filter by section")
    
    # Generation options
    generation_group = parser.add_argument_group("Generation Options")
    generation_group.add_argument("--model", default="gemini-1.5-flash", help="Model to use for generation")
    generation_group.add_argument("--temperature", type=float, default=0.7, help="Temperature for generation")
    generation_group.add_argument("--max-items", type=int, help="Maximum number of items to generate")
    generation_group.add_argument("--force", action="store_true", help="Force generation even if dependencies aren't met")
    generation_group.add_argument("--retry-failed", action="store_true", help="Retry previously failed items")
    generation_group.add_argument("--delay", type=int, default=0, help="Delay between generations in seconds")
    
    # Reset options
    reset_group = parser.add_argument_group("Reset Options")
    reset_group.add_argument("--reset", action="store_true", help="Reset content status to 'Not Started'")
    reset_group.add_argument("--reset-all", action="store_true", help="Reset all content items")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Process content IDs
    content_ids = None
    if args.content_ids:
        content_ids = [cid.strip() for cid in args.content_ids.split(',')]
    
    # Handle reset
    if args.reset or args.reset_all:
        reset_count = reset_content_status(content_ids, args.section, args.reset_all)
        logger.info(f"Reset {reset_count} content items")
        return
    
    # Generate content
    success_count, failure_count = generate_content_batch(
        status=args.status,
        content_ids=content_ids,
        section=args.section,
        model=args.model,
        temperature=args.temperature,
        max_items=args.max_items,
        force=args.force,
        retry_failed=args.retry_failed,
        delay=args.delay
    )
    
    logger.info(f"Generation complete: {success_count} succeeded, {failure_count} failed")

if __name__ == "__main__":
    main()
