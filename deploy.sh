#!/bin/bash

# to run this file - ./deploy.sh

# Stop the script if any command fails
set -e

echo "🚀 Starting Deployment..."

# 1. Pull the latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# 2. Rebuild and restart the stack.
# compose owns both the app and the postgres container and brings them up
# together; a plain "docker run" would start the app with no database attached.
echo "🏗️  Rebuilding and restarting containers..."
docker compose up -d --build

# 3. Show what came up
echo "📋 Container status:"
docker compose ps

echo "✅ Deployment Complete! Streamlit on :8501, FastAPI on :8502."
