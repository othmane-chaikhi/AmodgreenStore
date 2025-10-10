import requests
from django.conf import settings
from .models import SiteConfig

def send_telegram_message(message):
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    # Fallback to DB config if settings are empty
    if not token or not chat_id:
        try:
            cfg = SiteConfig.get_solo()
            token = token or cfg.telegram_bot_token
            chat_id = chat_id or cfg.telegram_chat_id
        except Exception:
            pass
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }
    try:
        if token and chat_id:
            requests.post(url, data=data, timeout=5)
    except Exception as e:
        print("Telegram error:", e)
