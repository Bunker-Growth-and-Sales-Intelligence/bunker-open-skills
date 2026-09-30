"""A marca da Bunker dentro do material: logo real, asterisco e a fonte embutida.

Tudo vai embutido em base64, e nada por URL. Material que baixa imagem da web depende de
internet na hora de imprimir e do site no ar na hora de abrir, e o do cliente não pode
depender de nenhum dos dois.

Os arquivos moram em `assets/` desta skill:

    bunker-logo-branco.png   logo sobre fundo escuro (capa e fecho)
    bunker-logo-preto.png    logo sobre fundo claro, já reduzido para o canto do slide
    asterisco.svg            o asterisco que abre o cabeçalho de cada slide
    schibsted-grotesk.css    a fonte da casa em base64, pesos 400 a 900
    capa.jpg                 a foto da capa, já recortada e em preto e branco

Nada aqui depende de biblioteca fora do Python: o logo preto vem pronto no arquivo.
"""
import base64
import os

ASSETS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       '..', '..', 'assets'))
CASA = 'Growth &amp; Sales Intelligence'
SITE = 'bunkerconsultancy.com'

_MIME = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
         '.svg': 'image/svg+xml', '.webp': 'image/webp'}


def caminho(nome):
    return os.path.join(ASSETS, nome)


def embutir(nome, mime=None):
    """A imagem de `assets/` como data URI, pronta para `src`."""
    mime = mime or _MIME.get(os.path.splitext(nome)[1].lower(), 'application/octet-stream')
    dados = base64.b64encode(open(caminho(nome), 'rb').read()).decode()
    return f'data:{mime};base64,{dados}'


def logo_preto():
    """O logo em preto, para o canto do slide claro.

    Vem pronto no arquivo, e não por filtro de CSS: filtro obriga o navegador a rasterizar
    a imagem na impressão, e o PDF engorda.
    """
    return embutir('bunker-logo-preto.png', 'image/png')


def logo_branco():
    return embutir('bunker-logo-branco.png', 'image/png')


def asterisco(cor='#0a0a0a', tam=18):
    """O asterisco da Bunker, a mesma marca que abre o cabeçalho do deck institucional."""
    svg = open(caminho('asterisco.svg'), encoding='utf-8').read()
    svg = svg.replace('#0a0a0a', cor).replace('<svg ', f'<svg width="{tam}" height="{tam}" ')
    return svg.replace('\n', '')


def fontes():
    """Schibsted Grotesk embutida, em `@font-face` com base64.

    O `<link>` do Google Fonts nem sempre chega a tempo na impressão, e quando não chega o
    PDF sai em Helvetica sem avisar ninguém.
    """
    return open(caminho('schibsted-grotesk.css'), encoding='utf-8').read()
