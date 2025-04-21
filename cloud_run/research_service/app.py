import os
import json
import requests
from flask import Flask, request, jsonify
from google.cloud import firestore
from google.cloud import storage
import vertexai
from vertexai.language_models import TextGenerationModel

# Initialize Flask app
app = Flask(__name__)

# Initialize Firestore client
db = firestore.Client()

# Initialize Vertex AI
project_id = os.environ.get('PROJECT_ID', 'aivibe-content-creation')
location = os.environ.get('LOCATION', 'us-central1')
vertexai.init(project=project_id, location=location)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200

@app.route('/identify-source-needs', methods=['POST'])
def identify_source_needs():
    """
    Identifies statements in content that require citations.
    
    Request JSON:
    {
        "content_id": "string",
        "content_text": "string"
    }
    """
    # Get request data
    request_data = request.get_json()
    
    if not request_data:
        return jsonify({'error': 'No request data provided'}), 400
    
    content_id = request_data.get('content_id')
    content_text = request_data.get('content_text')
    
    if not content_id or not content_text:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Use Vertex AI to identify statements needing citations
    prompt = f"""
    You are an expert research assistant for the AI Community & Sustainability Hub.
    
    Analyze the following content and identify statements that require citations.
    For each statement requiring a citation, extract the statement and categorize it by type
    (statistical, conceptual, methodological, case example, etc.).
    
    Content:
    {content_text}
    
    Format your response as a JSON array of objects with the following structure:
    [
      {{
        "statement": "The exact statement that needs citation",
        "type": "statistical|conceptual|methodological|case_example|other",
        "context": "Brief description of where this appears in the content",
        "requirements": {{
          "recency": "How recent the source should be (e.g., 'Last 2 years')",
          "authority": "Type of authority needed (e.g., 'Academic', 'Industry report')",
          "specific_needs": "Any specific requirements for this source"
        }}
      }}
    ]
    """
    
    # Call Vertex AI
    model = TextGenerationModel.from_pretrained("text-bison@002")
    response = model.predict(
        prompt=prompt,
        temperature=0.2,
        max_output_tokens=2048
    )
    
    # Parse the response
    try:
        source_needs = json.loads(response.text)
    except json.JSONDecodeError:
        # If not valid JSON, try to extract JSON from the text
        try:
            # Look for JSON array in the response
            start_idx = response.text.find('[')
            end_idx = response.text.rfind(']') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response.text[start_idx:end_idx]
                source_needs = json.loads(json_str)
            else:
                raise ValueError("Could not extract JSON from response")
        except Exception as e:
            return jsonify({
                'error': f'Failed to parse source needs: {str(e)}',
                'raw_response': response.text
            }), 500
    
    # Store source needs in Firestore
    content_ref = db.collection('content-items').document(content_id)
    content_ref.update({
        'sources.needs': source_needs,
        'metadata.updated': firestore.SERVER_TIMESTAMP
    })
    
    return jsonify({
        'status': 'success',
        'source_needs': source_needs,
        'count': len(source_needs)
    })

