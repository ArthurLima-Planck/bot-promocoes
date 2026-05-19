from database import criar_tabelas, salvar_verificacao
from scraper import verificar_link
from telegram_alert import enviar_telegram, enviar_log


def carregar_produtos():
    produtos = []
    produto_atual = None
    loja_atual = None

    with open("produtos.txt", "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()

            if not linha:
                continue

            if linha.startswith("produto:"):
                if produto_atual:
                    produtos.append(produto_atual)

                nome = linha.replace("produto:", "").strip()

                produto_atual = {
                    "nome": nome,
                    "queda_percentual": 12,
                    "links": []
                }

            elif linha.startswith("queda:"):
                queda = linha.replace("queda:", "").strip()

                if produto_atual:
                    produto_atual["queda_percentual"] = float(queda)

            elif linha.startswith("loja:"):
                loja_atual = linha.replace("loja:", "").strip()

            elif linha.startswith("url:"):
                url = linha.replace("url:", "").strip()

                if produto_atual and loja_atual:
                    produto_atual["links"].append({
                        "loja": loja_atual,
                        "url": url
                    })

                    loja_atual = None

    if produto_atual:
        produtos.append(produto_atual)

    return produtos


def verificar_produtos():
    produtos = carregar_produtos()

    for produto in produtos:
        nome = produto["nome"]
        queda_minima = produto["queda_percentual"]

        resultados_validos = []
        relatorio = f"🔍 Verificando: {nome}\n\n"

        for item in produto["links"]:
            loja = item["loja"]
            url = item["url"]

            resultado = verificar_link(url)

            status = resultado["status"]
            preco = resultado["preco"]
            erro = resultado["erro"]

            salvar_verificacao(nome, loja, url, preco, status)

            if preco:
                resultados_validos.append({
                    "loja": loja,
                    "url": url,
                    "preco": preco
                })

                relatorio += f"✅ {loja}: R$ {preco:.2f}\n"
            else:
                relatorio += f"⚠️ {loja}: sem preço ({status})\n"

        if len(resultados_validos) < 2:
            relatorio += "\n❌ Não tem preços suficientes para calcular média."
            enviar_log(relatorio)
            continue

        media = sum(item["preco"] for item in resultados_validos) / len(resultados_validos)

        relatorio += f"\n📊 Média: R$ {media:.2f}\n"
        relatorio += f"📉 Queda mínima configurada: {queda_minima}%\n\n"

        achou_promocao = False

        for item in resultados_validos:
            loja = item["loja"]
            url = item["url"]
            preco = item["preco"]

            queda = ((media - preco) / media) * 100

            relatorio += f"{loja}: {queda:.1f}% abaixo/acima da média\n"

            if queda >= queda_minima:
                achou_promocao = True

                enviar_telegram(
                    f"🔥 PROMOÇÃO ENCONTRADA\n\n"
                    f"Produto: {nome}\n"
                    f"Loja: {loja}\n"
                    f"Preço: R$ {preco:.2f}\n"
                    f"Média: R$ {media:.2f}\n"
                    f"Queda: {queda:.1f}%\n\n"
                    f"{url}"
                )

        if not achou_promocao:
            relatorio += "\n✅ Nenhuma promoção forte encontrada."

        enviar_log(relatorio)


def main():
    criar_tabelas()
    verificar_produtos()
    print("Finalizado")


if __name__ == "__main__":
    main()
