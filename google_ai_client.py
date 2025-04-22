#!/usr/bin/env python3
"""
Google Generative AI client module for the Agentic AI Content Creation System.

This module provides a unified interface for interacting with Google's Generative AI API.
It supports both Python and Node.js implementations, with automatic fallback.
"""

import os
import json
import subprocess
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if Google Generative AI package is available
try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False
    print("Warning: google-generativeai package not found. Using Node.js implementation instead.")

class GoogleAIClient:
    """Google Generative AI client class."""

    def __init__(self, api_key=None, model_name="gemini-1.5-flash"):
        """Initialize the Google Generative AI client.

        Args:
            api_key (str, optional): Google Generative AI API key. If not provided,
                                     it will be loaded from the GOOGLE_GENAI_API_KEY environment variable.
            model_name (str, optional): Model name to use. Defaults to "gemini-1.5-flash".
        """
        self.api_key = api_key or os.environ.get('GOOGLE_GENAI_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_GENAI_API_KEY environment variable not found")

        self.model_name = model_name

        # Initialize the Python client if available
        if GOOGLE_AI_AVAILABLE:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)

    def generate_content(self, prompt, temperature=0.7, max_tokens=None):
        """Generate content using Google Generative AI.

        Args:
            prompt (str): The prompt for content generation.
            temperature (float, optional): Temperature for generation. Defaults to 0.7.
            max_tokens (int, optional): Maximum number of tokens to generate. Defaults to None.

        Returns:
            str: The generated content.
        """
        if GOOGLE_AI_AVAILABLE:
            # Use Python client
            generation_config = {}
            if temperature is not None:
                generation_config['temperature'] = temperature
            if max_tokens is not None:
                generation_config['max_output_tokens'] = max_tokens

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.text
        else:
            # Use Node.js client
            return self._generate_with_node(prompt, temperature, max_tokens)

    def _generate_with_node(self, prompt, temperature=0.7, max_tokens=None):
        """Generate content using Google Generative AI Node.js client.

        Args:
            prompt (str): The prompt for content generation.
            temperature (float, optional): Temperature for generation. Defaults to 0.7.
            max_tokens (int, optional): Maximum number of tokens to generate. Defaults to None.

        Returns:
            str: The generated content.
        """
        # Create a temporary file for output
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as temp_file:
            output_file = temp_file.name

        # Build command
        cmd = [
            'node', 'google-ai-test.js',
            f'--prompt={prompt}',
            f'--model={self.model_name}',
            f'--output={output_file}'
        ]

        if temperature is not None:
            cmd.append(f'--temperature={temperature}')

        if max_tokens is not None:
            cmd.append(f'--max_tokens={max_tokens}')

        # Run the Node.js script
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if process.returncode != 0:
            raise Exception(f"Error generating content with Node.js: {process.stderr}")

        # Read the generated content
        with open(output_file, 'r') as f:
            content = f.read()

        # Clean up the temporary file
        os.remove(output_file)

        return content

    def generate_json(self, prompt, schema=None, temperature=0.2):
        """Generate JSON content using Google Generative AI.

        Args:
            prompt (str): The prompt for content generation.
            schema (dict, optional): JSON schema to validate against. Defaults to None.
            temperature (float, optional): Temperature for generation. Defaults to 0.2.

        Returns:
            dict: The generated JSON content.
        """
        # Add instructions for JSON output
        json_prompt = f"{prompt}\n\nReturn your response as a valid JSON object. Do not include any explanations or markdown formatting."

        if schema:
            json_prompt += f"\n\nYour response should conform to the following JSON schema: {json.dumps(schema)}"

        # Generate content
        response_text = self.generate_content(json_prompt, temperature=temperature)

        # Clean up the response if it contains markdown code blocks
        # First, try to extract content between code blocks if present
        if "```json" in response_text and "```" in response_text.split("```json", 1)[1]:
            response_text = response_text.split("```json", 1)[1].split("```", 1)[0]
        elif "```" in response_text and "```" in response_text.split("```", 1)[1]:
            response_text = response_text.split("```", 1)[1].split("```", 1)[0]
        else:
            # Otherwise just remove any markdown code block markers
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "", 1)
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "", 1)
            if response_text.endswith("```"):
                response_text = response_text.replace("```", "", 1)

        # Parse JSON
        try:
            return json.loads(response_text.strip())
        except json.JSONDecodeError as e:
            # Try to find valid JSON in the response
            try:
                # Look for array or object start/end
                if response_text.strip().startswith('[') and ']' in response_text:
                    valid_json = response_text.strip().split(']', 1)[0] + ']'
                    return json.loads(valid_json)
                elif response_text.strip().startswith('{') and '}' in response_text:
                    valid_json = response_text.strip().split('}', 1)[0] + '}'
                    return json.loads(valid_json)
            except Exception:
                pass

            raise ValueError(f"Failed to parse response as JSON: {e}\nResponse: {response_text}")

# Create a singleton instance
client = GoogleAIClient()

def generate_content(prompt, model_name="gemini-1.5-flash", temperature=0.7, max_tokens=None):
    """Generate content using Google Generative AI.

    Args:
        prompt (str): The prompt for content generation.
        model_name (str, optional): Model name to use. Defaults to "gemini-1.5-flash".
        temperature (float, optional): Temperature for generation. Defaults to 0.7.
        max_tokens (int, optional): Maximum number of tokens to generate. Defaults to None.

    Returns:
        str: The generated content.
    """
    # Create a client with the specified model
    client = GoogleAIClient(model_name=model_name)

    # Generate content
    return client.generate_content(prompt, temperature, max_tokens)

def generate_json(prompt, schema=None, model_name="gemini-1.5-flash", temperature=0.2):
    """Generate JSON content using Google Generative AI.

    Args:
        prompt (str): The prompt for content generation.
        schema (dict, optional): JSON schema to validate against. Defaults to None.
        model_name (str, optional): Model name to use. Defaults to "gemini-1.5-flash".
        temperature (float, optional): Temperature for generation. Defaults to 0.2.

    Returns:
        dict: The generated JSON content.
    """
    # Create a client with the specified model
    client = GoogleAIClient(model_name=model_name)

    # Generate JSON
    return client.generate_json(prompt, schema, temperature)

if __name__ == "__main__":
    # Simple test
    import argparse

    parser = argparse.ArgumentParser(description="Test Google Generative AI client.")
    parser.add_argument("--prompt", default="Write a short introduction to generative AI.", help="Prompt for content generation")
    parser.add_argument("--model", default="gemini-1.5-flash", help="Model name")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature for generation")
    parser.add_argument("--max_tokens", type=int, default=None, help="Maximum number of tokens to generate")
    parser.add_argument("--json", action="store_true", help="Generate JSON content")

    args = parser.parse_args()

    try:
        if args.json:
            # Generate JSON
            result = generate_json(args.prompt, model_name=args.model, temperature=args.temperature)
            print(json.dumps(result, indent=2))
        else:
            # Generate content
            result = generate_content(args.prompt, args.model, args.temperature, args.max_tokens)
            print(result)
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)
