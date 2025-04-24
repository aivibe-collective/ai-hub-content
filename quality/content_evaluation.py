#!/usr/bin/env python3
"""
Content Evaluation Framework for AI Hub Content.

This script evaluates the quality of generated content based on various criteria:
- Accuracy: Factual correctness and technical accuracy
- Relevance: Alignment with target audience and learning objectives
- Engagement: Writing quality, clarity, and engagement
- Mission Alignment: Integration of mission pillars
- Source Quality: Quality and integration of sources
"""

import os
import sys
import re
import argparse
import logging
import json
from typing import Dict, List, Optional, Tuple
import markdown
from bs4 import BeautifulSoup

# Import our custom modules
from source_evaluation import parse_sources_from_markdown, evaluate_sources

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContentEvaluation:
    """Content evaluation class."""
    
    def __init__(self, content_path: str, content_id: Optional[str] = None):
        """Initialize with content path.
        
        Args:
            content_path: Path to the content file
            content_id: Content ID (if not provided, will try to extract from filename)
        """
        self.content_path = content_path
        self.content_id = content_id or self._extract_content_id(content_path)
        self.content = self._load_content()
        self.html = markdown.markdown(self.content)
        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.sources = parse_sources_from_markdown(self.content)
        self.source_evaluations = evaluate_sources(self.sources)
        
        # Initialize scores
        self.scores = {
            "accuracy": 0,
            "relevance": 0,
            "engagement": 0,
            "mission_alignment": 0,
            "source_quality": 0,
            "total": 0,
            "average": 0
        }
        
        # Initialize notes
        self.notes = {
            "accuracy": "",
            "relevance": "",
            "engagement": "",
            "mission_alignment": "",
            "source_quality": "",
            "general": ""
        }
    
    def _extract_content_id(self, path: str) -> str:
        """Extract content ID from filename.
        
        Args:
            path: Path to content file
            
        Returns:
            Content ID
        """
        filename = os.path.basename(path)
        name_without_ext = os.path.splitext(filename)[0]
        return name_without_ext
    
    def _load_content(self) -> str:
        """Load content from file.
        
        Returns:
            Content as string
        """
        with open(self.content_path, 'r') as f:
            return f.read()
    
    def evaluate_source_quality(self) -> Tuple[int, str]:
        """Evaluate source quality.
        
        Returns:
            Tuple of (score, notes)
        """
        if not self.sources:
            return 1, "No sources found"
        
        # Calculate average source quality
        avg_currency = sum(eval.currency_score for eval in self.source_evaluations) / len(self.source_evaluations)
        avg_authority = sum(eval.authority_score for eval in self.source_evaluations) / len(self.source_evaluations)
        avg_total = sum(eval.average_score for eval in self.source_evaluations) / len(self.source_evaluations)
        
        # Check source integration
        source_citations = re.findall(r'\[\w+\d+\w*\]', self.content)
        unique_citations = set(source_citations)
        
        # Calculate score based on source quality and integration
        score = 3  # Default middle score
        notes = []
        
        # Source quality
        if avg_total >= 4.0:
            score += 1
            notes.append("High-quality sources")
        elif avg_total <= 2.0:
            score -= 1
            notes.append("Low-quality sources")
        
        # Source recency
        if avg_currency >= 4.0:
            score += 0.5
            notes.append("Recent sources")
        elif avg_currency <= 2.0:
            score -= 0.5
            notes.append("Outdated sources")
        
        # Source authority
        if avg_authority >= 4.0:
            score += 0.5
            notes.append("Authoritative sources")
        elif avg_authority <= 2.0:
            score -= 0.5
            notes.append("Low-authority sources")
        
        # Source integration
        if len(unique_citations) >= 3:
            score += 0.5
            notes.append(f"Good source integration ({len(unique_citations)} unique citations)")
        elif len(unique_citations) <= 1:
            score -= 0.5
            notes.append("Poor source integration")
        
        # Cap score at 1-5
        score = max(1, min(5, round(score)))
        
        return score, "; ".join(notes)
    
    def evaluate_mission_alignment(self) -> Tuple[int, str]:
        """Evaluate mission alignment.
        
        Returns:
            Tuple of (score, notes)
        """
        # Mission pillars to look for
        pillars = {
            "responsible_ai": ["responsible ai", "ethical", "ethics", "bias", "fairness", "transparency", "accountability"],
            "sustainability": ["sustainability", "sustainable", "environmental", "carbon", "energy", "climate"],
            "inclusion": ["inclusion", "inclusive", "diversity", "diverse", "accessibility", "accessible", "global"]
        }
        
        # Check for mission pillar mentions
        pillar_mentions = {}
        for pillar, keywords in pillars.items():
            mentions = 0
            for keyword in keywords:
                mentions += len(re.findall(r'\b' + keyword + r'\b', self.content.lower()))
            pillar_mentions[pillar] = mentions
        
        # Calculate score based on mission pillar integration
        score = 3  # Default middle score
        notes = []
        
        # Check if any pillars are mentioned
        total_mentions = sum(pillar_mentions.values())
        if total_mentions == 0:
            score = 1
            notes.append("No mission pillars mentioned")
        elif total_mentions >= 10:
            score += 1
            notes.append(f"Strong mission pillar integration ({total_mentions} mentions)")
        
        # Check if all pillars are mentioned
        mentioned_pillars = sum(1 for p, m in pillar_mentions.items() if m > 0)
        if mentioned_pillars == len(pillars):
            score += 1
            notes.append("All mission pillars mentioned")
        elif mentioned_pillars == 0:
            score = 1
            notes.append("No mission pillars mentioned")
        
        # Check for dedicated sections on mission pillars
        section_titles = [h.text.lower() for h in self.soup.find_all(['h1', 'h2', 'h3', 'h4'])]
        pillar_sections = 0
        for title in section_titles:
            for pillar, keywords in pillars.items():
                if any(keyword in title for keyword in keywords):
                    pillar_sections += 1
                    break
        
        if pillar_sections > 0:
            score += 0.5
            notes.append(f"Dedicated sections for mission pillars ({pillar_sections})")
        
        # Cap score at 1-5
        score = max(1, min(5, round(score)))
        
        return score, "; ".join(notes)
    
    def evaluate_engagement(self) -> Tuple[int, str]:
        """Evaluate engagement and writing quality.
        
        Returns:
            Tuple of (score, notes)
        """
        # Basic readability metrics
        word_count = len(re.findall(r'\b\w+\b', self.content))
        sentence_count = len(re.findall(r'[.!?]+', self.content))
        paragraph_count = len(re.findall(r'\n\s*\n', self.content))
        
        # Check for engagement elements
        has_examples = len(re.findall(r'\bexample\b|\bfor instance\b|\bsuch as\b', self.content.lower())) > 0
        has_questions = len(re.findall(r'\?', self.content)) > 5
        has_lists = len(re.findall(r'\n\s*[-*]\s', self.content)) > 3
        has_code = len(re.findall(r'```', self.content)) > 0
        has_images = len(re.findall(r'!\[', self.content)) > 0
        
        # Calculate score based on engagement elements
        score = 3  # Default middle score
        notes = []
        
        # Word count
        if word_count < 500:
            score -= 1
            notes.append(f"Too short ({word_count} words)")
        elif word_count > 2000:
            score += 0.5
            notes.append(f"Good length ({word_count} words)")
        
        # Engagement elements
        engagement_elements = sum([has_examples, has_questions, has_lists, has_code, has_images])
        if engagement_elements >= 4:
            score += 1
            notes.append("Excellent variety of engagement elements")
        elif engagement_elements >= 2:
            score += 0.5
            notes.append("Good variety of engagement elements")
        elif engagement_elements == 0:
            score -= 1
            notes.append("No engagement elements")
        
        # Structure
        if paragraph_count > 10:
            score += 0.5
            notes.append("Well-structured with multiple paragraphs")
        
        # Cap score at 1-5
        score = max(1, min(5, round(score)))
        
        return score, "; ".join(notes)
    
    def evaluate_accuracy(self) -> Tuple[int, str]:
        """Evaluate accuracy.
        
        Note: Full accuracy evaluation requires domain expertise.
        This is a simplified version based on source quality and other heuristics.
        
        Returns:
            Tuple of (score, notes)
        """
        # This is a simplified accuracy evaluation
        # A full evaluation would require domain expertise
        
        # Use source quality as a proxy for accuracy
        source_score, _ = self.evaluate_source_quality()
        
        # Check for hedging language (indicates uncertainty)
        hedging_terms = ["may", "might", "could", "possibly", "perhaps", "seems", "appears"]
        hedging_count = 0
        for term in hedging_terms:
            hedging_count += len(re.findall(r'\b' + term + r'\b', self.content.lower()))
        
        # Calculate score
        score = source_score  # Start with source quality score
        notes = []
        
        # Adjust based on hedging
        if hedging_count > 10:
            score -= 0.5
            notes.append(f"Excessive hedging language ({hedging_count} instances)")
        
        # Check for technical terms
        technical_terms = ["algorithm", "model", "neural", "training", "inference", "parameter", "hyperparameter", "gradient", "backpropagation", "optimization"]
        technical_count = 0
        for term in technical_terms:
            technical_count += len(re.findall(r'\b' + term + r'\b', self.content.lower()))
        
        if technical_count > 10:
            score += 0.5
            notes.append(f"Good use of technical terminology ({technical_count} terms)")
        
        # Cap score at 1-5
        score = max(1, min(5, round(score)))
        
        notes.append("Note: Full accuracy evaluation requires domain expertise")
        
        return score, "; ".join(notes)
    
    def evaluate_relevance(self) -> Tuple[int, str]:
        """Evaluate relevance to target audience.
        
        Note: Full relevance evaluation requires knowledge of the target audience.
        This is a simplified version based on heuristics.
        
        Returns:
            Tuple of (score, notes)
        """
        # This is a simplified relevance evaluation
        # A full evaluation would require knowledge of the target audience
        
        # Extract audience from content ID
        audience = "beginner"  # Default
        if self.content_id and "-BEG-" in self.content_id:
            audience = "beginner"
        elif self.content_id and "-INT-" in self.content_id:
            audience = "intermediate"
        elif self.content_id and "-ADV-" in self.content_id:
            audience = "advanced"
        
        # Check for audience-appropriate language
        if audience == "beginner":
            # Check for explanations of basic terms
            explanations = len(re.findall(r'\bis\s+a\b|\bmeans\b|\brefers to\b', self.content.lower()))
            simple_language = len(re.findall(r'\bsimple\b|\bbasic\b|\bfundamental\b|\bintroduction\b', self.content.lower()))
            
            score = 3  # Default
            notes = []
            
            if explanations > 10:
                score += 1
                notes.append(f"Good explanations of terms for beginners ({explanations} instances)")
            
            if simple_language > 5:
                score += 0.5
                notes.append("Appropriate language for beginners")
            
        elif audience == "intermediate":
            # Check for more advanced concepts but still with explanations
            advanced_concepts = len(re.findall(r'\barchitecture\b|\bimplementation\b|\bframework\b|\bworkflow\b', self.content.lower()))
            practical_examples = len(re.findall(r'\bexample\b|\bcase study\b|\bapplication\b', self.content.lower()))
            
            score = 3  # Default
            notes = []
            
            if advanced_concepts > 5 and practical_examples > 5:
                score += 1
                notes.append("Good balance of concepts and practical examples for intermediate audience")
            
        elif audience == "advanced":
            # Check for technical depth
            technical_depth = len(re.findall(r'\boptimization\b|\barchitecture\b|\bimplementation\b|\balgorithm\b|\bperformance\b', self.content.lower()))
            research_references = len(re.findall(r'\bresearch\b|\bstudy\b|\bpaper\b|\bpublication\b', self.content.lower()))
            
            score = 3  # Default
            notes = []
            
            if technical_depth > 10:
                score += 1
                notes.append("Appropriate technical depth for advanced audience")
            
            if research_references > 5:
                score += 0.5
                notes.append("Good research references for advanced audience")
        
        # Cap score at 1-5
        score = max(1, min(5, round(score)))
        
        notes.append(f"Evaluated for {audience} audience based on content ID")
        
        return score, "; ".join(notes)
    
    def evaluate(self) -> Dict:
        """Evaluate content on all criteria.
        
        Returns:
            Dictionary with evaluation results
        """
        # Evaluate each criterion
        self.scores["source_quality"], self.notes["source_quality"] = self.evaluate_source_quality()
        self.scores["mission_alignment"], self.notes["mission_alignment"] = self.evaluate_mission_alignment()
        self.scores["engagement"], self.notes["engagement"] = self.evaluate_engagement()
        self.scores["accuracy"], self.notes["accuracy"] = self.evaluate_accuracy()
        self.scores["relevance"], self.notes["relevance"] = self.evaluate_relevance()
        
        # Calculate total and average scores
        self.scores["total"] = sum([
            self.scores["accuracy"],
            self.scores["relevance"],
            self.scores["engagement"],
            self.scores["mission_alignment"],
            self.scores["source_quality"]
        ])
        self.scores["average"] = self.scores["total"] / 5
        
        # Determine overall quality rating
        if self.scores["average"] >= 4.5:
            quality_rating = "Excellent"
        elif self.scores["average"] >= 4.0:
            quality_rating = "Very Good"
        elif self.scores["average"] >= 3.0:
            quality_rating = "Good"
        elif self.scores["average"] >= 2.0:
            quality_rating = "Fair"
        else:
            quality_rating = "Poor"
        
        # Compile results
        return {
            "content_id": self.content_id,
            "content_path": self.content_path,
            "scores": self.scores,
            "notes": self.notes,
            "quality_rating": quality_rating,
            "source_count": len(self.sources),
            "word_count": len(re.findall(r'\b\w+\b', self.content))
        }
    
    def print_evaluation(self):
        """Print evaluation results to console."""
        evaluation = self.evaluate()
        
        print(f"\nContent Evaluation for {evaluation['content_id']}")
        print(f"Path: {evaluation['content_path']}")
        print(f"Word Count: {evaluation['word_count']}")
        print(f"Source Count: {evaluation['source_count']}")
        print("\nScores:")
        print(f"  Accuracy: {evaluation['scores']['accuracy']}/5 - {evaluation['notes']['accuracy']}")
        print(f"  Relevance: {evaluation['scores']['relevance']}/5 - {evaluation['notes']['relevance']}")
        print(f"  Engagement: {evaluation['scores']['engagement']}/5 - {evaluation['notes']['engagement']}")
        print(f"  Mission Alignment: {evaluation['scores']['mission_alignment']}/5 - {evaluation['notes']['mission_alignment']}")
        print(f"  Source Quality: {evaluation['scores']['source_quality']}/5 - {evaluation['notes']['source_quality']}")
        print(f"\nOverall Rating: {evaluation['quality_rating']} ({evaluation['scores']['average']:.1f}/5)")
    
    def save_evaluation(self, output_path: Optional[str] = None):
        """Save evaluation results to JSON file.
        
        Args:
            output_path: Path to save evaluation results (default: content_path + .evaluation.json)
        """
        evaluation = self.evaluate()
        
        if not output_path:
            output_path = f"{self.content_path}.evaluation.json"
        
        with open(output_path, 'w') as f:
            json.dump(evaluation, f, indent=2)
        
        logger.info(f"Saved evaluation to {output_path}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Evaluate content quality")
    parser.add_argument("content_path", help="Path to content file")
    parser.add_argument("--content-id", help="Content ID (if not in filename)")
    parser.add_argument("--output", help="Path to save evaluation results")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    evaluation = ContentEvaluation(args.content_path, args.content_id)
    
    if args.json:
        print(json.dumps(evaluation.evaluate(), indent=2))
    else:
        evaluation.print_evaluation()
    
    if args.output:
        evaluation.save_evaluation(args.output)
    else:
        evaluation.save_evaluation()

if __name__ == "__main__":
    main()
