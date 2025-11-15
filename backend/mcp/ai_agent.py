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
import pandas as pd

from .models import SQLDatabaseConnection, SQLToolExecution, OpenAIMCPRequest
from .utils import is_openai_configured
from .visualization import VisualizationGenerator

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
            # Execute agent and capture SQL queries from tool calls
            logger.info(f"AI Agent processing query: {user_query}")
            
            # Use stream to capture tool calls with SQL queries (for AgentExecutor)
            sql_queries = []
            final_output = None
            
            try:
                # AgentExecutor.stream() returns chunks with actions and steps
                for chunk in self.agent.stream({"input": user_query}):
                    # Extract SQL from actions in each chunk
                    if "actions" in chunk:
                        for action in chunk["actions"]:
                            if hasattr(action, "tool"):
                                tool_name = action.tool
                                # Capture SQL queries from sql_db_query tool (not checker)
                                if tool_name == "sql_db_query":
                                    if hasattr(action, "tool_input"):
                                        tool_input = action.tool_input
                                        if isinstance(tool_input, dict) and "query" in tool_input:
                                            query = tool_input["query"]
                                            if isinstance(query, str) and query.strip().upper().startswith("SELECT"):
                                                sql_queries.append(query)
                                                logger.info(f"Captured SQL query from stream: {query[:100]}...")
                    
                    # Also check steps (some chunks have steps instead of actions)
                    if "steps" in chunk:
                        for step in chunk["steps"]:
                            if hasattr(step, "action"):
                                action = step.action
                                if hasattr(action, "tool") and action.tool == "sql_db_query":
                                    if hasattr(action, "tool_input"):
                                        tool_input = action.tool_input
                                        if isinstance(tool_input, dict) and "query" in tool_input:
                                            query = tool_input["query"]
                                            if isinstance(query, str) and query.strip().upper().startswith("SELECT"):
                                                sql_queries.append(query)
                                                logger.info(f"Captured SQL query from stream steps: {query[:100]}...")
                    
                    # Keep track of final output
                    if "output" in chunk:
                        final_output = chunk["output"]
                
                # If we didn't get output from stream, use invoke
                if final_output is None:
                    result = self.agent.invoke({"input": user_query})
                    final_output = result.get("output", "")
            except Exception as stream_error:
                # If streaming fails, fall back to invoke
                logger.warning(f"Streaming failed, using invoke: {stream_error}")
                result = self.agent.invoke({"input": user_query})
                final_output = result.get("output", "")
            
            execution_time = int((time.time() - start_time) * 1000)

            # Extract SQL query - use captured queries or fall back to extraction method
            sql_query = None
            if sql_queries:
                sql_query = sql_queries[-1]  # Use the last SELECT query
                logger.info(f"Using SQL query from stream: {sql_query[:100]}...")
            else:
                # Create a result dict for extraction method
                result_dict = {"output": final_output} if final_output else {}
                sql_query = self._extract_sql_query(result_dict, mcp_request)
                if sql_query:
                    logger.info(f"Extracted SQL query from fallback method: {sql_query[:100]}...")
                else:
                    logger.warning("No SQL query could be extracted from agent execution")

            # Generate visualization if applicable
            visualization = None
            if sql_query:  # Only if we have SQL query
                try:
                    logger.info(f"Attempting to generate visualization for SQL: {sql_query[:100]}...")
                    # Execute SQL to get DataFrame for visualization
                    df = self._execute_sql_to_dataframe(sql_query)

                    if df is not None and not df.empty:
                        logger.info(f"DataFrame created with {len(df)} rows, {len(df.columns)} columns")
                        logger.info(f"DataFrame columns: {list(df.columns)}")
                        logger.info(f"DataFrame head:\n{df.head()}")
                        
                        viz_generator = VisualizationGenerator()
                        should_viz = viz_generator.should_visualize(user_query, sql_query, df)
                        logger.info(f"Should visualize: {should_viz}")
                        
                        if should_viz:
                            visualization = viz_generator.generate_visualization(
                                df=df,
                                query=user_query,
                                sql_query=sql_query,
                                config={}
                            )
                            if visualization:
                                logger.info(f"Visualization generated successfully: {visualization.get('chart_type')}")
                                logger.info(f"Visualization keys: {list(visualization.keys())}")
                            else:
                                logger.warning("Visualization generator returned None despite should_visualize=True")
                        else:
                            logger.info("Visualization generator determined visualization not suitable")
                    else:
                        logger.warning(f"DataFrame is empty or None, skipping visualization")
                except Exception as e:
                    logger.error(f"Error generating visualization: {e}", exc_info=True)
                    # Continue without visualization - text response is more important
            else:
                logger.warning("No SQL query available, skipping visualization generation")

            # Update tool execution
            tool_execution.tool_output = {
                "user_query": user_query,
                "result": final_output or "",
                "intermediate_steps": str(sql_queries)[:1000],
                "visualization_generated": visualization is not None,
            }
            tool_execution.sql_query = sql_query
            tool_execution.query_result = {"output": final_output or ""}
            tool_execution.status = "success"
            tool_execution.execution_time_ms = execution_time
            tool_execution.save()

            response = {
                "success": True,
                "user_query": user_query,
                "sql_query": sql_query,
                "result": final_output or "",
                "execution_time_ms": execution_time,
                "tool_execution_id": tool_execution.id,
            }
            
            # Add visualization if available
            if visualization:
                response["visualization"] = visualization

            return response

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

    def _extract_sql_query(self, result: Dict, mcp_request: Optional[OpenAIMCPRequest] = None) -> Optional[str]:
        """
        Extract SQL query from agent result using multiple methods

        Args:
            result: Agent execution result
            mcp_request: Optional MCP request to query related SQLToolExecution records
        Returns:
            SQL query string or None
        """
        try:
            sql_queries = []
            
            # Method 1: Extract from messages in result (for openai-tools agent type)
            if "messages" in result:
                for message in result["messages"]:
                    # Check if message has tool_calls
                    if hasattr(message, "tool_calls") and message.tool_calls:
                        for tool_call in message.tool_calls:
                            tool_name = tool_call.get("name", "")
                            tool_args = tool_call.get("args", {})
                            
                            if "sql" in tool_name.lower() and "query" in tool_name.lower():
                                if isinstance(tool_args, dict) and "query" in tool_args:
                                    query = tool_args["query"]
                                    if isinstance(query, str) and query.strip().upper().startswith("SELECT"):
                                        sql_queries.append(query)
            
            # Method 2: Try to extract from intermediate steps (for other agent types)
            intermediate_steps = result.get("intermediate_steps", [])
            for step in intermediate_steps:
                if len(step) >= 2:
                    action = step[0]
                    if hasattr(action, "tool"):
                        tool_name = action.tool
                        if tool_name == "sql_db_query":
                            if hasattr(action, "tool_input"):
                                tool_input = action.tool_input
                                if isinstance(tool_input, dict) and "query" in tool_input:
                                    query = tool_input["query"]
                                    if query.strip().upper().startswith("SELECT"):
                                        sql_queries.append(query)
                                elif isinstance(tool_input, str):
                                    if tool_input.strip().upper().startswith("SELECT"):
                                        sql_queries.append(tool_input)

            # Method 3: Query SQLToolExecution records (fallback)
            if not sql_queries and mcp_request:
                from django.utils import timezone
                from datetime import timedelta
                
                recent_executions = SQLToolExecution.objects.filter(
                    mcp_request=mcp_request,
                    sql_query__isnull=False,
                    sql_query__startswith="SELECT",
                    created_at__gte=timezone.now() - timedelta(minutes=1)
                ).order_by('-created_at')
                
                if recent_executions.exists():
                    sql_query = recent_executions.first().sql_query
                    logger.info(f"Extracted SQL query from SQLToolExecution: {sql_query[:100]}...")
                    return sql_query

            # Return the last SELECT query if found
            if sql_queries:
                logger.info(f"Extracted SQL query: {sql_queries[-1][:100]}...")
                return sql_queries[-1]

            logger.info("No SELECT query found in any extraction method")
            return None
        except Exception as e:
            logger.error(f"Error extracting SQL query: {e}", exc_info=True)
            return None

    def _execute_sql_to_dataframe(self, sql_query: str) -> Optional[pd.DataFrame]:
        """
        Execute SQL query and return results as DataFrame
        
        Args:
            sql_query: SQL query string
            
        Returns:
            DataFrame with query results or None if error
        """
        try:
            if not sql_query or not sql_query.strip():
                return None
            
            # Use the database connection to execute SQL
            # SQLDatabase has a run method that returns string, but we need DataFrame
            # So we use pandas.read_sql directly with the database URI
            return pd.read_sql(sql_query, self.connection.database_uri)
            
        except Exception as e:
            logger.warning(f"Could not execute SQL to DataFrame: {e}")
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
