importar sqlite3


def criar_tabelas():
 conn = sqlite3.conectar("promocoes.db")

 cursor = conn.cursor()

 cursor.executar("""
 CRIAR TABELA SE NÃO EXISTIR historico_precos (
 id INTEIRO CHAVE PRIMÁRIA AUTOINCREMENTO,
 texto do produto,
 loja TEXTO,
 url TEXTO,
 preco REAL,
 texto de status
        )
 """)

 cursor.executar("""
 CRIAR TABELA SE NÃO EXISTIR alertas (
 id INTEIRO CHAVE PRIMÁRIA AUTOINCREMENTO,
 texto do produto,
 loja TEXTO,
 url TEXTO,
 tipo TEXTO
        )
 """)

 conexão.comprometer-se()
 conexão.fechar()


def salvar_verificacao(produto, loja, url, preco, status):
 conn = sqlite3.conectar("promocoes.db")

 cursor = conn.cursor()

 cursor.executar("""
 INSERIR EM histórico_precos
 (produto, loja, url, preco, status)
 VALORES (?,?,?,?,?)
 """, (produto, loja, url, preco, status))

 conexão.comprometer-se()
 conexão.fechar()


def pegar_media_preco(produto, url):
 conn = sqlite3.conectar("promocoes.db")

 cursor = conn.cursor()

 cursor.executar("""
 SELECIONE AVG(preco)
 DE histórico_precos
 ONDE produto = ?
 E url = ?
 E preco NÃO É NULO
 """, (produto, url))

 resultado = cursor.buscar()[0]

 conexão.fechar()

    retornar resultado


def alerta_ja_enviado_recente(produto, loja, url, tipo):
    retornar Falso


def salvar_alerta(produto, loja, url, tipo, preco=Nenhum):
    passar
