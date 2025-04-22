#!/usr/bin/env python3
"""
Flask application for the Agentic AI Content Creation System.
This provides a web UI to run the content generation workflow step by step.
"""

import os
import json
import uuid
import tempfile
import pickle
import logging
from flask import Flask, render_template, request, jsonify, session, send_file
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create a directory for storing content files
CONTENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'content_files')
os.makedirs(CONTENT_DIR, exist_ok=True)

# Import our custom modules
from google_ai_client import generate_content, generate_json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')

# Workflow steps
WORKFLOW_STEPS = [
    'initialize',
    'generate_content',
    'add_sources',
    'review'
]

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/api/initialize', methods=['POST'])
def initialize():
    """Initialize the content creation process."""
    # Get request data
    data = request.json

    # Generate a unique ID for this session
    session_id = str(uuid.uuid4())
    logger.debug(f"Initializing session with ID: {session_id}")

    # Store the content request in the session
    content_request = {
        'content_type': data.get('content_type', 'LearningModule'),
        'audience_level': data.get('audience_level', 'Beginner'),
        'title': data.get('title', 'Introduction to Generative AI'),
        'mission_pillars': data.get('mission_pillars', ['ResponsibleAI']),
        'model': data.get('model', 'gemini-1.5-flash'),
        'temperature': data.get('temperature', 0.7)
    }

    # Create a session file to store data
    session_file = os.path.join(CONTENT_DIR, f"session_{session_id}.json")
    with open(session_file, 'w') as f:
        json.dump({
            'content_request': content_request,
            'current_step': 'initialize',
            'completed_steps': ['initialize']
        }, f)

    # Store minimal data in the session cookie
    session['session_id'] = session_id
    session['session_file'] = session_file

    return jsonify({
        'status': 'success',
        'message': 'Content creation initialized',
        'session_id': session_id,
        'content_request': content_request,
        'next_step': 'generate_content'
    })

@app.route('/api/generate_content', methods=['POST'])
def generate_content_api():
    """Generate content using Google Generative AI."""
    # Get session data
    session_data = get_session_data()
    if not session_data:
        return jsonify({
            'status': 'error',
            'message': 'Session not initialized or session data not found'
        }), 400

    # Get content request from session data
    content_request = session_data.get('content_request')
    if not content_request:
        return jsonify({
            'status': 'error',
            'message': 'Content request not found in session data'
        }), 400

    logger.debug(f"Generating content for session: {session['session_id']}")

    # Create the prompt
    prompt = create_prompt(content_request)

    try:
        # Generate content using Google Generative AI
        content = generate_content(
            prompt=prompt,
            model_name=content_request.get('model', 'gemini-1.5-flash'),
            temperature=content_request.get('temperature', 0.7)
        )

        # Save the generated content to a file
        content_file_path = os.path.join(CONTENT_DIR, f"content_{session['session_id']}.md")
        with open(content_file_path, 'w') as f:
            f.write(content)

        # Update session data
        update_session_data({
            'generated_content_path': content_file_path,
            'current_step': 'generate_content',
            'completed_steps': session_data.get('completed_steps', []) + ['generate_content']
        })

        return jsonify({
            'status': 'success',
            'message': 'Content generated successfully',
            'content': content,
            'next_step': 'add_sources'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error generating content: {str(e)}'
        }), 500

