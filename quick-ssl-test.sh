#!/bin/bash

# Quick diagnostic script for SSL setup

DOMAIN="mythicai.me"

echo "🔍 Quick SSL Diagnostic for $DOMAIN"
echo ""

# 1. Check DNS
echo "1️⃣  Checking DNS..."
DNS_IP=$(dig +short $DOMAIN | tail -1)
if [ -z "$DNS_IP" ]; then
    echo "   ❌ DNS not resolving!"
else
    echo "   ✅ DNS resolves to: $DNS_IP"
fi
echo ""

# 2. Check HTTP accessibility
echo "2️⃣  Checking HTTP accessibility..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN" --max-time 5 || echo "000")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "   ✅ HTTP is accessible (HTTP $HTTP_CODE)"
else
    echo "   ❌ HTTP returned: $HTTP_CODE"
fi
echo ""

# 3. Check ACME challenge endpoint
echo "3️⃣  Checking ACME challenge endpoint..."
ACME_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN/.well-known/acme-challenge/test" --max-time 5 || echo "000")
if [ "$ACME_CODE" = "404" ]; then
    echo "   ✅ ACME endpoint is accessible (404 is OK - file doesn't exist yet)"
elif [ "$ACME_CODE" = "200" ]; then
    echo "   ✅ ACME endpoint is accessible (200 - file exists)"
else
    echo "   ⚠️  ACME endpoint returned: $ACME_CODE"
fi
echo ""

# 4. Check nginx container
echo "4️⃣  Checking nginx container..."
if docker compose ps web | grep -q "Up"; then
    echo "   ✅ Nginx container is running"
else
    echo "   ❌ Nginx container is not running!"
fi
echo ""

# 5. Check certbot directory in container
echo "5️⃣  Checking certbot directory in nginx container..."
if docker compose exec -T web test -d /var/www/certbot 2>/dev/null; then
    echo "   ✅ /var/www/certbot directory exists"
    docker compose exec -T web ls -la /var/www/certbot/ 2>/dev/null | head -5
else
    echo "   ❌ /var/www/certbot directory not found!"
fi
echo ""

# 6. Check if certificates already exist
echo "6️⃣  Checking for existing certificates..."
if docker compose exec -T web test -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" 2>/dev/null; then
    echo "   ✅ Certificates already exist!"
    docker compose exec -T web ls -la "/etc/letsencrypt/live/$DOMAIN/" 2>/dev/null
else
    echo "   ℹ️  No certificates found (this is OK for first setup)"
fi
echo ""

# 7. Check nginx config
echo "7️⃣  Checking nginx configuration..."
if docker compose exec -T web nginx -t 2>&1 | grep -q "successful"; then
    echo "   ✅ Nginx configuration is valid"
else
    echo "   ❌ Nginx configuration has errors!"
    docker compose exec -T web nginx -t 2>&1
fi
echo ""

echo "📋 Summary:"
echo "   If all checks pass, you can run: ./fix-ssl.sh"
echo "   If ACME endpoint fails, check nginx logs: docker compose logs web | tail -20"

