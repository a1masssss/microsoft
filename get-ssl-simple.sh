#!/bin/bash

set -e

DOMAIN="mythicai.me"
EMAIL="admin@mythicai.me"

echo "🔐 Getting SSL for $DOMAIN"
echo ""

# 1. Use HTTP config first
echo "📝 Using HTTP config..."
cp web/nginx-http.conf web/nginx.conf
docker compose restart web
sleep 2

# 2. Stop auto-renewal certbot
docker compose stop certbot 2>/dev/null || true

# 3. Get certificates
echo "🔐 Getting certificates..."
docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --non-interactive \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Certificates obtained!"
    
    # 4. Switch to SSL config
    echo "🔄 Switching to SSL..."
    cp web/nginx.conf web/nginx-http-backup.conf
    cp web/nginx-ssl.conf web/nginx.conf
    docker compose restart web
    
    # 5. Start certbot auto-renewal
    docker compose up -d certbot
    
    echo ""
    echo "✅ Done! https://$DOMAIN"
else
    echo ""
    echo "❌ Failed! Check logs: docker compose logs web"
    docker compose up -d certbot
    exit 1
fi

