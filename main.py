importar json

de banco de dados importar (
 criar_tabelas,
 salvar_verificacao,
 pegar_media_preco
)

de raspador importar link_verificador

de alerta_telegram importar enviar_telegram


def carregar_produtos():
 com abrir(
        "produtos.json",
        "r",
 codificação="utf-8"
    ) como arquivo:

 retornar json.carregar(arquivo)


def verificar_produtos():
 produtos = carregar_produtos()

 para produto em produtos:

 nome = produto["nome"]

 parágrafo item em produto["links"]:

 loja = item["loja"]
 url = item["url"]

 resultado = link_verificador(url)

 status = resultado["status"]
 preco = resultado["preco"]

            imprimir(nome, loja, status, preco)

            salvar_verificacao(
 nome,
 loja,
 url,
 preco,
 status
            )

 mídia = pegar_media_preco(
 nome,
 url
            )

 se preco e mídia:

 se preco < mídia * 0,85:

 mensagem = (
                        f"🔥 PROMOÇÃO\n\n"
                        f"Produto: {nome}\n"
                        f"Loja: {loja}\n"
                        f"Preço: R$ {preco}\n"
                        f"Média: R$ {mídia:. . .2f}\n\n"
                        f"{url}"
                    )

                    enviar_telegram(mensagem)


def principal():
    criar_tabelas()

    verificar_produtos()

    imprimir("Finalizado")


se __nome__ == "__principal__":
    principal()
