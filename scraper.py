import requests
import re


def verificar_link(url):
    if "mercadolivre.com" in url:
        html = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20
        ).text

        item_id = None

        match = re.search(r'"item_id":"(MLB\d+)"', html)
        if match:
            item_id = match.group(1)

        if not item_id:
            match = re.search(r'meli://item\?id=(MLB\d+)', html)
            if match:
                item_id = match.group(1)

        print("ITEM ID:", item_id)

        if item_id:
            api = requests.get(
                f"https://api.mercadolibre.com/items/{item_id}",
                timeout=20
            )

            print(api.status_code)
            print(api.text[:500])

            if api.status_code == 200:
                dados = api.json()

                return {
                    "status": "online",
                    "preco": dados.get("price"),
                    "erro": None
                }

        return {
            "status": "erro",
            "preco": None,
            "erro": "Item ID não encontrado"
        }

    return {
        "status": "erro",
        "preco": None,
        "erro": "teste"
    }
