from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MCPProtocolView,
    DeepQueryView,
    QuickExploreView,
    QuickQueryView,
    AIQueryView,
    MCPStatisticsView,
    SQLDatabaseConnectionViewSet,
    SQLToolExecutionViewSet,
    MCPToolSchemaViewSet,
    MCPSessionViewSet,
    MCPRequestLogViewSet,
)

app_name = 'mcp'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'databases', SQLDatabaseConnectionViewSet, basename='database')
router.register(r'executions', SQLToolExecutionViewSet, basename='execution')
router.register(r'tools', MCPToolSchemaViewSet, basename='tool')
router.register(r'sessions', MCPSessionViewSet, basename='session')
router.register(r'logs', MCPRequestLogViewSet, basename='log')

urlpatterns = [
    # MCP Protocol endpoint (JSON-RPC 2.0)
    path('protocol/', MCPProtocolView.as_view(), name='protocol'),

    # AI Natural Language Query
    path('ai-query/', AIQueryView.as_view(), name='ai-query'),

    # Deep Query (chain operations)
    path('deep-query/', DeepQueryView.as_view(), name='deep-query'),

    # Quick Operations
    path('quick/explore/', QuickExploreView.as_view(), name='quick-explore'),
    path('quick/query/', QuickQueryView.as_view(), name='quick-query'),

    # Statistics
    path('statistics/', MCPStatisticsView.as_view(), name='statistics'),

    # ViewSets (CRUD operations)
    path('', include(router.urls)),
]
