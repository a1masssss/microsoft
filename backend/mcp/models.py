from django.db import models

# Create your models here.
# TODO: Implement models for the project 

# MCP Model

from django.db import models


class MCPRequestLog(models.Model):
    # Какая функция была вызвана (например: "list_tables", "select", "update")
    function_name = models.CharField(max_length=255)

    # Что запросил пользователь
    user_query = models.TextField()

    # Сформированный SQL-запрос
    sql_query = models.TextField(blank=True, null=True)

    # Ответ от PostgreSQL
    db_response = models.TextField(blank=True, null=True)

    # Ответ MCP — что делать дальше ("continue", "stop", "error", "next_step", текст и т.п.)
    mcp_response = models.TextField(blank=True, null=True)

    # Нужно ли продолжать цепочку действий?
    should_continue = models.BooleanField(default=False)

    # Время
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mcp_request_log"

    def __str__(self):
        return f"{self.function_name} at {self.created_at}"
