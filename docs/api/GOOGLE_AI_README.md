# Google Generative AI Integration

This repository contains implementations for integrating Google's Generative AI API into your applications.

## Overview

Google's Generative AI API provides access to powerful language models like Gemini, which can generate text, translate languages, write different kinds of creative content, and answer your questions in an informative way.

## Implementations

We provide implementations in multiple languages:

1. **TypeScript/JavaScript (Content Alchemist)**
   - Uses the Genkit framework
   - Configured with environment variables
   - Handles errors gracefully

2. **Node.js**
   - Uses the official `@google/generative-ai` package
   - Simple and straightforward implementation
   - Includes command-line interface

3. **Python**
   - Uses the official `google-generativeai` package
   - Includes environment variable configuration
   - Provides retry logic for handling API queues

## Setup

### Environment Variables

Create a `.env` file with your Google Generative AI API key:

```
GOOGLE_GENAI_API_KEY="your-api-key-here"
```

### Installation

#### Node.js

```bash
npm install @google/generative-ai dotenv
```

#### Python

```bash
pip install google-generativeai python-dotenv
```

## Usage

### Node.js

```javascript
const { generateContent } = require('./google-ai-client');

async function main() {
  const prompt = "Write a short introduction to generative AI.";
  const content = await generateContent(prompt);
  console.log(content);
}

main();
```

Or use the command-line interface:

```bash
node google-ai-test.js --prompt="Write a short introduction to generative AI" --output="output.md"
```

### Python

```python
from google_ai_client import generate_content

prompt = "Write a short introduction to generative AI."
content = generate_content(prompt)
print(content)
```

Or use the command-line interface:

```bash
python google_ai_test.py --prompt="Write a short introduction to generative AI" --output="output.md"
```

## Models

Google provides several models with different capabilities:

- `gemini-1.5-flash`: Fast and efficient, good for most tasks
- `gemini-1.5-pro`: More capable, better for complex tasks
- `gemini-2.0-flash`: Latest version, improved capabilities
- `gemini-2.0-pro`: Latest version, highest quality results

## Error Handling

The implementations include error handling for common issues:

1. **Missing API Key**: Checks if the API key is provided
2. **API Errors**: Catches and reports API errors
3. **Queue Management**: Handles "Too many current requests" errors with retry logic

## Best Practices

1. **Environment Variables**: Always store API keys in environment variables
2. **Error Handling**: Implement robust error handling for API calls
3. **Retry Logic**: Add retry logic with exponential backoff for rate limiting
4. **Model Selection**: Choose the appropriate model for your use case
5. **Prompt Engineering**: Craft effective prompts for better results

## Examples

See the `examples` directory for more examples of using the Google Generative AI API for different tasks:

- Text generation
- Content summarization
- Question answering
- Creative writing
- Code generation

## Resources

- [Google AI Studio](https://ai.google.dev/)
- [Google Generative AI Documentation](https://ai.google.dev/docs)
- [Gemini API Reference](https://ai.google.dev/api/rest/v1beta/models)
- [Prompt Engineering Guide](https://ai.google.dev/docs/prompting)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
