#!/bin/bash
# deploy.sh
# Deploys the FastAPI ADK backend to Google Cloud Run

# Usage: ./deploy.sh [PROJECT_ID]

PROJECT_ID=$1

if [ -z "$PROJECT_ID" ]
then
      echo "Error: Please provide your Google Cloud Project ID."
      echo "Usage: ./deploy.sh my-gcp-project-123"
      exit 1
fi

echo "Deploying to Google Cloud Run in project $PROJECT_ID..."
echo "This will containerize the app using buildpacks/Dockerfile and push to Artifact Registry."

gcloud run deploy live-ai-tutor \
  --source . \
  --project=$PROJECT_ID \
  --region=us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=us-central1"

echo "Deployment complete!"
