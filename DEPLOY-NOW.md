# 🚀 БЫСТРОЕ РАЗВЕРТЫВАНИЕ

## Проблемы которые решены:
1. ❌ Django backend падал с `ModuleNotFoundError: No module named 'backend.settings'`
2. ❌ Неправильная структура volume в docker-compose.yml
3. ✅ Добавлен тестовый файл для ACME challenge

## На сервере выполни:

```bash
cd ~/microsoft

# Получи изменения
git pull

# Запусти исправление
chmod +x deploy-fix.sh
./deploy-fix.sh
```

## Проверь что работает:

### 1. Backend должен запуститься без ошибок:
```bash
docker compose logs backend
```
Не должно быть `ModuleNotFoundError`!

### 2. Проверь ACME challenge:
```bash
curl -I http://mythicai.me/.well-known/acme-challenge/test
```
Должно вернуть `HTTP/1.1 200 OK`

### 3. Проверь API:
```bash
curl http://mythicai.me/api/
```

## Если все работает → Настрой SSL:

```bash
./setup-ssl.sh
```

## Что исправлено в коде:

### 1. backend/Dockerfile
```dockerfile
# Было:
COPY backend/ .

# Стало:
COPY ./backend .
```

### 2. docker-compose.yml
```yaml
# Было:
volumes:
  - ./backend:/app/backend  # Неправильно!

# Стало:
volumes:
  - ./backend:/app          # Правильно!
```

## Структура теперь правильная:

```
/app/
├── backend/settings.py    ✅ Django найдет
├── manage.py              ✅ В правильном месте
├── mcp/
└── telegram/
```

## Если что-то не работает:

```bash
# Пересобери backend полностью
docker compose down
docker compose build --no-cache backend
docker compose up -d

# Смотри логи
docker compose logs -f backend
```

## Важно:

1. DNS должен указывать на твой сервер (проверь: `dig mythicai.me`)
2. Порты 80 и 443 должны быть открыты
3. ACME challenge ОБЯЗАН работать перед SSL setup!

---

## Кратко:

```bash
cd ~/microsoft
git pull
chmod +x deploy-fix.sh
./deploy-fix.sh

# Проверь:
curl -I http://mythicai.me/.well-known/acme-challenge/test

# Если OK → запусти SSL:
./setup-ssl.sh
```

**Всё просто, бля! 😎**