@app.route('/research-sources', methods=['POST'])
def research_sources():
    """
    Researches potential sources for a given source need.
    
    Request JSON:
    {
        "content_id": "string",
        "source_need_index": int
    }
    """
    # Get request data
    request_data = request.get_json()
    
    if not request_data:
        return jsonify({'error': 'No request data provided'}), 400
    
    content_id = request_data.get('content_id')
    source_need_index = request_data.get('source_need_index')
    
    if not content_id or source_need_index is None:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Get content data from Firestore
    content_ref = db.collection('content-items').document(content_id)
    content_data = content_ref.get().to_dict()
    
    if not content_data or 'sources' not in content_data or 'needs' not in content_data['sources']:
        return jsonify({'error': 'Source needs not found for this content'}), 404
    
    # Get the specific source need
    source_needs = content_data['sources']['needs']
    if source_need_index >= len(source_needs):
        return jsonify({'error': 'Source need index out of range'}), 400
    
    source_need = source_needs[source_need_index]
    
    # Use Vertex AI to research potential sources
    prompt = f"""
    You are an expert research assistant for the AI Community & Sustainability Hub.
    
    Research potential sources for the following statement that needs citation:
    
    Statement: "{source_need['statement']}"
    Type: {source_need['type']}
    Requirements:
    - Recency: {source_need['requirements']['recency']}
    - Authority: {source_need['requirements']['authority']}
    - Specific needs: {source_need['requirements']['specific_needs']}
    
    Generate a list of 5 potential sources that would be appropriate for citing this statement.
    For each source, provide:
    1. Title
    2. Authors
    3. Publication/Publisher
    4. Year
    5. URL or DOI (if available)
    6. Brief description of why this source is appropriate
    
    Format your response as a JSON array of objects.
    """
    
    # Call Vertex AI
    model = TextGenerationModel.from_pretrained("text-bison@002")
    response = model.predict(
        prompt=prompt,
        temperature=0.2,
        max_output_tokens=2048
    )
    
    # Parse the response
    try:
        potential_sources = json.loads(response.text)
    except json.JSONDecodeError:
        # If not valid JSON, try to extract JSON from the text
        try:
            # Look for JSON array in the response
            start_idx = response.text.find('[')
            end_idx = response.text.rfind(']') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response.text[start_idx:end_idx]
                potential_sources = json.loads(json_str)
            else:
                raise ValueError("Could not extract JSON from response")
        except Exception as e:
            return jsonify({
                'error': f'Failed to parse potential sources: {str(e)}',
                'raw_response': response.text
            }), 500
    
    # Store potential sources in Firestore
    source_needs[source_need_index]['potential_sources'] = potential_sources
    content_ref.update({
        'sources.needs': source_needs,
        'metadata.updated': firestore.SERVER_TIMESTAMP
    })
    
    return jsonify({
        'status': 'success',
        'potential_sources': potential_sources,
        'count': len(potential_sources)
    })

@app.route('/evaluate-source', methods=['POST'])
def evaluate_source():
    """
    Evaluates a potential source using the CRAAP test.
    
    Request JSON:
    {
        "content_id": "string",
        "source_need_index": int,
        "source_index": int
    }
    """
    # Get request data
    request_data = request.get_json()
    
    if not request_data:
        return jsonify({'error': 'No request data provided'}), 400
    
    content_id = request_data.get('content_id')
    source_need_index = request_data.get('source_need_index')
    source_index = request_data.get('source_index')
    
    if not content_id or source_need_index is None or source_index is None:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Get content data from Firestore
    content_ref = db.collection('content-items').document(content_id)
    content_data = content_ref.get().to_dict()
    
    if not content_data or 'sources' not in content_data or 'needs' not in content_data['sources']:
        return jsonify({'error': 'Source needs not found for this content'}), 404
    
    # Get the specific source need and potential source
    source_needs = content_data['sources']['needs']
    if source_need_index >= len(source_needs):
        return jsonify({'error': 'Source need index out of range'}), 400
    
    source_need = source_needs[source_need_index]
    
    if 'potential_sources' not in source_need or source_index >= len(source_need['potential_sources']):
        return jsonify({'error': 'Source index out of range'}), 400
    
    source = source_need['potential_sources'][source_index]
    
    # Use Vertex AI to evaluate the source using CRAAP test
    prompt = f"""
    You are an expert source evaluator for the AI Community & Sustainability Hub.
    
    Evaluate the following source using the CRAAP test criteria:
    
    Source:
    - Title: {source['title']}
    - Authors: {source['authors']}
    - Publication/Publisher: {source['publication']}
    - Year: {source['year']}
    - URL/DOI: {source.get('url', 'Not provided')}
    
    Statement to be cited: "{source_need['statement']}"
    
    Apply the CRAAP test criteria:
    1. Currency: How recent is the information? Is it up-to-date for the topic?
    2. Relevance: How well does it address the specific information need?
    3. Authority: How credible is the author/publisher? Are they experts in the field?
    4. Accuracy: Is the information supported by evidence? Can it be verified?
    5. Purpose: Is the source objective or does it have a bias or agenda?
    
    For each criterion, provide a score from 1-5 (5 being the highest) and a brief justification.
    Also provide an overall score and recommendation.
    
    Format your response as a JSON object.
    """
    
    # Call Vertex AI
    model = TextGenerationModel.from_pretrained("text-bison@002")
    response = model.predict(
        prompt=prompt,
        temperature=0.2,
        max_output_tokens=2048
    )
    
    # Parse the response
    try:
        evaluation = json.loads(response.text)
    except json.JSONDecodeError:
        # If not valid JSON, try to extract JSON from the text
        try:
            # Look for JSON object in the response
            start_idx = response.text.find('{')
            end_idx = response.text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response.text[start_idx:end_idx]
                evaluation = json.loads(json_str)
            else:
                raise ValueError("Could not extract JSON from response")
        except Exception as e:
            return jsonify({
                'error': f'Failed to parse evaluation: {str(e)}',
                'raw_response': response.text
            }), 500
    
    # Store evaluation in Firestore
    source_needs[source_need_index]['potential_sources'][source_index]['evaluation'] = evaluation
    content_ref.update({
        'sources.needs': source_needs,
        'metadata.updated': firestore.SERVER_TIMESTAMP
    })
    
    return jsonify({
        'status': 'success',
        'evaluation': evaluation
    })

