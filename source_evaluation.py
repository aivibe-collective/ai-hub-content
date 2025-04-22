#!/usr/bin/env python3
"""
Source Evaluation Module using the CRAAP framework.

This module evaluates sources based on the CRAAP criteria:
- Currency: How recent is the information?
- Relevance: How important is the information for your needs?
- Authority: Who is the creator/author/publisher?
- Accuracy: How reliable, truthful, and correct is the content?
- Purpose: Why does the information exist?
"""

import re
import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

@dataclass
class Source:
    """Represents a source with metadata for evaluation."""
    citation: str
    year: Optional[int] = None
    authors: List[str] = None
    title: str = ""
    publication: str = ""
    url: str = ""
    doi: str = ""
    source_type: str = ""  # academic, industry, news, etc.
    
    def __post_init__(self):
        """Extract additional metadata from citation if not provided."""
        if not self.year and self.citation:
            # Try to extract year from citation
            year_match = re.search(r'\((\d{4})\)', self.citation)
            if year_match:
                self.year = int(year_match.group(1))
        
        if not self.authors and self.citation:
            # Try to extract authors from citation
            author_match = re.match(r'^\[(.*?)\]', self.citation)
            if author_match:
                author_part = author_match.group(1)
                self.authors = [author.strip() for author in author_part.split(',')]
        
        if not self.title and self.citation:
            # Try to extract title from citation
            title_match = re.search(r'\. \*?(.*?)\*?\.', self.citation)
            if title_match:
                self.title = title_match.group(1).strip()
        
        if not self.publication and self.citation:
            # Try to extract publication from citation
            pub_match = re.search(r'\*([^*]+)\*', self.citation)
            if pub_match:
                self.publication = pub_match.group(1).strip()
        
        if not self.url and self.citation:
            # Try to extract URL from citation
            url_match = re.search(r'(https?://\S+)', self.citation)
            if url_match:
                self.url = url_match.group(1).strip()
        
        if not self.doi and self.citation:
            # Try to extract DOI from citation
            doi_match = re.search(r'https://doi.org/([\S]+)', self.citation)
            if doi_match:
                self.doi = doi_match.group(1).strip()

@dataclass
class CRAAPEvaluation:
    """Evaluation of a source using the CRAAP framework."""
    source: Source
    currency_score: int = 0  # 1-5 scale
    relevance_score: int = 0  # 1-5 scale
    authority_score: int = 0  # 1-5 scale
    accuracy_score: int = 0  # 1-5 scale
    purpose_score: int = 0  # 1-5 scale
    notes: Dict[str, str] = None
    
    def __post_init__(self):
        """Initialize notes dictionary if not provided."""
        if self.notes is None:
            self.notes = {
                "currency": "",
                "relevance": "",
                "authority": "",
                "accuracy": "",
                "purpose": ""
            }
    
    @property
    def total_score(self) -> int:
        """Calculate the total CRAAP score."""
        return (self.currency_score + self.relevance_score + 
                self.authority_score + self.accuracy_score + 
                self.purpose_score)
    
    @property
    def average_score(self) -> float:
        """Calculate the average CRAAP score."""
        return self.total_score / 5
    
    @property
    def quality_rating(self) -> str:
        """Get a qualitative rating based on the average score."""
        avg = self.average_score
        if avg >= 4.5:
            return "Excellent"
        elif avg >= 4.0:
            return "Very Good"
        elif avg >= 3.0:
            return "Good"
        elif avg >= 2.0:
            return "Fair"
        else:
            return "Poor"
    
    def to_dict(self) -> Dict:
        """Convert the evaluation to a dictionary."""
        return {
            "source": {
                "citation": self.source.citation,
                "year": self.source.year,
                "authors": self.source.authors,
                "title": self.source.title,
                "publication": self.source.publication,
                "url": self.source.url,
                "doi": self.source.doi,
                "source_type": self.source.source_type
            },
            "scores": {
                "currency": self.currency_score,
                "relevance": self.relevance_score,
                "authority": self.authority_score,
                "accuracy": self.accuracy_score,
                "purpose": self.purpose_score,
                "total": self.total_score,
                "average": self.average_score,
                "rating": self.quality_rating
            },
            "notes": self.notes
        }


def evaluate_currency(source: Source) -> Tuple[int, str]:
    """
    Evaluate the currency of a source.
    
    Args:
        source: The source to evaluate
        
    Returns:
        Tuple of (score, notes)
    """
    current_year = datetime.datetime.now().year
    
    if not source.year:
        return 1, "Year unknown, cannot evaluate currency"
    
    age = current_year - source.year
    
    # Different fields have different standards for currency
    if source.source_type == "technology" or source.source_type == "ai":
        # Technology and AI move quickly
        if age <= 1:
            return 5, "Very recent, excellent currency for technology/AI"
        elif age <= 3:
            return 4, "Recent, good currency for technology/AI"
        elif age <= 5:
            return 3, "Moderately recent, acceptable for some technology/AI topics"
        elif age <= 10:
            return 2, "Somewhat dated for technology/AI"
        else:
            return 1, "Outdated for technology/AI"
    else:
        # General academic or other sources
        if age <= 2:
            return 5, "Very recent"
        elif age <= 5:
            return 4, "Recent"
        elif age <= 10:
            return 3, "Moderately recent"
        elif age <= 15:
            return 2, "Somewhat dated"
        else:
            return 1, "Older source"


