# Agentic AI Content Creation System Test Plan

This document outlines the comprehensive test plan for the Agentic AI Content Creation System. It includes test environment setup, test case design, execution procedures, and reporting guidelines.

## 1. Test Environment

### 1.1 Test Project Setup

The test environment consists of a separate Google Cloud project with the following components:

- **Project ID**: `aivibe-content-creation-test`
- **Region**: `us-central1`
- **Cloud Storage**: `aivibe-content-test` bucket
- **Firestore**: Test collections for content items, templates, sources, and users
- **Pub/Sub**: Test topics for event communication
- **Cloud Functions**: Test versions of all Cloud Functions
- **Cloud Run**: Test versions of all Cloud Run services

### 1.2 Test Data

The test environment includes the following test data:

- **Content Plans**: Sample content plans for different content types and audience levels
- **Templates**: Content templates from the production environment
- **Source Data**: Sample source documents and metadata
- **User Feedback**: Mock feedback from reviewers

### 1.3 Environment Setup

The test environment can be set up using the following scripts:

- `test/setup_test_env.py`: Sets up local test data and directories
- `deployment/deploy_test_env.sh`: Deploys the test environment to Google Cloud

## 2. Test Case Design

The test cases are organized by component, following the workflow steps in the Enhanced Agentic AI Content Creation Workflow document.

### 2.1 Template Selection (Workflow Step 1)

| Test ID | Description | Input | Expected Output | Method |
|---------|-------------|-------|----------------|--------|
| TC1.1 | Valid Template | Content plan for a "Beginner" learning module | System recommends "LearningModule.md" template | Unit test |
| TC1.2 | Invalid Template | Content plan for a blog post | System does not recommend "CaseStudy.md" template | Unit test |
| TC1.3 | No Template | Content plan with invalid content type | System fails with clear error message | Unit test |
| TC1.5 | Firestore Error | Content plan with valid parameters but Firestore error | System raises exception | Unit test |
| TC1.6 | Empty Content Plan | Content plan with empty title and objectives | System handles gracefully | Unit test |
| TC1.4 | Template Customization | Content plan and selected template | Suggestions for template modifications | Manual |

### 2.2 File Structure Creation (Workflow Step 2)

| Test ID | Description | Input | Expected Output | Method |
|---------|-------------|-------|----------------|--------|
| TC2.1 | Valid Structure | "LearningModule.md" template | Correct folder structure created | Integration test |
| TC2.2 | Name Conventions | Any template | Folders and files follow naming conventions | Integration test |
| TC2.3 | Asset Management | "CaseStudy.md" template | Asset subdirectories and placeholders created | Integration test |

### 2.3 Content Planning (Workflow Step 3)

| Test ID | Description | Input | Expected Output | Method |
|---------|-------------|-------|----------------|--------|
| TC3.1 | Audience Analysis | Content plan for "Beginner AI" | Key concepts identified for beginner audience | Unit test |
| TC3.2 | Knowledge Graph Integration | Content plan for "RAG" | Related content identified in knowledge graph | Integration test |
| TC3.3 | Learning Objective Alignment | Content plan for "Intermediate MLOps" | SMART learning objectives generated | Unit test |

### 2.4 Section Population (Workflow Step 4)

| Test ID | Description | Input | Expected Output | Method |
|---------|-------------|-------|----------------|--------|
| TC4.1 | Context-Aware Generation | "Introduction" section for "RAG" module | Appropriate introduction to RAG | Integration test |
| TC4.2 | Style Consistency | Multiple sections from different content plans | Consistent style and formatting | Integration test |
| TC4.3 | Multi-Modal Content Creation | Content plan for "Data Visualization" | Suggestions for visualizations and code examples | Integration test |

### 2.5 Source Collection and Documentation (Workflow Step 5)

| Test ID | Description | Input | Expected Output | Method |
|---------|-------------|-------|----------------|--------|
| TC5.1 | Source Need Identification | Section with factual claim | System flags citation needed | Unit test |
| TC5.2 | Source Research | Source need | System researches potential sources | Unit test |
| TC5.3 | CRAAP Test | Set of mock sources | System evaluates sources using CRAAP criteria | Unit test |
| TC5.6 | Outdated Source | Source from 2010 with outdated information | System gives low currency and accuracy scores | Unit test |
| TC5.7 | Biased Source | Source from commercial vendor with extreme claims | System gives low purpose and accuracy scores | Unit test |
| TC5.8 | Anonymous Source | Source with no clear author | System gives low authority score | Unit test |
| TC5.9 | Malformed URL | Source with invalid URL | System handles error gracefully | Unit test |
| TC5.4 | Citation Generation | Section and list of sources | In-text citations in correct format | Unit test |
| TC5.5 | Source Integration | Section and selected source | Source integrated with proper citation | Unit test |

### 2.6 Mission Pillars Integration (Workflow Step 6)

| Test ID | Description | Input | Expected Output | Method |
|---------|-------------|-------|----------------|--------|
| TC6.1 | Pillar Alignment | Generated content section | Mission pillar integration points identified | Integration test |
| TC6.2 | Balance | Complete module | All mission pillars represented | Integration test |
| TC6.3 | Mission Impact Measurement | Content plan for "Responsible AI" | Metrics for measuring mission-related outcomes | Integration test |

