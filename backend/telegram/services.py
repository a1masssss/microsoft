import os
import logging
import requests
from typing import Dict, Any
from .models import TelegramUser, ChatInteraction

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'


class TelegramService:
    """Handles Telegram bot interactions"""

    @staticmethod
    def send_message(chat_id: int, text: str, parse_mode: str = 'HTML') -> Dict[str, Any]:
        """
        Send message to Telegram user

        Args:
            chat_id: Telegram chat ID
            text: Message text to send
            parse_mode: Message formatting (HTML or Markdown)

        Returns:
            Response from Telegram API
        """
        url = f'{TELEGRAM_API_URL}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending message: {e}")
            return {'ok': False, 'error': str(e)}


class MessageHandler:
    """Handles incoming messages"""

    @staticmethod
    def get_or_create_user(user_data: Dict[str, Any]) -> TelegramUser:
        """Get or create TelegramUser from update data"""
        user, created = TelegramUser.objects.update_or_create(
            user_id=user_data['id'],
            defaults={
                'username': user_data.get('username'),
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'language_code': user_data.get('language_code'),
                'is_bot': user_data.get('is_bot', False)
            }
        )
        return user

    @staticmethod
    def handle_message(message_data: Dict[str, Any]) -> str:
        """
        Process incoming message

        Args:
            message_data: Message data from Telegram

        Returns:
            Response text to send back
        """
        user_data = message_data.get('from', {})
        message_text = message_data.get('text', '')
        chat_id = message_data.get('chat', {}).get('id')

        # Get or create user
        user = MessageHandler.get_or_create_user(user_data)

        # Handle commands
        if message_text.startswith('/start'):
            response_text = (
                f"Привет, {user.first_name or 'друг'}! \n\n"
                "Я бот для работы с базой данных через естественный язык.\n\n"
                "Отправь мне запрос, например:\n"
                "• Общее количество транзакций для S1lk Pay в Q1 2024\n"
                "• Топ 5 мерчантов по выручке в Казахстане за прошлый год\n"
                "• Процент отклонений для CID 12345 в октябре"
            )
        elif message_text.startswith('/help'):
            response_text = (
                "Доступные команды:\n\n"
                "/start - Начать работу с ботом\n"
                "/help - Показать эту справку\n\n"
                "Просто отправь мне свой запрос на естественном языке!"
            )
        else:
            # TODO: Here will be AI/SQL query processing
            response_text = (
                f"Получил твой запрос: \"{message_text}\"\n\n"
                "Обработка запросов пока в разработке. Скоро добавим AI для генерации SQL запросов!"
            )

        # Log interaction
        ChatInteraction.objects.create(
            user=user,
            message_text=message_text,
            response_text=response_text,
            success=True
        )

        # Send response
        TelegramService.send_message(chat_id, response_text)

        return response_text