def evaluate_authority(source: Source) -> Tuple[int, str]:
    """
    Evaluate the authority of a source.
    
    Args:
        source: The source to evaluate
        
    Returns:
        Tuple of (score, notes)
    """
    # Check for academic publications
    academic_indicators = [
        "journal", "proceedings", "conference", "university", 
        "ieee", "acm", "springer", "elsevier", "wiley", "sage",
        "oxford", "cambridge", "mit", "harvard", "stanford"
    ]
    
    # Check for reputable organizations
    reputable_orgs = [
        "google", "microsoft", "ibm", "meta", "openai", "anthropic",
        "deepmind", "amazon", "apple", "nvidia", "intel", "mit", 
        "stanford", "harvard", "berkeley", "oxford", "cambridge"
    ]
    
    # Initialize score
    score = 3  # Default to middle score
    notes = []
    
    # Check publication venue
    if source.publication:
        pub_lower = source.publication.lower()
        for indicator in academic_indicators:
            if indicator in pub_lower:
                score += 1
                notes.append(f"Published in academic venue: {source.publication}")
                break
    
    # Check authors and affiliations
    if source.authors:
        for org in reputable_orgs:
            author_str = " ".join(source.authors).lower()
            if org in author_str:
                score += 1
                notes.append(f"Author(s) affiliated with reputable organization: {org}")
                break
    
    # Check for DOI (indicates peer-reviewed academic work)
    if source.doi:
        score += 1
        notes.append("Has DOI, likely peer-reviewed academic work")
    
    # Cap score at 5
    score = min(score, 5)
    
    # If we have no information, reduce score
    if not source.publication and not source.authors and not source.doi:
        score = 1
        notes = ["Insufficient information to evaluate authority"]
    
    return score, "; ".join(notes)


def evaluate_source(source: Source, topic: str = "", keywords: List[str] = None) -> CRAAPEvaluation:
    """
    Evaluate a source using the CRAAP framework.
    
    Args:
        source: The source to evaluate
        topic: The topic the source should be relevant to
        keywords: List of keywords the source should ideally contain
        
    Returns:
        A CRAAPEvaluation object
    """
    # Initialize evaluation
    evaluation = CRAAPEvaluation(source=source)
    
    # Evaluate Currency
    evaluation.currency_score, evaluation.notes["currency"] = evaluate_currency(source)
    
    # Evaluate Authority
    evaluation.authority_score, evaluation.notes["authority"] = evaluate_authority(source)
    
    # For Relevance, Accuracy, and Purpose, we would need more context or content analysis
    # For now, set default values
    evaluation.relevance_score = 3
    evaluation.notes["relevance"] = "Relevance evaluation requires content analysis"
    
    evaluation.accuracy_score = 3
    evaluation.notes["accuracy"] = "Accuracy evaluation requires content analysis"
    
    evaluation.purpose_score = 3
    evaluation.notes["purpose"] = "Purpose evaluation requires content analysis"
    
    return evaluation


def evaluate_sources(sources: List[Source], topic: str = "", keywords: List[str] = None) -> List[CRAAPEvaluation]:
    """
    Evaluate multiple sources using the CRAAP framework.
    
    Args:
        sources: List of sources to evaluate
        topic: The topic the sources should be relevant to
        keywords: List of keywords the sources should ideally contain
        
    Returns:
        List of CRAAPEvaluation objects
    """
    return [evaluate_source(source, topic, keywords) for source in sources]


def parse_sources_from_markdown(markdown_content: str) -> List[Source]:
    """
    Parse sources from markdown content.
    
    Args:
        markdown_content: Markdown content containing sources
        
    Returns:
        List of Source objects
    """
    sources = []
    
    # Look for a Sources section
    sources_section_match = re.search(r'## Sources\s+(.*?)(?=##|\Z)', markdown_content, re.DOTALL)
    
    if not sources_section_match:
        return sources
    
    sources_text = sources_section_match.group(1).strip()
    
    # Extract individual sources (assuming each source is on its own line)
    source_lines = [line.strip() for line in sources_text.split('\n') if line.strip()]
    
    for line in source_lines:
        if line and line[0] == '[':
            sources.append(Source(citation=line))
    
    return sources


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python source_evaluation.py <markdown_file>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        content = f.read()
    
    sources = parse_sources_from_markdown(content)
    print(f"Found {len(sources)} sources")
    
    evaluations = evaluate_sources(sources)
    
    print("\nSource Evaluations:")
    for i, eval in enumerate(evaluations):
        print(f"\nSource {i+1}: {eval.source.citation[:100]}...")
        print(f"  Currency: {eval.currency_score}/5 - {eval.notes['currency']}")
        print(f"  Authority: {eval.authority_score}/5 - {eval.notes['authority']}")
        print(f"  Overall Rating: {eval.quality_rating} ({eval.average_score:.1f}/5)")
