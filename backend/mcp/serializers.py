from rest_framework import serializers
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
# MCP Protocol Serializers (JSON-RPC 2.0)
# ============================================

class OpenAIMCPRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for MCP requests following JSON-RPC 2.0 protocol
    """
    class Meta:
        model = OpenAIMCPRequest
        fields = [
            "id",
            "jsonrpc",
            "method",
            "params",
            "request_id",
            "session_id",
            "user_id",
            "created_at",
            "raw_request",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_jsonrpc(self, value):
        """Validate JSON-RPC version"""
        if value != "2.0":
            raise serializers.ValidationError("Only JSON-RPC 2.0 is supported")
        return value

    def validate_method(self, value):
        """Validate MCP method"""
        valid_methods = [
            "tools/list",
            "tools/call",
            "resources/list",
            "resources/read",
            "prompts/list",
            "prompts/get",
        ]
        if value not in valid_methods:
            raise serializers.ValidationError(
                f"Invalid method. Must be one of: {', '.join(valid_methods)}"
            )
        return value


class OpenAIMCPResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for MCP responses following JSON-RPC 2.0 protocol
    """
    request = OpenAIMCPRequestSerializer(read_only=True)
    request_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = OpenAIMCPResponse
        fields = [
            "id",
            "request",
            "request_id",
            "jsonrpc",
            "result",
            "error",
            "response_id",
            "status",
            "created_at",
            "processing_time_ms",
            "raw_response",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, data):
        """Validate that either result or error is present, but not both"""
        has_result = data.get("result") is not None
        has_error = data.get("error") is not None

        if has_result and has_error:
            raise serializers.ValidationError(
                "Response cannot have both 'result' and 'error'"
            )

        if not has_result and not has_error and data.get("status") != "pending":
            raise serializers.ValidationError(
                "Response must have either 'result' or 'error'"
            )

        return data

    def validate_error(self, value):
        """Validate error object structure (JSON-RPC 2.0)"""
        if value is not None:
            if not isinstance(value, dict):
                raise serializers.ValidationError("Error must be a JSON object")

            required_fields = ["code", "message"]
            for field in required_fields:
                if field not in value:
                    raise serializers.ValidationError(
                        f"Error object must contain '{field}'"
                    )

            if not isinstance(value["code"], int):
                raise serializers.ValidationError("Error code must be an integer")

            if not isinstance(value["message"], str):
                raise serializers.ValidationError("Error message must be a string")

        return value


# ============================================
# LangChain SQL Toolkit Serializers
# ============================================

class SQLDatabaseConnectionSerializer(serializers.ModelSerializer):
    """
    Serializer for SQL database connections
    Hides sensitive database_uri in list views
    """
    database_uri_masked = serializers.SerializerMethodField()

    class Meta:
        model = SQLDatabaseConnection
        fields = [
            "id",
            "name",
            "database_uri",
            "database_uri_masked",
            "db_type",
            "sample_rows_in_table_info",
            "include_tables",
            "exclude_tables",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "database_uri_masked"]
        extra_kwargs = {
            "database_uri": {"write_only": True},
        }

    def get_database_uri_masked(self, obj):
        """Return masked database URI for security"""
        uri = obj.database_uri
        if "://" in uri:
            protocol, rest = uri.split("://", 1)
            if "@" in rest:
                credentials, host = rest.split("@", 1)
                return f"{protocol}://***:***@{host}"
        return "***"

    def validate_include_tables(self, value):
        """Validate include_tables is a list"""
        if value is not None and not isinstance(value, list):
            raise serializers.ValidationError("include_tables must be a list")
        return value

    def validate_exclude_tables(self, value):
        """Validate exclude_tables is a list"""
        if value is not None and not isinstance(value, list):
            raise serializers.ValidationError("exclude_tables must be a list")
        return value


class SQLDatabaseConnectionListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing database connections
    """
    database_uri_masked = serializers.SerializerMethodField()

    class Meta:
        model = SQLDatabaseConnection
        fields = [
            "id",
            "name",
            "database_uri_masked",
            "db_type",
            "is_active",
            "updated_at",
        ]

    def get_database_uri_masked(self, obj):
        """Return masked database URI"""
        uri = obj.database_uri
        if "://" in uri:
            protocol, rest = uri.split("://", 1)
            if "@" in rest:
                credentials, host = rest.split("@", 1)
                return f"{protocol}://***:***@{host}"
        return "***"


class SQLToolExecutionSerializer(serializers.ModelSerializer):
    """
    Serializer for SQL tool execution tracking
    """
    mcp_request = OpenAIMCPRequestSerializer(read_only=True)
    mcp_request_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    database = SQLDatabaseConnectionListSerializer(read_only=True)
    database_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = SQLToolExecution
        fields = [
            "id",
            "mcp_request",
            "mcp_request_id",
            "database",
            "database_id",
            "tool_name",
            "tool_input",
            "tool_output",
            "sql_query",
            "query_result",
            "status",
            "error_message",
            "execution_time_ms",
            "created_at",
            "completed_at",
        ]
        read_only_fields = ["id", "created_at", "completed_at"]

    def validate_tool_name(self, value):
        """Validate tool name is one of the supported tools"""
        valid_tools = [
            "QuerySQLDataBaseTool",
            "InfoSQLDatabaseTool",
            "ListSQLDatabaseTool",
            "QuerySQLCheckerTool",
        ]
        if value not in valid_tools:
            raise serializers.ValidationError(
                f"Invalid tool name. Must be one of: {', '.join(valid_tools)}"
            )
        return value


class SQLToolExecutionListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing tool executions
    """
    database_name = serializers.CharField(source="database.name", read_only=True)

    class Meta:
        model = SQLToolExecution
        fields = [
            "id",
            "database_name",
            "tool_name",
            "status",
            "execution_time_ms",
            "created_at",
        ]


