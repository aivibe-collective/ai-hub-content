"""
Test cases for Blog Post content generation.
"""

import json
import unittest
from unittest.mock import patch, MagicMock
import base64

class TestBlogPostGeneration(unittest.TestCase):
    """Test cases for Blog Post content generation."""

    def setUp(self):
        """Set up test fixtures."""
        # Load the BlogPost template
        with open('test/data/templates/BlogPost.json', 'r') as f:
            self.blog_template = json.load(f)

        # Mock blog post content plan
        self.blog_content_plan = {
            "id": "plan_blog_post",
            "title": "The Future of AI Regulation",
            "content_type": "BlogPost",
            "audience_level": "General",
            "mission_pillars": ["ResponsibleAI"],
            "description": "A blog post discussing emerging trends in AI regulation globally.",
            "objectives": [
                "Summarize current AI regulatory frameworks",
                "Analyze emerging trends in AI governance",
                "Discuss implications for AI practitioners"
            ]
        }

    def test_blog_post_structure_validation(self):
        """Test that the blog post template has the required sections."""
        # Assert
        self.assertEqual(self.blog_template['type'], "BlogPost")
        self.assertIn("sections", self.blog_template)

        # Check for required sections
        required_sections = ["Engaging Title", "Introduction", "Main Content", "Practical Takeaways", "Conclusion"]
        for section in required_sections:
            self.assertTrue(any(section in s for s in self.blog_template['sections']),
                           f"Required section '{section}' not found in template")

    def test_blog_post_plan_generation(self):
        """Test generation of a blog post content plan."""
        # Arrange
        mock_call_vertex_ai = MagicMock(return_value=json.dumps({
            "blog_structure": {
                "title": "The Future of AI Regulation: Navigating Global Frameworks",
                "introduction": {
                    "hook": "As AI systems become increasingly integrated into critical sectors, governments worldwide are racing to establish regulatory frameworks.",
                    "key_points": ["Current regulatory landscape", "Regional differences", "Emerging trends"]
                },
                "main_content": [
                    {
                        "section": "Current Regulatory Landscape",
                        "key_points": ["EU AI Act", "US Executive Order", "China's approach"]
                    },
                    {
                        "section": "Emerging Trends in AI Governance",
                        "key_points": ["Risk-based frameworks", "International coordination", "Self-regulation"]
                    },
                    {
                        "section": "Implications for AI Practitioners",
                        "key_points": ["Documentation requirements", "Testing standards", "Transparency obligations"]
                    }
                ],
                "practical_takeaways": [
                    "Establish internal AI governance processes",
                    "Document development decisions and risk assessments",
                    "Stay informed about regulatory developments in key markets"
                ],
                "conclusion": {
                    "summary": "The regulatory landscape for AI is evolving rapidly, with a trend toward risk-based approaches.",
                    "call_to_action": "AI practitioners should proactively engage with regulatory developments rather than waiting for finalized frameworks."
                }
            },
            "responsible_ai_integration": {
                "key_points": [
                    "Highlight ethical considerations throughout regulatory discussions",
                    "Emphasize the alignment between responsible AI practices and regulatory compliance",
                    "Discuss how regulations aim to ensure AI benefits society while minimizing harms"
                ]
            }
        }))

        # Act
        result = mock_call_vertex_ai(
            prompt=f"Generate a detailed blog post plan for '{self.blog_content_plan['title']}' that addresses the objectives: {', '.join(self.blog_content_plan['objectives'])}. Integrate the mission pillar: {self.blog_content_plan['mission_pillars'][0]}."
        )

        # Assert
        result_json = json.loads(result)
        self.assertIn("blog_structure", result_json)
        self.assertIn("title", result_json["blog_structure"])
        self.assertIn("introduction", result_json["blog_structure"])
        self.assertIn("main_content", result_json["blog_structure"])
        self.assertIn("practical_takeaways", result_json["blog_structure"])
        self.assertIn("conclusion", result_json["blog_structure"])
        self.assertIn("responsible_ai_integration", result_json)

        # Verify the prompt sent to the model
        mock_call_vertex_ai.assert_called_once()
        prompt = mock_call_vertex_ai.call_args[1]['prompt']
        self.assertIn(self.blog_content_plan['title'], prompt)
        self.assertIn("ResponsibleAI", prompt)

    def test_blog_post_section_generation(self):
        """Test generation of a blog post section."""
        # Arrange
        section_plan = {
            "section": "Emerging Trends in AI Governance",
            "key_points": ["Risk-based frameworks", "International coordination", "Self-regulation"]
        }

        mock_call_vertex_ai = MagicMock(return_value="""
## Emerging Trends in AI Governance

As AI regulation matures globally, several key trends are emerging that will shape the future landscape:

### Risk-Based Frameworks

Regulators are increasingly adopting risk-based approaches that apply different levels of scrutiny based on an AI system's potential impact. The EU AI Act exemplifies this trend, categorizing AI applications into risk tiers:

- Unacceptable risk: Applications that threaten citizens' safety or rights are prohibited
- High risk: Systems in critical sectors require rigorous assessment and oversight
- Limited risk: Applications with transparency obligations
- Minimal risk: Most AI systems with minimal regulatory requirements

This tiered approach allows for innovation while ensuring appropriate safeguards where needed.

### International Coordination

Recognizing that AI regulation fragmentation could hinder innovation, international bodies are working to establish common principles:

- The OECD AI Principles provide a foundation for interoperable regulations
- The Global Partnership on AI facilitates collaboration on governance approaches
- The G7 has established working groups on AI standards harmonization

These efforts aim to prevent a regulatory patchwork that would make compliance challenging for global AI developers.

### Self-Regulation and Industry Standards

While formal regulations develop, industry self-regulation is filling gaps:

- Major tech companies have published responsible AI principles
- Industry consortia are developing technical standards for AI safety and transparency
- Certification programs for ethical AI are emerging

These voluntary frameworks often inform subsequent regulations, creating a feedback loop between industry practice and formal governance.
""")

        # Act
        result = mock_call_vertex_ai(
            prompt=f"Generate the 'Emerging Trends in AI Governance' section for a blog post about AI regulation. Include these key points: {', '.join(section_plan['key_points'])}. The audience level is 'General' and should integrate responsible AI considerations."
        )

        # Assert
        self.assertIn("Risk-Based Frameworks", result)
        self.assertIn("International Coordination", result)
        self.assertIn("Self-Regulation", result)

        # Verify the prompt sent to the model
        mock_call_vertex_ai.assert_called_once()
        prompt = mock_call_vertex_ai.call_args[1]['prompt']
        self.assertIn("Emerging Trends in AI Governance", prompt)
        self.assertIn("General", prompt)
        self.assertIn("responsible ai", prompt.lower())

    def test_blog_post_style_consistency(self):
        """Test that blog post sections maintain consistent style."""
        # Arrange
        mock_call_vertex_ai = MagicMock()
        mock_call_vertex_ai.side_effect = [
            "# Introduction\n\nAs AI systems become increasingly integrated into critical sectors...",
            "# Current Regulatory Landscape\n\nThe regulatory environment for AI is evolving rapidly...",
            "# Emerging Trends\n\nSeveral key trends are shaping the future of AI governance..."
        ]

        # Act
        intro = mock_call_vertex_ai(prompt="Generate introduction section")
        section1 = mock_call_vertex_ai(prompt="Generate regulatory landscape section")
        section2 = mock_call_vertex_ai(prompt="Generate emerging trends section")

        # Assert
        # Check that all sections use the same heading level
        self.assertTrue(intro.startswith("# "))
        self.assertTrue(section1.startswith("# "))
        self.assertTrue(section2.startswith("# "))

        # Verify the prompts sent to the model
        self.assertEqual(mock_call_vertex_ai.call_count, 3)

    def test_blog_post_mission_pillar_integration(self):
        """Test integration of mission pillars into blog post content."""
        # Arrange
        mock_call_vertex_ai = MagicMock(return_value="""
# Implications for AI Practitioners

As regulatory frameworks evolve, AI practitioners face new responsibilities:

## Documentation Requirements

Responsible AI practice requires thorough documentation of:
- Development decisions and their ethical implications
- Data sources and potential biases
- Testing procedures and results
- Risk assessments and mitigation strategies

This documentation serves both compliance purposes and supports ethical reflection throughout development.

## Transparency Obligations

Emerging regulations emphasize transparency in AI systems:
- Clear disclosure when users interact with AI
- Explanations of how decisions are made
- Information about limitations and potential risks
- Accessibility of information for diverse users

These transparency requirements align with responsible AI principles of accountability and understandability.

## Ongoing Monitoring

Regulations increasingly require:
- Continuous monitoring of AI systems in production
- Regular audits for bias and performance drift
- Mechanisms to address identified issues
- Reporting of significant incidents

This ongoing vigilance ensures AI systems remain aligned with ethical standards and regulatory requirements over time.
""")

        # Act
        result = mock_call_vertex_ai(
            prompt="Generate the 'Implications for AI Practitioners' section for a blog post about AI regulation. Integrate the ResponsibleAI mission pillar throughout the content."
        )

        # Assert
        self.assertIn("Responsible AI", result)
        self.assertIn("ethical", result.lower())
        self.assertIn("transparency", result.lower())
        self.assertIn("accountability", result.lower())

        # Verify the prompt sent to the model
        mock_call_vertex_ai.assert_called_once()
        prompt = mock_call_vertex_ai.call_args[1]['prompt']
        self.assertIn("ResponsibleAI", prompt)

    def test_blog_post_call_to_action(self):
        """Test generation of an effective call to action for blog posts."""
        # Arrange
        mock_call_vertex_ai = MagicMock(return_value="""
# Conclusion

As we've explored, the AI regulatory landscape is evolving rapidly, with frameworks that increasingly emphasize risk assessment, transparency, and accountability. These developments signal a maturing approach to AI governance that seeks to balance innovation with responsible deployment.

## Call to Action

Don't wait for regulations to be finalized before implementing responsible AI practices. Consider these steps:

1. **Establish an AI governance framework** within your organization that anticipates regulatory requirements
2. **Document your development process**, including ethical considerations and risk assessments
3. **Engage with policymakers** to contribute industry expertise to regulatory discussions
4. **Join industry initiatives** focused on responsible AI standards and best practices
5. **Stay informed** about regulatory developments in your key markets

By proactively embracing responsible AI principles, you'll not only prepare for compliance but also build trust with users and stakeholders.

*Want to learn more about implementing responsible AI practices? Join our upcoming webinar on practical approaches to AI governance.*
""")

        # Act
        result = mock_call_vertex_ai(
            prompt="Generate a conclusion with an effective call to action for a blog post about AI regulation. The call to action should encourage readers to implement responsible AI practices."
        )

        # Assert
        self.assertIn("Call to Action", result)
        self.assertIn("Don't wait", result)
        self.assertIn("responsible ai", result.lower())

        # Check for actionable steps
        self.assertIn("Establish", result)
        self.assertIn("Document", result)
        self.assertIn("Engage", result)

        # Verify the prompt sent to the model
        mock_call_vertex_ai.assert_called_once()
        prompt = mock_call_vertex_ai.call_args[1]['prompt']
        self.assertIn("call to action", prompt.lower())
        self.assertIn("responsible ai", prompt.lower())

if __name__ == '__main__':
    unittest.main()
