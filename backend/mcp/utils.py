"""
Utility functions for MCP application
Includes OpenAI LLM initialization and helper functions
"""

from django.conf import settings
from langchain_openai import ChatOpenAI
from typing import Optional
import os


def get_openai_llm(
    temperature: Optional[float] = None,
    model: Optional[str] = None,
) -> ChatOpenAI:
    """
    Get configured OpenAI LLM instance

    Args:
        temperature: Override default temperature
        model: Override default model

    Returns:
        ChatOpenAI instance

    Raises:
        ValueError: If OPENAI_API_KEY is not set
    """
    api_key = settings.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set. Please set it in your .env file or environment variables."
        )

    return ChatOpenAI(
        model=model or settings.OPENAI_MODEL,
        temperature=temperature if temperature is not None else settings.OPENAI_TEMPERATURE,
        api_key=api_key,
    )


def is_openai_configured() -> bool:
    """
    Check if OpenAI API key is configured

    Returns:
        True if API key is set, False otherwise
    """
    api_key = settings.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')
    return bool(api_key and api_key.strip())


def get_llm_for_sql_toolkit(
    temperature: float = 0.0,
    model: Optional[str] = None
) -> Optional[ChatOpenAI]:
    """
    Get LLM for SQL Toolkit operations
    Returns None if OpenAI is not configured

    Args:
        temperature: Temperature for LLM (default: 0.0 for deterministic SQL)
        model: Model to use

    Returns:
        ChatOpenAI instance or None
    """
    try:
        if is_openai_configured():
            return get_openai_llm(temperature=temperature, model=model)
        return None
    except Exception:
        return None


def format_sql_result(result: str, max_length: int = 1000) -> str:
    """
    Format SQL query result for display

    Args:
        result: Raw SQL result string
        max_length: Maximum length of formatted result

    Returns:
        Formatted result string
    """
    if len(result) > max_length:
        return result[:max_length] + f"\n... (truncated, total length: {len(result)})"
    return result


def validate_sql_query(query: str) -> tuple[bool, Optional[str]]:
    """
    Basic SQL query validation

    Args:
        query: SQL query string

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, "Query is empty"

    query_lower = query.lower().strip()

    # Check for dangerous operations
    dangerous_keywords = ['drop', 'truncate', 'delete', 'alter', 'create']
    for keyword in dangerous_keywords:
        if query_lower.startswith(keyword):
            return False, f"Query starts with dangerous keyword: {keyword.upper()}"

    return True, None


def parse_table_list(table_string: str) -> list[str]:
    """
    Parse comma-separated table list from LangChain output

    Args:
        table_string: Comma-separated table names

    Returns:
        List of table names
    """
    if not table_string:
        return []

    return [table.strip() for table in table_string.split(',') if table.strip()]


def create_mcp_error_response(code: int, message: str, data: Optional[dict] = None) -> dict:
    """
    Create MCP-compliant error response

    Args:
        code: Error code (JSON-RPC 2.0)
        message: Error message
        data: Optional additional data

    Returns:
        Error response dict
    """
    error = {
        "code": code,
        "message": message,
    }

    if data:
        error["data"] = data

    return error


def create_mcp_success_response(result: any, response_id: str) -> dict:
    """
    Create MCP-compliant success response

    Args:
        result: Result data
        response_id: Response ID

    Returns:
        Success response dict
    """
    return {
        "jsonrpc": "2.0",
        "id": response_id,
        "result": result,
    }


# Common error codes
MCP_ERROR_CODES = {
    "PARSE_ERROR": -32700,
    "INVALID_REQUEST": -32600,
    "METHOD_NOT_FOUND": -32601,
    "INVALID_PARAMS": -32602,
    "INTERNAL_ERROR": -32603,
    "SERVER_ERROR": -32000,
}
