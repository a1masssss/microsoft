"""
Telegram Mini App authentication middleware
"""
import logging
from django.http import JsonResponse
from .auth import validate_telegram_init_data
from .models import TelegramUser

logger = logging.getLogger(__name__)


class TelegramAuthMiddleware:
    """
    Middleware to authenticate Telegram Mini App users

    Checks for Authorization header with Telegram initData
    Validates and attaches telegram_user to request
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip auth for non-API endpoints
        if not request.path.startswith('/api/telegram/'):
            return self.get_response(request)

        # Skip auth for health check
        if request.path == '/api/telegram/health/':
            return self.get_response(request)

        # Get init_data from Authorization header
        auth_header = request.headers.get('Authorization', '')

        # DEBUG: Log what we received
        logger.info(f"Path: {request.path}")
        logger.info(f"Authorization header: {auth_header[:50] if auth_header else 'EMPTY'}")
        logger.info(f"All headers: {dict(request.headers)}")

        if not auth_header.startswith('tma '):
            return JsonResponse(
                {'error': 'Missing or invalid Authorization header'},
                status=401
            )

        init_data = auth_header[4:]  # Remove 'tma ' prefix

        # Validate init_data
        user_data = validate_telegram_init_data(init_data)

        if not user_data or not user_data.get('user_id'):
            return JsonResponse(
                {'error': 'Invalid Telegram authentication'},
                status=401
            )

        # Get or create user
        try:
            user, _ = TelegramUser.objects.update_or_create(
                user_id=user_data['user_id'],
                defaults={
                    'username': user_data.get('username'),
                    'first_name': user_data.get('first_name'),
                    'last_name': user_data.get('last_name'),
                    'language_code': user_data.get('language_code'),
                    'is_bot': False
                }
            )

            # Attach user to request
            request.telegram_user = user

        except Exception as e:
            logger.error(f"Error creating/updating user: {e}")
            return JsonResponse(
                {'error': 'Authentication error'},
                status=500
            )

        return self.get_response(request)
