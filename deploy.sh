#!/bin/bash
# deploy.sh — Deploys the unified Live AI Tutor to Google Cloud Run
# Usage: ./deploy.sh
#
# Required env vars (or set inline):
#   GOOGLE_API_KEY          — Gemini API key for the backend
#   VITE_GEMINI_API_KEY     — Gemini API key baked into the frontend build

set -euo pipefail

PROJECT_ID="live-ai-tutor"
REGION="us-central1"
SERVICE_NAME="live-homework-tutor"

# Use env vars or fall back to the backend .env file
if [ -z "${GOOGLE_API_KEY:-}" ] && [ -f backend/.env ]; then
    export $(grep -v '^#' backend/.env | xargs)
fi

if [ -z "${VITE_GEMINI_API_KEY:-}" ]; then
    VITE_GEMINI_API_KEY="${GOOGLE_API_KEY}"
fi

if [ -z "${GOOGLE_API_KEY:-}" ]; then
    echo "Error: GOOGLE_API_KEY is not set. Export it or add it to backend/.env"
    exit 1
fi

echo "=== Deploying $SERVICE_NAME to Cloud Run ==="
echo "Project:  $PROJECT_ID"
echo "Region:   $REGION"

gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_API_KEY=$GOOGLE_API_KEY,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$REGION" \
  --set-build-env-vars="VITE_GEMINI_API_KEY=$VITE_GEMINI_API_KEY" \
  --memory=1Gi \
  --timeout=300

echo ""
echo "=== Deployment complete! ==="
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --project="$PROJECT_ID" --region="$REGION" --format="value(status.url)")
echo "Live at: $SERVICE_URL"