@app.route('/generate-citation', methods=['POST'])
def generate_citation():
    """
    Generates a citation for a selected source in the specified format.
    
    Request JSON:
    {
        "content_id": "string",
        "source_need_index": int,
        "source_index": int,
        "citation_style": "string" (e.g., "APA", "MLA", "Chicago", "IEEE")
    }
    """
    # Get request data
    request_data = request.get_json()
    
    if not request_data:
        return jsonify({'error': 'No request data provided'}), 400
    
    content_id = request_data.get('content_id')
    source_need_index = request_data.get('source_need_index')
    source_index = request_data.get('source_index')
    citation_style = request_data.get('citation_style', 'APA')
    
    if not content_id or source_need_index is None or source_index is None:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Get content data from Firestore
    content_ref = db.collection('content-items').document(content_id)
    content_data = content_ref.get().to_dict()
    
    if not content_data or 'sources' not in content_data or 'needs' not in content_data['sources']:
        return jsonify({'error': 'Source needs not found for this content'}), 404
    
    # Get the specific source need and potential source
    source_needs = content_data['sources']['needs']
    if source_need_index >= len(source_needs):
        return jsonify({'error': 'Source need index out of range'}), 400
    
    source_need = source_needs[source_need_index]
    
    if 'potential_sources' not in source_need or source_index >= len(source_need['potential_sources']):
        return jsonify({'error': 'Source index out of range'}), 400
    
    source = source_need['potential_sources'][source_index]
    
    # Use Vertex AI to generate citation
    prompt = f"""
    You are an expert citation generator for the AI Community & Sustainability Hub.
    
    Generate a citation for the following source in {citation_style} format:
    
    Source:
    - Title: {source['title']}
    - Authors: {source['authors']}
    - Publication/Publisher: {source['publication']}
    - Year: {source['year']}
    - URL/DOI: {source.get('url', 'Not provided')}
    
    Also generate an in-text citation example for this source.
    
    Format your response as a JSON object with the following structure:
    {{
      "reference": "The full reference for the reference list",
      "in_text_citation": "Example of in-text citation",
      "parenthetical_citation": "Example of parenthetical citation (if applicable)"
    }}
    """
    
    # Call Vertex AI
    model = TextGenerationModel.from_pretrained("text-bison@002")
    response = model.predict(
        prompt=prompt,
        temperature=0.2,
        max_output_tokens=1024
    )
    
    # Parse the response
    try:
        citation = json.loads(response.text)
    except json.JSONDecodeError:
        # If not valid JSON, try to extract JSON from the text
        try:
            # Look for JSON object in the response
            start_idx = response.text.find('{')
            end_idx = response.text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response.text[start_idx:end_idx]
                citation = json.loads(json_str)
            else:
                raise ValueError("Could not extract JSON from response")
        except Exception as e:
            return jsonify({
                'error': f'Failed to parse citation: {str(e)}',
                'raw_response': response.text
            }), 500
    
    # Store citation in Firestore
    source_needs[source_need_index]['potential_sources'][source_index]['citation'] = citation
    
    # If this is the first citation generated, create a references collection
    if 'references' not in content_data.get('sources', {}):
        content_ref.update({
            'sources.references': []
        })
    
    # Add the reference to the references collection if not already present
    reference_entry = {
        'source': source,
        'citation': citation,
        'source_need_index': source_need_index,
        'citation_style': citation_style
    }
    
    content_ref.update({
        'sources.needs': source_needs,
        'sources.references': firestore.ArrayUnion([reference_entry]),
        'metadata.updated': firestore.SERVER_TIMESTAMP
    })
    
    return jsonify({
        'status': 'success',
        'citation': citation
    })

