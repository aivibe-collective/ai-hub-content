# Security Guidelines for AI Hub Content Creation System

This document outlines security best practices for working with the AI Hub Content Creation System.

## Handling Credentials

### Google Cloud Service Account

1. **Never commit credentials to the repository**
   - Service account key files (JSON) should never be committed to Git
   - Use environment variables or secure secret management instead

2. **Create a dedicated service account**
   - Create a service account with minimal permissions needed
   - Follow the principle of least privilege

3. **Rotate credentials regularly**
   - Rotate service account keys every 90 days
   - Immediately revoke compromised credentials

### Supabase Credentials

1. **Use environment variables**
   - Store Supabase URL and key in environment variables
   - Never hardcode these values in source code

2. **Use separate projects for development and production**
   - Create separate Supabase projects for different environments
   - Use different credentials for each environment

### Environment Variables

1. **Use .env files locally**
   - Store environment variables in .env files for local development
   - Ensure .env files are in .gitignore

2. **Use secure secret management in production**
   - Use Google Secret Manager, AWS Secrets Manager, or similar services
   - Avoid storing secrets in environment variables in production

## API Security

### Google AI API

1. **Set appropriate quotas**
   - Configure API quotas to prevent unexpected usage
   - Monitor API usage regularly

2. **Use API key restrictions**
   - Restrict API keys by IP address, referrer, or API
   - Create separate API keys for different components

### Supabase API

1. **Use Row-Level Security (RLS)**
   - Implement RLS policies in Supabase
   - Restrict access to sensitive data

2. **Use JWT authentication**
   - Implement proper authentication for API access
   - Validate JWT tokens on the server

## Code Security

1. **Dependency management**
   - Regularly update dependencies
   - Use tools like Dependabot to automate updates

2. **Code scanning**
   - Use static code analysis tools
   - Implement security linting in CI/CD

3. **Input validation**
   - Validate all user inputs
   - Sanitize data before processing

## Reporting Security Issues

If you discover a security vulnerability, please send an email to security@aivibe.org. Do not disclose security vulnerabilities publicly until they have been handled by the security team.

## Security Checklist for Developers

- [ ] No credentials in code or Git history
- [ ] Environment variables properly configured
- [ ] API keys have appropriate restrictions
- [ ] Dependencies are up to date
- [ ] Input validation implemented
- [ ] Error handling doesn't expose sensitive information
- [ ] Logging doesn't include sensitive data
- [ ] Authentication properly implemented
- [ ] Authorization checks in place
