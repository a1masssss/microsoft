#!/usr/bin/env python
"""
Script to setup Telegram webhook
Run this script to register webhook URL with Telegram
"""
import os
import sys
import requests
from pathlib import Path

# Add Django project to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from dotenv import load_dotenv
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL')
TELEGRAM_SECRET_TOKEN = os.getenv('TELEGRAM_SECRET_TOKEN')


def setup_webhook():
    """Setup webhook for Telegram bot"""

    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env")
        return False

    if not TELEGRAM_WEBHOOK_URL:
        print("❌ Error: TELEGRAM_WEBHOOK_URL not found in .env")
        return False

    print(f"🔧 Setting up webhook...")
    print(f"📍 Webhook URL: {TELEGRAM_WEBHOOK_URL}")

    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook'

    payload = {
        'url': TELEGRAM_WEBHOOK_URL,
        'drop_pending_updates': True,
    }

    if TELEGRAM_SECRET_TOKEN:
        payload['secret_token'] = TELEGRAM_SECRET_TOKEN
        print(f"🔐 Using secret token for security")

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()

        if result.get('ok'):
            print("✅ Webhook set successfully!")
            print(f"📝 Response: {result.get('description')}")
            return True
        else:
            print(f"❌ Failed to set webhook: {result.get('description')}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False


def get_webhook_info():
    """Get current webhook information"""

    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env")
        return

    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo'

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        result = response.json()

        if result.get('ok'):
            info = result.get('result', {})
            print("\n📊 Current Webhook Info:")
            print(f"   URL: {info.get('url', 'Not set')}")
            print(f"   Pending updates: {info.get('pending_update_count', 0)}")

            if info.get('last_error_message'):
                print(f"   ⚠️  Last error: {info.get('last_error_message')}")
                print(f"   ⚠️  Error date: {info.get('last_error_date')}")
            else:
                print("   ✅ No errors")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting webhook info: {e}")


def delete_webhook():
    """Delete webhook"""

    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env")
        return False

    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook'

    try:
        response = requests.post(url, json={'drop_pending_updates': True}, timeout=10)
        response.raise_for_status()
        result = response.json()

        if result.get('ok'):
            print("✅ Webhook deleted successfully!")
            return True
        else:
            print(f"❌ Failed to delete webhook: {result.get('description')}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == '__main__':
    print("🤖 Telegram Webhook Setup\n")

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'info':
            get_webhook_info()
        elif command == 'delete':
            delete_webhook()
        elif command == 'setup':
            setup_webhook()
            get_webhook_info()
        else:
            print(f"❌ Unknown command: {command}")
            print("\nAvailable commands:")
            print("  setup  - Setup webhook")
            print("  info   - Get webhook info")
            print("  delete - Delete webhook")
    else:
        # Default: setup webhook
        setup_webhook()
        get_webhook_info()
