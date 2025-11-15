from django.db import models


# ============================================
# MCP Protocol Models (JSON-RPC 2.0)
# ============================================

class OpenAIMCPRequest(models.Model):
    """
    MCP Request following JSON-RPC 2.0 protocol
    Used for tracking incoming MCP requests from OpenAI
    """
    # JSON-RPC 2.0 fields
    jsonrpc = models.CharField(max_length=10, default="2.0", help_text="JSON-RPC version")
    method = models.CharField(max_length=255, help_text="MCP method (e.g., 'tools/list', 'tools/call')")
    params = models.JSONField(blank=True, null=True, help_text="Request parameters")
    request_id = models.CharField(max_length=255, db_index=True, help_text="Request identifier")

    # Metadata
    session_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    user_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Raw request data
    raw_request = models.JSONField(blank=True, null=True, help_text="Complete raw request")

    class Meta:
        db_table = "openai_mcp_request"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at", "method"]),
            models.Index(fields=["session_id", "-created_at"]),
        ]

    def __str__(self):
        return f"[{self.method}] ID:{self.request_id} at {self.created_at}"


class OpenAIMCPResponse(models.Model):
    """
    MCP Response following JSON-RPC 2.0 protocol
    Links to the corresponding request
    """
    # Link to request
    request = models.ForeignKey(
        OpenAIMCPRequest,
        on_delete=models.CASCADE,
        related_name="responses"
    )

    # JSON-RPC 2.0 fields
    jsonrpc = models.CharField(max_length=10, default="2.0")
    result = models.JSONField(blank=True, null=True, help_text="Success result")
    error = models.JSONField(blank=True, null=True, help_text="Error object if failed")
    response_id = models.CharField(max_length=255, help_text="Matches request_id")

    # Status tracking
    status = models.CharField(
        max_length=50,
        choices=[
            ("success", "Success"),
            ("error", "Error"),
            ("pending", "Pending"),
        ],
        default="pending"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    processing_time_ms = models.IntegerField(blank=True, null=True, help_text="Processing time in milliseconds")

    # Raw response data
    raw_response = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = "openai_mcp_response"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Response to {self.request.method} - {self.status}"


# ============================================
# LangChain SQL Toolkit Models
# ============================================

class SQLDatabaseConnection(models.Model):
    """
    Configuration for SQL database connections used with LangChain SQL Toolkit
    """
    name = models.CharField(max_length=255, unique=True, help_text="Connection name/identifier")
    database_uri = models.CharField(max_length=1024, help_text="Database connection URI")

    # Database info
    db_type = models.CharField(
        max_length=50,
        choices=[
            ("postgresql", "PostgreSQL"),
            ("mysql", "MySQL"),
            ("sqlite", "SQLite"),
            ("mssql", "Microsoft SQL Server"),
            ("oracle", "Oracle"),
        ],
        default="postgresql"
    )

    # Toolkit configuration
    sample_rows_in_table_info = models.IntegerField(default=3, help_text="Number of sample rows to include")
    include_tables = models.JSONField(blank=True, null=True, help_text="List of tables to include")
    exclude_tables = models.JSONField(blank=True, null=True, help_text="List of tables to exclude")

    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sql_database_connection"

    def __str__(self):
        return f"{self.name} ({self.db_type})"


class SQLToolExecution(models.Model):
    """
    Tracks execution of LangChain SQL Toolkit tools
    """
    # MCP context
    mcp_request = models.ForeignKey(
        OpenAIMCPRequest,
        on_delete=models.CASCADE,
        related_name="sql_tool_executions",
        blank=True,
        null=True
    )

    # Database connection
    database = models.ForeignKey(
        SQLDatabaseConnection,
        on_delete=models.CASCADE,
        related_name="tool_executions"
    )

    # Tool information
    tool_name = models.CharField(
        max_length=255,
        choices=[
            ("QuerySQLDataBaseTool", "Query SQL Database"),
            ("InfoSQLDatabaseTool", "Get Database Info"),
            ("ListSQLDatabaseTool", "List Database Tables"),
            ("QuerySQLCheckerTool", "Check SQL Query"),
        ],
        help_text="LangChain SQL tool used"
    )

    # Input/Output
    tool_input = models.JSONField(help_text="Input parameters for the tool")
    tool_output = models.JSONField(blank=True, null=True, help_text="Tool execution result")

    # SQL query details (for query tools)
    sql_query = models.TextField(blank=True, null=True, help_text="Generated or checked SQL query")
    query_result = models.JSONField(blank=True, null=True, help_text="SQL query results")

    # Execution metadata
    status = models.CharField(
        max_length=50,
        choices=[
            ("success", "Success"),
            ("error", "Error"),
            ("pending", "Pending"),
        ],
        default="pending"
    )
    error_message = models.TextField(blank=True, null=True)
    execution_time_ms = models.IntegerField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "sql_tool_execution"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tool_name", "-created_at"]),
            models.Index(fields=["database", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.tool_name} on {self.database.name} - {self.status}"


class MCPRequestLog(models.Model):
    """
    Model for logging MCP (Model Context Protocol) requests and responses.
    Detailed logging for MCP request flow - enhanced for better tracking
    """
    # Link to MCP request/response
    mcp_request = models.ForeignKey(
        OpenAIMCPRequest,
        on_delete=models.CASCADE,
        related_name="logs",
        blank=True,
        null=True
    )
    
    # Function/tool information
    function_name = models.CharField(max_length=255, help_text="Function or tool called")
    user_query = models.TextField(help_text="Original user query")

    # SQL details
    sql_query = models.TextField(blank=True, null=True, help_text="Generated SQL query")
    db_response = models.TextField(blank=True, null=True, help_text="Database response")

    # MCP response details
    mcp_response = models.TextField(blank=True, null=True, help_text="MCP response text")
    should_continue = models.BooleanField(default=False, help_text="Continue chain of actions?")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mcp_request_log"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.function_name} at {self.created_at}"


# ============================================
# Tool Schema Registry
# ============================================

class MCPToolSchema(models.Model):
    """
    Registry of available MCP tools and their schemas
    Used for tools/list MCP method
    """
    # Tool identification
    name = models.CharField(max_length=255, unique=True, help_text="Tool name")
    description = models.TextField(help_text="Tool description")

    # JSON Schema for tool input/output
    input_schema = models.JSONField(help_text="JSON Schema for tool input")
    output_schema = models.JSONField(blank=True, null=True, help_text="JSON Schema for tool output")

    # Tool category
    category = models.CharField(
        max_length=100,
        choices=[
            ("sql_query", "SQL Query"),
            ("sql_info", "SQL Information"),
            ("sql_admin", "SQL Administration"),
            ("general", "General"),
        ],
        default="general"
    )

    # Associated LangChain tool (if any)
    langchain_tool_class = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="LangChain tool class name"
    )

    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mcp_tool_schema"
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.name} ({self.category})"

    def to_mcp_tool_format(self):
        """Convert to MCP tools/list format"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }


# ============================================
# Session Management
# ============================================

class MCPSession(models.Model):
    """
    Track MCP sessions for context management
    """
    session_id = models.CharField(max_length=255, unique=True, db_index=True)
    user_id = models.CharField(max_length=255, blank=True, null=True)

    # Session context
    database = models.ForeignKey(
        SQLDatabaseConnection,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sessions"
    )

    # Session state
    context_data = models.JSONField(blank=True, null=True, help_text="Session context and variables")
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "mcp_session"
        ordering = ["-last_activity"]

    def __str__(self):
        return f"Session {self.session_id} - {self.user_id or 'Anonymous'}"

class Transaction(models.Model):
    """
    Model representing financial transactions from the Parquet dataset.
    Contains 11.5M+ transaction records with card, merchant, and transaction details.
    """
    
    # Transaction identifiers
    transaction_id = models.CharField(
        max_length=255, 
        unique=True, 
        db_index=True,
        help_text="Unique identifier for the transaction (UUID format)"
    )
    transaction_timestamp = models.DateTimeField(
        db_index=True,
        help_text="Timestamp when the transaction occurred"
    )
    
    # Card information
    card_id = models.BigIntegerField(
        db_index=True,
        help_text="Identifier for the card used in the transaction"
    )
    expiry_date = models.CharField(
        max_length=10,
        help_text="Card expiry date in MM/YY format"
    )
    issuer_bank_name = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Name of the bank that issued the card"
    )
    
    # Merchant information
    merchant_id = models.BigIntegerField(
        db_index=True,
        help_text="Unique identifier for the merchant"
    )
    merchant_mcc = models.IntegerField(
        db_index=True,
        help_text="Merchant Category Code (MCC)"
    )
    mcc_category = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Human-readable category of the merchant (e.g., 'Grocery & Food Markets')"
    )
    merchant_city = models.CharField(
        max_length=255,
        db_index=True,
        help_text="City where the merchant is located"
    )
    
    # Transaction details
    transaction_type = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Type of transaction (e.g., 'POS', 'Online', etc.)"
    )
    transaction_amount_kzt = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Transaction amount in Kazakhstani Tenge (KZT)"
    )
    original_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Original amount in original currency (if different from KZT)"
    )
    transaction_currency = models.CharField(
        max_length=3,
        help_text="Currency code of the transaction (ISO 4217)"
    )
    acquirer_country_iso = models.CharField(
        max_length=3,
        db_index=True,
        help_text="ISO country code of the acquirer"
    )
    
    # Payment method details
    pos_entry_mode = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Point of Sale entry mode (e.g., 'Contactless', 'Chip', etc.)"
    )
    wallet_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_index=True,
        help_text="Digital wallet type (e.g., 'Apple Pay', 'Google Pay', etc.)"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this record was created in the database"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when this record was last updated"
    )
    
    class Meta:
        db_table = 'mcp_transactions'
        ordering = ['-transaction_timestamp']
        indexes = [
            models.Index(fields=['transaction_timestamp', 'card_id']),
            models.Index(fields=['merchant_id', 'transaction_timestamp']),
            models.Index(fields=['issuer_bank_name', 'transaction_timestamp']),
            models.Index(fields=['mcc_category', 'transaction_timestamp']),
        ]
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.transaction_amount_kzt} KZT"
    
    @property
    def formatted_amount(self):
        """Returns formatted transaction amount with currency."""
        return f"{self.transaction_amount_kzt:,.2f} KZT"
