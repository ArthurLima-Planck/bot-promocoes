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
