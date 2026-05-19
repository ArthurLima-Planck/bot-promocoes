from urllib.parse import urlparse, parse_qs


def extrair_id_mercado_livre(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    if "wid" in query:
        return query["wid"][0]

    match = re.search(r"(MLB\d+)", url)
    if match:
        return match.group(1)

    return None


def extrair_preco_mercado_livre_api(url):
    item_id = extrair_id_mercado_livre(url)

    if not item_id:
        return None

    api_url = f"https://api.mercadolibre.com/items/{item_id}"

    response = requests.get(api_url, timeout=20)

    if response.status_code != 200:
        print("Erro API Mercado Livre:", response.status_code, response.text)
        return None

    dados = response.json()

    preco = dados.get("price")

    if preco:
        return float(preco)

    return None
