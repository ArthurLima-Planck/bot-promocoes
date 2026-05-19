import sqlite3


def criar_tabelas():
    conn = sqlite3.connect("promocoes.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_precos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto TEXT,
            loja TEXT,
            url TEXT,
            preco REAL,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()


def salvar_verificacao(produto, loja, url, preco, status):
    conn = sqlite3.connect("promocoes.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO historico_precos
        (produto, loja, url, preco, status)
        VALUES (?, ?, ?, ?, ?)
    """, (produto, loja, url, preco, status))

    conn.commit()
    conn.close()


def pegar_media_preco(produto, url):
    conn = sqlite3.connect("promocoes.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT AVG(preco)
        FROM historico_precos
        WHERE produto = ?
        AND url = ?
        AND preco IS NOT NULL
    """, (produto, url))

    resultado = cursor.fetchone()[0]

    conn.close()

    return resultado
