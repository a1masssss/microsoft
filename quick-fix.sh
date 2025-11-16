#!/bin/bash

echo "🔧 Quick fix для backend..."

# Stop and remove backend
docker compose stop backend
docker compose rm -f backend

# Rebuild backend
echo "🔨 Rebuilding backend..."
docker compose build backend

# Start backend
echo "🚀 Starting backend..."
docker compose up -d backend

# Wait
echo "⏳ Waiting 15 seconds..."
sleep 15

# Check status
echo ""
echo "📊 Status:"
docker compose ps

echo ""
echo "📋 Backend logs:"
docker compose logs backend --tail 20

echo ""
echo "✅ Done! Check if backend is running above"
echo ""
echo "If backend is healthy, run: chmod +x get-ssl.sh && ./get-ssl.sh"

