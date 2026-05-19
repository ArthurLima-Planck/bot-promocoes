import requests
import re
import json
from bs4 import BeautifulSoup


def numero_para_float(texto):
    if not texto:
        return None

    texto = texto.replace("R$", "").replace("\xa0", " ").strip()

    match = re.search(r"\d{1,3}(?:\.\d{3})*,\d{2}", texto)
    if not match:
        match = re.search(r"\d+,\d{2}", texto)

    if not match:
        return None

    valor = match.group()
    valor = valor.replace(".", "").replace(",", ".")

    try:
        return float(valor)
    except:
        return None


def pegar_json_ld(soup):
    dados = []

    scripts = soup.find_all("script", type="application/ld+json")

    for script in scripts:
        try:
            texto = script.string
            if texto:
                dados.append(json.loads(texto))
        except:
            pass

    return dados


def procurar_preco_em_json(obj):
    if isinstance(obj, dict):
        for chave, valor in obj.items():
            if chave.lower() in ["price", "lowprice", "highprice"]:
                try:
                    return float(valor)
                except:
                    pass

            resultado = procurar_preco_em_json(valor)
            if resultado:
                return resultado

    elif isinstance(obj, list):
        for item in obj:
            resultado = procurar_preco_em_json(item)
            if resultado:
                return resultado

    return None


def extrair_preco_kabum(soup):
    textos = soup.get_text(" ", strip=True)

    # tenta pegar preço no pix primeiro
    padroes_pix = [
        r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}\s*no PIX",
        r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}\s*à vista",
        r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}"
    ]

    for padrao in padroes_pix:
        resultado = re.search(padrao, textos, re.IGNORECASE)

        if resultado:
            preco = numero_para_float(resultado.group())
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

    for dados in pegar_json_ld(soup):
        preco = procurar_preco_em_json(dados)
        if preco:
            return preco

    return None


def extrair_preco_mercado_livre(soup):
    seletores = [
        ".andes-money-amount__fraction",
        ".ui-pdp-price__second-line .andes-money-amount__fraction",
        ".ui-pdp-price .andes-money-amount__fraction",
        "[itemprop='price']"
    ]

    for seletor in seletores:
        elemento = soup.select_one(seletor)

        if elemento:
            content = elemento.get("content")
            if content:
                try:
                    return float(content)
                except:
                    pass

            texto = elemento.get_text()
            texto = texto.replace(".", "")

            try:
                return float(texto)
            except:
                pass

    for dados in pegar_json_ld(soup):
        preco = procurar_preco_em_json(dados)
        if preco:
            return preco

    return None


def extrair_preco_generico(soup):
    texto = soup.get_text(" ", strip=True)

    resultado = re.search(
        r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}",
        texto
    )

    if resultado:
        return numero_para_float(resultado.group())

    return None


def verificar_link(url):
    try:
        response = requests.get(
            url,
            timeout=25,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
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

        if "kabum.com.br" in url_lower:
            preco = extrair_preco_kabum(soup)

        elif "amazon.com.br" in url_lower:
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
