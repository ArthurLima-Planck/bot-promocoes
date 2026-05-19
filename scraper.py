import re
import json
import requests
from bs4 import BeautifulSoup


def numero_para_float(texto):
    if not texto:
        return None

    texto = str(texto)
    texto = texto.replace("R$", "").replace("\xa0", " ").strip()

    match = re.search(r"\d{1,3}(?:\.\d{3})*,\d{2}", texto)
    if match:
        valor = match.group().replace(".", "").replace(",", ".")
        return float(valor)

    match = re.search(r"\b\d+(?:\.\d+)?\b", texto)
    if match:
        return float(match.group())

    return None


def pegar_html_requests(url):
    response = requests.get(
        url,
        timeout=25,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"
        }
    )

    if response.status_code >= 400:
        return None, f"HTTP {response.status_code}"

    return response.text, None


def extrair_item_id_mercado_livre(html):
    padroes = [
        r'"item_id":"(MLB\d+)"',
        r'"itemId":"(MLB\d+)"',
        r'item\?id=(MLB\d+)',
        r'meli://item\?id=(MLB\d+)',
        r'wid=(MLB\d+)',
        r'(MLB\d{8,})'
    ]

    for padrao in padroes:
        match = re.search(padrao, html)

        if match:
            return match.group(1)

    return None


def extrair_preco_mercado_livre_html(html):
    padroes = [
        r'"price":\s?(\d+(?:\.\d+)?)',
        r'"localItemPrice":\s?(\d+(?:\.\d+)?)',
        r'"itemPrice":\s?(\d+(?:\.\d+)?)',
        r'"actual_price":\s?(\d+(?:\.\d+)?)',
        r'<meta property="og:title" content="[^"]*R\$\s?(\d+(?:\.\d{3})*(?:,\d{2})?)',
        r'R\$\s?(\d+(?:\.\d{3})*(?:,\d{2})?)'
    ]

    for padrao in padroes:
        match = re.search(padrao, html)

        if match:
            preco = numero_para_float(match.group(1))

            if preco:
                return preco

    return None


def extrair_preco_mercado_livre_api(item_id):
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

        if response.status_code != 200:
            print("Mercado Livre API erro:", response.status_code, response.text)
            return None

        dados = response.json()
        preco = dados.get("price")

        if preco:
            return float(preco)

    except Exception as erro:
        print("Erro API ML:", erro)

    return None


def extrair_preco_mercado_livre(url):
    html, erro = pegar_html_requests(url)

    if erro or not html:
        return None

    preco_html = extrair_preco_mercado_livre_html(html)

    if preco_html:
        return preco_html

    item_id = extrair_item_id_mercado_livre(html)

    print("Mercado Livre item_id encontrado:", item_id)

    preco_api = extrair_preco_mercado_livre_api(item_id)

    if preco_api:
        return preco_api

    return None


def extrair_preco_kabum(soup):
    texto = soup.get_text(" ", strip=True)

    padroes = [
        r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}\s*no PIX",
        r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}\s*à vista",
        r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}"
    ]

    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE)

        if match:
            preco = numero_para_float(match.group())

            if preco:
                return preco

    return None


def extrair_preco_amazon(soup):
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


def extrair_preco_generico(soup):
    texto = soup.get_text(" ", strip=True)

    match = re.search(
        r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}",
        texto
    )

    if match:
        return numero_para_float(match.group())

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

    html, erro = pegar_html_requests(url)

    if erro:
        return {
            "status": "erro",
            "preco": None,
            "erro": erro
        }

    soup = BeautifulSoup(html, "html.parser")

    if "kabum.com.br" in url_lower:
        preco = extrair_preco_kabum(soup)

    elif "amazon.com.br" in url_lower:
        preco = extrair_preco_amazon(soup)

    else:
        preco = extrair_preco_generico(soup)

    return {
        "status": "online",
        "preco": preco,
        "erro": None
    }
