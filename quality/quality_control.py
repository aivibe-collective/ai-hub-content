#!/usr/bin/env python3
"""
Quality Control for AI Hub Content Creation System.

This script implements content quality thresholds and automatic regeneration
of content that doesn't meet quality standards.
"""

import os
import sys
import glob
import json
import logging
import argparse
import time
from typing import Dict, List, Optional, Tuple
import pandas as pd
from datetime import datetime

# Import our custom modules
from supabase_client import (
    is_connected, get_content_inventory, update_content_status,
    get_content_item, update_content_item
)
from content_workflow_supabase import generate_content_for_id
from content_evaluation import ContentEvaluation

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QualityControl:
    """Quality control class for content generation."""
    
    def __init__(self, thresholds: Dict[str, float] = None):
        """Initialize quality control.
        
        Args:
            thresholds: Dictionary of quality thresholds
        """
        # Default thresholds
        self.thresholds = {
            'average_score': 3.5,
            'accuracy_score': 3.0,
            'relevance_score': 3.0,
            'engagement_score': 3.0,
            'mission_alignment_score': 3.0,
            'source_quality_score': 3.0,
            'min_word_count': 1000,
            'min_source_count': 3
        }
        
        # Update with provided thresholds
        if thresholds:
            self.thresholds.update(thresholds)
    
    def evaluate_content(self, content_path: str) -> Tuple[bool, Dict]:
        """Evaluate content quality.
        
        Args:
            content_path: Path to content file
            
        Returns:
            Tuple of (passes_thresholds, evaluation_results)
        """
        # Check if file exists
        if not os.path.exists(content_path):
            logger.error(f"Content file not found: {content_path}")
            return False, {}
        
        # Evaluate content
        evaluation = ContentEvaluation(content_path)
        results = evaluation.evaluate()
        
        # Check if content meets thresholds
        passes_thresholds = True
        failures = []
        
        # Check scores
        for score_type in ['average_score', 'accuracy_score', 'relevance_score', 
                          'engagement_score', 'mission_alignment_score', 'source_quality_score']:
            if score_type in self.thresholds and score_type in results['scores']:
                if results['scores'][score_type] < self.thresholds[score_type]:
                    passes_thresholds = False
                    failures.append(f"{score_type} below threshold: {results['scores'][score_type]} < {self.thresholds[score_type]}")
        
        # Check word count
        if 'min_word_count' in self.thresholds and 'word_count' in results:
            if results['word_count'] < self.thresholds['min_word_count']:
                passes_thresholds = False
                failures.append(f"Word count below threshold: {results['word_count']} < {self.thresholds['min_word_count']}")
        
        # Check source count
        if 'min_source_count' in self.thresholds and 'source_count' in results:
            if results['source_count'] < self.thresholds['min_source_count']:
                passes_thresholds = False
                failures.append(f"Source count below threshold: {results['source_count']} < {self.thresholds['min_source_count']}")
        
        # Add failures to results
        results['passes_thresholds'] = passes_thresholds
        results['failures'] = failures
        
        return passes_thresholds, results
    
    def check_and_regenerate(self, content_id: str, model: str = "gemini-1.5-flash", 
                           temperature: float = 0.7, max_attempts: int = 3, 
                           delay: int = 60, force: bool = False) -> Tuple[bool, Dict]:
        """Check content quality and regenerate if needed.
        
        Args:
            content_id: Content ID to check
            model: Model to use for regeneration
            temperature: Temperature for regeneration
            max_attempts: Maximum number of regeneration attempts
            delay: Delay between attempts in seconds
            force: Whether to force regeneration even if content passes thresholds
            
        Returns:
            Tuple of (success, final_evaluation)
        """
        # Check Supabase connection
        if not is_connected():
            logger.error("Not connected to Supabase")
            return False, {}
        
        # Get content item
        content_item = get_content_item(content_id)
        if not content_item:
            logger.error(f"Content item {content_id} not found")
            return False, {}
        
        # Check if content exists
        content_path = os.path.join('generated_content', f"{content_id}.md")
        if not os.path.exists(content_path):
            logger.warning(f"Content file not found: {content_path}")
            if not force:
                logger.info("Generating content for the first time")
                success = generate_content_for_id(content_id, model, temperature, force=True)
                if not success:
                    logger.error(f"Failed to generate content for {content_id}")
                    return False, {}
            else:
                logger.error(f"Content file not found and force is True")
                return False, {}
        
        # Evaluate initial content
        passes_thresholds, evaluation = self.evaluate_content(content_path)
        
        # If content passes thresholds and not forcing regeneration, return
        if passes_thresholds and not force:
            logger.info(f"Content {content_id} passes quality thresholds")
            return True, evaluation
        
        # Log quality issues
        if not passes_thresholds:
            logger.warning(f"Content {content_id} fails quality thresholds:")
            for failure in evaluation['failures']:
                logger.warning(f"  - {failure}")
        
        # Regenerate content
        attempt = 1
        best_evaluation = evaluation
        best_score = evaluation['scores'].get('average_score', 0)
        
        while attempt <= max_attempts:
            logger.info(f"Regeneration attempt {attempt}/{max_attempts} for {content_id}")
            
            # Update content status
            update_content_status(content_id, "Regenerating", {
                "attempt": attempt,
                "max_attempts": max_attempts,
                "previous_score": best_score,
                "regeneration_time": datetime.now().isoformat()
            })
            
            # Try a different temperature for variety
            adjusted_temperature = min(0.9, temperature + (attempt * 0.1))
            
            # Generate content
            success = generate_content_for_id(content_id, model, adjusted_temperature, force=True)
            
            if not success:
                logger.error(f"Failed to regenerate content for {content_id} (attempt {attempt})")
                attempt += 1
                
                if delay > 0:
                    logger.info(f"Waiting {delay} seconds before next attempt...")
                    time.sleep(delay)
                
                continue
            
            # Evaluate regenerated content
            passes_thresholds, new_evaluation = self.evaluate_content(content_path)
            new_score = new_evaluation['scores'].get('average_score', 0)
            
            logger.info(f"Regenerated content score: {new_score:.2f} (previous best: {best_score:.2f})")
            
            # Keep track of best version
            if new_score > best_score:
                best_evaluation = new_evaluation
                best_score = new_score
                
                # If content now passes thresholds, we're done
                if passes_thresholds:
                    logger.info(f"Content {content_id} now passes quality thresholds (score: {best_score:.2f})")
                    
                    # Update content status
                    update_content_status(content_id, "Completed", {
                        "regeneration_attempts": attempt,
                        "final_score": best_score,
                        "quality_rating": best_evaluation['quality_rating']
                    })
                    
                    return True, best_evaluation
            
            # Next attempt
            attempt += 1
            
            if delay > 0 and attempt <= max_attempts:
                logger.info(f"Waiting {delay} seconds before next attempt...")
                time.sleep(delay)
        
        # After all attempts, update status based on best version
        if best_score >= self.thresholds['average_score']:
            logger.info(f"Content {content_id} meets minimum quality threshold after {max_attempts} attempts (score: {best_score:.2f})")
            
            # Update content status
            update_content_status(content_id, "Completed", {
                "regeneration_attempts": max_attempts,
                "final_score": best_score,
                "quality_rating": best_evaluation['quality_rating']
            })
            
            return True, best_evaluation
        else:
            logger.warning(f"Content {content_id} still fails quality thresholds after {max_attempts} attempts (best score: {best_score:.2f})")
            
            # Update content status
            update_content_status(content_id, "Quality Check Failed", {
                "regeneration_attempts": max_attempts,
                "best_score": best_score,
                "failures": best_evaluation['failures']
            })
            
            return False, best_evaluation
    
    def batch_quality_check(self, content_ids: Optional[List[str]] = None, 
                          status: Optional[str] = None,
                          section: Optional[str] = None,
                          model: str = "gemini-1.5-flash",
                          temperature: float = 0.7,
                          max_attempts: int = 3,
                          delay: int = 60,
                          force: bool = False) -> Dict[str, Dict]:
        """Batch check and regenerate content.
        
        Args:
            content_ids: List of content IDs to check
            status: Filter by status
            section: Filter by section
            model: Model to use for regeneration
            temperature: Temperature for regeneration
            max_attempts: Maximum number of regeneration attempts
            delay: Delay between attempts in seconds
            force: Whether to force regeneration even if content passes thresholds
            
        Returns:
            Dictionary of results by content ID
        """
        # Check Supabase connection
        if not is_connected():
            logger.error("Not connected to Supabase")
            return {}
        
        # Get content items
        content_items = get_content_inventory()
        if not content_items:
            logger.error("No content items found in inventory")
            return {}
        
        # Apply filters
        filtered_items = content_items
        
        if content_ids:
            filtered_items = [item for item in filtered_items if item.get('content_id') in content_ids]
        
        if status:
            filtered_items = [item for item in filtered_items if item.get('status') == status]
        
        if section:
            filtered_items = [item for item in filtered_items if item.get('section') == section]
        
        if not filtered_items:
            logger.info(f"No content items match the criteria (status={status}, content_ids={content_ids}, section={section})")
            return {}
        
        # Check and regenerate each item
        results = {}
        
        for item in filtered_items:
            content_id = item['content_id']
            title = item.get('title', content_id)
            
            logger.info(f"Checking quality for: {title} ({content_id})")
            
            success, evaluation = self.check_and_regenerate(
                content_id=content_id,
                model=model,
                temperature=temperature,
                max_attempts=max_attempts,
                delay=delay,
                force=force
            )
            
            results[content_id] = {
                'title': title,
                'success': success,
                'evaluation': evaluation
            }
        
        return results
    
    def generate_quality_report(self, results: Dict[str, Dict]) -> str:
        """Generate HTML quality report.
        
        Args:
            results: Dictionary of quality check results
            
        Returns:
            HTML report
        """
        if not results:
            return "<h1>No results to report</h1>"
        
        # Count successes and failures
        success_count = sum(1 for r in results.values() if r['success'])
        failure_count = len(results) - success_count
        
        # Create HTML report
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Quality Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .success {{ background-color: #dff0d8; }}
        .failure {{ background-color: #f2dede; }}
        .metric-card {{ background-color: #f0f8ff; border-radius: 5px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 24px; font-weight: bold; margin: 10px 0; }}
        .metric-label {{ font-size: 14px; color: #666; }}
        .container {{ display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 20px; }}
        .card {{ flex: 1; min-width: 200px; }}
    </style>
</head>
<body>
    <h1>Content Quality Report</h1>
    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="container">
        <div class="card metric-card">
            <div class="metric-label">Total Content Items</div>
            <div class="metric-value">{len(results)}</div>
        </div>
        <div class="card metric-card">
            <div class="metric-label">Passed Quality Check</div>
            <div class="metric-value">{success_count}</div>
        </div>
        <div class="card metric-card">
            <div class="metric-label">Failed Quality Check</div>
            <div class="metric-value">{failure_count}</div>
        </div>
        <div class="card metric-card">
            <div class="metric-label">Success Rate</div>
            <div class="metric-value">{success_count / len(results):.1%}</div>
        </div>
    </div>
    
    <h2>Quality Thresholds</h2>
    <table>
        <tr>
            <th>Metric</th>
            <th>Threshold</th>
        </tr>
"""
        
        # Add threshold rows
        for metric, threshold in self.thresholds.items():
            html += f"""
        <tr>
            <td>{metric.replace('_', ' ').title()}</td>
            <td>{threshold}</td>
        </tr>"""
        
        html += """
    </table>
    
    <h2>Individual Results</h2>
    <table>
        <tr>
            <th>Content ID</th>
            <th>Title</th>
            <th>Status</th>
            <th>Average Score</th>
            <th>Quality Rating</th>
            <th>Word Count</th>
            <th>Source Count</th>
            <th>Issues</th>
        </tr>
"""
        
        # Add individual result rows
        for content_id, result in results.items():
            evaluation = result.get('evaluation', {})
            scores = evaluation.get('scores', {})
            
            row_class = "success" if result['success'] else "failure"
            
            html += f"""
        <tr class="{row_class}">
            <td>{content_id}</td>
            <td>{result['title']}</td>
            <td>{"Passed" if result['success'] else "Failed"}</td>
            <td>{scores.get('average', 0):.2f}</td>
            <td>{evaluation.get('quality_rating', 'N/A')}</td>
            <td>{evaluation.get('word_count', 0)}</td>
            <td>{evaluation.get('source_count', 0)}</td>
            <td>"""
            
            if 'failures' in evaluation and evaluation['failures']:
                for failure in evaluation['failures']:
                    html += f"{failure}<br>"
            else:
                html += "None"
            
            html += """</td>
        </tr>"""
        
        html += """
    </table>
</body>
</html>
"""
        
        return html


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Content Quality Control")
    
    # Content selection
    selection_group = parser.add_argument_group("Content Selection")
    selection_group.add_argument("--content-ids", help="Comma-separated list of content IDs to check")
    selection_group.add_argument("--status", default="Completed", help="Filter by status (default: Completed)")
    selection_group.add_argument("--section", help="Filter by section")
    
    # Quality thresholds
    threshold_group = parser.add_argument_group("Quality Thresholds")
    threshold_group.add_argument("--min-average-score", type=float, default=3.5, help="Minimum average score")
    threshold_group.add_argument("--min-accuracy-score", type=float, default=3.0, help="Minimum accuracy score")
    threshold_group.add_argument("--min-relevance-score", type=float, default=3.0, help="Minimum relevance score")
    threshold_group.add_argument("--min-engagement-score", type=float, default=3.0, help="Minimum engagement score")
    threshold_group.add_argument("--min-mission-alignment-score", type=float, default=3.0, help="Minimum mission alignment score")
    threshold_group.add_argument("--min-source-quality-score", type=float, default=3.0, help="Minimum source quality score")
    threshold_group.add_argument("--min-word-count", type=int, default=1000, help="Minimum word count")
    threshold_group.add_argument("--min-source-count", type=int, default=3, help="Minimum source count")
    
    # Regeneration options
    regen_group = parser.add_argument_group("Regeneration Options")
    regen_group.add_argument("--model", default="gemini-1.5-flash", help="Model to use for regeneration")
    regen_group.add_argument("--temperature", type=float, default=0.7, help="Temperature for regeneration")
    regen_group.add_argument("--max-attempts", type=int, default=3, help="Maximum number of regeneration attempts")
    regen_group.add_argument("--delay", type=int, default=60, help="Delay between attempts in seconds")
    regen_group.add_argument("--force", action="store_true", help="Force regeneration even if content passes thresholds")
    
    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument("--report", help="Path to save HTML report")
    
    args = parser.parse_args()
    
    # Parse content IDs
    content_ids = None
    if args.content_ids:
        content_ids = [cid.strip() for cid in args.content_ids.split(',')]
    
    # Create quality thresholds
    thresholds = {
        'average_score': args.min_average_score,
        'accuracy_score': args.min_accuracy_score,
        'relevance_score': args.min_relevance_score,
        'engagement_score': args.min_engagement_score,
        'mission_alignment_score': args.min_mission_alignment_score,
        'source_quality_score': args.min_source_quality_score,
        'min_word_count': args.min_word_count,
        'min_source_count': args.min_source_count
    }
    
    # Create quality control
    qc = QualityControl(thresholds)
    
    # Run batch quality check
    results = qc.batch_quality_check(
        content_ids=content_ids,
        status=args.status,
        section=args.section,
        model=args.model,
        temperature=args.temperature,
        max_attempts=args.max_attempts,
        delay=args.delay,
        force=args.force
    )
    
    # Generate report
    if results:
        report_html = qc.generate_quality_report(results)
        
        if args.report:
            with open(args.report, 'w') as f:
                f.write(report_html)
            logger.info(f"Report saved to {args.report}")
        
        # Print summary
        success_count = sum(1 for r in results.values() if r['success'])
        logger.info(f"Quality check complete: {success_count}/{len(results)} passed")
    else:
        logger.warning("No content items were checked")

if __name__ == "__main__":
    main()
