"""A cor, as larguras de desenho e os ajudantes que toda forma usa.

A moldura, o cinza e a tipografia são da Bunker. A cor viva é a do cliente, com duas: a
primária é o que vai bem e o destaque, a secundária é o alerta. Sem cliente definido, o
material sai em preto e vermelho da Bunker.

    from grafico import paleta
    paleta.definir_marca('#005e29', '#f26e20')     # antes de desenhar

As formas leem a cor daqui na hora de desenhar, então a ordem de import não importa.
"""
import html

BUNKER = ('#0a0a0a', '#b03a2e', '#555555')   # preto, vermelho e o cinza escuro da segunda série

INK, MUTE, TXT, GRADE = '#0a0a0a', '#bdbdbd', '#8a8a8a', '#ededed'

# O desenho nasce na largura em que vai aparecer. Encolher SVG por CSS encolhe a letra junto.
MEIA = 468      # meia coluna do painel
CHEIA = 980     # a página inteira do painel
A4 = 658        # a coluna de texto da folha A4, com 18 mm de margem de cada lado

PRIMARIA, SECUNDARIA, PRIMARIA_CLARA = BUNKER


def definir_marca(primaria, secundaria, primaria_clara=None):
    """Troca a cor do cliente. Chame antes de desenhar."""
    global PRIMARIA, SECUNDARIA, PRIMARIA_CLARA
    PRIMARIA, SECUNDARIA, PRIMARIA_CLARA = primaria, secundaria, primaria_clara or primaria
    return PRIMARIA, SECUNDARIA, PRIMARIA_CLARA


def destaque():
    """A cor do que vai bem, o destaque que a manchete nomeia."""
    return PRIMARIA


def alerta():
    """A cor do que piorou, do que foi cedido, do que a manchete condena."""
    return SECUNDARIA


def esc(t):
    return html.escape(str(t))


def larg_texto(texto, fs, negrito=False):
    """Largura estimada de um texto: 0,55 do corpo por caractere (0,62 em negrito). Erra para
    mais, que é o lado certo: avisa antes de encostar."""
    return len(str(texto)) * fs * (0.62 if negrito else 0.55)
