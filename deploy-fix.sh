#!/bin/bash

set -e

echo "🚀 Django Backend Fix & SSL Setup Deployment"
echo "==========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on server
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    exit 1
fi

# Step 1: Stop containers
echo -e "${YELLOW}⏹️  Stopping all containers...${NC}"
docker compose down

# Step 2: Remove old backend image
echo -e "${YELLOW}🗑️  Removing old backend image...${NC}"
docker rmi microsoft-backend 2>/dev/null || echo "No old image to remove"

# Step 3: Create ACME challenge directory
echo -e "${YELLOW}📁 Creating ACME challenge directory...${NC}"
mkdir -p ./web/certbot/www/.well-known/acme-challenge
echo "test-acme-challenge-works" > ./web/certbot/www/.well-known/acme-challenge/test

# Step 4: Rebuild backend with no cache
echo -e "${YELLOW}🔨 Rebuilding backend (this may take a minute)...${NC}"
docker compose build --no-cache backend

# Step 5: Start all services
echo -e "${YELLOW}🚀 Starting all services...${NC}"
docker compose up -d

# Step 6: Wait for services
echo -e "${YELLOW}⏳ Waiting for services to initialize...${NC}"
sleep 10

# Step 7: Check container status
echo ""
echo -e "${GREEN}📊 Container Status:${NC}"
docker compose ps

# Step 8: Check backend logs
echo ""
echo -e "${GREEN}📋 Backend Logs (last 30 lines):${NC}"
docker compose logs backend --tail=30

# Step 9: Test ACME challenge
echo ""
echo -e "${GREEN}🔐 Testing ACME Challenge:${NC}"
DOMAIN=${DOMAIN_NAME:-mythicai.me}
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://$DOMAIN/.well-known/acme-challenge/test

# Step 10: Test if backend is responding
echo ""
echo -e "${GREEN}🏥 Testing Backend Health:${NC}"
sleep 2
curl -s http://localhost:8000/api/ || echo "Backend not responding yet, give it more time"

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Verify ACME challenge works:"
echo "   curl -I http://$DOMAIN/.well-known/acme-challenge/test"
echo ""
echo "2. If ACME challenge works, run SSL setup:"
echo "   ./setup-ssl.sh"
echo ""
echo "3. Monitor logs with:"
echo "   docker compose logs -f backend"

