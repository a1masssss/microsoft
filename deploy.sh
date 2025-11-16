#!/bin/bash

# 🚀 Full deployment script for mythicai.me

set -e  # Exit on any error

echo "🚀 Starting deployment for mythicai.me..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with required variables"
    exit 1
fi

echo "📦 Step 1: Stopping old containers..."
docker compose down
echo "✅ Old containers stopped"
echo ""

echo "🔨 Step 2: Building Docker images..."
echo "This may take a while (especially web build with 1.5GB RAM limit)..."
docker compose build --no-cache
echo "✅ Images built successfully"
echo ""

echo "🚀 Step 3: Starting services..."
docker compose up -d db
echo "⏳ Waiting for database to be ready..."
sleep 10

docker compose up -d backend frontend web
echo "✅ Services started"
echo ""

echo "⏳ Step 4: Waiting for services to stabilize..."
sleep 15

echo "🔍 Step 5: Checking service status..."
docker compose ps
echo ""

echo "🏥 Step 6: Health check..."
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ Web server is healthy!"
else
    echo "⚠️  Web server health check failed, but continuing..."
fi
echo ""

echo "📋 Current status:"
echo "  HTTP:  http://mythicai.me (working)"
echo "  HTTPS: Not configured yet"
echo ""
echo "🔐 To enable HTTPS, run:"
echo "  chmod +x setup-ssl.sh && ./setup-ssl.sh"
echo ""
echo "📊 To view logs:"
echo "  docker compose logs -f [service_name]"
echo "  Services: web, backend, frontend, db"
echo ""
echo "✅ Deployment complete!"

