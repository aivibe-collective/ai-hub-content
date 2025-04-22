#!/usr/bin/env node

/**
 * Script to test the Google Generative AI API integration.
 */

const fs = require('fs');
const path = require('path');
const { GoogleGenerativeAI } = require('@google/generative-ai');
require('dotenv').config();

/**
 * Set up the Google Generative AI client.
 * @returns {GoogleGenerativeAI} The Google Generative AI client.
 */
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

/**
 * Generate content using Google Generative AI.
 * @param {string} prompt - The prompt for content generation.
 * @param {string} modelName - The model name to use.
 * @param {number} temperature - Temperature for generation (0.0 to 1.0).
 * @param {number} maxTokens - Maximum number of tokens to generate.
 * @returns {Promise<string>} The generated content.
 */
async function generateContent(prompt, modelName = 'gemini-1.5-flash', temperature = 0.7, maxTokens = null) {
  // Set up the client
  const genAI = setupGenAI();

  // Get the model
  const model = genAI.getGenerativeModel({ model: modelName });

  // Set generation config
  const generationConfig = {};

  if (temperature !== null && temperature !== undefined) {
    generationConfig.temperature = temperature;
  }

  if (maxTokens !== null && maxTokens !== undefined) {
    generationConfig.maxOutputTokens = maxTokens;
  }

  // Generate content
  const result = await model.generateContent({
    contents: [{ role: 'user', parts: [{ text: prompt }] }],
    generationConfig
  });

  const response = await result.response;

  return response.text();
}

/**
 * Generate JSON content using Google Generative AI.
 * @param {string} prompt - The prompt for content generation.
 * @param {string} modelName - The model name to use.
 * @param {number} temperature - Temperature for generation (0.0 to 1.0).
 * @returns {Promise<object>} The generated JSON content.
 */
async function generateJson(prompt, modelName = 'gemini-1.5-flash', temperature = 0.2) {
  // Add instructions for JSON output
  const jsonPrompt = `${prompt}\n\nReturn your response as a valid JSON object. Do not include any explanations or markdown formatting.`;

  // Generate content
  const responseText = await generateContent(jsonPrompt, modelName, temperature);

  // Clean up the response if it contains markdown code blocks
  let cleanedResponse = responseText;
  if (cleanedResponse.startsWith('```json')) {
    cleanedResponse = cleanedResponse.replace('```json', '');
  } else if (cleanedResponse.startsWith('```')) {
    cleanedResponse = cleanedResponse.replace('```', '');
  }

  if (cleanedResponse.endsWith('```')) {
    cleanedResponse = cleanedResponse.replace(/```$/, '');
  }

  // Parse JSON
  try {
    return JSON.parse(cleanedResponse.trim());
  } catch (error) {
    throw new Error(`Failed to parse response as JSON: ${error.message}\nResponse: ${responseText}`);
  }
}

/**
 * Main function to test Google Generative AI API.
 */
async function main() {
  // Parse command line arguments
  const args = process.argv.slice(2);
  const promptArg = args.find(arg => arg.startsWith('--prompt='));
  const modelArg = args.find(arg => arg.startsWith('--model='));
  const outputArg = args.find(arg => arg.startsWith('--output='));
  const temperatureArg = args.find(arg => arg.startsWith('--temperature='));
  const maxTokensArg = args.find(arg => arg.startsWith('--max_tokens='));
  const jsonArg = args.find(arg => arg === '--json');

  const prompt = promptArg ? promptArg.split('=')[1] : 'Write a short introduction to generative AI.';
  const model = modelArg ? modelArg.split('=')[1] : 'gemini-1.5-flash';
  const output = outputArg ? outputArg.split('=')[1] : 'google_ai_output.md';
  const temperature = temperatureArg ? parseFloat(temperatureArg.split('=')[1]) : 0.7;
  const maxTokens = maxTokensArg ? parseInt(maxTokensArg.split('=')[1]) : null;
  const generateAsJson = !!jsonArg;

  try {
    // Generate content
    console.log(`Generating content with model: ${model}`);
    console.log(`Prompt: ${prompt}`);
    console.log(`Temperature: ${temperature}`);
    if (maxTokens) console.log(`Max Tokens: ${maxTokens}`);
    console.log(`Output Format: ${generateAsJson ? 'JSON' : 'Text'}`);

    let content;
    if (generateAsJson) {
      // Generate JSON
      content = await generateJson(prompt, model, temperature);
      content = JSON.stringify(content, null, 2);
    } else {
      // Generate text
      content = await generateContent(prompt, model, temperature, maxTokens);
    }

    // Save content to file
    fs.writeFileSync(output, content);

    console.log(`Content generated and saved to ${output}`);

    // Display the generated content
    console.log('\nGenerated Content:');
    console.log('='.repeat(80));
    console.log(content.length > 1000 ? content.substring(0, 500) + '\n... [content truncated] ...\n' + content.substring(content.length - 500) : content);
    console.log('='.repeat(80));

    return 0;
  } catch (error) {
    console.error(`Error: ${error.message}`);
    return 1;
  }
}

// Run the main function
main().then(process.exit).catch(error => {
  console.error(error);
  process.exit(1);
});
