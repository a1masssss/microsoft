"""
AI Agent for Natural Language to SQL using LangChain SQL Agent
Processes user queries in natural language and executes SQL automatically
"""

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from django.conf import settings
from typing import Dict, Any, Optional
import time
import logging

from .models import SQLDatabaseConnection, SQLToolExecution, OpenAIMCPRequest
from .utils import is_openai_configured

logger = logging.getLogger(__name__)


class SQLAIAgent:
    """AI Agent for natural language SQL queries"""

    def __init__(self, database_connection: SQLDatabaseConnection):
        """
        Initialize AI Agent with database connection

        Args:
            database_connection: SQLDatabaseConnection instance
        """
        self.connection = database_connection
        self.db = None
        self.agent = None
        self._initialize_agent()

    def _initialize_agent(self):
        """Initialize LangChain SQL Agent"""
        if not is_openai_configured():
            raise ValueError("OpenAI API key is not configured")

        # Create SQLDatabase
        self.db = SQLDatabase.from_uri(
            self.connection.database_uri,
            sample_rows_in_table_info=self.connection.sample_rows_in_table_info,
            include_tables=self.connection.include_tables or None,
        )

        # Create OpenAI LLM
        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY,
        )

        # Create SQL Agent
        self.agent = create_sql_agent(
            llm=llm,
            db=self.db,
            agent_type="openai-tools",  # Best for OpenAI models
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
            max_execution_time=30,
        )

    def query(
        self,
        user_query: str,
        mcp_request: Optional[OpenAIMCPRequest] = None
    ) -> Dict[str, Any]:
        """
        Process natural language query and return results

        Args:
            user_query: Natural language query from user
            mcp_request: Optional MCP request for tracking

        Returns:
            dict with success, result/error, execution details
        """
        start_time = time.time()

        # Create tool execution record
        tool_execution = SQLToolExecution.objects.create(
            mcp_request=mcp_request,
            database=self.connection,
            tool_name="SQLAIAgent",
            tool_input={"user_query": user_query},
            status="pending",
        )

        try:
            # Execute agent
            logger.info(f"AI Agent processing query: {user_query}")
            result = self.agent.invoke({"input": user_query})

            execution_time = int((time.time() - start_time) * 1000)

            # Extract SQL query from agent's intermediate steps if available
            sql_query = self._extract_sql_query(result)

            # Update tool execution
            tool_execution.tool_output = {
                "user_query": user_query,
                "result": result.get("output", ""),
                "intermediate_steps": str(result.get("intermediate_steps", []))[:1000],
            }
            tool_execution.sql_query = sql_query
            tool_execution.query_result = {"output": result.get("output", "")}
            tool_execution.status = "success"
            tool_execution.execution_time_ms = execution_time
            tool_execution.save()

            return {
                "success": True,
                "user_query": user_query,
                "sql_query": sql_query,
                "result": result.get("output", ""),
                "execution_time_ms": execution_time,
                "tool_execution_id": tool_execution.id,
            }

        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"AI Agent error: {e}", exc_info=True)

            # Update tool execution with error
            tool_execution.status = "error"
            tool_execution.error_message = str(e)
            tool_execution.execution_time_ms = execution_time
            tool_execution.save()

            return {
                "success": False,
                "user_query": user_query,
                "error": str(e),
                "execution_time_ms": execution_time,
                "tool_execution_id": tool_execution.id,
            }

    def _extract_sql_query(self, result: Dict) -> Optional[str]:
        """
        Extract SQL query from agent result

        Args:
            result: Agent execution result

        Returns:
            SQL query string or None
        """
        try:
            # Try to extract from intermediate steps
            intermediate_steps = result.get("intermediate_steps", [])
            for step in intermediate_steps:
                if len(step) >= 2:
                    action = step[0]
                    if hasattr(action, "tool_input"):
                        tool_input = action.tool_input
                        if isinstance(tool_input, dict) and "query" in tool_input:
                            return tool_input["query"]
                        elif isinstance(tool_input, str):
                            # Sometimes it's just a string SQL query
                            return tool_input
            return None
        except Exception as e:
            logger.warning(f"Could not extract SQL query: {e}")
            return None


def process_natural_language_query(
    user_query: str,
    database_id: int,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Process natural language query using AI Agent

    Args:
        user_query: User's natural language query
        database_id: ID of database connection to use
        session_id: Optional session ID for tracking
        user_id: Optional user ID for tracking

    Returns:
        dict with success status and results
    """
    try:
        # Get database connection
        connection = SQLDatabaseConnection.objects.get(id=database_id, is_active=True)

        # Create MCP request for tracking
        mcp_request = OpenAIMCPRequest.objects.create(
            jsonrpc="2.0",
            method="ai_query",
            params={"user_query": user_query, "database_id": database_id},
            request_id=f"ai_query_{int(time.time() * 1000)}",
            session_id=session_id,
            user_id=user_id,
            raw_request={"user_query": user_query, "database_id": database_id},
        )

        # Create and use AI Agent
        agent = SQLAIAgent(connection)
        result = agent.query(user_query, mcp_request)

        return {
            **result,
            "database": {
                "id": connection.id,
                "name": connection.name,
                "type": connection.db_type,
            },
        }

    except SQLDatabaseConnection.DoesNotExist:
        return {
            "success": False,
            "error": f"Database connection not found: {database_id}",
        }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e),
        }
    except Exception as e:
        logger.error(f"Error processing AI query: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }
