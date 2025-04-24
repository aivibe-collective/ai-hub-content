# Single Content Item Development Workflow

This document provides a detailed, step-by-step workflow for developing a single content item for the AI Community & Sustainability Hub. Follow this process for each content piece to ensure consistency, quality, and alignment with the Hub's mission pillars.

## Pre-Development Phase

### 1. Content Item Selection & Dependency Check

- **Identify the content item** from the inventory (e.g., LRN-BEG-001: What is Generative AI?)
- **Check dependencies** in the dependency map
- **Verify that all prerequisite content** is complete or in progress
- **Document any blockers** if prerequisites are not ready

### 2. Content Plan Creation

- **Complete the content plan template** with the following information:
  - Content ID and title
  - Content type (Learning Module, Case Study, etc.)
  - Target audience details (technical level, role/context, resource constraints)
  - Primary mission pillars (1-2) and connections to other pillars
  - SMART objectives (specific, measurable, achievable, relevant, time-bound)
  - Outline of key sections (based on the appropriate template from `/Standards/OutlineTemplates/`)
  - Practical components to be included
  - Required expertise and resources
  - Estimated development time
  - **Source requirements and quality standards**:
    - Types of sources needed (academic, industry, case studies, etc.)
    - Recency requirements for different information types
    - Quality criteria for acceptable sources
  - **Citation style** to be used (APA, IEEE, Chicago, etc.)

- **Reference the Sample_Content_Plan_What_Is_GenAI.md** as a model

### 3. Resource Allocation & Timeline

- **Identify the content creator(s)** with the required expertise
- **Assign reviewers** for different aspects of the content:
  - Technical reviewer(s) for accuracy and best practices
  - Mission pillar reviewer(s) for alignment with Hub mission
  - Audience reviewer(s) for relevance and clarity
  - **Source/fact-checking reviewer(s)** for citation accuracy and source quality
  - Accessibility specialist(s) for inclusive design
  - Editorial reviewer(s) for style and consistency
- **Identify research resources** needed for source collection:
  - Access to academic databases
  - Industry report subscriptions
  - Citation management tools
- **Create a development timeline** with the following milestones:
  - Content plan approval
  - Initial draft completion
  - Source collection and documentation
  - Internal review
  - Revision completion
  - Multi-dimensional review (including source verification)
  - Final revision
  - Editorial review
  - Publication

### 4. Kickoff Meeting

- **Schedule a kickoff meeting** with the content creator(s) and key stakeholders
- **Review the content plan** and ensure alignment on objectives and approach
- **Clarify any questions** about the content requirements
- **Confirm timeline and deliverables**

## Development Phase

### 5. Initial Draft Creation

- **Select the appropriate template** from `/Standards/OutlineTemplates/`
- **Develop content following the template structure**
- **Ensure integration of mission pillars** throughout the content
- **Use clear, accessible language** appropriate for the target audience
- **Include visual elements** (diagrams, screenshots, etc.) where helpful
- **Develop practical components** (exercises, tools, templates, etc.)
- **Mark statements requiring citations** with [SOURCE NEEDED] tags, being specific about the type of information needed:

  ```markdown
  [SOURCE NEEDED: Statistics on AI adoption rates among SMEs in 2023]
  [SOURCE NEEDED: Definition of transformer architecture]
  [SOURCE NEEDED: Case example of successful implementation in retail]
  ```

### 6. Source Collection and Documentation

- **Create a source request log** from all [SOURCE NEEDED] tags in the draft
  - Use the [Source Request Log Template](/Source_Request_Log_Template.md) for structured tracking
- **Categorize source needs** by information type (statistical, conceptual, methodological, etc.)
- **Research potential sources** using appropriate repositories:
  - Academic databases (Google Scholar, IEEE Xplore, ACM Digital Library)
  - Industry sources (Gartner, Forrester, McKinsey, industry associations)
  - Government/NGO publications (EU AI Act, NIST, ISO standards)
  - Tech publications and conference proceedings
  - Hub-specific resources and previous content

- **Evaluate sources** using the CRAAP test criteria:
  - Use the [Source Evaluation Matrix Template](/Source_Evaluation_Matrix_Template.md) to compare sources
  - **Currency**: Is the information up-to-date and appropriate for your topic?
  - **Relevance**: Does it directly address your specific needs?
  - **Authority**: Is the author/publisher credible and expert in the field?
  - **Accuracy**: Is the information supported by evidence and verifiable?
  - **Purpose**: Is the source objective or does it have a bias or agenda?

- **Document selected sources** in the required citation format
- **Extract key information** from sources (statistics, definitions, methodologies, quotes)
- **Integrate sources into content**:
  - Add in-text citations in the appropriate format
  - Include direct quotes where the original wording is important
  - Paraphrase information with proper attribution
  - Add visual citations for data visualizations
