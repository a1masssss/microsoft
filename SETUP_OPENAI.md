# Настройка OpenAI для SQL-агента

## 1. Добавьте ключ в .env файл

Откройте `.env` файл в корне проекта и добавьте:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-ваш-ключ-здесь
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0
```

## 2. Получить ключ OpenAI

1. Зайдите на https://platform.openai.com/api-keys
2. Создайте новый API ключ
3. Скопируйте и вставьте в .env

## 3. Перезапустите сервер

```bash
cd backend
python manage.py runserver
```

## 4. Тестируем endpoint

### Через Swagger UI:
```
http://127.0.0.1:8000/api/docs/
```

### Через curl:
```bash
# JSON ответ
curl "http://127.0.0.1:8000/api/mcp/query-transactions/?q=дай транзакции за последний месяц My Favorite Bank"

# CSV экспорт
curl "http://127.0.0.1:8000/api/mcp/query-transactions/?q=покажи Fuel операции&format=csv" -o result.csv
```

### Примеры запросов:
- "дай транзакции за последний месяц My Favorite Bank"
- "покажи все платежи в категории Fuel за декабрь"
- "сколько было ECOM операций в Караганде"
- "транзакции Apple Pay за неделю"
- "топ 10 транзакций по сумме"

## Ответ:

```json
{
  "data": [
    {
      "transaction_id": "...",
      "transaction_timestamp": "2023-12-01T10:00:00Z",
      "issuer_bank_name": "My Favorite Bank",
      "transaction_amount_kzt": "1500.00",
      ...
    }
  ],
  "sql": "SELECT * FROM mcp_transactions WHERE ...",
  "error": null
}
```

## Troubleshooting

**Ошибка: "OpenAI API ключ не настроен"**
- Проверьте, что ключ добавлен в .env
- Перезапустите сервер

**Ошибка: "Небезопасный SQL"**
- Агент разрешает только SELECT запросы
- UPDATE/DELETE/DROP запрещены

**SQL слишком сложный**
- Упростите запрос
- Используйте более конкретные критерии

