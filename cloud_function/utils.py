import os
from google.cloud import storage
from google.cloud import firestore

def create_hub_structure(base_directory, directory_list):
    """
    Creates the specified directory structure in Cloud Storage.

    Args:
        base_directory (str): The root directory name.
        directory_list (list): A list of subdirectories to create.
    """
    print(f"Creating directory structure under {base_directory}/")

    # Initialize Cloud Storage client
    storage_client = storage.Client()

    # Get the default bucket or specify a bucket name
    bucket_name = os.environ.get('CONTENT_BUCKET', 'aivibe-content')
    bucket = storage_client.bucket(bucket_name)

    # Create empty objects for each directory path to simulate directory structure
    for dir_path in directory_list:
        # Construct the full path with a trailing slash to indicate a directory
        full_path = os.path.join(base_directory, dir_path, '.keep')

        try:
            # Create an empty blob to represent the directory
            blob = bucket.blob(full_path)
            blob.upload_from_string('')
            print(f"Created: {full_path}")
        except Exception as e:
            print(f"Error creating directory {full_path}: {e}")

    return f"Created directory structure in bucket {bucket_name}"

def store_content_metadata(content_id, metadata):
    """
    Stores content metadata in Firestore.

    Args:
        content_id (str): Unique identifier for the content.
        metadata (dict): Metadata for the content item.

    Returns:
        str: Status message.
    """
    # Initialize Firestore client
    db = firestore.Client()

    # Reference to the content-items collection
    content_ref = db.collection('content-items').document(content_id)

    # Set the metadata
    content_ref.set(metadata)

    return f"Stored metadata for content {content_id}"

def get_template(template_type, audience_level):
    """
    Retrieves the appropriate template based on content type and audience level.

    Args:
        template_type (str): Type of content (e.g., 'LearningModule', 'CaseStudy').
        audience_level (str): Audience level (e.g., 'Beginner', 'Intermediate', 'Expert').

    Returns:
        dict: Template data.
    """
    # Initialize Firestore client
    db = firestore.Client()

    # Query for the template
    templates_ref = db.collection('templates')
    query = templates_ref.where('type', '==', template_type)

    if audience_level:
        query = query.where('audience_levels', 'array_contains', audience_level)

    templates = query.stream()

    # Get the first matching template
    for template in templates:
        return template.to_dict()

    # If no template found, return None
    return None

def call_vertex_ai(prompt, model="text-bison@002", temperature=0.2, max_output_tokens=1024):
    """
    Calls Vertex AI to generate content.

    Args:
        prompt (str): The prompt to send to the model.
        model (str): The model to use.
        temperature (float): The temperature for generation.
        max_output_tokens (int): Maximum tokens to generate.

    Returns:
        str: Generated content.
    """
    from vertexai.language_models import TextGenerationModel

    # Initialize the model
    generation_model = TextGenerationModel.from_pretrained(model)

    # Generate content
    response = generation_model.predict(
        prompt=prompt,
        temperature=temperature,
        max_output_tokens=max_output_tokens
    )

    return response.text

def publish_event(topic, event_data):
    """
    Publishes an event to Pub/Sub.

    Args:
        topic (str): The Pub/Sub topic to publish to.
        event_data (dict): The event data to publish.

    Returns:
        str: The message ID.
    """
    from google.cloud import pubsub_v1
    import json

    # Initialize the publisher client
    publisher = pubsub_v1.PublisherClient()

    # The topic path
    topic_path = publisher.topic_path(os.environ.get('PROJECT_ID'), topic)

    # Convert the event data to JSON
    data = json.dumps(event_data).encode('utf-8')

    # Publish the message
    future = publisher.publish(topic_path, data)

    return future.result()

def upload_content_to_storage(content_id, content_text, bucket_name=None):
    """
    Uploads content to Cloud Storage.

    Args:
        content_id (str): Unique identifier for the content.
        content_text (str): The content text to upload.
        bucket_name (str, optional): The bucket name. Defaults to environment variable.

    Returns:
        str: The GCS URI of the uploaded content.
    """
    # Initialize Cloud Storage client
    storage_client = storage.Client()

    # Get the bucket
    if not bucket_name:
        bucket_name = os.environ.get('CONTENT_BUCKET', 'aivibe-content')
    bucket = storage_client.bucket(bucket_name)

    # Create the blob
    blob_name = f"content/{content_id}.md"
    blob = bucket.blob(blob_name)

    # Upload the content
    blob.upload_from_string(content_text)

    return f"gs://{bucket_name}/{blob_name}"

def download_content_from_storage(content_id, bucket_name=None):
    """
    Downloads content from Cloud Storage.

    Args:
        content_id (str): Unique identifier for the content.
        bucket_name (str, optional): The bucket name. Defaults to environment variable.

    Returns:
        str: The content text.
    """
    # Initialize Cloud Storage client
    storage_client = storage.Client()

    # Get the bucket
    if not bucket_name:
        bucket_name = os.environ.get('CONTENT_BUCKET', 'aivibe-content')
    bucket = storage_client.bucket(bucket_name)

    # Get the blob
    blob_name = f"content/{content_id}.md"
    blob = bucket.blob(blob_name)

    # Download the content
    content_text = blob.download_as_text()

    return content_text

def get_template_by_id(template_id):
    """
    Retrieves a template by its ID.

    Args:
        template_id (str): The template ID.

    Returns:
        dict: Template data.

    Raises:
        ValueError: If the template is not found.
    """
    # Initialize Firestore client
    db = firestore.Client()

    # Get the template document
    template_ref = db.collection('templates').document(template_id)
    template_doc = template_ref.get()

    # Check if the template exists
    if not template_doc.exists:
        raise ValueError(f"Template {template_id} not found")

    # Return the template data
    return template_doc.to_dict()

def get_content_by_id(content_id):
    """
    Retrieves content by its ID.

    Args:
        content_id (str): The content ID.

    Returns:
        dict: Content data.

    Raises:
        ValueError: If the content is not found.
    """
    # Initialize Firestore client
    db = firestore.Client()

    # Get the content document
    content_ref = db.collection('content-items').document(content_id)
    content_doc = content_ref.get()

    # Check if the content exists
    if not content_doc.exists:
        raise ValueError(f"Content {content_id} not found")

    # Return the content data
    return content_doc.to_dict()