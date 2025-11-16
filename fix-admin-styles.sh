#!/bin/bash

# Script to fix Django admin styles in production by adding WhiteNoise

set -e

echo "🔧 Fixing Django Admin Styles - Adding WhiteNoise Support"
echo "==========================================================="

# Check if we're on the production server
if [ -f "/etc/os-release" ]; then
    echo "✓ Running on production server"
else
    echo "⚠️  This script should be run on the production server"
fi

echo ""
echo "📋 Changes made:"
echo "  1. Added whitenoise==6.6.0 to requirements.txt"
echo "  2. Added WhiteNoiseMiddleware to Django settings"
echo "  3. Configured CompressedManifestStaticFilesStorage"
echo "  4. Updated Dockerfile CMD to run collectstatic on startup"
echo ""

# Navigate to project directory
cd ~/microsoft

echo "🛑 Stopping backend container..."
docker-compose stop backend

echo "🔨 Rebuilding backend container..."
docker-compose build --no-cache backend

echo "🚀 Starting backend container..."
docker-compose up -d backend

echo ""
echo "⏳ Waiting for backend to start..."
sleep 10

echo ""
echo "📊 Checking backend logs..."
docker-compose logs --tail=50 backend

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🔍 Testing admin styles:"
echo "   Visit: http://mythicai.me/admin/"
echo ""
echo "💡 If styles still don't load, run:"
echo "   docker-compose exec backend python manage.py collectstatic --noinput"
echo ""

