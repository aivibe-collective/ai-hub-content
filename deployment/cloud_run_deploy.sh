#!/bin/bash

# Script to deploy Cloud Run services for the Agentic AI Content Creation system

# Set variables
PROJECT_ID="aivibe-content-creation"
REGION="us-central1"
CONTENT_BUCKET="aivibe-content"

# Build and deploy the research service
cd cloud_run/research_service

# Build the container image
gcloud builds submit --tag gcr.io/$PROJECT_ID/research-service

# Deploy the service
gcloud run deploy research-service \
  --image gcr.io/$PROJECT_ID/research-service \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,CONTENT_BUCKET=$CONTENT_BUCKET

echo "Cloud Run services deployed successfully!"
