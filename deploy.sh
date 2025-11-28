#!/bin/bash

# to run this file - ./deploy.sh
# git pass: ***REMOVED-GITHUB-TOKEN***

# Stop the script if any command fails
set -e

echo "🚀 Starting Deployment..."

# 1. Pull the latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# 2. Rebuild the Docker Image
echo "🏗️  Rebuilding Docker image..."
docker build -t health-app .

# 3. Stop & Remove Old Container
echo "🛑 Removing old container..."
# The '|| true' ensures the script continues even if the container doesn't exist yet
docker rm -f health-server || true

# 4. Start New Container
echo "▶️  Starting new container..."
docker run -d \
  --name health-server \
  --restart unless-stopped \
  -p 8080:8080 \
  -p 8501:8501 \
  --env-file .env \
  health-app

echo "✅ Deployment Complete! App is running."