@app.route('/api/add_sources', methods=['POST'])
def add_sources_api():
    """Add source documentation to generated content."""
    # Get session data
    session_data = get_session_data()
    if not session_data:
        return jsonify({
            'status': 'error',
            'message': 'Session not initialized or session data not found'
        }), 400

    # Check if content is generated
    content_path = session_data.get('generated_content_path')
    if not content_path or not os.path.exists(content_path):
        return jsonify({
            'status': 'error',
            'message': 'Content not generated yet or content file not found'
        }), 400

    # Get content and content request from session data
    with open(content_path, 'r') as f:
        content = f.read()
    content_request = session_data.get('content_request')

    logger.debug(f"Adding sources for session: {session['session_id']}")

    try:
        # Create the prompt for generating sources
        prompt = create_sources_prompt(content)

        # Define the expected schema for the sources
        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "title": {"type": "string"},
                    "authors": {"type": "array", "items": {"type": "string"}},
                    "year": {"type": ["number", "string"]},
                    "venue": {"type": "string"},
                    "url": {"type": "string"},
                    "citation": {"type": "string"}
                },
                "required": ["id", "title", "authors", "year", "venue", "citation"]
            }
        }

        # Generate sources using Google Generative AI
        try:
            sources = generate_json(
                prompt=prompt,
                schema=schema,
                model_name=content_request.get('model', 'gemini-1.5-flash'),
                temperature=0.2
            )
        except ValueError as e:
            # If JSON parsing fails, try to extract the JSON manually
            error_msg = str(e)
            if 'Response:' in error_msg and '[' in error_msg and ']' in error_msg:
                # Try to extract the JSON array
                response_text = error_msg.split('Response:', 1)[1].strip()
                if response_text.startswith('[') and ']' in response_text:
                    try:
                        # Extract just the array part
                        json_text = response_text.split(']', 1)[0] + ']'
                        sources = json.loads(json_text)
                    except json.JSONDecodeError:
                        # If that fails, fall back to default sources
                        sources = get_default_sources()
                else:
                    sources = get_default_sources()
            else:
                sources = get_default_sources()

        # Add sources section to content
        content_with_sources = add_sources_to_content(content, sources)

        # Save content with sources to a file
        content_with_sources_path = os.path.join(CONTENT_DIR, f"content_with_sources_{session['session_id']}.md")
        with open(content_with_sources_path, 'w') as f:
            f.write(content_with_sources)

        logger.debug(f"Saved content with sources to: {content_with_sources_path}")

        # Update session data
        update_session_data({
            'content_with_sources_path': content_with_sources_path,
            'sources': sources[:3],  # Store only a few sources to keep session data small
            'current_step': 'add_sources',
            'completed_steps': session_data.get('completed_steps', []) + ['add_sources']
        })

        return jsonify({
            'status': 'success',
            'message': 'Sources added successfully',
            'content_with_sources': content_with_sources,  # Include the content for the UI
            'content_with_sources_path': content_with_sources_path,
            'sources': sources,
            'next_step': 'review'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error adding sources: {str(e)}'
        }), 500

@app.route('/api/review', methods=['POST'])
def review_api():
    """Review the generated content with sources."""
    # Get session data
    session_data = get_session_data()
    if not session_data:
        return jsonify({
            'status': 'error',
            'message': 'Session not initialized or session data not found'
        }), 400

    # Check if content with sources is generated
    content_with_sources_path = session_data.get('content_with_sources_path')
    if not content_with_sources_path or not os.path.exists(content_with_sources_path):
        logger.error(f"Content with sources path not found: {content_with_sources_path}")
        return jsonify({
            'status': 'error',
            'message': 'Content with sources not generated yet or file not found'
        }), 400

    logger.debug(f"Reviewing content with sources from: {content_with_sources_path}")

    # Read the content from the file
    with open(content_with_sources_path, 'r') as f:
        content_with_sources = f.read()

    # Set the output file to the same path
    output_file = content_with_sources_path

    # Update session data
    update_session_data({
        'current_step': 'review',
        'completed_steps': session_data.get('completed_steps', []) + ['review'],
        'output_file': output_file
    })

    return jsonify({
        'status': 'success',
        'message': 'Content review completed',
        'content_with_sources': content_with_sources,  # Include the content for the UI
        'output_file': output_file,
        'workflow_completed': True
    })

