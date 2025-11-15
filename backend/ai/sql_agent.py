"""
SQL Agent для LangChain с безопасным выполнением запросов.
Работает с таблицей mcp_transactions (Transaction model).
"""

import os
import re
from typing import Dict, List, Any
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from django.conf import settings


# Безопасные SQL команды (только SELECT)
SAFE_SQL_KEYWORDS = {'SELECT', 'FROM', 'WHERE', 'GROUP', 'BY', 'ORDER', 'HAVING', 'LIMIT', 'OFFSET', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'ON', 'AS', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'ILIKE', 'IS', 'NULL', 'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'DISTINCT', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END'}

# Запрещенные команды
FORBIDDEN_KEYWORDS = {'UPDATE', 'DELETE', 'DROP', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE', 'GRANT', 'REVOKE'}

# Максимальная длина SQL запроса (fail-safe)
MAX_SQL_LENGTH = 5000


def validate_sql_safety(sql: str) -> tuple:
    """
    Проверяет безопасность SQL запроса.
    
    Returns:
        (is_safe, error_message)
    """
    sql_upper = sql.upper().strip()
    
    # Проверка на запрещенные команды
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf'\b{keyword}\b', sql_upper):
            return False, f"Запрещенная команда: {keyword}"
    
    # Проверка что начинается с SELECT
    if not sql_upper.startswith('SELECT'):
        return False, "Разрешены только SELECT запросы"
    
    # Проверка длины
    if len(sql) > MAX_SQL_LENGTH:
        return False, f"SQL запрос слишком длинный (максимум {MAX_SQL_LENGTH} символов)"
    
    # Проверка на сложные конструкции (можно расширить)
    if ';' in sql and sql.count(';') > 1:
        return False, "Множественные SQL команды запрещены"
    
    return True, ""


def get_database_uri() -> str:
    """Получает URI базы данных из Django settings."""
    db_config = settings.DATABASES['default']
    return f"postgresql://{db_config['USER']}:{db_config['PASSWORD']}@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"


def create_safe_sql_agent():
    """
    Создает безопасный SQL агент для работы с таблицей transactions.
    """
    # Получаем URI базы данных
    db_uri = get_database_uri()
    
    # Создаем SQLDatabase с ограничением только на таблицу transactions
    db = SQLDatabase.from_uri(
        db_uri,
        include_tables=['mcp_transactions'],  # Только наша таблица
        sample_rows_in_table_info=3,  # Примеры строк для контекста
    )
    
    # Получаем LLM
    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=settings.OPENAI_TEMPERATURE,
        openai_api_key=settings.OPENAI_API_KEY,
    )
    
    # Промпт для агента
    system_prompt = """Ты SQL-агент. Преобразуй запрос пользователя в SQL SELECT.

Правила:
- Нельзя использовать UPDATE, INSERT, DELETE, DROP.
- Всегда делай безопасные запросы с LIMIT 1000.
- Если пользователь просит "месяц", используй interval '1 month'.
- Работай только с таблицей mcp_transactions и только с указанными полями.
- Поля таблицы: transaction_id, transaction_timestamp, card_id, issuer_bank_name, merchant_id, mcc_category, merchant_city, transaction_type, transaction_amount_kzt, transaction_currency, pos_entry_mode, wallet_type.
- Для дат используй transaction_timestamp.
- Для банков используй issuer_bank_name.
- Для категорий используй mcc_category.
- Для городов используй merchant_city.
- Для типов транзакций используй transaction_type.

Верни только SQL, который можно выполнить."""
    
    # Создаем агента
    agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        verbose=True,  # Включаем verbose для отладки
        max_iterations=5,  # Ограничиваем количество итераций
        max_execution_time=30,  # Таймаут 30 секунд
        system_message=system_prompt,
    )
    
    return agent, db


def generate_sql_with_llm(query: str) -> str:
    """
    Генерирует SQL запрос из естественного языка используя OpenAI напрямую.
    """
    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=settings.OPENAI_TEMPERATURE,
        openai_api_key=settings.OPENAI_API_KEY,
        timeout=15,
    )
    
    schema_info = """
Таблица: mcp_transactions
Поля:
- transaction_id (UUID, уникальный ID)
- transaction_timestamp (TIMESTAMP, дата и время транзакции)
- card_id (BIGINT)
- expiry_date (VARCHAR)
- issuer_bank_name (VARCHAR, название банка эмитента)
- merchant_id (BIGINT)
- merchant_mcc (INTEGER)
- mcc_category (VARCHAR, категория магазина, например 'Fuel', 'Grocery & Food Markets')
- merchant_city (VARCHAR, город магазина)
- transaction_type (VARCHAR, тип: 'POS', 'BILL_PAYMENT', 'ECOM', etc)
- transaction_amount_kzt (DECIMAL, сумма в KZT)
- original_amount (DECIMAL, nullable)
- transaction_currency (VARCHAR)
- acquirer_country_iso (VARCHAR)
- pos_entry_mode (VARCHAR)
- wallet_type (VARCHAR, nullable, например 'Apple Pay', 'Google Pay')
"""
    
    prompt = f"""{schema_info}

Преобразуй запрос пользователя в SQL SELECT для PostgreSQL.

Правила:
- ТОЛЬКО SELECT запросы
- Всегда добавляй LIMIT 1000
- Для дат используй transaction_timestamp
- Для "последний месяц" используй: WHERE transaction_timestamp >= CURRENT_DATE - INTERVAL '1 month'
- Для названий банков используй issuer_bank_name с ILIKE для частичного поиска
- Возвращай ТОЛЬКО SQL код, без пояснений

Запрос пользователя: {query}

SQL:"""
    
    response = llm.invoke(prompt)
    sql = response.content.strip()
    
    # Убираем markdown форматирование если есть
    sql = sql.replace("```sql", "").replace("```", "").strip()
    
    return sql


def run_query_nl(query: str) -> Dict[str, Any]:
    """
    Выполняет естественно-языковой запрос и возвращает результаты.
    
    Args:
        query: Текстовый запрос на естественном языке
        
    Returns:
        dict с ключами:
            - data: список словарей с результатами
            - sql: сгенерированный SQL запрос
            - error: сообщение об ошибке (если есть)
    """
    if not query or not query.strip():
        return {
            "data": [],
            "sql": "",
            "error": "Пустой запрос"
        }
    
    # Проверяем наличие OpenAI ключа
    if not settings.OPENAI_API_KEY:
        return {
            "data": [],
            "sql": "",
            "error": "OpenAI API ключ не настроен"
        }
    
    try:
        # Генерируем SQL напрямую через LLM
        sql = generate_sql_with_llm(query)
        print(f"🔍 Generated SQL: {sql}")
        
        # Проверяем безопасность SQL
        is_safe, error_msg = validate_sql_safety(sql)
        if not is_safe:
            return {
                "data": [],
                "sql": sql,
                "error": f"Небезопасный SQL: {error_msg}"
            }
        
        # Добавляем LIMIT если его нет
        sql_upper = sql.upper()
        if "LIMIT" not in sql_upper:
            sql = sql.rstrip(";") + " LIMIT 1000;"
        
        # Выполняем SQL напрямую через Django
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            data = [dict(zip(columns, row)) for row in rows]
        
        return {
            "data": data,
            "sql": sql,
            "error": None
        }
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ ERROR: {error_details}")
        return {
            "data": [],
            "sql": "",
            "error": f"Ошибка выполнения запроса: {str(e)}"
        }

