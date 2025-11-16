import logging
import time
import traceback
import io
import base64
from datetime import timedelta, datetime
import pandas as pd
from django.conf import settings
from django.db.models import Avg, Count
from django.utils import timezone
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from urllib.parse import quote

from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import (
    QuerySQLDatabaseTool,
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
)

from .utils import (
    get_llm_for_sql_toolkit,
    is_openai_configured,
    format_sql_result,
    validate_sql_query,
    parse_table_list,
    create_mcp_error_response,
    MCP_ERROR_CODES,
)

from .models import (
    OpenAIMCPRequest,
    OpenAIMCPResponse,
    SQLDatabaseConnection,
    SQLToolExecution,
    MCPRequestLog,
    MCPToolSchema,
    MCPSession,
)
from .serializers import (
    SQLDatabaseConnectionSerializer,
    SQLDatabaseConnectionListSerializer,
    SQLToolExecutionSerializer,
    SQLToolExecutionListSerializer,
    MCPRequestLogSerializer,
    MCPToolSchemaSerializer,
    MCPSessionSerializer,
    MCPSessionListSerializer,
    MCPStatisticsSerializer,
)
from telegram.models import ChatInteraction
from telegram.utils import get_telegram_user_from_request

try:
    from google import generativeai as genai
except ImportError:  # pragma: no cover - handled via requirements
    genai = None

logger = logging.getLogger(__name__)
_gemini_model = None


def _get_gemini_model():
    global _gemini_model
    if not settings.GEMINI_API_KEY:
        raise ValueError("Gemini API key is not configured")

    if genai is None:
        raise ValueError("google-generativeai package is not installed")

    if _gemini_model is None:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel("gemini-2.0-flash-exp")
    return _gemini_model


# ============================================
# Helper Functions
# ============================================

def create_langchain_db(connection: SQLDatabaseConnection):
    """Create LangChain SQLDatabase from connection"""
    try:
        # LangChain SQLDatabase only supports include_tables, not exclude_tables
        db = SQLDatabase.from_uri(
            connection.database_uri,
            sample_rows_in_table_info=connection.sample_rows_in_table_info,
            include_tables=connection.include_tables or None,
        )
        return db
    except Exception as e:
        raise ValueError(f"Failed to connect to database: {str(e)}")


def execute_sql_tool(tool_name: str, db, tool_input: dict, connection: SQLDatabaseConnection, mcp_request=None):
    """
    Execute a LangChain SQL tool and track execution

    Args:
        tool_name: Name of the tool to execute
        db: LangChain SQLDatabase instance
        tool_input: Input parameters for the tool
        connection: SQLDatabaseConnection instance
        mcp_request: Optional MCP request for tracking

    Returns:
        dict with success status, result/error, and execution time
    """
    start_time = time.time()

    # Create tool execution record
    tool_execution = SQLToolExecution.objects.create(
        mcp_request=mcp_request,
        database=connection,
        tool_name=tool_name,
        tool_input=tool_input,
        status="pending",
    )

    try:
        # Check if OpenAI is configured (for tools that need it)
        if not is_openai_configured():
            # Some tools might work without LLM, but log a warning
            pass

        # Get LLM if configured (for tools that need it)
        llm = get_llm_for_sql_toolkit()

        # Select and execute the appropriate tool
        if tool_name in ("QuerySQLDataBaseTool", "QuerySQLDatabaseTool"):
            tool = QuerySQLDatabaseTool(db=db)
            query = tool_input.get("query", "")

            # Basic validation
            is_valid, error_msg = validate_sql_query(query)
            if not is_valid:
                raise ValueError(f"Invalid query: {error_msg}")

            result = tool.invoke(query)
            tool_execution.sql_query = query

        elif tool_name == "ListSQLDatabaseTool":
            tool = ListSQLDatabaseTool(db=db)
            result = tool.invoke("")

        elif tool_name == "InfoSQLDatabaseTool":
            tool = InfoSQLDatabaseTool(db=db)
            table_names = tool_input.get("table_names", "")
            result = tool.invoke(table_names)

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

        # Calculate execution time
        execution_time = int((time.time() - start_time) * 1000)

        # Format result if it's a string (SQL query result)
        formatted_result = result
        if isinstance(result, str):
            formatted_result = format_sql_result(result)

        # Update tool execution record
        tool_execution.tool_output = {"result": formatted_result}
        tool_execution.query_result = {"data": formatted_result}
        tool_execution.status = "success"
        tool_execution.execution_time_ms = execution_time
        tool_execution.completed_at = timezone.now()
        tool_execution.save()

        return {
            "success": True,
            "result": formatted_result,
            "execution_time_ms": execution_time,
            "tool_execution_id": tool_execution.id,
        }

    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)

        # Update tool execution with error
        tool_execution.status = "error"
        tool_execution.error_message = str(e)
        tool_execution.execution_time_ms = execution_time
        tool_execution.completed_at = timezone.now()
        tool_execution.save()

        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "execution_time_ms": execution_time,
            "tool_execution_id": tool_execution.id,
        }


