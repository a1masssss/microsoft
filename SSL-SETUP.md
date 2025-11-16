# 🔐 SSL Setup для mythicai.me

## Быстрая установка

### Шаг 1: Соберите и запустите контейнеры (БЕЗ SSL)

```bash
# На сервере
cd ~/microsoft

# Остановить старые контейнеры
docker compose down

# Пересобрать
docker compose build --no-cache

# Запустить (пока без SSL)
docker compose up -d

# Проверить что все работает
docker compose ps
```

Убедитесь что nginx работает на порту 80:
```bash
curl http://mythicai.me/health
# Должно вернуть: healthy
```

### Шаг 2: Получите SSL сертификаты

```bash
# Сделать скрипт исполняемым
chmod +x setup-ssl.sh

# Запустить установку SSL
./setup-ssl.sh
```

Этот скрипт:
1. ✅ Получит SSL сертификаты от Let's Encrypt
2. ✅ Переключит nginx на HTTPS конфигурацию
3. ✅ Перезапустит nginx

### Шаг 3: Готово! 🎉

Теперь сайт доступен по HTTPS:
- https://mythicai.me
- https://www.mythicai.me

HTTP трафик автоматически перенаправляется на HTTPS.

## Автоматическое обновление сертификатов

Сертификаты будут автоматически обновляться каждые 12 часов через контейнер `certbot`.

Проверить статус:
```bash
docker compose logs certbot
```

## Ручное обновление сертификатов

Если нужно обновить сертификаты вручную:

```bash
docker compose run --rm certbot renew
docker compose restart web
```

## Проверка SSL

```bash
# Проверить что HTTPS работает
curl -I https://mythicai.me

# Проверить что HTTP редиректит на HTTPS
curl -I http://mythicai.me
```

## Откат на HTTP (если нужно)

Если что-то пошло не так:

```bash
# Восстановить HTTP конфигурацию
cp web/nginx-http-backup.conf web/nginx.conf

# Перезапустить nginx
docker compose restart web
```

## Troubleshooting

### Ошибка: "Failed to authenticate some domains"

Проверьте:
1. DNS записи указывают на ваш сервер:
   ```bash
   nslookup mythicai.me
   nslookup www.mythicai.me
   ```

2. Порты 80 и 443 открыты:
   ```bash
   sudo ufw status
   # Если нужно, откройте порты:
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

3. Nginx работает:
   ```bash
   docker compose ps web
   curl http://mythicai.me/health
   ```

### Ошибка: "Rate limit exceeded"

Let's Encrypt имеет лимиты:
- 5 неудачных попыток в час для одного домена

Подождите час и попробуйте снова, или используйте staging mode для тестирования:

```bash
docker compose run --rm certbot certonly --webroot \
    --webroot-path=/var/www/certbot \
    --email admin@mythicai.me \
    --agree-tos \
    --staging \
    -d mythicai.me \
    -d www.mythicai.me
```

### Проверить логи

```bash
# Логи nginx
docker compose logs web

# Логи certbot
docker compose logs certbot

# Логи backend
docker compose logs backend
```

