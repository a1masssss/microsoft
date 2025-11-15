from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import (
    OpenAIMCPRequest,
    OpenAIMCPResponse,
    SQLDatabaseConnection,
    SQLToolExecution,
    MCPRequestLog,
    MCPToolSchema,
    MCPSession,
)


# ============================================
# Inline Admin Classes
# ============================================

class OpenAIMCPResponseInline(TabularInline):
    """Inline for MCP Responses"""
    model = OpenAIMCPResponse
    extra = 0
    fields = ('status', 'response_id', 'processing_time_ms', 'created_at')
    readonly_fields = ('response_id', 'processing_time_ms', 'created_at')
    can_delete = False


class SQLToolExecutionInline(TabularInline):
    """Inline for SQL Tool Executions"""
    model = SQLToolExecution
    extra = 0
    fields = ('tool_name', 'status', 'execution_time_ms', 'created_at')
    readonly_fields = ('execution_time_ms', 'created_at')
    can_delete = False


class MCPRequestLogInline(TabularInline):
    """Inline for MCP Request Logs"""
    model = MCPRequestLog
    extra = 0
    fields = ('function_name', 'should_continue', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = False


# ============================================
# MCP Protocol Admin Classes
# ============================================

@admin.register(OpenAIMCPRequest)
class OpenAIMCPRequestAdmin(ModelAdmin):
    """Admin for MCP Requests"""
    list_display = ('request_id', 'method', 'session_id', 'user_id', 'created_at')
    list_filter = ('method', 'created_at', 'session_id')
    search_fields = ('request_id', 'method', 'session_id', 'user_id')
    readonly_fields = ('jsonrpc', 'request_id', 'created_at', 'raw_request')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Request Info', {
            'fields': ('jsonrpc', 'method', 'request_id', 'params')
        }),
        ('Metadata', {
            'fields': ('session_id', 'user_id', 'created_at')
        }),
        ('Raw Data', {
            'fields': ('raw_request',),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [OpenAIMCPResponseInline, SQLToolExecutionInline, MCPRequestLogInline]


@admin.register(OpenAIMCPResponse)
class OpenAIMCPResponseAdmin(ModelAdmin):
    """Admin for MCP Responses"""
    list_display = ('response_id', 'request', 'status', 'processing_time_ms', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('response_id', 'request__request_id', 'request__method')
    readonly_fields = ('request', 'jsonrpc', 'response_id', 'processing_time_ms', 'created_at', 'raw_response')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Response Info', {
            'fields': ('request', 'jsonrpc', 'response_id', 'status')
        }),
        ('Result/Error', {
            'fields': ('result', 'error')
        }),
        ('Metadata', {
            'fields': ('processing_time_ms', 'created_at')
        }),
        ('Raw Data', {
            'fields': ('raw_response',),
            'classes': ('collapse',)
        }),
    )


# ============================================
# SQL Database Admin Classes
# ============================================

@admin.register(SQLDatabaseConnection)
class SQLDatabaseConnectionAdmin(ModelAdmin):
    """Admin for SQL Database Connections"""
    list_display = ('name', 'db_type', 'is_active', 'created_at', 'updated_at')
    list_filter = ('db_type', 'is_active', 'created_at')
    search_fields = ('name', 'database_uri')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Connection Info', {
            'fields': ('name', 'database_uri', 'db_type', 'is_active')
        }),
        ('Configuration', {
            'fields': ('sample_rows_in_table_info', 'include_tables', 'exclude_tables')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    inlines = [SQLToolExecutionInline]
    
    def get_readonly_fields(self, request, obj=None):
        """Mask database URI in list view"""
        if obj:
            return self.readonly_fields + ('database_uri',)
        return self.readonly_fields


@admin.register(SQLToolExecution)
class SQLToolExecutionAdmin(ModelAdmin):
    """Admin for SQL Tool Executions"""
    list_display = ('id', 'tool_name', 'database', 'status', 'execution_time_ms', 'created_at')
    list_filter = ('tool_name', 'status', 'database', 'created_at')
    search_fields = ('tool_name', 'database__name', 'sql_query', 'error_message')
    readonly_fields = ('mcp_request', 'database', 'tool_name', 'execution_time_ms', 'created_at', 'completed_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Execution Info', {
            'fields': ('mcp_request', 'database', 'tool_name', 'status')
        }),
        ('Input/Output', {
            'fields': ('tool_input', 'tool_output')
        }),
        ('SQL Details', {
            'fields': ('sql_query', 'query_result')
        }),
        ('Error Info', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('execution_time_ms', 'created_at', 'completed_at')
        }),
    )


# ============================================
# Logging Admin Classes
# ============================================

@admin.register(MCPRequestLog)
class MCPRequestLogAdmin(ModelAdmin):
    """Admin for MCP Request Logs"""
    list_display = ('function_name', 'mcp_request', 'should_continue', 'created_at')
    list_filter = ('function_name', 'should_continue', 'created_at')
    search_fields = ('function_name', 'user_query', 'sql_query', 'mcp_request__request_id')
    readonly_fields = ('mcp_request', 'function_name', 'created_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Log Info', {
            'fields': ('mcp_request', 'function_name', 'should_continue', 'created_at')
        }),
        ('Query Details', {
            'fields': ('user_query', 'sql_query', 'db_response')
        }),
        ('Response', {
            'fields': ('mcp_response',),
            'classes': ('collapse',)
        }),
    )


# ============================================
# Tool Schema Admin Classes
# ============================================

@admin.register(MCPToolSchema)
class MCPToolSchemaAdmin(ModelAdmin):
    """Admin for MCP Tool Schemas"""
    list_display = ('name', 'category', 'langchain_tool_class', 'is_active', 'updated_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'langchain_tool_class')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('category', 'name')
    
    fieldsets = (
        ('Tool Info', {
            'fields': ('name', 'description', 'category', 'is_active')
        }),
        ('Schema', {
            'fields': ('input_schema', 'output_schema')
        }),
        ('LangChain Integration', {
            'fields': ('langchain_tool_class',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


# ============================================
# Session Admin Classes
# ============================================

@admin.register(MCPSession)
class MCPSessionAdmin(ModelAdmin):
    """Admin for MCP Sessions"""
    list_display = ('session_id', 'user_id', 'database', 'is_active', 'last_activity')
    list_filter = ('is_active', 'database', 'created_at', 'last_activity')
    search_fields = ('session_id', 'user_id', 'database__name')
    readonly_fields = ('session_id', 'created_at', 'last_activity')
    date_hierarchy = 'last_activity'
    ordering = ('-last_activity',)
    
    fieldsets = (
        ('Session Info', {
            'fields': ('session_id', 'user_id', 'is_active')
        }),
        ('Context', {
            'fields': ('database', 'context_data')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_activity', 'expires_at')
        }),
    )
