import os
import logging
import hmac
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .services import MessageHandler

logger = logging.getLogger(__name__)

TELEGRAM_SECRET_TOKEN = os.getenv('TELEGRAM_SECRET_TOKEN')


def verify_telegram_request(request):
    """
    Verify that request comes from Telegram

    Args:
        request: Django request object

    Returns:
        bool: True if request is valid
    """
    if not TELEGRAM_SECRET_TOKEN:
        logger.warning("TELEGRAM_SECRET_TOKEN not set, skipping verification")
        return True

    token_from_header = request.headers.get('X-Telegram-Bot-Api-Secret-Token', '')
    return hmac.compare_digest(token_from_header, TELEGRAM_SECRET_TOKEN)


@csrf_exempt
@require_http_methods(["POST"])
def telegram_webhook(request):
    """
    Handle incoming webhook requests from Telegram

    Args:
        request: Django request object containing Telegram update

    Returns:
        JsonResponse with status
    """
    try:
        # Verify request
        if not verify_telegram_request(request):
            logger.warning("Invalid request: secret token mismatch")
            return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)

        # Parse update
        import json
        update = json.loads(request.body.decode('utf-8'))

        logger.info(f"Received update: {update.get('update_id')}")

        # Handle message
        if 'message' in update:
            message_data = update['message']
            MessageHandler.handle_message(message_data)

        # Handle callback query
        elif 'callback_query' in update:
            # TODO: Implement callback query handling
            logger.info("Callback query received (not implemented yet)")

        return JsonResponse({'status': 'ok'})

    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def health_check(_request):
    """Simple health check endpoint"""
    return JsonResponse({'status': 'ok', 'service': 'telegram-bot'})