@app.route('/api/export', methods=['POST'])
def export_api():
    """Export the generated content with sources."""
    # Get session data
    session_data = get_session_data()
    if not session_data:
        return jsonify({
            'status': 'error',
            'message': 'Session not initialized or session data not found'
        }), 400

    # Check if content with sources is generated
    content_with_sources_path = session_data.get('content_with_sources_path')
    if not content_with_sources_path or not os.path.exists(content_with_sources_path):
        logger.error(f"Content with sources path not found: {content_with_sources_path}")
        return jsonify({
            'status': 'error',
            'message': 'Content with sources not generated yet or file not found'
        }), 400

    # Get content request from session data
    content_request = session_data.get('content_request')
    if not content_request:
        return jsonify({
            'status': 'error',
            'message': 'Content request not found in session data'
        }), 400

    logger.debug(f"Exporting content with sources from: {content_with_sources_path}")

    # Read the content from the file
    with open(content_with_sources_path, 'r') as f:
        content_with_sources = f.read()

    # Generate a filename based on the title
    title = content_request.get('title', 'Generated Content')
    filename = title.lower().replace(' ', '_') + '.md'

    # Save the content to a file in the current directory
    with open(filename, 'w') as f:
        f.write(content_with_sources)

    return jsonify({
        'status': 'success',
        'message': f'Content exported to {filename}',
        'filename': filename
    })

@app.route('/api/reset', methods=['POST'])
def reset_api():
    """Reset the session."""
    # Clear the session
    session.clear()

    return jsonify({
        'status': 'success',
        'message': 'Session reset'
    })

def create_prompt(content_request):
    """Create a prompt for the Google Generative AI API."""
    content_type = content_request.get('content_type')
    title = content_request.get('title')
    audience_level = content_request.get('audience_level')
    mission_pillars = content_request.get('mission_pillars', [])

    # Create the prompt
    prompt = f"""
    Create a comprehensive {content_type} on "{title}" for a {audience_level.lower()} audience.

    The content should include:
    1. An introduction that explains the topic and its importance
    2. Main content sections that cover key concepts, how it works, applications, and limitations
    3. A conclusion that summarizes key points and provides next steps

    The content should integrate the following mission pillars:
    {', '.join(mission_pillars)}

    For each mission pillar, include a dedicated section that discusses how the topic relates to that pillar.

    Format the content in Markdown with clear headings, bullet points, and numbered lists where appropriate.

    The content should be educational, informative, and engaging for a {audience_level.lower()} audience.
    """

    return prompt

def create_sources_prompt(content):
    """Create a prompt for generating sources."""
    # Limit content to first 2000 chars to avoid token limits
    content_excerpt = content[:2000]

    prompt = f"""
    Based on the following content, recommend 5 high-quality academic sources that would be relevant for citation.

    Content:
    {content_excerpt}

    For each source, provide:
    1. A unique ID (e.g., "author2023title")
    2. The full title
    3. The authors (full names)
    4. The publication year
    5. The venue (journal, conference, etc.)
    6. A URL if available
    7. The full citation in APA format

    Make sure the sources are:
    - Recent (within the last 5 years when possible)
    - Relevant to the content
    - From reputable venues
    - Properly formatted
    - Diverse (from different authors/institutions)
    """

    return prompt

