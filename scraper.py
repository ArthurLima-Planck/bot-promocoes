import requests
import re


def verificar_link(url):
    try:
        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        if response.status_code == 404:
            return {
                "status": "fora_do_ar",
                "preco": None,
                "erro": "404"
            }

        html = response.text

        resultado = re.search(
            r"R\$ ?(\d+[.,]\d+)",
            html
        )

        preco = None

        if resultado:
            preco = resultado.group(1)

            preco = (
                preco
                .replace(".", "")
                .replace(",", ".")
            )

            preco = float(preco)

        return {
            "status": "online",
            "preco": preco,
            "erro": None
        }

    except Exception as erro:
        return {
            "status": "erro",
            "preco": None,
            "erro": str(erro)
        }
