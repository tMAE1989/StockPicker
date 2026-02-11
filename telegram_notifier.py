import requests
import os

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def send_message(self, message):
        """Sends a message to the configured Telegram chat."""
        if not self.bot_token or not self.chat_id:
            print("Telegram credentials not set. Skipping notification.")
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                print(f"Telegram Error {response.status_code}: {response.text}")
            response.raise_for_status()
            print("Telegram notification sent.")
        except Exception as e:
            print(f"Failed to send Telegram notification: {e}")
