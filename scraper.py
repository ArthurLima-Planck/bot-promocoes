importar solicitações
importar ré


def link_verificador(url):
    tentar:
 resposta = solicitações.pegar(
 url,
 tempo limite=15,
 cabeçalhos={
                "Agente do usuário": "Mozilla/5.0"
            }
        )

        se resposta.código_de status == 404:
            retornar {
                "status": "fora_do_ar",
                "preco": Nenhum,
                "erro": "404"
            }

 html = resposta.texto

 resultado = re.procurar(
            r"R\$ ?(\d+[.,]\d+)",
 HTML
        )

 preco = Nenhum

        se resultado:
 preco = resultado.grupo(1)

 preco = (
 preco
                .substituir(".", "")
                .substituir(",", ".")
            )

 preco = flutuador(preco)

        retornar {
            "status": "online",
            "preco": preco,
            "erro": Nenhum
        }

    exceto Exceção como erro:
        retornar {
            "status": "erro",
            "preco": Nenhum,
            "erro": str(erro)
    }
