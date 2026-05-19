import os
import requests


def enviar_telegram(mensagem):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": mensagem
        }
    )

    print("Telegram:", response.status_code)
