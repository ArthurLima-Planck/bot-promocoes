import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs


def numero_para_float(texto):
    if not texto:
        return None

    texto = str(texto).replace("R$", "").replace(".", "").replace(",", ".")
    match = re.search(r"\d+(?:\.\d+)?", texto)

    if match:
        return float(match.group())

    return None


def pegar_html(url):
    r = requests.get(
        url,
        timeout=25,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "pt-BR,pt;q=0.9"
        }
    )

    if r.status_code >= 400:
        return None

    return r.text


def extrair_id_ml_da_url(url):
    query = parse_qs(urlparse(url).query)

    if "wid" in query:
        return query["wid"][0]

    if "item_id" in query:
        return query["item_id"][0]

    match = re.search(r"(MLB\d+)", url)

    if match:
        return match.group(1)

    return None


def preco_ml_api(item_id):
    if not item_id:
        return None

    api_url = f"https://api.mercadolibre.com/items/{item_id}"

    r = requests.get(
        api_url,
        timeout=20,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    print("ML API:", api_url, r.status_code)

    if r.status_code != 200:
        print(r.text[:300])
        return None

    dados = r.json()
    preco = dados.get("price")

    if preco:
        return float(preco)

    return None


def preco_ml_html(html):
    padroes = [
        r'"price":\s*(\d+(?:\.\d+)?)',
        r'"localItemPrice":\s*(\d+(?:\.\d+)?)',
        r'"itemPrice":\s*(\d+(?:\.\d+)?)',
        r'og:title" content="[^"]*R\$\s?(\d+(?:\.\d{3})*(?:,\d{2})?)',
        r'R\$\s?(\d+(?:\.\d{3})*(?:,\d{2})?)'
    ]

    for padrao in padroes:
        match = re.search(padrao, html)

        if match:
            return numero_para_float(match.group(1))

    return None


def extrair_preco_mercado_livre(url):
    item_id = extrair_id_ml_da_url(url)

    print("ML ITEM ID URL:", item_id)

    preco = preco_ml_api(item_id)

    if preco:
        return preco

    html = pegar_html(url)

    if not html:
        return None

    match = re.search(r'"item_id":"(MLB\d+)"', html)

    if match:
        item_id_html = match.group(1)
        print("ML ITEM ID HTML:", item_id_html)

        preco = preco_ml_api(item_id_html)

        if preco:
            return preco

    preco = preco_ml_html(html)

    if preco:
        return preco

    return None


def extrair_preco_kabum(html):
    match = re.search(
        r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}\s*no PIX",
        html,
        re.IGNORECASE
    )

    if match:
        return numero_para_float(match.group())

    match = re.search(
        r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}",
        html
    )

    if match:
        return numero_para_float(match.group())

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