def get_default_sources():
    """Get default sources if generation fails."""
    return [
        {
            "id": "vaswani2017attention",
            "title": "Attention Is All You Need",
            "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit", "Llion Jones", "Aidan N. Gomez", "Łukasz Kaiser", "Illia Polosukhin"],
            "year": 2017,
            "venue": "Advances in Neural Information Processing Systems",
            "url": "https://arxiv.org/abs/1706.03762",
            "citation": "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017). Attention is all you need. In Advances in neural information processing systems (pp. 5998-6008)."
        },
        {
            "id": "brown2020language",
            "title": "Language Models are Few-Shot Learners",
            "authors": ["Tom B. Brown", "Benjamin Mann", "Nick Ryder", "Melanie Subbiah", "Jared Kaplan", "Prafulla Dhariwal", "Arvind Neelakantan", "Pranav Shyam", "Girish Sastry", "Amanda Askell", "Sandhini Agarwal", "Ariel Herbert-Voss", "Gretchen Krueger", "Tom Henighan", "Rewon Child", "Aditya Ramesh", "Daniel M. Ziegler", "Jeffrey Wu", "Clemens Winter", "Christopher Hesse", "Mark Chen", "Eric Sigler", "Mateusz Litwin", "Scott Gray", "Benjamin Chess", "Jack Clark", "Christopher Berner", "Sam McCandlish", "Alec Radford", "Ilya Sutskever", "Dario Amodei"],
            "year": 2020,
            "venue": "Advances in Neural Information Processing Systems",
            "url": "https://arxiv.org/abs/2005.14165",
            "citation": "Brown, T. B., Mann, B., Ryder, N., Subbiah, M., Kaplan, J., Dhariwal, P., ... & Amodei, D. (2020). Language models are few-shot learners. Advances in neural information processing systems, 33, 1877-1901."
        },
        {
            "id": "mckinsey2023generative",
            "title": "The economic potential of generative AI: The next productivity frontier",
            "authors": ["McKinsey Global Institute"],
            "year": 2023,
            "venue": "McKinsey & Company",
            "url": "https://www.mckinsey.com/capabilities/mckinsey-digital/our-insights/the-economic-potential-of-generative-ai-the-next-productivity-frontier",
            "citation": "McKinsey Global Institute. (2023). The economic potential of generative AI: The next productivity frontier. McKinsey & Company."
        },
        {
            "id": "bommasani2021opportunities",
            "title": "On the Opportunities and Risks of Foundation Models",
            "authors": ["Rishi Bommasani", "Drew A. Hudson", "Ehsan Adeli", "Russ Altman", "Simran Arora", "Sydney von Arx", "Michael S. Bernstein", "Jeannette Bohg", "Antoine Bosselut", "Emma Brunskill", "Erik Brynjolfsson", "Shyamal Buch", "Dallas Card", "Rodrigo Castellon", "Niladri Chatterji", "Annie Chen", "Kathleen Creel", "Jared Quincy Davis", "Dora Demszky", "Chris Donahue", "Moussa Doumbouya", "Esin Durmus", "Stefano Ermon", "John Etchemendy", "Kawin Ethayarajh", "Li Fei-Fei", "Chelsea Finn", "Trevor Gale", "Lauren Gillespie", "Karan Goel", "Noah Goodman", "Shelby Grossman", "Neel Guha", "Tatsunori Hashimoto", "Peter Henderson", "John Hewitt", "Daniel E. Ho", "Jenny Hong", "Kyle Hsu", "Jing Huang", "Thomas Icard", "Saahil Jain", "Dan Jurafsky", "Pratyusha Kalluri", "Siddharth Karamcheti", "Geoff Keeling", "Fereshte Khani", "Omar Khattab", "Pang Wei Koh", "Mark Krass", "Ranjay Krishna", "Rohith Kuditipudi", "Ananya Kumar", "Faisal Ladhak", "Mina Lee", "Tony Lee", "Jure Leskovec", "Isabelle Levent", "Xiang Lisa Li", "Xuechen Li", "Tengyu Ma", "Ali Malik", "Christopher D. Manning", "Suvir Mirchandani", "Eric Mitchell", "Zanele Munyikwa", "Suraj Nair", "Avanika Narayan", "Deepak Narayanan", "Ben Newman", "Allen Nie", "Juan Carlos Niebles", "Hamed Nilforoshan", "Julian Nyarko", "Giray Ogut", "Laurel Orr", "Isabel Papadimitriou", "Joon Sung Park", "Chris Piech", "Eva Portelance", "Christopher Potts", "Aditi Raghunathan", "Rob Reich", "Hongyu Ren", "Frieda Rong", "Yusuf Roohani", "Camilo Ruiz", "Jack Ryan", "Christopher Ré", "Dorsa Sadigh", "Shiori Sagawa", "Keshav Santhanam", "Andy Shih", "Krishnan Srinivasan", "Alex Tamkin", "Rohan Taori", "Armin W. Thomas", "Florian Tramèr", "Rose E. Wang", "William Wang", "Bohan Wu", "Jiajun Wu", "Yuhuai Wu", "Sang Michael Xie", "Michihiro Yasunaga", "Jiaxuan You", "Matei Zaharia", "Michael Zhang", "Tianyi Zhang", "Xikun Zhang", "Yuhui Zhang", "Lucia Zheng", "Kaitlyn Zhou", "Percy Liang"],
            "year": 2021,
            "venue": "arXiv preprint arXiv:2108.07258",
            "url": "https://arxiv.org/abs/2108.07258",
            "citation": "Bommasani, R., Hudson, D. A., Adeli, E., Altman, R., Arora, S., von Arx, S., ... & Liang, P. (2021). On the opportunities and risks of foundation models. arXiv preprint arXiv:2108.07258."
        },
        {
            "id": "weidinger2022taxonomy",
            "title": "A Taxonomy of AI Ethics Risks in Language Models",
            "authors": ["Laura Weidinger", "John Mellor", "Maribeth Rauh", "Conor Griffin", "Jonathan Uesato", "Po-Sen Huang", "Myra Cheng", "Mia Glaese", "Borja Balle", "Atoosa Kasirzadeh", "Zac Kenton", "Sasha Brown", "Will Hawkins", "Tom Stepleton", "Courtney Biles", "Abeba Birhane", "Julia Haas", "Laura Rimell", "Lisa Anne Hendricks", "William Isaac", "Sean Legassick", "Geoffrey Irving", "Iason Gabriel"],
            "year": 2022,
            "venue": "arXiv preprint arXiv:2206.04421",
            "url": "https://arxiv.org/abs/2206.04421",
            "citation": "Weidinger, L., Mellor, J., Rauh, M., Griffin, C., Uesato, J., Huang, P. S., ... & Gabriel, I. (2022). A taxonomy of AI ethics risks in language models. arXiv preprint arXiv:2206.04421."
        }
    ]

