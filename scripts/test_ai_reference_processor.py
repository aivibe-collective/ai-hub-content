#!/usr/bin/env python3
"""
Test the AI Reference Processor.

This script tests the AI Reference Processor by processing a sample reference
and generating references for sample content.
"""

import os
import json
import logging
import argparse
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import our custom modules
from ai_reference_processor import (
    process_reference_with_ai,
    generate_references_for_content,
    format_references_as_markdown
)

def test_process_reference():
    """Test processing a reference with AI."""
    print("\n=== Testing Reference Processing ===\n")
    
    # Sample references to test
    test_references = [
        "Smith, J. (2020). The impact of AI on society. Journal of Technology, 45(2), 123-145. https://doi.org/10.1234/jtech.2020.45.2.123",
        "Johnson, A. B., & Williams, C. D. (2019). Machine learning applications. In Advanced Computing (pp. 78-92). Springer.",
        "Brown et al. The future of robotics. IEEE Conference on Robotics, 2021.",
        "Wikipedia. (2022). Artificial intelligence. Retrieved from https://en.wikipedia.org/wiki/Artificial_intelligence",
        "This is just a text snippet without any structured citation format."
    ]
    
    for i, ref in enumerate(test_references):
        print(f"\nTest Reference {i+1}:")
        print(f"Original: {ref}")
        
        # Process the reference
        processed = process_reference_with_ai(ref)
        
        # Print the results
        print("\nProcessed Reference:")
        print(f"Title: {processed.get('title', 'N/A')}")
        print(f"Authors: {processed.get('authors', 'N/A')}")
        print(f"Publication Date: {processed.get('publication_date', 'N/A')}")
        print(f"Publication Name: {processed.get('publication_name', 'N/A')}")
        print(f"URL: {processed.get('url', 'N/A')}")
        print(f"DOI: {processed.get('doi', 'N/A')}")
        print(f"Reference Type: {processed.get('reference_type', 'N/A')}")
        print(f"Valid Reference: {processed.get('is_valid_reference', False)}")
        print(f"Confidence Score: {processed.get('confidence_score', 0)}")
        print(f"Verification: {json.dumps(processed.get('verification', {}), indent=2)}")
        print(f"APA Citation: {processed.get('apa_citation', 'N/A')}")
        print("\n" + "-"*50)

def test_generate_references():
    """Test generating references for content with AI."""
    print("\n=== Testing Reference Generation ===\n")
    
    # Sample content to test
    sample_content = """
    # Introduction to Artificial Intelligence
    
    Artificial Intelligence (AI) is a field of computer science that focuses on creating machines capable of intelligent behavior. AI systems can perform tasks that typically require human intelligence, such as visual perception, speech recognition, decision-making, and language translation.
    
    ## Types of AI
    
    There are two main types of AI:
    
    1. **Narrow AI**: Designed to perform a specific task, such as voice recognition or image classification.
    2. **General AI**: Capable of performing any intellectual task that a human can do.
    
    ## Applications of AI
    
    AI has numerous applications across various industries:
    
    - **Healthcare**: Diagnosis, drug discovery, personalized medicine
    - **Finance**: Fraud detection, algorithmic trading, risk assessment
    - **Transportation**: Autonomous vehicles, traffic management
    - **Education**: Personalized learning, automated grading
    
    ## Ethical Considerations
    
    As AI becomes more prevalent, several ethical considerations arise:
    
    - Privacy concerns
    - Bias and fairness
    - Job displacement
    - Accountability and transparency
    
    ## Conclusion
    
    AI continues to evolve rapidly, offering tremendous potential benefits while also presenting significant challenges. Understanding both the capabilities and limitations of AI is essential for responsible development and deployment.
    """
    
    # Generate references
    print("Generating references for sample content...")
    references = generate_references_for_content(sample_content, "Artificial Intelligence")
    
    # Print the results
    print(f"\nGenerated {len(references)} references:")
    for i, ref in enumerate(references):
        print(f"\nReference {i+1}:")
        print(f"Title: {ref.get('title', 'N/A')}")
        print(f"Authors: {ref.get('authors', 'N/A')}")
        print(f"Publication Date: {ref.get('publication_date', 'N/A')}")
        print(f"Publication Name: {ref.get('publication_name', 'N/A')}")
        print(f"Reference Type: {ref.get('reference_type', 'N/A')}")
        print(f"Citation Context: {ref.get('citation_context', 'N/A')}")
        print(f"APA Citation: {ref.get('apa_citation', 'N/A')}")
    
    # Format references as Markdown
    markdown = format_references_as_markdown(references)
    
    print("\n=== Formatted References (Markdown) ===\n")
    print(markdown)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the AI Reference Processor.")
    parser.add_argument("--test-process", action="store_true", help="Test processing references")
    parser.add_argument("--test-generate", action="store_true", help="Test generating references")
    parser.add_argument("--test-all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    # If no specific test is selected, run all tests
    if not (args.test_process or args.test_generate) or args.test_all:
        test_process_reference()
        test_generate_references()
    else:
        if args.test_process:
            test_process_reference()
        if args.test_generate:
            test_generate_references()
