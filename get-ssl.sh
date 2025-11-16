#!/bin/bash

# Get SSL certificates for mythicai.me (simplified version)

echo "🔐 Getting SSL certificates for mythicai.me..."
echo ""

# First, check if certificates already exist
if docker compose run --rm certbot certificates | grep -q "mythicai.me"; then
    echo "⚠️  Certificates already exist!"
    echo ""
    echo "To force renewal, run:"
    echo "  docker compose run --rm certbot delete --cert-name mythicai.me"
    echo "  Then run this script again"
    echo ""
    read -p "Do you want to continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get new certificates
docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email admin@mythicai.me \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d mythicai.me \
    -d www.mythicai.me

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Certificates obtained successfully!"
    echo ""
    echo "🔄 Switching to HTTPS configuration..."
    
    # Backup current config
    cp web/nginx.conf web/nginx-http-backup.conf
    
    # Switch to SSL config
    cp web/nginx-ssl.conf web/nginx.conf
    
    echo "🔄 Restarting nginx..."
    docker compose restart web
    
    echo ""
    echo "✅ Done! Your site is now available at:"
    echo "   https://mythicai.me"
    echo "   https://www.mythicai.me"
    echo ""
    echo "HTTP will automatically redirect to HTTPS"
else
    echo ""
    echo "❌ Failed to obtain certificates!"
    echo ""
    echo "Check that:"
    echo "  1. DNS mythicai.me points to this server IP"
    echo "  2. Port 80 is accessible from internet"
    echo "  3. Nginx is running: docker compose ps web"
    echo ""
    echo "Test with: curl -I http://mythicai.me/.well-known/acme-challenge/test"
fi

