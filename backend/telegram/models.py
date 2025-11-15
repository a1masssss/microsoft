from django.db import models


class TelegramUser(models.Model):
    """Stores Telegram user information"""
    user_id = models.BigIntegerField(unique=True, db_index=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    language_code = models.CharField(max_length=10, null=True, blank=True)
    is_bot = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'telegram_users'
        verbose_name = 'Telegram User'
        verbose_name_plural = 'Telegram Users'

    def __str__(self):
        return f"{self.user_id} - {self.username or self.first_name}"


class ChatInteraction(models.Model):
    """Logs all chat interactions for audit and improvement"""
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='interactions')
    message_text = models.TextField()
    response_text = models.TextField(null=True, blank=True)
    query_generated = models.TextField(null=True, blank=True) 
    query_result = models.JSONField(null=True, blank=True)  
    success = models.BooleanField(default=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_interactions'
        verbose_name = 'Chat Interaction'
        verbose_name_plural = 'Chat Interactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
