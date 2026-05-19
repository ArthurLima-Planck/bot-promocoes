import os
import requests


def enviar_telegram(mensagem, chat_id=None):
    token = os.getenv("TELEGRAM_TOKEN")

    if chat_id is None:
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": mensagem
        }
    )

    print("Telegram:", response.status_code, response.text)


def enviar_log(mensagem):
    log_chat_id = os.getenv("TELEGRAM_LOG_CHAT_ID")

    if not log_chat_id:
        print(mensagem)
        return

    enviar_telegram(mensagem, log_chat_id)