@app.route('/integrate-source', methods=['POST'])
def integrate_source():
    """
    Generates text that integrates a source into the content.
    
    Request JSON:
    {
        "content_id": "string",
        "source_need_index": int,
        "source_index": int,
        "integration_type": "string" (e.g., "quote", "paraphrase", "summary")
    }
    """
    # Get request data
    request_data = request.get_json()
    
    if not request_data:
        return jsonify({'error': 'No request data provided'}), 400
    
    content_id = request_data.get('content_id')
    source_need_index = request_data.get('source_need_index')
    source_index = request_data.get('source_index')
    integration_type = request_data.get('integration_type', 'paraphrase')
    
    if not content_id or source_need_index is None or source_index is None:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Get content data from Firestore
    content_ref = db.collection('content-items').document(content_id)
    content_data = content_ref.get().to_dict()
    
    if not content_data or 'sources' not in content_data or 'needs' not in content_data['sources']:
        return jsonify({'error': 'Source needs not found for this content'}), 404
    
    # Get the specific source need and potential source
    source_needs = content_data['sources']['needs']
    if source_need_index >= len(source_needs):
        return jsonify({'error': 'Source need index out of range'}), 400
    
    source_need = source_needs[source_need_index]
    
    if 'potential_sources' not in source_need or source_index >= len(source_need['potential_sources']):
        return jsonify({'error': 'Source index out of range'}), 400
    
    source = source_need['potential_sources'][source_index]
    
    # Check if citation exists
    if 'citation' not in source:
        return jsonify({'error': 'Citation not generated for this source yet'}), 400
    
    # Use Vertex AI to generate integrated text
    prompt = f"""
    You are an expert content writer for the AI Community & Sustainability Hub.
    
    Generate text that integrates the following source into content about AI:
    
    Statement needing citation: "{source_need['statement']}"
    
    Source:
    - Title: {source['title']}
    - Authors: {source['authors']}
    - Publication/Publisher: {source['publication']}
    - Year: {source['year']}
    
    Citation:
    - Reference: {source['citation']['reference']}
    - In-text citation: {source['citation']['in_text_citation']}
    
    Integration type: {integration_type}
    
    Guidelines:
    - For "quote": Use a direct quote from the source with proper quotation marks and citation
    - For "paraphrase": Restate the information in your own words with proper citation
    - For "summary": Condense larger sections of information with proper citation
    
    Generate text that could be inserted directly into the content, with proper citation included.
    """
    
    # Call Vertex AI
    model = TextGenerationModel.from_pretrained("text-bison@002")
    response = model.predict(
        prompt=prompt,
        temperature=0.3,
        max_output_tokens=1024
    )
    
    # Store integrated text in Firestore
    source_needs[source_need_index]['integrated_text'] = response.text
    source_needs[source_need_index]['integration_type'] = integration_type
    source_needs[source_need_index]['selected_source_index'] = source_index
    
    content_ref.update({
        'sources.needs': source_needs,
        'metadata.updated': firestore.SERVER_TIMESTAMP
    })
    
    return jsonify({
        'status': 'success',
        'integrated_text': response.text,
        'integration_type': integration_type
    })

if __name__ == '__main__':
    # This is used when running locally
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