- **Compile a complete reference list** at the end of the content
- **Verify all [SOURCE NEEDED] tags** have been replaced with proper citations
- **Check citation style consistency** throughout the document

### 7. Internal Review

- **Submit the draft for internal review** by immediate team members
- **Gather feedback** on:
  - Alignment with content plan
  - Adherence to template structure
  - Technical accuracy
  - Clarity and accessibility
  - Mission pillar integration
  - Practical component effectiveness
  - Prompt effectiveness and quality
- **Document all feedback** in a structured format
- **Use the AI review workflow in the UI** to:
  - Automatically analyze content quality
  - Check for consistency with mission pillars
  - Identify potential gaps in source coverage
  - Suggest improvements to structure and flow
  - Evaluate prompt effectiveness

### 8. First Revision

- **Revise the content** based on internal feedback
- **Track changes made** in response to each feedback item
- **Note any areas requiring further input** or clarification
- **Update prompts in the prompt management system** based on feedback:
  - Store prompts in the database with version tracking
  - Document prompt effectiveness and issues
  - Create improved prompt variants based on feedback
  - Tag prompts with relevant metadata for future reference
- **Prepare the revised draft** for formal review

## Review Phase

### 9. Multi-dimensional Review

- **Submit the revised draft for formal review** by:
  - **Technical Reviewer(s):** Verify accuracy, robustness, and technical best practices
  - **Mission Pillar Reviewer(s):** Assess depth and relevance of mission pillar integration
  - **Audience Reviewer(s):** Evaluate clarity, relevance, and engagement for target audience
  - **SME Advisor(s):** Provide industry-specific feedback (for business-focused content)
  - **Source/Fact-checking Reviewer(s):** Verify citation accuracy and source quality

- **Run automated checks** where applicable:
  - Grammar/style checkers
  - Accessibility checkers
  - Bias detection tools (if relevant)
  - Sustainability measurement tools (if code is involved)
  - Citation format checker
  - URL/DOI validator

- **Conduct initial source verification review**:
  - Verify technical accuracy of cited information
  - Check proper representation of source information
  - Validate claims against original sources
  - Assess citation style consistency
  - Evaluate source quality and diversity

### 10. Feedback Consolidation

- **Collect all review feedback** in a central document
- **Categorize feedback** by type (technical, mission alignment, audience, etc.)
- **Identify any conflicting feedback** that needs resolution
- **Prioritize feedback items** based on impact and importance
- **Schedule a feedback discussion** if significant issues or conflicts exist
- **Store all references in the database** with:
  - Complete bibliographic information
  - Quality assessment scores (CRAAP test results)
  - Usage context and relevance ratings
  - Tags for topic areas and content sections
  - Accessibility of the source (open access, subscription, etc.)

### 11. Second Revision

- **Revise the content** based on all formal review feedback
- **Document how each feedback item was addressed**
- **Highlight any significant changes** for the editorial review
- **Update practical components** based on feedback
- **Ensure all mission pillar integration points** are strengthened
- **Use automated regeneration based on feedback**:
  - Feed structured feedback into the prompt system
  - Generate alternative sections that address specific issues
  - Compare original and regenerated content
  - Selectively incorporate improvements
  - Document which sections were regenerated and why

## Finalization Phase

### 12. Editorial Review

- **Submit the revised content for editorial review**
- **Check for:**
  - Style consistency
  - Grammar and spelling
  - Flow and readability
  - Formatting consistency
  - Appropriate use of visuals
  - Clear instructions for practical components

### 13. Final Revision

- **Make final adjustments** based on editorial feedback
- **Ensure all visual elements** are properly formatted and labeled
- **Verify all links** to related content or external resources
- **Finalize practical components** and ensure they are ready for use
- **Prepare the content package** for final approval
- **Update the prompt database** with final versions of effective prompts

### 14. Final Approval

- **Submit the complete content package** to the Content Strategist
- **Include:**
  - Final content draft
  - All practical components
  - Summary of review process and key changes
  - Database of references used with quality metrics
  - Prompt versions with effectiveness ratings
  - Any outstanding concerns or notes
- **Obtain formal sign-off** before proceeding to publication

### 15. Publication Preparation

- **Format the content** according to the Hub's visual design kit and style guide
- **Optimize for accessibility** across different devices and screen sizes
- **Add appropriate tags** based on mission pillars, audience, topic, etc.
- **Create metadata** for search and discovery
- **Prepare any promotional materials** (social media posts, newsletter blurbs, etc.)
- **Ensure all references are properly stored** in the central reference database

### 16. Publication & Dependency Update

- **Publish the content** on the Hub platform
- **Update the dependency tracking system** to mark this item as complete
- **Notify teams working on dependent content** that this prerequisite is now available
- **Document any lessons learned** from the development process
- **Archive successful prompts** in the prompt library for reuse

## Post-Publication Phase

### 17. Monitoring & Feedback Collection