### 2.7 Practical Components Development (Workflow Step 7)

| Test ID | Description | Input | Expected Output | Method |
|---------|-------------|-------|----------------|--------|
| TC7.1 | Activity Alignment | Learning objectives | Activities aligned with objectives | Integration test |
| TC7.2 | Code Generation | Content section requiring code example | Syntactically correct code | Unit test |
| TC7.3 | Multi-Modal Component Generation | Content plan for "Advanced RAG" | Interactive elements, datasets, templates | Integration test |

### 2.8 Accessible Language and Formatting (Workflow Step 8)

| Test ID | Description | Input | Expected Output | Method |
|---------|-------------|-------|----------------|--------|
| TC8.1 | Readability | Generated content section | Good readability score | Unit test |
| TC8.2 | Terminology | Generated module | Consistent terminology | Unit test |
| TC8.3 | Multi-level Content Adaptation | Content plan for concept at different levels | Explanations at different expertise levels | Integration test |

### 2.9 Quality Assurance Checks (Workflow Step 9)

| Test ID | Description | Input | Expected Output | Method |
|---------|-------------|-------|----------------|--------|
| TC9.1 | Compliance | Module with missing sections | System reports missing sections | Unit test |
| TC9.2 | Accuracy | Section with incorrect information | System flags inaccuracy | Integration test |
| TC9.3 | Automated Error Detection | Content with formatting issues | System identifies and corrects issues | Integration test |

### 2.10 Human Review Interface (Workflow Step 10)

| Test ID | Description | Input | Expected Output | Method |
|---------|-------------|-------|----------------|--------|
| TC10.1 | Feedback Collection | Reviewer feedback | Feedback stored with correct content | Integration test |
| TC10.2 | Review Tracking | Content under review | System displays review status | Integration test |
| TC10.3 | Guided Review Process | Different content types | Review focus areas and checklists | Integration test |

### 2.11 Revision and Final Output (Workflow Step 11)

| Test ID | Description | Input | Expected Output | Method |
|---------|-------------|-------|----------------|--------|
| TC11.1 | Feedback Processing | Reviewer feedback | System processes feedback and updates content | Integration test |
| TC11.2 | Version Control | Content with multiple modifications | All versions stored | Unit test |
| TC11.3 | Version Comparison | Two content versions | Comparison view with highlighted changes | Integration test |

## 3. Test Execution

### 3.1 Unit Tests

Unit tests can be run using the `test/run_tests.py` script:

```bash
# Run all unit tests
python test/run_tests.py

# Run specific test modules
python test/run_tests.py --modules test_template_selection test_source_collection

# Run tests in verbose mode
python test/run_tests.py --verbose

# Set up local test environment and run tests
python test/run_tests.py --setup

# Set up cloud test environment (requires local setup first)
python test/run_tests.py --cloud-setup

# List available test modules
python test/run_tests.py --list
```

### 3.2 Integration Tests

Integration tests require a deployed test environment:

1. Deploy the test environment:
   ```bash
   chmod +x deployment/deploy_test_env.sh
   ./deployment/deploy_test_env.sh
   ```

2. Run integration tests:
   ```bash
   python test/run_integration_tests.py
   ```

### 3.3 Manual Tests

Some tests require manual verification:

1. Template Customization (TC1.4)
2. Multi-Modal Content Creation (TC4.3)
3. Human Review Interface (TC10.1, TC10.2, TC10.3)

## 4. Test Reporting

### 4.1 Test Results

Test results are reported in the following formats:

- **Unit Test Reports**: Generated by the test runner
- **Integration Test Reports**: Generated by the integration test runner
- **Manual Test Reports**: Documented in the test results spreadsheet

### 4.2 Issue Tracking

Issues found during testing should be documented with:

- Test ID
- Description of the issue
- Steps to reproduce
- Expected vs. actual behavior
- Severity (High, Medium, Low)

### 4.3 Test Coverage

Test coverage is measured using:

- Code coverage for unit tests
- Workflow coverage for integration tests
- Feature coverage for manual tests

## 5. Continuous Integration

The test suite is integrated into the CI/CD pipeline:

1. Unit tests run on every pull request
2. Integration tests run on merges to the main branch
3. Manual tests run before major releases

## 6. Test Data Management

### 6.1 Test Data Generation

Test data can be generated using:

```bash
python test/setup_test_env.py
```

### 6.2 Test Data Cleanup

Test data can be cleaned up using:

```bash
# Clean up local test data
python test/cleanup_test_env.py

# Clean up local and cloud test data
python test/cleanup_test_env.py --cloud

# Force cleanup without confirmation
python test/cleanup_test_env.py --force
```

## 7. Troubleshooting

Common issues and their solutions:

- **Authentication Errors**: Ensure you're authenticated with the correct Google Cloud project
- **Missing Dependencies**: Run `pip install -r requirements.txt` to install all dependencies
- **API Errors**: Check that all required APIs are enabled in the test project
- **Timeout Errors**: Increase the timeout values in the test configuration

## 8. Conclusion

This test plan provides a comprehensive approach to validating the Agentic AI Content Creation System. By following this plan, we can ensure that the system meets all requirements and functions correctly in all scenarios.
