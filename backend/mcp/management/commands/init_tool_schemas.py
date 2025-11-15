"""
Management command to initialize MCP Tool Schemas
Creates real tool schemas for LangChain SQL Toolkit
"""

from django.core.management.base import BaseCommand
from mcp.models import MCPToolSchema


class Command(BaseCommand):
    help = 'Initialize MCP Tool Schemas for LangChain SQL Toolkit'

    def handle(self, *args, **options):
        """Create tool schemas"""

        schemas = [
            {
                "name": "query_sql_database",
                "description": "Execute a SQL query on the database and return the results. Use this for SELECT statements and data retrieval.",
                "category": "sql_query",
                "langchain_tool_class": "QuerySQLDataBaseTool",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "database_id": {
                            "type": "integer",
                            "description": "ID of the database connection to use"
                        },
                        "query": {
                            "type": "string",
                            "description": "The SQL SELECT query to execute"
                        }
                    },
                    "required": ["database_id", "query"]
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "result": {
                            "type": "string",
                            "description": "Query results as formatted string"
                        },
                        "execution_time_ms": {
                            "type": "integer",
                            "description": "Query execution time in milliseconds"
                        }
                    }
                }
            },
            {
                "name": "list_sql_database_tables",
                "description": "List all tables available in the database. Use this to discover what tables exist.",
                "category": "sql_info",
                "langchain_tool_class": "ListSQLDatabaseTool",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "database_id": {
                            "type": "integer",
                            "description": "ID of the database connection to use"
                        }
                    },
                    "required": ["database_id"]
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "tables": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of table names"
                        }
                    }
                }
            },
            {
                "name": "get_sql_database_schema",
                "description": "Get detailed schema information for specified tables including columns, types, and sample data.",
                "category": "sql_info",
                "langchain_tool_class": "InfoSQLDatabaseTool",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "database_id": {
                            "type": "integer",
                            "description": "ID of the database connection to use"
                        },
                        "table_names": {
                            "type": "string",
                            "description": "Comma-separated list of table names to get schema for"
                        }
                    },
                    "required": ["database_id", "table_names"]
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "schema": {
                            "type": "string",
                            "description": "Detailed schema information with CREATE TABLE statements and sample rows"
                        }
                    }
                }
            }
        ]

        created_count = 0
        updated_count = 0

        for schema_data in schemas:
            tool, created = MCPToolSchema.objects.update_or_create(
                name=schema_data["name"],
                defaults={
                    "description": schema_data["description"],
                    "category": schema_data["category"],
                    "langchain_tool_class": schema_data["langchain_tool_class"],
                    "input_schema": schema_data["input_schema"],
                    "output_schema": schema_data["output_schema"],
                    "is_active": True,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created: {schema_data["name"]}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Updated: {schema_data["name"]}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Done! Created: {created_count}, Updated: {updated_count}'
            )
        )
