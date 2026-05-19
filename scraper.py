import re
import json
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


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


def pegar_html_playwright(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox"]
            )

            page = browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
                locale="pt-BR"
            )

            page.goto(url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(8000)

            titulo = page.title()
            html = page.content()

            print("TÍTULO DA PÁGINA:", titulo)

            if "captcha" in html.lower() or "robot" in html.lower() or "robô" in html.lower():
                print("POSSÍVEL BLOQUEIO/CAPTCHA DETECTADO")

            browser.close()

            return html, None

    except Exception as erro:
        return None, str(erro)


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
    texto = soup.get_text(" ", strip=True)

    padroes = [
        r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}\s*no PIX",
        r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}\s*à vista",
        r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}"
    ]

    for padrao in padroes:
        resultado = re.search(padrao, texto, re.IGNORECASE)

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
        "meta[itemprop='price']",
        "[itemprop='price']",
        ".andes-money-amount__fraction",
        ".ui-pdp-price__second-line .andes-money-amount__fraction",
        ".ui-pdp-price .andes-money-amount__fraction"
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

            texto = elemento.get_text().replace(".", "").strip()

            if texto.isdigit():
                return float(texto)

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


def extrair_preco_por_loja(url, soup):
    url_lower = url.lower()

    if "kabum.com.br" in url_lower:
        return extrair_preco_kabum(soup)

    if "amazon.com.br" in url_lower:
        return extrair_preco_amazon(soup)

    if "mercadolivre.com" in url_lower:
        return extrair_preco_mercado_livre(soup)

    return extrair_preco_generico(soup)


def verificar_link(url):
    url_lower = url.lower()

    usar_playwright = (
        "amazon.com.br" in url_lower
        or "mercadolivre.com" in url_lower
    )

    if usar_playwright:
        html, erro = pegar_html_playwright(url)
    else:
        html, erro = pegar_html_requests(url)

    if erro:
        return {
            "status": "erro",
            "preco": None,
            "erro": erro
        }

    if not html:
        return {
            "status": "erro",
            "preco": None,
            "erro": "HTML vazio"
        }

    soup = BeautifulSoup(html, "html.parser")

    preco = extrair_preco_por_loja(url, soup)

    return {
        "status": "online",
        "preco": preco,
        "erro": None
    }
