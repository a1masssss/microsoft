from django.urls import path
from .views import (
    MCPProtocolView,
    QuickExploreView,
    QuickQueryView,
    MCPStatisticsView,
)

app_name = 'mcp'

urlpatterns = [
    # MCP Protocol endpoint (JSON-RPC 2.0)
    path('protocol/', MCPProtocolView.as_view(), name='protocol'),

    # Quick Operations
    path('quick/explore/', QuickExploreView.as_view(), name='quick-explore'),
    path('quick/query/', QuickQueryView.as_view(), name='quick-query'),

    # Statistics
    path('statistics/', MCPStatisticsView.as_view(), name='statistics'),
]
