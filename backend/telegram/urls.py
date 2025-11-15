from django.urls import path
from . import views

app_name = 'telegram'

urlpatterns = [
    path('webhook/', views.telegram_webhook, name='webhook'),
    path('health/', views.health_check, name='health'),
]
