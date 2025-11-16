#!/bin/bash

# Fix Django backend and rebuild everything
echo "🔧 Fixing Django backend..."

# Stop containers
echo "⏹️  Stopping containers..."
docker compose down

# Remove old backend image to force rebuild
echo "🗑️  Removing old backend image..."
docker rmi microsoft-backend 2>/dev/null || true

# Rebuild and start
echo "🔨 Rebuilding containers..."
docker compose build --no-cache backend

echo "🚀 Starting containers..."
docker compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 5

# Check status
echo "📊 Container status:"
docker compose ps

echo ""
echo "📋 Backend logs:"
docker compose logs backend --tail=20

echo ""
echo "✅ Done! Check if backend is running properly."
echo ""
echo "Test ACME challenge with:"
echo "curl -I http://mythicai.me/.well-known/acme-challenge/test"

