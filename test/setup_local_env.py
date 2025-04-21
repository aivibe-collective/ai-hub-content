"""
Setup script for the local test environment.
This script initializes the local test environment by:
1. Creating necessary directories
2. Setting up test data
"""

import os
import json
import shutil
from pathlib import Path
import config

def create_test_directories():
    """Create necessary directories for test data."""
    directories = [
        config.TEST_DATA_DIR,
        config.CONTENT_PLANS_DIR,
        config.SOURCE_DATA_DIR,
        config.TEMPLATES_DIR,
        config.USER_FEEDBACK_DIR
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def extract_sections_from_template(template_content):
    """Extract section headers from template content."""
    sections = []
    lines = template_content.split('\n')
    
    for line in lines:
        if line.startswith('**') and ':' in line:
            # Extract section name from lines like "**1. Introduction & Context:**"
            section_name = line.strip('*: ')
            sections.append(section_name)
    
    return sections

def setup_local_templates():
    """Initialize local test templates."""
    try:
        # Load template files from HubContent
        template_files = {
            "LearningModule": "../HubContent/Standards/OutlineTemplates/LearningModule.md",
            "CaseStudy": "../HubContent/Standards/OutlineTemplates/CaseStudy.md",
            "BlogPost": "../HubContent/Standards/OutlineTemplates/BlogPodcast.md",
            "ToolGuide": "../HubContent/Standards/OutlineTemplates/ToolGuide.md",
            "SectorPlaybook": "../HubContent/Standards/OutlineTemplates/SectorPlaybook.md"
        }
        
        # Add templates to local test data
        for template_type, file_path in template_files.items():
            try:
                with open(file_path, 'r') as f:
                    template_content = f.read()
                
                # Create template document
                template_data = {
                    'type': template_type,
                    'content': template_content,
                    'audience_levels': ["Beginner", "Intermediate", "Expert"],
                    'sections': extract_sections_from_template(template_content)
                }
                
                # Save to local test data
                template_path = os.path.join(config.TEMPLATES_DIR, f"{template_type}.json")
                with open(template_path, 'w') as f:
                    json.dump(template_data, f, indent=2)
                
                print(f"Added template to local test data: {template_type}")
                
            except Exception as e:
                print(f"Error processing template {template_type}: {str(e)}")
        
        return True
    except Exception as e:
        print(f"Error setting up local templates: {str(e)}")
        return False

def generate_test_content_plans():
    """Generate test content plans for different scenarios."""
    content_plans = [
        {
            "id": "plan_learning_beginner",
            "title": "Introduction to Generative AI",
            "content_type": config.ContentTypes.LEARNING_MODULE,
            "audience_level": config.AudienceLevels.BEGINNER,
            "mission_pillars": [config.MissionPillars.RESPONSIBLE_AI, config.MissionPillars.INCLUSION],
            "description": "A beginner-friendly introduction to generative AI concepts and applications.",
            "objectives": [
                "Understand the basic principles of generative AI",
                "Identify common generative AI applications",
                "Recognize ethical considerations in generative AI"
            ]
        },
        {
            "id": "plan_case_study",
            "title": "Implementing RAG for Customer Support",
            "content_type": config.ContentTypes.CASE_STUDY,
            "audience_level": config.AudienceLevels.INTERMEDIATE,
            "mission_pillars": [config.MissionPillars.EXPERTISE, config.MissionPillars.SUSTAINABILITY],
            "description": "A case study on implementing Retrieval Augmented Generation for customer support.",
            "objectives": [
                "Demonstrate RAG implementation in a real-world scenario",
                "Analyze performance improvements in customer support",
                "Evaluate cost and sustainability impacts"
            ]
        },
        {
            "id": "plan_blog_post",
            "title": "The Future of AI Regulation",
            "content_type": config.ContentTypes.BLOG_POST,
            "audience_level": config.AudienceLevels.GENERAL,
            "mission_pillars": [config.MissionPillars.RESPONSIBLE_AI],
            "description": "A blog post discussing emerging trends in AI regulation globally.",
            "objectives": [
                "Summarize current AI regulatory frameworks",
                "Analyze emerging trends in AI governance",
                "Discuss implications for AI practitioners"
            ]
        },
        {
            "id": "plan_invalid",
            "title": "Invalid Content Plan",
            "content_type": "InvalidType",
            "audience_level": "Unknown",
            "mission_pillars": [],
            "description": "A content plan with invalid parameters for testing error handling.",
            "objectives": [
                "Test system response to invalid content type",
                "Verify error handling for unknown audience level"
            ]
        },
        {
            "id": "plan_empty",
            "title": "",
            "content_type": config.ContentTypes.LEARNING_MODULE,
            "audience_level": config.AudienceLevels.BEGINNER,
            "mission_pillars": [],
            "description": "",
            "objectives": []
        }
    ]
    
    # Save content plans to files
    for plan in content_plans:
        file_path = os.path.join(config.CONTENT_PLANS_DIR, f"{plan['id']}.json")
        with open(file_path, 'w') as f:
            json.dump(plan, f, indent=2)
        print(f"Generated test content plan: {plan['id']}")
    
    return content_plans

def generate_test_source_data():
    """Generate test source data for source collection testing."""
    sources = [
        {
            "id": "source1",
            "title": "The state of AI in 2023: Generative AI's breakout year",
            "authors": ["McKinsey & Company"],
            "publication": "McKinsey Digital",
            "year": 2023,
            "url": "https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai-in-2023-generative-ais-breakout-year",
            "type": "industry_report",
            "content_snippet": "47% of organizations are using generative AI in at least one business function, according to our latest McKinsey Global Survey on AI."
        },
        {
            "id": "source2",
            "title": "Attention Is All You Need",
            "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit", "Llion Jones", "Aidan N. Gomez", "Łukasz Kaiser", "Illia Polosukhin"],
            "publication": "Advances in Neural Information Processing Systems",
            "year": 2017,
            "url": "https://arxiv.org/abs/1706.03762",
            "doi": "10.48550/arXiv.1706.03762",
            "type": "academic_paper",
            "content_snippet": "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely."
        },
        {
            "id": "source3",
            "title": "EU AI Act: A Risk-Based Approach to AI Regulation",
            "authors": ["European Commission"],
            "publication": "European Commission",
            "year": 2023,
            "url": "https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai",
            "type": "regulatory_document",
            "content_snippet": "The AI Act follows a risk-based approach, where AI systems are categorized based on the risk they pose to users."
        },
        {
            "id": "source4",
            "title": "Sustainable AI: Environmental Implications, Challenges and Opportunities",
            "authors": ["Emma Strubell", "Ananya Ganesh", "Andrew McCallum"],
            "publication": "ACM Conference on Fairness, Accountability, and Transparency",
            "year": 2020,
            "doi": "10.1145/3442188.3445922",
            "type": "academic_paper",
            "content_snippet": "Training a single large language model can emit as much carbon as five cars in their lifetimes."
        },
        {
            "id": "source5",
            "title": "Outdated AI Information",
            "authors": ["Legacy Researcher"],
            "publication": "Journal of Historical AI",
            "year": 2010,
            "url": "https://example.com/outdated",
            "type": "academic_paper",
            "content_snippet": "Neural networks will never be practical for commercial applications due to computational limitations."
        },
        {
            "id": "source6",
            "title": "Biased AI Research",
            "authors": ["Biased Author"],
            "publication": "Commercial AI Vendor Blog",
            "year": 2023,
            "url": "https://example.com/biased-research",
            "type": "blog_post",
            "content_snippet": "Our proprietary AI system outperforms all others by at least 200% on all benchmarks.",
            "bias_indicators": ["commercial interest", "no methodology details", "extreme claims"]
        },
        {
            "id": "source7",
            "title": "Anonymous AI Research",
            "authors": [],
            "publication": "Unknown Publisher",
            "year": 2022,
            "url": "",
            "type": "web_content",
            "content_snippet": "AI will replace 90% of all jobs within 5 years."
        },
        {
            "id": "source8",
            "title": "Malformed URL Source",
            "authors": ["Valid Researcher"],
            "publication": "Valid Journal",
            "year": 2023,
            "url": "htp:/malformed-url",
            "type": "academic_paper",
            "content_snippet": "This source has a malformed URL for testing error handling."
        }
    ]
    
    # Save sources to files
    for source in sources:
        file_path = os.path.join(config.SOURCE_DATA_DIR, f"{source['id']}.json")
        with open(file_path, 'w') as f:
            json.dump(source, f, indent=2)
        print(f"Generated test source data: {source['id']}")
    
    return sources

