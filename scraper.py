import re
import requests
from bs4 import BeautifulSoup


def numero_para_float(texto):
    if not texto:
        return None

    texto = str(texto)
    texto = texto.replace("R$", "")
    texto = texto.replace("\xa0", " ")
    texto = texto.strip()

    match = re.search(r"\d{1,3}(?:\.\d{3})*,\d{2}", texto)
    if match:
        valor = match.group()
        valor = valor.replace(".", "").replace(",", ".")
        return float(valor)

    match = re.search(r"\b\d+(?:\.\d+)?\b", texto)
    if match:
        return float(match.group())

    return None


def pegar_html(url):
    try:
        response = requests.get(
            url,
            timeout=25,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
                "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"
            }
        )

        if response.status_code >= 400:
            print("HTTP erro:", response.status_code)
            return None

        return response.text

    except Exception as erro:
        print("Erro ao pegar HTML:", erro)
        return None


def extrair_item_id_mercado_livre(html):
    padroes = [
        r'"item_id":"(MLB\d+)"',
        r'"itemId":"(MLB\d+)"',
        r'"itemId":\s*"(MLB\d+)"',
        r'meli://item\?id=(MLB\d+)',
        r'item\?id=(MLB\d+)',
        r'"item_id":\s*"(MLB\d+)"',
        r'"itemId":\s*"(MLB\d+)"'
    ]

    for padrao in padroes:
        match = re.search(padrao, html)

        if match:
            return match.group(1)

    return None


def extrair_preco_mercado_livre_html(html):
    padroes = [
        r'"price":\s*(\d+(?:\.\d+)?)',
        r'"localItemPrice":\s*(\d+(?:\.\d+)?)',
        r'"itemPrice":\s*(\d+(?:\.\d+)?)',
        r'"actual_price":\s*(\d+(?:\.\d+)?)',
        r'property="og:title"\s+content="[^"]*R\$\s?(\d+(?:\.\d{3})*(?:,\d{2})?)',
        r'name="twitter:title"\s+content="[^"]*R\$\s?(\d+(?:\.\d{3})*(?:,\d{2})?)',
        r'R\$\s?(\d+(?:\.\d{3})*(?:,\d{2})?)'
    ]

    for padrao in padroes:
        match = re.search(padrao, html)

        if match:
            preco = numero_para_float(match.group(1))

            if preco:
                return preco

    return None


def preco_mercado_livre_api(item_id):
    if not item_id:
        return None

    url = f"https://api.mercadolibre.com/items/{item_id}"

    try:
        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json"
            }
        )

        print("ML API:", url, response.status_code)

        if response.status_code != 200:
            print(response.text[:300])
            return None

        dados = response.json()
        preco = dados.get("price")

        if preco:
            return float(preco)

        return None

    except Exception as erro:
        print("Erro API Mercado Livre:", erro)
        return None


def extrair_preco_mercado_livre(url):
    html = pegar_html(url)

    if not html:
        return None

    item_id = extrair_item_id_mercado_livre(html)
    print("ML ITEM ID HTML:", item_id)

    preco_api = preco_mercado_livre_api(item_id)

    if preco_api:
        return preco_api

    preco_html = extrair_preco_mercado_livre_html(html)

    if preco_html:
        return preco_html

    return None


def extrair_preco_kabum(html):
    padroes = [
        r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}\s*no PIX",
        r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}\s*à vista",
        r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}"
    ]

    for padrao in padroes:
        match = re.search(padrao, html, re.IGNORECASE)

        if match:
            preco = numero_para_float(match.group())

            if preco:
                return preco

    return None


def extrair_preco_amazon(html):
    soup = BeautifulSoup(html, "html.parser")

    seletores = [
        ".a-price .a-offscreen",
        "#corePrice_feature_div .a-offscreen",
        "#corePriceDisplay_desktop_feature_div .a-offscreen",
        "#priceblock_ourprice",
        "#priceblock_dealprice"
    ]

    for seletor in seletores:
        elemento = soup.select_one(seletor)

        if elemento:
            preco = numero_para_float(elemento.get_text())

            if preco:
                return preco

    return None


def verificar_link(url):
    url_lower = url.lower()

    if "mercadolivre.com" in url_lower:
        preco = extrair_preco_mercado_livre(url)

        return {
            "status": "online",
            "preco": preco,
            "erro": None
        }

    html = pegar_html(url)

    if not html:
        return {
            "status": "erro",
            "preco": None,
            "erro": "HTML vazio"
        }

    if "kabum.com.br" in url_lower:
        preco = extrair_preco_kabum(html)

    elif "amazon.com.br" in url_lower:
        preco = extrair_preco_amazon(html)

    else:
        preco = None

    return {
        "status": "online",
        "preco": preco,
        "erro": None
    }