# ============================================
# Deep Query Views (Chain Operations)
# ============================================

class DeepQueryView(APIView):
    """
    Deep Query endpoint - execute multiple SQL operations in a chain

    Example:
    POST /api/mcp/deep-query/
    {
        "database_id": 1,
        "operations": [
            {"type": "list_tables"},
            {"type": "table_info", "tables": ["users", "orders"]},
            {"type": "query", "sql": "SELECT * FROM users LIMIT 10"}
        ]
    }
    """

    def post(self, request):
        """Execute a chain of SQL operations"""
        database_id = request.data.get("database_id")
        operations = request.data.get("operations", [])
        session_id = request.headers.get("X-Session-ID")
        user_id = request.headers.get("X-User-ID")

        if not database_id:
            return Response(
                {"error": "database_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not operations:
            return Response(
                {"error": "operations list is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get database connection
        try:
            connection = SQLDatabaseConnection.objects.get(id=database_id, is_active=True)
        except SQLDatabaseConnection.DoesNotExist:
            return Response(
                {"error": f"Database connection not found: {database_id}"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Create MCP request for tracking
        mcp_request = OpenAIMCPRequest.objects.create(
            jsonrpc="2.0",
            method="deep_query",
            params={"database_id": database_id, "operations": operations},
            request_id=f"deep_query_{int(timezone.now().timestamp() * 1000)}",
            session_id=session_id,
            user_id=user_id,
            raw_request=request.data,
        )

        # Create LangChain database
        try:
            db = create_langchain_db(connection)
        except Exception as e:
            error_response = {
                "error": f"Failed to connect to database: {str(e)}",
                "database": connection.name,
            }

            error_obj = create_mcp_error_response(
                MCP_ERROR_CODES["INTERNAL_ERROR"],
                str(e)
            )
            OpenAIMCPResponse.objects.create(
                request=mcp_request,
                jsonrpc="2.0",
                error=error_obj,
                response_id=mcp_request.request_id,
                status="error",
            )

            return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Execute operations in sequence
        results = []
        total_start_time = time.time()
        should_continue = True

        for idx, operation in enumerate(operations):
            if not should_continue:
                results.append({
                    "operation": operation.get("type"),
                    "index": idx,
                    "success": False,
                    "error": "Skipped due to previous operation failure",
                    "skipped": True,
                })
                continue

            op_type = operation.get("type")

            try:
                if op_type == "list_tables":
                    result = self.execute_list_tables(db, connection, mcp_request)

                elif op_type == "table_info":
                    tables = operation.get("tables", [])
                    result = self.execute_table_info(db, connection, tables, mcp_request)

                elif op_type == "query":
                    sql = operation.get("sql")
                    if not sql:
                        raise ValueError("sql parameter is required for query operation")
                    result = self.execute_query(db, connection, sql, mcp_request)

                else:
                    result = {
                        "success": False,
                        "error": f"Unknown operation type: {op_type}",
                    }

                results.append({
                    "operation": op_type,
                    "index": idx,
                    **result,
                })

                # Stop chain if operation failed
                if not result.get("success", False):
                    should_continue = False

            except Exception as e:
                results.append({
                    "operation": op_type,
                    "index": idx,
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                })
                should_continue = False

        total_time = int((time.time() - total_start_time) * 1000)

        # Determine overall status
        all_successful = all(r.get("success", False) for r in results if not r.get("skipped", False))

        # Create response
        response_data = {
            "database": {
                "id": connection.id,
                "name": connection.name,
                "type": connection.db_type,
            },
            "results": results,
            "total_operations": len(operations),
            "executed_operations": len([r for r in results if not r.get("skipped", False)]),
            "successful_operations": len([r for r in results if r.get("success", False)]),
            "failed_operations": len([r for r in results if not r.get("success", False) and not r.get("skipped", False)]),
            "total_execution_time_ms": total_time,
            "all_successful": all_successful,
        }

        # Create MCP response
        error_obj = None if all_successful else create_mcp_error_response(
            MCP_ERROR_CODES["INTERNAL_ERROR"],
            "Some operations failed"
        )
        OpenAIMCPResponse.objects.create(
            request=mcp_request,
            jsonrpc="2.0",
            result=response_data if all_successful else None,
            error=error_obj,
            response_id=mcp_request.request_id,
            status="success" if all_successful else "error",
            processing_time_ms=total_time,
            raw_response=response_data,
        )

        return Response(response_data)

    def execute_list_tables(self, db, connection, mcp_request):
        """List all tables in the database"""
        result = execute_sql_tool(
            "ListSQLDatabaseTool",
            db,
            {},
            connection,
            mcp_request
        )

        if result["success"]:
            # Parse table list (comma-separated string)
            tables_raw = result["result"]
            tables = [t.strip() for t in tables_raw.split(",") if t.strip()]
            return {
                **result,
                "tables": tables,
                "count": len(tables),
            }
        return result

    def execute_table_info(self, db, connection, tables, mcp_request):
        """Get detailed information about specified tables"""
        if not tables:
            return {
                "success": False,
                "error": "tables parameter is required for table_info operation",
            }

        result = execute_sql_tool(
            "InfoSQLDatabaseTool",
            db,
            {"table_names": ", ".join(tables)},
            connection,
            mcp_request
        )

        if result["success"]:
            return {
                **result,
                "tables_queried": tables,
            }
        return result

    def execute_query(self, db, connection, sql, mcp_request):
        """Execute SQL query"""
        result = execute_sql_tool(
            "QuerySQLDataBaseTool",
            db,
            {"query": sql},
            connection,
            mcp_request
        )

        if result["success"]:
            return {
                **result,
                "sql": sql,
            }
        return result


# ============================================
# Quick Chain Views (@54>?@545;5==K5 F5?>G:8)
# ============================================

class QuickExploreView(APIView):
    """
    KAB@>5 8AA;54>20=85 : ?>4:;NG5=85 -> A?8A>: B01;8F -> 8=D>@<0F8O > B01;8F0E

    Example:
    POST /api/mcp/quick/explore/
    {
        "database_id": 1
    }
    """

    def post(self, request):
        database_id = request.data.get("database_id")

        if not database_id:
            return Response(
                {"error": "database_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            connection = SQLDatabaseConnection.objects.get(id=database_id, is_active=True)
        except SQLDatabaseConnection.DoesNotExist:
            return Response(
                {"error": "Database not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Create MCP request
        mcp_request = OpenAIMCPRequest.objects.create(
            jsonrpc="2.0",
            method="quick_explore",
            params={"database_id": database_id},
            request_id=f"explore_{int(timezone.now().timestamp() * 1000)}",
            session_id=request.headers.get("X-Session-ID"),
            user_id=request.headers.get("X-User-ID"),
            raw_request=request.data,
        )

        start_time = time.time()

        try:
            db = create_langchain_db(connection)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        results = {
            "database": {
                "id": connection.id,
                "name": connection.name,
                "type": connection.db_type,
            }
        }

        # Step 1: List tables
        list_result = execute_sql_tool("ListSQLDatabaseTool", db, {}, connection, mcp_request)

        if list_result["success"]:
            tables = parse_table_list(list_result["result"])
            results["tables"] = tables
            results["table_count"] = len(tables)

            # Step 2: Get info for all tables (limit to first 10 to avoid too much data)
            tables_to_query = tables[:10]
            info_result = execute_sql_tool(
                "InfoSQLDatabaseTool",
                db,
                {"table_names": ", ".join(tables_to_query)},
                connection,
                mcp_request
            )

            if info_result["success"]:
                results["table_info"] = info_result["result"]
                results["tables_queried"] = tables_to_query
            else:
                results["table_info_error"] = info_result["error"]
        else:
            results["error"] = list_result["error"]

        total_time = int((time.time() - start_time) * 1000)
        results["total_execution_time_ms"] = total_time

        # Create MCP response
        OpenAIMCPResponse.objects.create(
            request=mcp_request,
            jsonrpc="2.0",
            result=results,
            response_id=mcp_request.request_id,
            status="success",
            processing_time_ms=total_time,
        )

        return Response(results)


class QuickQueryView(APIView):
    """
    KAB@K9 70?@>A: ?>4:;NG5=85 -> 2K?>;=5=85 SQL

    Example:
    POST /api/mcp/quick/query/
    {
        "database_id": 1,
        "sql": "SELECT * FROM users LIMIT 10"
    }
    """

    def post(self, request):
        database_id = request.data.get("database_id")
        sql = request.data.get("sql")

        if not database_id or not sql:
            return Response(
                {"error": "database_id and sql are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            connection = SQLDatabaseConnection.objects.get(id=database_id, is_active=True)
            db = create_langchain_db(connection)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Create MCP request
        mcp_request = OpenAIMCPRequest.objects.create(
            jsonrpc="2.0",
            method="quick_query",
            params={"database_id": database_id, "sql": sql},
            request_id=f"query_{int(timezone.now().timestamp() * 1000)}",
            session_id=request.headers.get("X-Session-ID"),
            user_id=request.headers.get("X-User-ID"),
            raw_request=request.data,
        )

        start_time = time.time()

        # Execute query
        query_result = execute_sql_tool(
            "QuerySQLDataBaseTool",
            db,
            {"query": sql},
            connection,
            mcp_request
        )

        total_time = int((time.time() - start_time) * 1000)

        results = {
            "database": {
                "id": connection.id,
                "name": connection.name,
                "type": connection.db_type,
            },
            "sql": sql,
            **query_result,
            "total_execution_time_ms": total_time,
        }

        # Create MCP response
        error_obj = None
        if not query_result["success"]:
            error_obj = create_mcp_error_response(
                MCP_ERROR_CODES["INTERNAL_ERROR"],
                query_result.get("error", "Query execution failed")
            )
        OpenAIMCPResponse.objects.create(
            request=mcp_request,
            jsonrpc="2.0",
            result=results if query_result["success"] else None,
            error=error_obj,
            response_id=mcp_request.request_id,
            status="success" if query_result["success"] else "error",
            processing_time_ms=total_time,
        )

        return Response(results)


# ============================================
# MCP Protocol Views
# ============================================

class MCPProtocolView(APIView):
    """
    Main MCP Protocol endpoint
    Handles JSON-RPC 2.0 requests for tools/list and tools/call
    """

    def post(self, request):
        """Handle MCP JSON-RPC 2.0 requests"""
        start_time = time.time()

        # Extract JSON-RPC fields
        jsonrpc = request.data.get("jsonrpc", "2.0")
        method = request.data.get("method")
        params = request.data.get("params", {})
        request_id = request.data.get("id")

        # Validate required fields
        if not method:
            error_obj = create_mcp_error_response(
                MCP_ERROR_CODES["INVALID_REQUEST"],
                "Invalid Request: method is required"
            )
            return Response({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": error_obj
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create MCP request record
        mcp_request = OpenAIMCPRequest.objects.create(
            jsonrpc=jsonrpc,
            method=method,
            params=params,
            request_id=str(request_id) if request_id else f"req_{int(timezone.now().timestamp() * 1000)}",
            session_id=request.headers.get("X-Session-ID"),
            user_id=request.headers.get("X-User-ID"),
            raw_request=request.data,
        )

        try:
            # Route to appropriate handler
            if method == "tools/list":
                result = self.handle_tools_list(params)
            elif method == "tools/call":
                result = self.handle_tools_call(params, mcp_request)
            else:
                raise ValueError(f"Unsupported method: {method}")

            # Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)

            # Create success response
            OpenAIMCPResponse.objects.create(
                request=mcp_request,
                jsonrpc="2.0",
                result=result,
                response_id=mcp_request.request_id,
                status="success",
                processing_time_ms=processing_time,
                raw_response={"jsonrpc": "2.0", "id": request_id, "result": result},
            )

            return Response({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result,
            })

        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)

            # Create error response
            error_obj = create_mcp_error_response(
                MCP_ERROR_CODES["INTERNAL_ERROR"],
                str(e),
                {"traceback": traceback.format_exc()}
            )

            OpenAIMCPResponse.objects.create(
                request=mcp_request,
                jsonrpc="2.0",
                error=error_obj,
                response_id=mcp_request.request_id,
                status="error",
                processing_time_ms=processing_time,
                raw_response={"jsonrpc": "2.0", "id": request_id, "error": error_obj},
            )

            return Response({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": error_obj,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def handle_tools_list(self, params):
        """Handle tools/list method"""
        # Get active tool schemas
        tools = MCPToolSchema.objects.filter(is_active=True)

        tools_list = [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema,
            }
            for tool in tools
        ]

        return {"tools": tools_list}

    def handle_tools_call(self, params, mcp_request):
        """Handle tools/call method"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if not tool_name:
            raise ValueError("Tool name is required")

        # Get tool schema
        try:
            tool_schema = MCPToolSchema.objects.get(name=tool_name, is_active=True)
        except MCPToolSchema.DoesNotExist:
            raise ValueError(f"Tool not found: {tool_name}")

        # Get database connection from arguments
        database_id = arguments.get("database_id")
        if not database_id:
            raise ValueError("database_id is required in arguments")

        try:
            connection = SQLDatabaseConnection.objects.get(id=database_id, is_active=True)
        except SQLDatabaseConnection.DoesNotExist:
            raise ValueError(f"Database connection not found: {database_id}")

        # Create LangChain database
        db = create_langchain_db(connection)

        # Execute the tool
        langchain_tool = tool_schema.langchain_tool_class or tool_name
        result = execute_sql_tool(langchain_tool, db, arguments, connection, mcp_request)

        if result["success"]:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": str(result["result"]),
                    }
                ],
                "isError": False,
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {result['error']}",
                    }
                ],
                "isError": True,
            }


# ============================================
# ViewSets for CRUD Operations
# ============================================

class SQLDatabaseConnectionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing SQL database connections"""
    queryset = SQLDatabaseConnection.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return SQLDatabaseConnectionListSerializer
        return SQLDatabaseConnectionSerializer

    @action(detail=True, methods=["post"])
    def test_connection(self, request, pk=None):
        """Test database connection"""
        connection = self.get_object()

        try:
            db = create_langchain_db(connection)
            # Try to list tables as a connection test
            tool = ListSQLDatabaseTool(db=db)
            result = tool.invoke("")

            tables = parse_table_list(result)

            return Response({
                "success": True,
                "message": "Connection successful",
                "tables": tables,
                "table_count": len(tables),
            })
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SQLToolExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing SQL tool execution history"""
    queryset = SQLToolExecution.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return SQLToolExecutionListSerializer
        return SQLToolExecutionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by database
        database_id = self.request.query_params.get("database_id")
        if database_id:
            queryset = queryset.filter(database_id=database_id)

        # Filter by tool name
        tool_name = self.request.query_params.get("tool_name")
        if tool_name:
            queryset = queryset.filter(tool_name=tool_name)

        # Filter by status
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset


class MCPToolSchemaViewSet(viewsets.ModelViewSet):
    """ViewSet for managing MCP tool schemas"""
    queryset = MCPToolSchema.objects.all()
    serializer_class = MCPToolSchemaSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by active status
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        # Filter by category
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)

        return queryset


class MCPSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing MCP sessions"""
    queryset = MCPSession.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return MCPSessionListSerializer
        return MCPSessionSerializer

    @action(detail=True, methods=["post"])
    def end_session(self, request, pk=None):
        """End an active session"""
        session = self.get_object()
        session.is_active = False
        session.save()

        return Response({
            "success": True,
            "message": "Session ended",
            "session_id": session.session_id,
        })


class MCPRequestLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing MCP request logs"""
    queryset = MCPRequestLog.objects.all()
    serializer_class = MCPRequestLogSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by function name
        function_name = self.request.query_params.get("function_name")
        if function_name:
            queryset = queryset.filter(function_name=function_name)

        # Filter by should_continue
        should_continue = self.request.query_params.get("should_continue")
        if should_continue is not None:
            queryset = queryset.filter(should_continue=should_continue.lower() == "true")

        return queryset


# ============================================
# AI Natural Language Query
# ============================================

class AIQueryView(APIView):
    """
    AI-powered natural language to SQL query endpoint

    Uses OpenAI + LangChain SQL Agent to automatically:
    1. Understand user's natural language query
    2. Generate appropriate SQL query
    3. Execute query on database
    4. Return human-readable results

    Example:
    POST /api/mcp/ai-query/
    {
        "database_id": 1,
        "query": "How many transactions were made in Almaty?"
    }
    """

    def post(self, request):
        """Process natural language query"""
        from .ai_agent import process_natural_language_query

        user_query = request.data.get("query")
        database_id = request.data.get("database_id")

        if not user_query:
            return Response(
                {"error": "query is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not database_id:
            return Response(
                {"error": "database_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get session/user from headers
        session_id = request.headers.get("X-Session-ID")
        user_id = request.headers.get("X-User-ID")

        # Process query with AI Agent
        result = process_natural_language_query(
            user_query=user_query,
            database_id=database_id,
            session_id=session_id,
            user_id=user_id,
        )

        # Persist interaction for Telegram users so History tab can show recent queries
        telegram_user = get_telegram_user_from_request(request)
        if telegram_user:
            try:
                response_payload = result.get("result")
                response_text = (
                    response_payload if isinstance(response_payload, str) else None
                ) or result.get("error") or ""

                ChatInteraction.objects.create(
                    user=telegram_user,
                    message_text=user_query,
                    response_text=response_text,
                    query_generated=result.get("sql_query"),
                    query_result=response_payload
                    if isinstance(response_payload, (dict, list))
                    else None,
                    success=result.get("success", False),
                    error_message=None if result.get("success") else result.get("error"),
                )
            except Exception as log_error:
                logger.warning(
                    "Failed to log Telegram history entry: %s", log_error, exc_info=True
                )

        if result["success"]:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AudioTranscriptionView(APIView):
    """Upload audio and return Gemini transcription."""

    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        audio_file = request.FILES.get("audio")

        if not audio_file:
            return Response({"error": "audio file is required"}, status=status.HTTP_400_BAD_REQUEST)

        if audio_file.size > 6 * 1024 * 1024:  # ~6MB
            return Response({"error": "Размер аудио слишком большой"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            model = _get_gemini_model()
        except ValueError as e:
            logger.error("Gemini configuration error: %s", e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            audio_bytes = audio_file.read()
            mime_type = audio_file.content_type or "audio/webm"
            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

            prompt = (
                "Transcribe this audio input to natural text. "
                "Return clean sentences in the detected language."
            )

            response = model.generate_content([
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": audio_b64,
                    }
                },
            ])

            transcript = (response.text or "").strip()

            if not transcript and response.candidates:
                parts = response.candidates[0].content.parts
                transcript = " ".join(getattr(part, "text", "") for part in parts).strip()

            if not transcript:
                raise ValueError("Gemini returned empty transcription")

            return Response({
                "success": True,
                "transcript": transcript,
                "mime_type": mime_type,
                "duration_seconds": request.data.get("duration"),
            })

        except ValueError as e:
            logger.warning("Transcription validation error: %s", e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Gemini transcription failed: %s", e, exc_info=True)
            return Response({"error": "Не удалось распознать аудио"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================
# Statistics and Analytics
# ============================================

class MCPStatisticsView(APIView):
    """Get MCP statistics and analytics"""

    def get(self, request):
        """Get overall statistics"""

        # Time range filter (default: last 7 days)
        days = int(request.query_params.get("days", 7))
        since = timezone.now() - timedelta(days=days)

        # Requests and responses
        total_requests = OpenAIMCPRequest.objects.filter(created_at__gte=since).count()
        total_responses = OpenAIMCPResponse.objects.filter(created_at__gte=since).count()
        successful_responses = OpenAIMCPResponse.objects.filter(
            created_at__gte=since, status="success"
        ).count()
        error_responses = OpenAIMCPResponse.objects.filter(
            created_at__gte=since, status="error"
        ).count()

        # Average processing time
        avg_processing_time = OpenAIMCPResponse.objects.filter(
            created_at__gte=since
        ).aggregate(Avg("processing_time_ms"))["processing_time_ms__avg"] or 0

        # Tool executions
        total_tool_executions = SQLToolExecution.objects.filter(created_at__gte=since).count()

        # Active sessions
        active_sessions = MCPSession.objects.filter(is_active=True).count()

        # Most used tools
        most_used_tools = list(
            SQLToolExecution.objects.filter(created_at__gte=since)
            .values("tool_name")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        # Requests by method
        requests_by_method = dict(
            OpenAIMCPRequest.objects.filter(created_at__gte=since)
            .values_list("method")
            .annotate(count=Count("id"))
        )

        stats = {
            "total_requests": total_requests,
            "total_responses": total_responses,
            "successful_responses": successful_responses,
            "error_responses": error_responses,
            "average_processing_time_ms": round(avg_processing_time, 2),
            "total_tool_executions": total_tool_executions,
            "active_sessions": active_sessions,
            "most_used_tools": most_used_tools,
            "requests_by_method": requests_by_method,
            "time_range_days": days,
        }

        serializer = MCPStatisticsSerializer(stats)
        return Response(serializer.data)


# ============================================
# Data Export
# ============================================

class ExportDataView(APIView):
    """
    Export SQL query results to CSV or Excel format
    
    POST /api/mcp/export/
    {
        "sql_query": "SELECT * FROM table",
        "format": "csv" | "excel",
        "database_id": 1,
        "filename": "optional_custom_name"
    }
    """

    def post(self, request):
        """Export query results to CSV or Excel"""
        sql_query = request.data.get("sql_query")
        export_format = request.data.get("format", "csv").lower()
        database_id = request.data.get("database_id")
        filename = request.data.get("filename")

        # Validation
        if not sql_query:
            return Response(
                {"error": "sql_query is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if export_format not in ["csv", "excel", "xlsx"]:
            return Response(
                {"error": "format must be 'csv' or 'excel'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not database_id:
            return Response(
                {"error": "database_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate SQL query (only SELECT statements)
        sql_query_upper = sql_query.strip().upper()
        if not sql_query_upper.startswith("SELECT"):
            return Response(
                {"error": "Only SELECT queries are allowed for export"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get database connection
            try:
                database = SQLDatabaseConnection.objects.get(
                    id=database_id,
                    is_active=True
                )
            except SQLDatabaseConnection.DoesNotExist:
                return Response(
                    {"error": f"Database with id {database_id} not found or inactive"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Execute SQL query and get DataFrame
            try:
                df = pd.read_sql(sql_query, database.database_uri)
            except Exception as e:
                return Response(
                    {"error": f"Failed to execute SQL query: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if DataFrame is empty
            if df is None or df.empty:
                return Response(
                    {"error": "Query returned no results"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Limit result size for safety (max 100k rows)
            MAX_ROWS = 100000
            if len(df) > MAX_ROWS:
                df = df.head(MAX_ROWS)
                # Note: We could return a warning, but for simplicity, just truncate

            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"query_results_{timestamp}"

            # Export based on format
            if export_format in ["excel", "xlsx"]:
                # Excel export
                try:
                    # Check if openpyxl is available
                    try:
                        import openpyxl
                    except ImportError:
                        return Response(
                            {"error": "openpyxl is required for Excel export. Please install it: pip install openpyxl"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )

                    # Convert any datetime columns to string for Excel compatibility
                    df_export = df.copy()
                    for col in df_export.columns:
                        if pd.api.types.is_datetime64_any_dtype(df_export[col]):
                            df_export[col] = df_export[col].astype(str)

                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df_export.to_excel(writer, sheet_name='Query Results', index=False)
                    output.seek(0)

                    excel_content = output.read()
                    response = HttpResponse(
                        excel_content,
                        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                    # Use both filename and filename* for better browser compatibility
                    safe_filename = quote(f"{filename}.xlsx")
                    response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"; filename*=UTF-8\'\'{safe_filename}'
                    response['Content-Length'] = str(len(excel_content))
                    return response
                except Exception as excel_error:
                    logger.error(f"Excel export error: {excel_error}", exc_info=True)
                    return Response(
                        {"error": f"Excel export failed: {str(excel_error)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                # CSV export
                output = io.StringIO()
                df.to_csv(output, index=False, encoding='utf-8')
                csv_content = output.getvalue()
                
                # Convert to bytes for proper content length
                csv_bytes = csv_content.encode('utf-8')

                response = HttpResponse(csv_bytes, content_type='text/csv; charset=utf-8')
                # Use both filename and filename* for better browser compatibility
                safe_filename = quote(f"{filename}.csv")
                response['Content-Disposition'] = f'attachment; filename="{filename}.csv"; filename*=UTF-8\'\'{safe_filename}'
                response['Content-Length'] = str(len(csv_bytes))
                return response

        except Exception as e:
            logger.error(f"Export failed: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Export failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