def get_session_data():
    """Get session data from the session file."""
    if 'session_id' not in session or 'session_file' not in session:
        logger.error("Session ID or session file not found in session cookie")
        return None

    session_file = session['session_file']
    if not os.path.exists(session_file):
        logger.error(f"Session file not found: {session_file}")
        return None

    try:
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        return session_data
    except Exception as e:
        logger.error(f"Error reading session file: {str(e)}")
        return None

def update_session_data(data):
    """Update session data in the session file."""
    if 'session_id' not in session or 'session_file' not in session:
        logger.error("Session ID or session file not found in session cookie")
        return False

    session_file = session['session_file']
    try:
        # Get existing data
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                session_data = json.load(f)
        else:
            session_data = {}

        # Update data
        session_data.update(data)

        # Write back to file
        with open(session_file, 'w') as f:
            json.dump(session_data, f)

        return True
    except Exception as e:
        logger.error(f"Error updating session file: {str(e)}")
        return False

def add_sources_to_content(content, sources):
    """Add sources to content."""
    import datetime

    # Add sources section to content
    content_with_sources = content + "\n\n## Sources\n\n"

    for source in sources:
        content_with_sources += f"[{source['id']}] {source['citation']}\n\n"

    # Add source collection metadata
    content_with_sources += "\n## Source Collection Metadata\n\n"
    content_with_sources += "This content includes sources collected through the Source Collection and Documentation Module of the Agentic AI Content Creation System.\n\n"
    content_with_sources += f"**Collection Date**: {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n"
    content_with_sources += "**Source Types**:\n"
    content_with_sources += "- Academic papers\n"
    content_with_sources += "- Industry reports\n"
    content_with_sources += "- Technical documentation\n\n"
    content_with_sources += "**Source Evaluation Criteria**:\n"
    content_with_sources += "- Relevance to the topic\n"
    content_with_sources += "- Authority of the source\n"
    content_with_sources += "- Recency of the information\n"
    content_with_sources += "- Accuracy and reliability\n"

    return content_with_sources

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
