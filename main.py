import json
from database import (
    criar_tabelas,
    salvar_verificacao,
    pegar_media_preco,
    alerta_ja_enviado_recentemente,
    salvar_alerta
)
from scraper import verificar_link
from telegram_alert import enviar_telegram


def carregar_produtos():
    with open("produtos.json", "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def calcular_queda(preco_atual, media):
    if not media or media <= 0:
 retornar 0

    retornar ((mídia - preco_atual) / mídia) * 100


def verificar_produtos():
 produtos = carregar_produtos()

 para produto em produtos:
 nome = produto["nome"]
 preco_alerta = produto.Pégar("preco_alerta")
 queda_percentual = produto.Pégar("queda_percentual", 15)

 parágrafo item em produto["links"]:
 loja = item["loja"]
 url = item["url"]

 resultado = link_verificador(url)

 status = resultado["status"]
 preco = resultado["preco"]
 erro = resultado["erro"]

            imprimir(f"{nome} | {loja} | {status} | {preco}")

            salvar_verificacao(nome, loja, url, preco, status)

 se status == "fora_do_ar":
 tipo = "fora_do_ar"

 se não alerta_ja_enviado_recente(nome, loja, url, tipo):
                    enviar_telegram(
                        f"⚠️ <b>Produto saiu do ar</b>\n\n"
                        f"<b>Produto:</b> {nome}\n"
                        f"<b>Loja:</b> {loja}\n"
                        f"<b>Erro:</b> {erro}\n\n"
                        f"{url}"
                    )
                    salvar_alerta(nome, loja, url, tipo)

 contínuo

 se status == "sem_estoque":
 tipo = "sem_estoque"

 se não alerta_ja_enviado_recente(nome, loja, url, tipo):
                    enviar_telegram(
                        f"📦 <b>Produto sem estoque</b>\n\n"
                        f"<b>Produto:</b> {nome}\n"
                        f"<b>Loja:</b> {loja}\n\n"
                        f"{url}"
                    )
                    salvar_alerta(nome, loja, url, tipo)

 contínuo

 se status!= "online":
                imprimir(f"Erro ignorado: {erro}")
 contínuo

 mídia = pegar_media_preco(nome, url)
 queda = calcular_queda(preco, mídia)

 promocao_por_preco_fixo = preco_alerta e preco <= preco_alerta
 promocao_por_media = mídia e queda >= queda_percentual

 se promoção_por_preco_fixo ou promoção_por_media:
 tipo = "promocao"

 se não alerta_ja_enviado_recente(nome, loja, url, tipo):
 mensagem = (
                        f"🔥 <b>PROMOÇÃO ENCONTRADA</b>\n\n"
                        f"<b>Produto:</b> {nome}\n"
                        f"<b>Loja:</b> {loja}\n"
                        f"<b>Preço atual:</b> R$ {preco:. . . .2f}\n"
                    )

 se mídia:
 mensagem += (
                            f"<b>Preço médio:</b> R$ {mídia:. . . .2f}\n"
                            f"<b>Queda:</b> {queda:. . . . 1f}%\n"
                        )

 mensagem += f"\n{url}"

                    enviar_telegram(mensagem)
                    salvar_alerta(nome, loja, url, tipo, preco)


def principal():
    criar_tabelas()
    verificar_produtos()
    imprimir("Finalizado.")


se __nome__ == "__principal__":
    principal()
