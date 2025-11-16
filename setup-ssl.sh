#!/bin/bash

# Simple SSL setup script for mythicai.me

echo "🔧 Step 1: Убедитесь что Docker контейнеры работают..."
docker compose ps

echo ""
echo "🔐 Step 2: Получаем SSL сертификаты для mythicai.me..."
docker compose run --rm certbot certonly --webroot \
    --webroot-path=/var/www/certbot \
    --email admin@mythicai.me \
    --agree-tos \
    --no-eff-email \
    -d mythicai.me \
    -d www.mythicai.me

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Сертификаты получены успешно!"
    echo ""
    echo "🔄 Step 3: Обновляем nginx конфигурацию на HTTPS..."
    
    # Backup current config
    cp web/nginx.conf web/nginx-http-backup.conf
    
    # Switch to SSL config
    cp web/nginx-ssl.conf web/nginx.conf
    
    echo "🔄 Step 4: Перезапускаем nginx..."
    docker compose restart web
    
    echo ""
    echo "✅ Готово! Теперь сайт доступен по HTTPS:"
    echo "   https://mythicai.me"
    echo "   https://www.mythicai.me"
    echo ""
    echo "📝 Сертификаты будут автоматически обновляться каждые 12 часов"
else
    echo ""
    echo "❌ Ошибка при получении сертификатов!"
    echo "Проверьте что:"
    echo "  1. DNS mythicai.me и www.mythicai.me указывают на этот сервер"
    echo "  2. Порты 80 и 443 открыты"
    echo "  3. Nginx контейнер работает: docker compose ps"
fi

