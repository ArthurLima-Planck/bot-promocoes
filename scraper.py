import requests
import re
from bs4 import BeautifulSoup


def limpar_preco(texto):
    if not texto:
        return None

    texto = texto.strip()
    texto = texto.replace("R$", "")
    texto = texto.replace("\xa0", " ")
    texto = texto.replace(" ", "")

    match = re.search(r"\d{1,3}(?:\.\d{3})*,\d{2}", texto)

    if not match:
        match = re.search(r"\d+,\d{2}", texto)

    if not match:
        return None

    preco = match.group()
    preco = preco.replace(".", "").replace(",", ".")

    try:
        return float(preco)
    except:
        return None


def extrair_preco_amazon(soup):
    seletores = [
        ".a-price .a-offscreen",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        "#corePrice_feature_div .a-offscreen",
        "#corePriceDisplay_desktop_feature_div .a-offscreen"
    ]

    for seletor in seletores:
        elemento = soup.select_one(seletor)

        if elemento:
            preco = limpar_preco(elemento.get_text())

            if preco:
                return preco

    return None


def extrair_preco_mercado_livre(soup):
    seletores = [
        ".andes-money-amount__fraction",
        ".ui-pdp-price__second-line .andes-money-amount__fraction",
        ".ui-pdp-price .andes-money-amount__fraction"
    ]

    for seletor in seletores:
        elemento = soup.select_one(seletor)

        if elemento:
            texto = elemento.get_text().strip()
            texto = texto.replace(".", "")

            try:
                return float(texto)
            except:
                pass

    return None


def extrair_preco_generico(soup):
    texto = soup.get_text(" ", strip=True)

    padroes = [
        r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}",
        r"\d{1,3}(?:\.\d{3})*,\d{2}"
    ]

    for padrao in padroes:
        resultado = re.search(padrao, texto)

        if resultado:
            preco = limpar_preco(resultado.group())

            if preco:
                return preco

    return None


def verificar_link(url):
    try:
        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"
            }
        )

        if response.status_code == 404:
            return {
                "status": "fora_do_ar",
                "preco": None,
                "erro": "404"
            }

        if response.status_code >= 400:
            return {
                "status": "erro",
                "preco": None,
                "erro": f"HTTP {response.status_code}"
            }

        soup = BeautifulSoup(response.text, "html.parser")

        url_lower = url.lower()

        preco = None

        if "amazon.com.br" in url_lower:
            preco = extrair_preco_amazon(soup)

        elif "mercadolivre.com" in url_lower:
            preco = extrair_preco_mercado_livre(soup)

        if not preco:
            preco = extrair_preco_generico(soup)

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
