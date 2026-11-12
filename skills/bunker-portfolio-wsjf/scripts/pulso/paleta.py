"""A paleta, as larguras de desenho e os ajudantes que toda forma usa.

A moldura, o cinza e a tipografia são da Bunker. A COR viva é do cliente atendido, e todo
cliente tem duas: a primária é o que vai bem e o destaque, a secundária é o alerta. Sem
cliente definido, o material sai em preto e vermelho da Bunker.

Três jeitos de passar a cor do cliente, e todos antes de desenhar:

    BUNKER_MARCA="#005e29,#f26e20" python3 meu_painel.py
    BUNKER_MARCA='{"primaria": "#005e29", "secundaria": "#f26e20"}' python3 meu_painel.py

    from pulso import paleta
    paleta.definir_marca('#005e29', '#f26e20')

`definir_marca` reescreve também os módulos `pulso.*` que já foram importados, então a
ordem de import não cria uma segunda verdade de cor.
"""
import html
import json
import os
import sys

# preto e vermelho da Bunker, e o cinza escuro como segunda série
BUNKER = ('#0a0a0a', '#b03a2e', '#555555')

INK, MUTE, TXT = '#0a0a0a', '#bdbdbd', '#969696'
GRADE = '#ededed'
# O desenho nasce na largura em que vai aparecer. Encolher um SVG de 980 para meia coluna
# por CSS deixaria o texto com metade do tamanho: margens, quantidade de rótulos e número
# de colunas mudam com o espaço, e a fonte fica onde está.
MEIA = 468          # uma coluna, quando o espaço é dividido ao meio
CHEIA = 980         # a página inteira
TERCO = 313         # um painel dentro da grade de três


def _da_env():
    bruto = os.environ.get('BUNKER_MARCA', '').strip()
    if not bruto:
        return None
    try:
        if bruto.startswith('{'):
            m = json.loads(bruto)
            return m['primaria'], m['secundaria'], m.get('primaria_clara', m['primaria'])
        partes = [x.strip() for x in bruto.split(',') if x.strip()]
        return partes[0], partes[1], (partes[2] if len(partes) > 2 else partes[0])
    except (ValueError, KeyError, IndexError):
        print(f'aviso: BUNKER_MARCA ilegível ({bruto}); saiu com a cor da Bunker',
              file=sys.stderr)
        return None


def _derivar(primaria, secundaria, clara):
    return {
        'PRIMARIA': primaria, 'SECUNDARIA': secundaria, 'PRIMARIA_CLARA': clara,
        'AMBAR': primaria,     # o destaque
        'AZ': clara,           # a segunda série, quando duas precisam se distinguir
        'ALERTA': secundaria,  # o alerta
        'VERDE': primaria,     # o que puxa para o lado bom
    }


_CORES = _derivar(*(_da_env() or BUNKER))
globals().update(_CORES)


def definir_marca(primaria, secundaria, primaria_clara=None):
    """Troca a cor do cliente, aqui e em todo módulo `pulso.*` já carregado."""
    novas = _derivar(primaria, secundaria, primaria_clara or primaria)
    globals().update(novas)
    for nome, mod in list(sys.modules.items()):
        if nome.startswith('pulso.') and mod is not None and nome != __name__:
            for k, v in novas.items():
                if hasattr(mod, k):
                    setattr(mod, k, v)
    return novas


def marca():
    """(primária, secundária, primária clara) em uso agora."""
    return PRIMARIA, SECUNDARIA, PRIMARIA_CLARA  # noqa: F821 (vêm de _CORES)


def esc(t):
    return html.escape(str(t))


def _eixo_y(p, esq, dir_, cima, h, topo, marcas=3):
    """Três marcas bastam: a grade ajuda a estimar, e o excesso só polui o desenho (g-2.1)."""
    for t in range(marcas):
        v = topo * t / (marcas - 1)
        yy = cima + h - (v / topo) * h if topo else cima + h
        p.append(f'<line x1="{esq}" y1="{yy:.1f}" x2="{dir_}" y2="{yy:.1f}" stroke="{GRADE}" stroke-width="1"/>')
        p.append(f'<text x="{esq-8}" y="{yy+4:.1f}" text-anchor="end" font-size="11" fill="{TXT}">{v:.0f}</text>')


def _cabe(x, texto, ja, fs=10):
    """Um rótulo de eixo só é desenhado se não encostar no anterior.

    O salto por índice não basta: "Início" é largo e o primeiro rótulo de data cai em cima
    dele. Aqui a decisão é por PIXEL, com a largura estimada do texto.
    """
    meia = len(texto) * fs * 0.55 / 2
    for xo, mo in ja:
        if abs(x - xo) < meia + mo + 6:
            return False
    ja.append((x, meia))
    return True


def _passo_rotulo(n, larg):
    """Quantos rótulos de eixo cabem sem virar borrão, na largura que este desenho tem."""
    cabem = max(int(larg / 62), 2)
    return max(1, -(-n // cabem))


eixo_y, cabe, passo_rotulo = _eixo_y, _cabe, _passo_rotulo
