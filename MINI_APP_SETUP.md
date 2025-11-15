# Как запустить Telegram Mini App

## Проблема
Mini App открывается в браузере, а не в Telegram!

## Решение

### 1. Создай бота (если еще нет)
1. Открой Telegram
2. Найди @BotFather
3. Отправь `/newbot`
4. Следуй инструкциям, получишь токен
5. Сохрани токен в `.env` как `TELEGRAM_BOT_TOKEN`

### 2. Настрой Mini App в боте
1. Открой @BotFather снова
2. Отправь `/newapp`
3. Выбери своего бота
4. Введи название: `My App`
5. Введи описание: `Database query app`
6. Загрузи иконку (512x512 PNG)
7. **ВАЖНО:** Введи URL твоего приложения:
   - Для разработки: `https://твой-ngrok-url.ngrok.io` (нужен ngrok или localtunnel)
   - Для продакшн: `https://твой-домен.com`
8. Отправь демо GIF (опционально, можно пропустить)

### 3. Запусти через туннель (для разработки)

#### Вариант A: ngrok (рекомендую)
```bash
# Установи ngrok
# https://ngrok.com/download

# Запусти vite dev server
cd frontend
npm run dev

# В другом терминале запусти ngrok
ngrok http 5173
```

Получишь URL типа `https://abc123.ngrok.io` - его используй в BotFather

#### Вариант B: localtunnel
```bash
# Установи
npm install -g localtunnel

# Запусти vite
npm run dev

# Запусти туннель
lt --port 5173
```

### 4. Открой Mini App в Telegram
1. Открой своего бота в Telegram
2. Внизу увидишь кнопку с иконкой своего приложения
3. Нажми на неё - откроется твой Mini App!

## Альтернатива: Telegram Bot с кнопкой

Если не хочешь возиться с Mini App кнопкой, можешь создать команду в боте:

```python
# Добавь в backend/telegram/bot.py (создай файл)
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler

async def start(update: Update, context):
    keyboard = [
        [KeyboardButton(
            text="Открыть приложение",
            web_app=WebAppInfo(url="https://твой-url.ngrok.io")
        )]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Нажми кнопку ниже:",
        reply_markup=reply_markup
    )

# Запуск
app = Application.builder().token("твой_токен").build()
app.add_handler(CommandHandler("start", start))
app.run_polling()
```

## Backend тоже нужен!

Не забудь запустить Django:
```bash
cd backend
python manage.py runserver
```

И настрой в `frontend/.env`:
```
VITE_API_URL=https://твой-backend-ngrok-url.ngrok.io/api/telegram
```

Для backend тоже нужен ngrok на порт 8000!