- **Track user engagement metrics** (views, completion rates, time spent, etc.)
- **Collect structured user feedback** (ratings, comments, surveys)
- **Monitor forum discussions** related to the content
- **Document any issues or improvement suggestions**
- **Analyze prompt effectiveness metrics** from production use
- **Track reference usage and quality metrics** in the database

### 18. Continuous Improvement

- **Schedule regular content reviews** (quarterly, annually, or triggered by significant updates)
- **Update content based on:**
  - User feedback
  - New developments in the field
  - Changes to related content
  - Platform updates
  - Prompt performance data
  - Reference quality assessments
- **Document all updates** in a version history
- **Use automated regeneration** for sections that need updating:
  - Create targeted prompts based on feedback and new requirements
  - Generate updated content sections
  - Review and integrate the regenerated content
  - Update the reference database with new sources
- **Refine prompts** based on performance metrics and feedback

## Workflow Tools & Templates

### Content Planning Tools

- **Content Plan Template** - For documenting the content strategy
- **SMART Objectives Worksheet** - For defining measurable outcomes
- **Mission Pillar Integration Checklist** - For ensuring alignment with Hub mission
- **Source Requirements Planner** - For identifying source needs and quality standards

### Development Tools

- **Content Outline Templates** - From `/Standards/OutlineTemplates/`
- **Style Guide** - For ensuring consistent writing
- **Visual Asset Guidelines** - For creating diagrams and illustrations
- **Source Request Log Template** - For tracking [SOURCE NEEDED] tags
- **Prompt Management System** - For creating, versioning, and optimizing prompts
- **Automated Regeneration Tool** - For targeted content regeneration based on feedback

### Source Management Tools

- **CRAAP Test Worksheet** - For evaluating source quality
- **Citation Style Guides** - For formatting citations correctly
- **Source Evaluation Matrix** - For comparing potential sources
- **Reference Management Tools** - Zotero, Mendeley, or EndNote for citation management
- **Reference Database** - For storing and retrieving all references with quality metrics
- **Source Usage Analytics** - For tracking reference usage across content items

### Review Tools

- **Review Checklists** - From `/Standards/ReviewChecklists/`
- **Source Verification Checklist** - For validating citations and references
- **Feedback Consolidation Template** - For organizing review input
- **Revision Tracking Document** - For documenting changes
- **AI Review Workflow** - For automated content quality assessment and improvement suggestions
- **Prompt Effectiveness Analyzer** - For evaluating and improving prompt performance

### Publication Tools

- **Content Formatting Guide** - For preparing content for the platform
- **Metadata Template** - For optimizing discoverability
- **Dependency Update Form** - For tracking completion in the inventory
- **Citation Verification Tool** - For checking URL/DOI functionality

## Example: Developing "What is Generative AI?" (LRN-BEG-001)

### Pre-Development

1. **Verify no dependencies** (this is a foundation piece)
2. **Create content plan** specifying:
   - Beginner audience of SME owners with limited technical knowledge
   - Primary mission pillars: Responsible AI and SME Relevance
   - SMART objectives: "Users will be able to explain generative AI and identify 3 potential applications for their business"
   - Practical components: Interactive demo, simple quiz, use case template

### Development

3. **Use Learning Module template** from `/Standards/OutlineTemplates/LearningModule.md`
4. **Create initial draft** with:
   - Clear, jargon-free explanations of generative AI
   - Visual comparisons between traditional and generative AI
   - Examples relevant to small businesses
   - Embedded ethical considerations
   - Step-by-step interactive components
   - [SOURCE NEEDED] tags for statistics, definitions, and examples

5. **Collect and document sources**:
   - Research recent statistics on generative AI adoption
   - Find authoritative definitions of key technical concepts
   - Identify credible case studies of SME implementations
   - Evaluate sources using CRAAP criteria
   - Create properly formatted citations
   - Integrate sources with appropriate in-text citations

### Review

6. **Submit for multi-dimensional review** to:
   - Technical expert (verify AI concepts are accurate)
   - SME advisor (ensure business relevance)
   - Responsible AI specialist (check ethical integration)
   - Non-technical reviewer (verify accessibility of concepts)
   - Source/fact-checking reviewer (verify citation accuracy)

7. **Revise based on feedback**, particularly strengthening:
   - Simplified explanations of complex concepts
   - More diverse business examples
   - Clearer ethical implications
   - Enhanced practical exercises
   - Improved source integration and citation

### Finalization

8. **Complete editorial review** for clarity and consistency
9. **Finalize all components** including interactive elements
10. **Perform final citation and reference verification** to ensure all sources are accurate, properly formatted, and functional
11. **Publish and update dependency system** to show LRN-BEG-001 is complete
12. **Notify teams** working on LRN-BEG-002, LRN-BEG-003, and other dependent content

---

This workflow provides a comprehensive process for developing a single content item from initial planning through publication and beyond. Adapt the specific steps as needed based on the content type, complexity, and available resources.
