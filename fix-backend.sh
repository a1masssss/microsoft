#!/bin/bash

echo "🔍 Checking backend logs..."
docker compose logs backend --tail 30

echo ""
echo "🔧 Rebuilding backend with correct structure..."

# Stop backend
docker compose stop backend

# Remove old backend image
docker compose rm -f backend

# Rebuild backend
docker compose build backend

# Start backend
docker compose up -d backend

echo ""
echo "⏳ Waiting 10 seconds for backend to start..."
sleep 10

echo ""
echo "🔍 Checking backend status..."
docker compose ps backend

echo ""
echo "📋 Recent backend logs:"
docker compose logs backend --tail 20