# ============================================
# Supporting Model Serializers
# ============================================

class MCPRequestLogSerializer(serializers.ModelSerializer):
    """
    Serializer for MCP request logs
    """
    mcp_request = OpenAIMCPRequestSerializer(read_only=True)
    mcp_request_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = MCPRequestLog
        fields = [
            "id",
            "mcp_request",
            "mcp_request_id",
            "function_name",
            "user_query",
            "sql_query",
            "db_response",
            "mcp_response",
            "should_continue",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MCPRequestLogListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing logs
    """
    class Meta:
        model = MCPRequestLog
        fields = [
            "id",
            "function_name",
            "should_continue",
            "created_at",
        ]


class MCPToolSchemaSerializer(serializers.ModelSerializer):
    """
    Serializer for MCP tool schemas
    """
    class Meta:
        model = MCPToolSchema
        fields = [
            "id",
            "name",
            "description",
            "input_schema",
            "output_schema",
            "category",
            "langchain_tool_class",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_input_schema(self, value):
        """Validate input_schema is a valid JSON Schema"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("input_schema must be a JSON object")

        # Basic JSON Schema validation
        if "type" not in value:
            raise serializers.ValidationError("input_schema must have 'type' field")

        return value

    def validate_output_schema(self, value):
        """Validate output_schema if provided"""
        if value is not None and not isinstance(value, dict):
            raise serializers.ValidationError("output_schema must be a JSON object")
        return value


class MCPToolSchemaListSerializer(serializers.ModelSerializer):
    """
    Serializer for MCP tools/list response
    """
    class Meta:
        model = MCPToolSchema
        fields = ["name", "description", "input_schema"]

    def to_representation(self, instance):
        """Convert to MCP tools/list format"""
        return {
            "name": instance.name,
            "description": instance.description,
            "inputSchema": instance.input_schema,
        }


class MCPSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for MCP sessions
    """
    database = SQLDatabaseConnectionListSerializer(read_only=True)
    database_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = MCPSession
        fields = [
            "id",
            "session_id",
            "user_id",
            "database",
            "database_id",
            "context_data",
            "is_active",
            "created_at",
            "last_activity",
            "expires_at",
        ]
        read_only_fields = ["id", "created_at", "last_activity"]

    def validate_session_id(self, value):
        """Validate session_id is unique for active sessions"""
        if self.instance is None:  # Creating new session
            if MCPSession.objects.filter(session_id=value, is_active=True).exists():
                raise serializers.ValidationError(
                    "An active session with this session_id already exists"
                )
        return value


class MCPSessionListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing sessions
    """
    database_name = serializers.CharField(source="database.name", read_only=True)

    class Meta:
        model = MCPSession
        fields = [
            "id",
            "session_id",
            "user_id",
            "database_name",
            "is_active",
            "last_activity",
        ]


# ============================================
# Nested Serializers for Complex Operations
# ============================================

class MCPToolCallRequestSerializer(serializers.Serializer):
    """
    Serializer for tools/call request
    """
    name = serializers.CharField(help_text="Tool name to call")
    arguments = serializers.JSONField(help_text="Tool input arguments")

    def validate_name(self, value):
        """Validate tool exists and is active"""
        if not MCPToolSchema.objects.filter(name=value, is_active=True).exists():
            raise serializers.ValidationError(f"Tool '{value}' not found or inactive")
        return value


class MCPToolCallResponseSerializer(serializers.Serializer):
    """
    Serializer for tools/call response
    """
    content = serializers.ListField(
        child=serializers.DictField(),
        help_text="Response content"
    )
    isError = serializers.BooleanField(default=False, help_text="Whether an error occurred")


class MCPToolsListResponseSerializer(serializers.Serializer):
    """
    Serializer for tools/list response
    """
    tools = MCPToolSchemaListSerializer(many=True)

    def to_representation(self, instance):
        """Format as MCP tools/list response"""
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.input_schema,
                }
                for tool in instance
            ]
        }


# ============================================
# Statistics and Analytics Serializers
# ============================================

class MCPStatisticsSerializer(serializers.Serializer):
    """
    Serializer for MCP statistics and analytics
    """
    total_requests = serializers.IntegerField()
    total_responses = serializers.IntegerField()
    successful_responses = serializers.IntegerField()
    error_responses = serializers.IntegerField()
    average_processing_time_ms = serializers.FloatField()
    total_tool_executions = serializers.IntegerField()
    active_sessions = serializers.IntegerField()
    most_used_tools = serializers.ListField(child=serializers.DictField())
    requests_by_method = serializers.DictField()
