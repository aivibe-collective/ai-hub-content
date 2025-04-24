#!/usr/bin/env python3
"""
Script to test the Google Generative AI API integration.
"""

import os
import argparse
import google.generativeai as genai
from dotenv import load_dotenv

def setup_genai():
    """Set up the Google Generative AI client."""
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.environ.get('GOOGLE_GENAI_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_GENAI_API_KEY environment variable not found")
    
    # Configure the client
    genai.configure(api_key=api_key)
    
    return genai

def generate_content(prompt, model_name="gemini-1.5-flash"):
    """Generate content using Google Generative AI."""
    # Set up the client
    genai = setup_genai()
    
    # Get the model
    model = genai.GenerativeModel(model_name)
    
    # Generate content
    response = model.generate_content(prompt)
    
    return response.text

def main():
    """Main function to test Google Generative AI API."""
    parser = argparse.ArgumentParser(description="Test Google Generative AI API integration.")
    parser.add_argument("--prompt", default="Write a short introduction to generative AI.", help="Prompt for content generation")
    parser.add_argument("--model", default="gemini-1.5-flash", help="Model name")
    parser.add_argument("--output", default="google_ai_output.md", help="Output file")
    
    args = parser.parse_args()
    
    try:
        # Generate content
        print(f"Generating content with model: {args.model}")
        print(f"Prompt: {args.prompt}")
        
        content = generate_content(args.prompt, args.model)
        
        # Save content to file
        with open(args.output, 'w') as f:
            f.write(content)
        
        print(f"Content generated and saved to {args.output}")
        
        # Display the generated content
        print("\nGenerated Content:")
        print("=" * 80)
        print(content)
        print("=" * 80)
        
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
