"""
Telegram Mini App authentication utilities
"""
import os
import hmac
import hashlib
import json
from typing import Optional, Dict, Any
from urllib.parse import parse_qsl


def validate_telegram_init_data(init_data: str) -> Optional[Dict[str, Any]]:
    """
    Validate Telegram WebApp initData

    Args:
        init_data: Query string from Telegram.WebApp.initData

    Returns:
        Parsed user data if valid, None otherwise
    """
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN not configured")

    try:
        # Parse init data
        parsed_data = dict(parse_qsl(init_data))

        # Extract hash
        received_hash = parsed_data.pop('hash', None)
        if not received_hash:
            return None

        # Build data check string
        data_check_arr = [f"{k}={v}" for k, v in sorted(parsed_data.items())]
        data_check_string = '\n'.join(data_check_arr)

        # Compute secret key
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=bot_token.encode(),
            digestmod=hashlib.sha256
        ).digest()

        # Compute hash
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        # Verify hash
        if not hmac.compare_digest(calculated_hash, received_hash):
            return None

        # Parse user data
        user_data = json.loads(parsed_data.get('user', '{}'))

        return {
            'user_id': user_data.get('id'),
            'username': user_data.get('username'),
            'first_name': user_data.get('first_name'),
            'last_name': user_data.get('last_name'),
            'language_code': user_data.get('language_code'),
            'is_premium': user_data.get('is_premium', False),
            'auth_date': parsed_data.get('auth_date'),
            'query_id': parsed_data.get('query_id'),
        }

    except (json.JSONDecodeError, ValueError, KeyError):
        return None
