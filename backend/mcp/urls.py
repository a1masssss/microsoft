from django.urls import path, re_path
from .views import QueryTransactionsView

app_name = 'mcp'

urlpatterns = [
    re_path(r'^query-transactions/?$', QueryTransactionsView.as_view(), name='query-transactions'),
]