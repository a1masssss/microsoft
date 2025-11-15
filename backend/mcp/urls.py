from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    # Deep Query Views
    DeepQueryView,
    QuickExploreView,
    QuickQueryView,

    # MCP Protocol
    MCPProtocolView,

    # ViewSets
    SQLDatabaseConnectionViewSet,
    SQLToolExecutionViewSet,
    MCPToolSchemaViewSet,
    MCPSessionViewSet,
    MCPRequestLogViewSet,

    # Statistics
    MCPStatisticsView,
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'databases', SQLDatabaseConnectionViewSet, basename='database')
router.register(r'executions', SQLToolExecutionViewSet, basename='execution')
router.register(r'tools', MCPToolSchemaViewSet, basename='tool')
router.register(r'sessions', MCPSessionViewSet, basename='session')
router.register(r'logs', MCPRequestLogViewSet, basename='log')

app_name = 'mcp'

urlpatterns = [
    # MCP Protocol endpoint (JSON-RPC 2.0)
    path('protocol/', MCPProtocolView.as_view(), name='protocol'),

    # Deep Query (Chain Operations)
    path('deep-query/', DeepQueryView.as_view(), name='deep-query'),

    # Quick Operations
    path('quick/explore/', QuickExploreView.as_view(), name='quick-explore'),
    path('quick/query/', QuickQueryView.as_view(), name='quick-query'),

    # Statistics
    path('statistics/', MCPStatisticsView.as_view(), name='statistics'),

    # Include router URLs
    path('', include(router.urls)),
]
