import json

from database import criar_tabelas
from telegram_alert import enviar_telegram


def main():
    criar_tabelas()
    enviar_telegram("TESTE TELEGRAM")
    print("Finalizado")


if __name__ == "__main__":
    main()
