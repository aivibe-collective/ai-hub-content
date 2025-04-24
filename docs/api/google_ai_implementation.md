# Google Generative AI Implementation Guide

This document provides a guide for implementing Google's Generative AI API in your application, based on the Content Alchemist implementation.

## 1. Environment Setup

First, you need to set up your environment with the necessary API key:

```
# .env file
GOOGLE_GENAI_API_KEY="your-api-key-here"
```

## 2. TypeScript Implementation (Content Alchemist)

The Content Alchemist application uses the Genkit framework to interact with Google's Generative AI API:

```typescript
// src/ai/ai-instance.ts
export const ai = genkit({
  promptDir: './prompts',
  plugins: [
    (() => {
      try {
        return googleAI({
          apiKey: process.env.GOOGLE_GENAI_API_KEY,
        });
      } catch (e) {
        console.error('Error initializing Google AI plugin:', e);
        throw e;
      }
    })(),
  ],
  model: 'googleai/gemini-2.0-flash',
});
```

## 3. Python Implementation

Here's how you can implement the same functionality in Python:

```python
import os
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
```

## 4. JavaScript/Node.js Implementation

Here's how you can implement the same functionality in JavaScript/Node.js:

```javascript
// ai-client.js
const { GoogleGenerativeAI } = require('@google/generative-ai');
require('dotenv').config();

function setupGenAI() {
  // Get API key
  const apiKey = process.env.GOOGLE_GENAI_API_KEY;
  if (!apiKey) {
    throw new Error('GOOGLE_GENAI_API_KEY environment variable not found');
  }
  
  // Initialize the API client
  const genAI = new GoogleGenerativeAI(apiKey);
  
  return genAI;
}

async function generateContent(prompt, modelName = 'gemini-1.5-flash') {
  // Set up the client
  const genAI = setupGenAI();
  
  // Get the model
  const model = genAI.getGenerativeModel({ model: modelName });
  
  // Generate content
  const result = await model.generateContent(prompt);
  const response = await result.response;
  
  return response.text();
}

module.exports = { generateContent };
```

## 5. Error Handling

Both implementations include error handling to catch issues with API initialization and content generation. The Content Alchemist implementation uses a try-catch block to handle initialization errors, and you should also handle errors during content generation.

## 6. Model Selection

The Content Alchemist application uses the `googleai/gemini-2.0-flash` model, but you can use other models like:
- `gemini-1.5-flash` (faster, more efficient)
- `gemini-1.5-pro` (more capable, better for complex tasks)
- `gemini-1.0-pro` (older version)

## 7. Queue Management

As you noticed in your error message, Google's API sometimes has a queue when there are too many requests:

```
Too many current requests. Your queue position is 5. Please wait for a while or switch to other models for a smoother experience.
```

To handle this, you can implement retry logic with exponential backoff:

```python
import time
import random

def generate_content_with_retry(prompt, model_name="gemini-1.5-flash", max_retries=5):
    """Generate content with retry logic."""
    retries = 0
    while retries < max_retries:
        try:
            return generate_content(prompt, model_name)
        except Exception as e:
            if "Too many current requests" in str(e):
                # Calculate backoff time with jitter
                backoff_time = (2 ** retries) + random.uniform(0, 1)
                print(f"API busy. Retrying in {backoff_time:.2f} seconds...")
                time.sleep(backoff_time)
                retries += 1
            else:
                # For other errors, raise immediately
                raise
    
    # If we've exhausted retries
    raise Exception(f"Failed to generate content after {max_retries} retries")
```

## 8. Best Practices

1. **Environment Variables**: Always store API keys in environment variables, never hardcode them
2. **Error Handling**: Implement robust error handling for API calls
3. **Retry Logic**: Add retry logic with exponential backoff for rate limiting
4. **Model Selection**: Choose the appropriate model for your use case
5. **Prompt Engineering**: Craft effective prompts for better results
6. **Response Validation**: Validate and sanitize API responses before using them

## 9. Testing

Create tests to ensure your implementation works correctly:

```python
def test_generate_content():
    """Test content generation."""
    prompt = "Write a short introduction to generative AI."
    content = generate_content(prompt)
    
    # Assert that content is not empty
    assert content and len(content) > 0
    
    # Assert that content is relevant to the prompt
    assert "generative" in content.lower() or "AI" in content
```

## 10. Conclusion

By following this guide, you can implement Google's Generative AI API in your application, similar to how it's done in the Content Alchemist application. The implementation provides a clean abstraction over the Google API, handling authentication and request formatting.
