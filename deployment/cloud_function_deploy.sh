#!/bin/bash

# Script to deploy Cloud Functions for the Agentic AI Content Creation system

# Set variables
PROJECT_ID="aivibe-content-creation"
REGION="us-central1"
CONTENT_BUCKET="aivibe-content"

# Create the content bucket if it doesn't exist
gsutil mb -p $PROJECT_ID -l $REGION gs://$CONTENT_BUCKET || true

# Deploy the initialize_content_creation function
gcloud functions deploy initialize-content-creation \
  --gen2 \
  --runtime=python39 \
  --region=$REGION \
  --source=./cloud_function \
  --entry-point=main \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,CONTENT_BUCKET=$CONTENT_BUCKET

# Deploy the select_template function
gcloud functions deploy select-template \
  --gen2 \
  --runtime=python39 \
  --region=$REGION \
  --source=./cloud_function \
  --entry-point=select_template \
  --trigger-topic=content-creation-events \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,CONTENT_BUCKET=$CONTENT_BUCKET

# Deploy the generate_content_plan function
gcloud functions deploy generate-content-plan \
  --gen2 \
  --runtime=python39 \
  --region=$REGION \
  --source=./cloud_function \
  --entry-point=generate_content_plan \
  --trigger-topic=content-creation-events \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,CONTENT_BUCKET=$CONTENT_BUCKET

echo "Cloud Functions deployed successfully!"
