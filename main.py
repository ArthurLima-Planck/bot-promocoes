import os
import requests


def enviar_telegram(mensagem):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    print("TOKEN existe?", bool(token))
    print("CHAT_ID existe?", bool(chat_id))
    print("CHAT_ID:", chat_id)

    if not token:
        print("ERRO: TELEGRAM_TOKEN não configurado")
        return

    if not chat_id:
        print("ERRO: TELEGRAM_CHAT_ID não configurado")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": mensagem
        }
    )

    print("Status Telegram:", response.status_code)
    print("Resposta Telegram:", response.text)