def generate_test_feedback():
    """Generate test feedback data for review testing."""
    feedback_data = [
        {
            "id": "feedback1",
            "content_id": "learning_module_1",
            "reviewer_id": "tech_reviewer1",
            "section": "Core Concepts",
            "feedback": "The explanation of transformer architecture is technically inaccurate. The attention mechanism description should be revised.",
            "severity": "high",
            "status": "open"
        },
        {
            "id": "feedback2",
            "content_id": "learning_module_1",
            "reviewer_id": "mission_reviewer1",
            "section": "Responsible AI & Sustainability in Practice",
            "feedback": "The section on environmental impact is well-written but could benefit from more specific examples of energy-efficient model deployment.",
            "severity": "medium",
            "status": "open"
        },
        {
            "id": "feedback3",
            "content_id": "case_study_1",
            "reviewer_id": "audience_reviewer1",
            "section": "Introduction & Context",
            "feedback": "The introduction assumes too much prior knowledge for an intermediate audience. Consider adding more background on RAG.",
            "severity": "medium",
            "status": "open"
        },
        {
            "id": "feedback4",
            "content_id": "case_study_1",
            "reviewer_id": "source_reviewer1",
            "section": "Results & Analysis",
            "feedback": "The claim about 40% efficiency improvement needs a citation. Also, the McKinsey source is cited incorrectly.",
            "severity": "high",
            "status": "open"
        }
    ]
    
    # Save feedback to files
    for feedback in feedback_data:
        file_path = os.path.join(config.USER_FEEDBACK_DIR, f"{feedback['id']}.json")
        with open(file_path, 'w') as f:
            json.dump(feedback, f, indent=2)
        print(f"Generated test feedback: {feedback['id']}")
    
    return feedback_data

def main():
    """Main function to set up the local test environment."""
    print("Setting up local test environment...")
    
    # Create test directories
    create_test_directories()
    
    # Generate test data
    generate_test_content_plans()
    generate_test_source_data()
    generate_test_feedback()
    
    # Set up local templates
    setup_local_templates()
    
    print("Local test environment setup complete!")

if __name__ == "__main__":
    main()
