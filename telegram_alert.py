import os
import requests


def enviar_telegram(mensagem):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    print("TOKEN existe?", bool(token))
    print("CHAT_ID existe?", bool(chat_id))
    print("CHAT_ID:", chat_id)

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": mensagem
        }
    )

    print("STATUS:", response.status_code)
    print("RESPOSTA:", response.text)
