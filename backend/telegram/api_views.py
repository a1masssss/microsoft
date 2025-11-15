"""
API endpoints for Telegram Mini App
"""
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import ChatInteraction
import json

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def get_current_user(request):
    """
    Get current authenticated user info

    Returns:
        User data from request.telegram_user
    """
    user = request.telegram_user

    return JsonResponse({
        'user_id': user.user_id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'language_code': user.language_code,
    })


@csrf_exempt
@require_http_methods(["POST"])
def send_query(request):
    """
    Process user query

    Body:
        {
            "query": "User's natural language query"
        }

    Returns:
        Response with query result
    """
    user = request.telegram_user

    try:
        data = json.loads(request.body.decode('utf-8'))
        query_text = data.get('query', '').strip()

        if not query_text:
            return JsonResponse(
                {'error': 'Query text is required'},
                status=400
            )

        # TODO: Implement AI/SQL processing here
        # For now, just echo back
        response_text = (
            f"Получил запрос: \"{query_text}\"\n\n"
            "Обработка запросов в разработке. "
            "Скоро добавим AI для генерации SQL!"
        )

        # Log interaction
        interaction = ChatInteraction.objects.create(
            user=user,
            message_text=query_text,
            response_text=response_text,
            success=True
        )

        return JsonResponse({
            'id': interaction.id,
            'query': query_text,
            'response': response_text,
            'success': True,
            'created_at': interaction.created_at.isoformat()
        })

    except json.JSONDecodeError:
        return JsonResponse(
            {'error': 'Invalid JSON'},
            status=400
        )
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        return JsonResponse(
            {'error': 'Internal server error'},
            status=500
        )


@csrf_exempt
@require_http_methods(["GET"])
def get_history(request):
    """
    Get user's query history

    Query params:
        limit: Number of records (default 10, max 50)

    Returns:
        List of recent interactions
    """
    user = request.telegram_user

    try:
        limit = min(int(request.GET.get('limit', 10)), 50)

        interactions = ChatInteraction.objects.filter(
            user=user
        ).order_by('-created_at')[:limit]

        history = [{
            'id': i.id,
            'query': i.message_text,
            'response': i.response_text,
            'success': i.success,
            'created_at': i.created_at.isoformat()
        } for i in interactions]

        return JsonResponse({
            'history': history,
            'count': len(history)
        })

    except ValueError:
        return JsonResponse(
            {'error': 'Invalid limit parameter'},
            status=400
        )
    except Exception as e:
        logger.error(f"Error fetching history: {e}", exc_info=True)
        return JsonResponse(
            {'error': 'Internal server error'},
            status=500
        )
