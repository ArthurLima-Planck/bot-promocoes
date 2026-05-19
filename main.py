import json

from database import (
    criar_tabelas,
    salvar_verificacao,
    pegar_media_preco
)

from scraper import verificar_link
from telegram_alert import enviar_telegram


def carregar_produtos():
    with open("produtos.json", "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def verificar_produtos():
    produtos = carregar_produtos()

    for produto in produtos:
        nome = produto["nome"]

        for item in produto["links"]:
            loja = item["loja"]
            url = item["url"]

            resultado = verificar_link(url)

            status = resultado["status"]
            preco = resultado["preco"]

            print(nome, loja, status, preco)

            salvar_verificacao(
                nome,
                loja,
                url,
                preco,
                status
            )

            media = pegar_media_preco(
                nome,
                url
            )

            if status == "fora_do_ar":
                enviar_telegram(
                    f"⚠ Produto fora do ar\n{nome}\n{loja}"
                )

            elif preco and media:
                if preco < media * 0.85:
                    enviar_telegram(
                        f"🔥 PROMOÇÃO\n{nome}\nR$ {preco}"
                    )


def main():
    criar_tabelas()
    verificar_produtos()
    print("Finalizado")


if __name__ == "__main__":
    main()
