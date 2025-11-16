# Django Backend Fix Guide

## Problem
The Django backend was failing with `ModuleNotFoundError: No module named 'backend.settings'` due to incorrect volume mounting in Docker.

## Root Cause
The issue was in `docker-compose.yml` where the volume mount was:
```yaml
- ./backend:/app/backend  # WRONG - creates nested structure
```

This created a nested structure where Django couldn't find the settings module.

## Solution

### Files Changed

1. **backend/Dockerfile**
   - Fixed COPY command to properly copy backend directory structure
   
2. **docker-compose.yml**
   - Fixed volume mount from `./backend:/app/backend` to `./backend:/app`
   - Removed redundant volume mounts for staticfiles and media

3. **Created ACME Challenge Test File**
   - Added test file at `web/certbot/www/.well-known/acme-challenge/test`
   - This allows testing Let's Encrypt validation before running certbot

## Deployment Steps

### On the Server

1. **Pull latest changes:**
   ```bash
   cd ~/microsoft
   git pull
   ```

2. **Run the fix script:**
   ```bash
   chmod +x deploy-fix.sh
   ./deploy-fix.sh
   ```

3. **Test ACME challenge:**
   ```bash
   curl -I http://mythicai.me/.well-known/acme-challenge/test
   ```
   
   Expected output should include `HTTP/1.1 200 OK`

4. **Check backend is working:**
   ```bash
   docker compose logs backend
   ```
   
   Should NOT show `ModuleNotFoundError` anymore

5. **If everything works, proceed with SSL:**
   ```bash
   ./setup-ssl.sh
   ```

## Verification

### 1. Check Containers are Running
```bash
docker compose ps
```

All containers should show "Up" status.

### 2. Check Backend Logs
```bash
docker compose logs backend --tail=50
```

Should see:
- Django server starting
- Database migrations running
- No import errors

### 3. Test API Endpoint
```bash
curl http://localhost:8000/api/
```

Should return a response (not 404 or error).

### 4. Test ACME Challenge
```bash
curl http://mythicai.me/.well-known/acme-challenge/test
```

Should return: `test-acme-challenge-works`

## Troubleshooting

### Backend Still Crashing?
```bash
# Check detailed logs
docker compose logs backend -f

# Rebuild without cache
docker compose build --no-cache backend
docker compose up -d
```

### ACME Challenge Not Working?
```bash
# Check nginx container
docker compose logs web

# Check if file exists in container
docker compose exec web ls -la /var/www/certbot/.well-known/acme-challenge/

# Check nginx config
docker compose exec web nginx -t
```

### Database Connection Issues?
```bash
# Check database is ready
docker compose logs db

# Restart backend after db is ready
docker compose restart backend
```

## File Structure (After Fix)

```
/app/                          # Container working directory
├── backend/                   # Django project settings
│   ├── __init__.py
│   ├── settings.py           # ✅ Found correctly now
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── mcp/                       # Django app
│   ├── models.py
│   ├── views.py
│   └── ...
├── telegram/                  # Django app
│   └── ...
├── manage.py                  # ✅ In correct location
└── frontend/                  # Mounted from host
    └── dist/
```

## Next Steps After Fix

1. ✅ Verify backend works
2. ✅ Test ACME challenge endpoint
3. 🔐 Run SSL setup (`./setup-ssl.sh`)
4. 🔄 Switch nginx to SSL config
5. ✅ Test HTTPS access

## Important Notes

- The volume mount `./backend:/app` ensures live code reloading during development
- Static files are served through the backend container
- Frontend dist is mounted separately for nginx to serve
- ACME challenge must work BEFORE running certbot for SSL

## Support

If issues persist:
1. Share output of `docker compose logs backend`
2. Share output of `curl -v http://mythicai.me/.well-known/acme-challenge/test`
3. Check if DNS is pointing correctly to your server IP

