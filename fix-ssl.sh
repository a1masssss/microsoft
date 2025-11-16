#!/bin/bash

set -e

DOMAIN="mythicai.me"
EMAIL="admin@mythicai.me"

echo "🔧 Fixing SSL setup for $DOMAIN..."
echo ""

# Step 1: Ensure certbot directories exist
echo "📁 Creating certbot directories..."
mkdir -p web/certbot/www
chmod -R 755 web/certbot

# Step 2: Check if nginx is running
echo "🔍 Checking nginx container..."
if ! docker compose ps web | grep -q "Up"; then
    echo "❌ Nginx container is not running!"
    echo "Starting containers..."
    docker compose up -d web
    sleep 3
fi

# Step 3: Test ACME challenge endpoint
echo "🧪 Testing ACME challenge endpoint..."
TEST_FILE="web/certbot/www/test.txt"
echo "test" > "$TEST_FILE"
docker compose exec -T web sh -c "echo 'test' > /var/www/certbot/test.txt" || true

sleep 2

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN/.well-known/acme-challenge/test.txt" || echo "000")
if [ "$HTTP_CODE" != "200" ] && [ "$HTTP_CODE" != "404" ]; then
    echo "⚠️  Warning: ACME challenge endpoint returned HTTP $HTTP_CODE"
    echo "   This might be OK if the file doesn't exist yet"
else
    echo "✅ ACME challenge endpoint is accessible"
fi

# Step 4: Reload nginx to ensure config is correct
echo "🔄 Reloading nginx configuration..."
docker compose exec web nginx -t && docker compose exec web nginx -s reload || {
    echo "❌ Nginx configuration error!"
    docker compose exec web nginx -t
    exit 1
}

# Step 5: Stop the auto-renewal certbot container temporarily
echo "⏸️  Stopping auto-renewal certbot container..."
docker compose stop certbot 2>/dev/null || true

# Step 6: Delete old certificates if they exist and are invalid
echo "🗑️  Cleaning up old certificates (if any)..."
docker compose run --rm certbot delete --cert-name $DOMAIN 2>/dev/null || true

# Step 7: Get new certificates
echo ""
echo "🔐 Requesting SSL certificates from Let's Encrypt..."
echo "   Domain: $DOMAIN, www.$DOMAIN"
echo "   Email: $EMAIL"
echo ""
echo "⏳ This may take 30-60 seconds while Let's Encrypt verifies your domain..."
echo "   (Checking if http://$DOMAIN/.well-known/acme-challenge/ is accessible)"
echo ""

# Test ACME endpoint first
echo "🧪 Quick test of ACME endpoint..."
TEST_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN/.well-known/acme-challenge/test" 2>/dev/null || echo "000")
if [ "$TEST_RESPONSE" = "404" ] || [ "$TEST_RESPONSE" = "000" ]; then
    echo "   ⚠️  ACME endpoint test returned HTTP $TEST_RESPONSE (this might be OK)"
else
    echo "   ✅ ACME endpoint is accessible (HTTP $TEST_RESPONSE)"
fi
echo ""

docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --non-interactive \
    -d "$DOMAIN" \
    -d "www.$DOMAIN" \
    --verbose \
    2>&1 | tee /tmp/certbot-output.log

CERT_EXIT_CODE=$?

# Step 8: Restart auto-renewal certbot container
echo "▶️  Restarting auto-renewal certbot container..."
docker compose up -d certbot 2>/dev/null || true

if [ $CERT_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Certificates obtained successfully!"
    echo ""
    
    # Step 9: Verify certificates exist
    if docker compose exec web test -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem"; then
        echo "✅ Certificate files verified"
    else
        echo "❌ Certificate files not found in container!"
        exit 1
    fi
    
    # Step 10: Switch to SSL configuration
    echo "🔄 Switching to HTTPS configuration..."
    cp web/nginx.conf web/nginx-http-backup.conf 2>/dev/null || true
    cp web/nginx-ssl.conf web/nginx.conf
    
    # Step 11: Test nginx config and reload
    echo "🧪 Testing nginx SSL configuration..."
    docker compose exec web nginx -t || {
        echo "❌ Nginx SSL configuration is invalid!"
        echo "Restoring HTTP config..."
        cp web/nginx-http-backup.conf web/nginx.conf
        docker compose restart web
        exit 1
    }
    
    echo "🔄 Restarting nginx with SSL..."
    docker compose restart web
    
    sleep 3
    
    # Step 12: Test HTTPS
    echo "🧪 Testing HTTPS..."
    HTTPS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN" || echo "000")
    if [ "$HTTPS_CODE" = "200" ] || [ "$HTTPS_CODE" = "301" ] || [ "$HTTPS_CODE" = "302" ]; then
        echo "✅ HTTPS is working! (HTTP $HTTPS_CODE)"
    else
        echo "⚠️  HTTPS returned HTTP $HTTPS_CODE (might need a moment to propagate)"
    fi
    
    echo ""
    echo "🎉 SSL setup complete!"
    echo ""
    echo "Your site is now available at:"
    echo "   https://$DOMAIN"
    echo "   https://www.$DOMAIN"
    echo ""
    echo "HTTP will automatically redirect to HTTPS"
    echo ""
    echo "📝 Certificates will auto-renew every 12 hours"
else
    # Restart certbot even if failed
    docker compose up -d certbot 2>/dev/null || true
    
    echo ""
    echo "❌ Failed to obtain certificates!"
    echo ""
    echo "Troubleshooting steps:"
    echo "1. Verify DNS: dig $DOMAIN"
    echo "2. Check port 80: curl -I http://$DOMAIN"
    echo "3. Test ACME: curl http://$DOMAIN/.well-known/acme-challenge/test"
    echo "4. Check nginx logs: docker compose logs web"
    echo "5. Check certbot logs: docker compose logs certbot"
    exit 1
fi

