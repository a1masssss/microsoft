from django.http import JsonResponse


def health_check(_request):
    """Simple health check endpoint"""
    return JsonResponse({'status': 'ok', 'service': 'telegram-miniapp'})
