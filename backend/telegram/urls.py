from django.urls import path
from . import views, api_views

app_name = 'telegram'

urlpatterns = [
    # Health check
    path('health/', views.health_check, name='health'),

    # Mini App API
    path('me/', api_views.get_current_user, name='current_user'),
    path('query/', api_views.send_query, name='send_query'),
    path('history/', api_views.get_history, name='history'),
]
