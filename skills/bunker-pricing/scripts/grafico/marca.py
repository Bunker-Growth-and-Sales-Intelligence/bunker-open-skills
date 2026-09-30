"""A marca da Bunker dentro do material: logo real, B em contorno e a fonte embutida.

Tudo vai embutido em base64, e nada por URL: material que baixa imagem da web depende de
internet na hora de imprimir. Os arquivos moram em `assets/` da skill, já no tamanho e na
cor em que aparecem, para a skill rodar só com a biblioteca padrão:

    bunker-logo-branco.png   logo sobre fundo escuro (capa, fecho, tema escuro)
    bunker-logo-preto.png    logo sobre fundo claro, reduzido ao dobro do tamanho em que aparece
    b-outline.png            o B em contorno, em preto
    b-outline-branco.png     o mesmo B, em branco, marca d'água da capa preta
    schibsted-grotesk.css    a fonte da casa em base64, pesos 400 a 900 (licença SIL OFL)
"""
import base64
import os

ASSETS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets'))
CASA = 'Growth &amp; Sales Intelligence'
SITE = 'bunkerconsultancy.com'


def caminho(nome):
    return os.path.join(ASSETS, nome)


def embutir(nome):
    """A imagem de `assets/` como data URI, pronta para `src`."""
    mime = {'.png': 'image/png', '.svg': 'image/svg+xml', '.jpg': 'image/jpeg'}[os.path.splitext(nome)[1].lower()]
    with open(caminho(nome), 'rb') as f:
        return f'data:{mime};base64,' + base64.b64encode(f.read()).decode()


def logo_branco():
    return embutir('bunker-logo-branco.png')


def logo_preto():
    return embutir('bunker-logo-preto.png')


def b_outline(branco=False):
    return embutir('b-outline-branco.png' if branco else 'b-outline.png')


def fontes():
    """Schibsted Grotesk embutida em `@font-face`. O link do Google Fonts nem sempre chega a
    tempo no Chrome headless, e o PDF sairia em Helvetica sem avisar ninguém."""
    with open(caminho('schibsted-grotesk.css'), encoding='utf-8') as f:
        return f.read()
