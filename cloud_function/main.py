import json
import uuid
import base64
import datetime
from flask import jsonify
from google.cloud import firestore

# Import utility functions
from cloud_function.utils import (
    store_content_metadata,
    get_template,
    call_vertex_ai,
    publish_event
)

def initialize_content_creation(request):
    """
    HTTP Cloud Function that initializes the content creation process.

    Args:
        request (flask.Request): The request object.
    Returns:
        The response text, or any set of values that can be turned into a Response object.
    """
    # Log the function invocation
    print("Agentic AI Content Creation Triggered!")

    try:
        # Parse the request JSON
        request_json = request.get_json(silent=True)

        if not request_json:
            return jsonify({
                'status': 'error',
                'message': 'No request data provided'
            }), 400

        # Extract content creation parameters
        content_type = request_json.get('content_type')
        audience_level = request_json.get('audience_level')
        title = request_json.get('title')
        mission_pillars = request_json.get('mission_pillars', [])

        # Validate required parameters
        if not all([content_type, title]):
            return jsonify({
                'status': 'error',
                'message': 'Missing required parameters: content_type, title'
            }), 400

        # Generate a unique content ID
        content_id = f"{content_type.lower()}-{str(uuid.uuid4())[:8]}"

        # Create content metadata
        metadata = {
            'metadata': {
                'title': title,
                'type': content_type,
                'status': 'initialized',
                'created': datetime.datetime.now().isoformat(),
                'updated': datetime.datetime.now().isoformat(),
                'audience': audience_level,
                'mission_pillars': mission_pillars
            },
            'workflow': {
                'current_stage': 'template_selection',
                'stages_completed': [],
                'assigned_reviewers': []
            }
        }

        # Store content metadata in Firestore
        store_content_metadata(content_id, metadata)

        # Publish event to trigger the template selection process
        event_data = {
            'content_id': content_id,
            'action': 'select_template'
        }
        publish_event('content-creation-events', event_data)

        # Return success response
        return jsonify({
            'status': 'success',
            'message': 'Content creation initialized',
            'content_id': content_id
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"Error initializing content creation: {str(e)}"
        }), 500

def select_template(event, context):
    """
    Background Cloud Function that selects an appropriate template for content creation.

    Args:
        event (dict): The dictionary with data specific to this type of event.
        context (google.cloud.functions.Context): The Cloud Functions event metadata.
    Returns:
        None
    """
    # Log the function invocation
    print(f"Template selection triggered: {event}")

    try:
        # Parse the Pub/Sub message
        pubsub_message = base64.b64decode(event['data']).decode('utf-8')
        message_data = json.loads(pubsub_message)

        # Extract content ID
        content_id = message_data.get('content_id')

        if not content_id:
            print("Error: No content ID provided")
            return

        # Get content metadata from Firestore
        db = firestore.Client()
        content_ref = db.collection('content-items').document(content_id)
        content_data = content_ref.get().to_dict()

        if not content_data:
            print(f"Error: Content {content_id} not found")
            return

        # Extract content type and audience level
        content_type = content_data['metadata']['type']
        audience_level = content_data['metadata'].get('audience')

        # Get appropriate template
        template = get_template(content_type, audience_level)

        if not template:
            print(f"Error: No template found for {content_type}, {audience_level}")
            # Update content status
            content_ref.update({
                'metadata.status': 'error',
                'workflow.current_stage': 'template_selection_failed'
            })
            return

        # Update content with template information
        content_ref.update({
            'template': template,
            'metadata.status': 'template_selected',
            'workflow.current_stage': 'content_planning',
            'workflow.stages_completed': firestore.ArrayUnion(['template_selection']),
            'metadata.updated': datetime.datetime.now().isoformat()
        })

        # Publish event to trigger the content planning process
        event_data = {
            'content_id': content_id,
            'action': 'generate_content_plan'
        }
        publish_event('content-creation-events', event_data)

        print(f"Template selected for content {content_id}")

    except Exception as e:
        print(f"Error in template selection: {str(e)}")

def generate_content_plan(event, context):
    """
    Background Cloud Function that generates a content plan.

    Args:
        event (dict): The dictionary with data specific to this type of event.
        context (google.cloud.functions.Context): The Cloud Functions event metadata.
    Returns:
        None
    """
    # Log the function invocation
    print(f"Content plan generation triggered: {event}")

    try:
        # Parse the Pub/Sub message
        pubsub_message = base64.b64decode(event['data']).decode('utf-8')
        message_data = json.loads(pubsub_message)

        # Extract content ID
        content_id = message_data.get('content_id')

        if not content_id:
            print("Error: No content ID provided")
            return

        # Get content metadata from Firestore
        db = firestore.Client()
        content_ref = db.collection('content-items').document(content_id)
        content_data = content_ref.get().to_dict()

        if not content_data:
            print(f"Error: Content {content_id} not found")
            return

        # Extract content information
        title = content_data['metadata']['title']
        content_type = content_data['metadata']['type']
        audience_level = content_data['metadata'].get('audience')
        mission_pillars = content_data['metadata'].get('mission_pillars', [])
        template = content_data.get('template', {})

        # Generate content plan using Vertex AI
        prompt = f"""
        You are an expert content planner for the AI Community & Sustainability Hub.
        Create a detailed content plan for a {content_type} titled '{title}'.

        Audience level: {audience_level if audience_level else 'General'}
        Primary mission pillars: {', '.join(mission_pillars) if mission_pillars else 'None specified'}

        The content should follow this template structure:
        {json.dumps(template, indent=2)}

        Generate a comprehensive content plan that includes:
        1. Specific learning objectives (SMART goals)
        2. Key concepts to cover in each section
        3. Practical examples and applications
        4. Visual elements to include
        5. Source requirements (types of sources needed)
        6. Mission pillar integration points

        Format the response as a structured JSON object.
        """

        # Call Vertex AI to generate the content plan
        content_plan_text = call_vertex_ai(
            prompt=prompt,
            temperature=0.2,
            max_output_tokens=2048
        )

        # Parse the content plan as JSON
        try:
            content_plan = json.loads(content_plan_text)
        except json.JSONDecodeError:
            # If not valid JSON, store as raw text
            content_plan = {"raw_plan": content_plan_text}

        # Update content with the generated plan
        content_ref.update({
            'content.plan': content_plan,
            'metadata.status': 'plan_generated',
            'workflow.current_stage': 'section_population',
            'workflow.stages_completed': firestore.ArrayUnion(['content_planning']),
            'metadata.updated': datetime.datetime.now().isoformat()
        })

        # Publish event to trigger the section population process
        event_data = {
            'content_id': content_id,
            'action': 'populate_sections'
        }
        publish_event('content-creation-events', event_data)

        print(f"Content plan generated for content {content_id}")

    except Exception as e:
        print(f"Error in content plan generation: {str(e)}")

# HTTP entry point for the Cloud Function
def main(request):
    return initialize_content_creation(request)