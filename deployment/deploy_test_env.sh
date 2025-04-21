#!/bin/bash

# Script to deploy the test environment for the Agentic AI Content Creation system

# Set variables
TEST_PROJECT_ID="aivibe-content-creation-test"
TEST_REGION="us-central1"
TEST_CONTENT_BUCKET="aivibe-content-test"

# Check if the test project exists
project_exists=$(gcloud projects list --filter="PROJECT_ID:$TEST_PROJECT_ID" --format="value(PROJECT_ID)")
if [ -z "$project_exists" ]; then
    echo "Test project $TEST_PROJECT_ID does not exist. Please create it first."
    exit 1
fi

# Set the current project
gcloud config set project $TEST_PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable aiplatform.googleapis.com

# Create the test bucket if it doesn't exist
echo "Creating test bucket..."
gsutil mb -p $TEST_PROJECT_ID -l $TEST_REGION gs://$TEST_CONTENT_BUCKET || true

# Create Pub/Sub topics
echo "Creating Pub/Sub topics..."
gcloud pubsub topics create content-creation-events-test || true
gcloud pubsub topics create source-collection-events-test || true
gcloud pubsub topics create review-events-test || true

# Set up Firestore
echo "Setting up Firestore..."
# Check if Firestore is already initialized
firestore_initialized=$(gcloud firestore databases list --format="value(name)")
if [ -z "$firestore_initialized" ]; then
    gcloud firestore databases create --region=$TEST_REGION
fi

# Deploy the test Cloud Functions
echo "Deploying test Cloud Functions..."

# Deploy the initialize_content_creation function
gcloud functions deploy initialize-content-creation-test \
  --gen2 \
  --runtime=python39 \
  --region=$TEST_REGION \
  --source=./cloud_function \
  --entry-point=main \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars=PROJECT_ID=$TEST_PROJECT_ID,CONTENT_BUCKET=$TEST_CONTENT_BUCKET

# Deploy the select_template function
gcloud functions deploy select-template-test \
  --gen2 \
  --runtime=python39 \
  --region=$TEST_REGION \
  --source=./cloud_function \
  --entry-point=select_template \
  --trigger-topic=content-creation-events-test \
  --set-env-vars=PROJECT_ID=$TEST_PROJECT_ID,CONTENT_BUCKET=$TEST_CONTENT_BUCKET

# Deploy the generate_content_plan function
gcloud functions deploy generate-content-plan-test \
  --gen2 \
  --runtime=python39 \
  --region=$TEST_REGION \
  --source=./cloud_function \
  --entry-point=generate_content_plan \
  --trigger-topic=content-creation-events-test \
  --set-env-vars=PROJECT_ID=$TEST_PROJECT_ID,CONTENT_BUCKET=$TEST_CONTENT_BUCKET

# Deploy the research service
echo "Deploying test Research Service..."
cd cloud_run/research_service

# Build the container image
gcloud builds submit --tag gcr.io/$TEST_PROJECT_ID/research-service-test

# Deploy the service
gcloud run deploy research-service-test \
  --image gcr.io/$TEST_PROJECT_ID/research-service-test \
  --platform managed \
  --region $TEST_REGION \
  --allow-unauthenticated \
  --set-env-vars=PROJECT_ID=$TEST_PROJECT_ID,CONTENT_BUCKET=$TEST_CONTENT_BUCKET

cd ../..

# Set up test data
echo "Setting up test data..."
export SETUP_CLOUD_RESOURCES=true
python test/setup_test_env.py

echo "Test environment deployment complete!"
echo "Test API endpoint: https://$TEST_REGION-$TEST_PROJECT_ID.cloudfunctions.net/initialize-content-creation-test"
echo "Test Research Service: $(gcloud run services describe research-service-test --region=$TEST_REGION --format='value(status.url)')"
