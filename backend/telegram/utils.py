"""
Utility helpers for Telegram Mini App integration outside the /api/telegram/ namespace.
"""
import logging
from typing import Optional

from .auth import validate_telegram_init_data
from .models import TelegramUser

logger = logging.getLogger(__name__)


def get_telegram_user_from_request(request) -> Optional[TelegramUser]:
    """
    Attempt to resolve TelegramUser from the Authorization header (initData).

    This mirrors the TelegramAuthMiddleware but can be used by endpoints
    outside /api/telegram/, such as the AI query view.
    """
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('tma '):
        return None

    init_data = auth_header[4:]
    try:
        user_data = validate_telegram_init_data(init_data)
    except ValueError as e:
        logger.warning(f"Telegram init data validation error: {e}")
        return None

    if not user_data or not user_data.get('user_id'):
        return None

    try:
        user, _ = TelegramUser.objects.update_or_create(
            user_id=user_data['user_id'],
            defaults={
                'username': user_data.get('username'),
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'language_code': user_data.get('language_code'),
                'is_bot': False,
            },
        )
        return user
    except Exception as exc:
        logger.error(f"Failed to resolve Telegram user for AI query: {exc}", exc_info=True)
        return None
