"""As formas de gráfico que a leitura de preço usa, em SVG puro, uma por pergunta.

Toda função recebe o dado já contado e a LARGURA em que o desenho vai aparecer, e devolve o
SVG como texto. Nada aqui lê arquivo nem calcula margem: o número chega pronto.

Regras que valem em todas (o porquê está em `references/graficos.md`): eixo do zero, cor só
no que a manchete nomeia e o resto em cinza, nome escrito na ponta em vez de legenda, uma
régua para julgar contra, e a parte CEDIDA hachurada dentro do bloco a que pertence.

| Pergunta | Forma |
|---|---|
| Como está a operação, em poucos números? | `kpis` |
| Da margem planejada, quanto ficou na mesa? | `mesa` |
| Do custo ao preço negociado, onde o preço se forma e onde se perde? | `ponte_deitada` |
| Quem ficou abaixo do planejado, e por quanto? | `pares` |
| Qual cenário fecha melhor? | `barras_sinal` |
| Para onde vai cada real do preço, da venda perfeita à negociada? | `composicao` |
"""
from decimal import Decimal

from . import paleta
from .paleta import INK, MUTE, TXT, GRADE, MEIA, esc, larg_texto

_ID = [0]


def _novo_id(pref):
    """Id único na página inteira: dois SVG na mesma página dividem o espaço de ids."""
    _ID[0] += 1
    return f'{pref}{_ID[0]}'


def br(v, casas=2):
    """Número no jeito brasileiro, com o sinal de menos tipográfico: −1.234,56."""
    v = float(v) if isinstance(v, Decimal) else v
    s = f'{abs(v):,.{casas}f}'.replace(',', '§').replace('.', ',').replace('§', '.')
    return ('−' if round(v, casas) < 0 else '') + s


def rs(v, casas=2):
    v = float(v) if isinstance(v, Decimal) else v
    return ('−R$ ' if round(v, casas) < 0 else 'R$ ') + br(abs(v), casas)


def _hachura(pid, cor, passo=6):
    """Hachura de 45 graus: separa o que foi CEDIDO do que foi realizado, sem competir com o
    sólido. O padrão vai dentro do próprio SVG, para o desenho continuar autocontido."""
    return (f'<defs><pattern id="{pid}" patternUnits="userSpaceOnUse" width="{passo}" '
            f'height="{passo}" patternTransform="rotate(45)">'
            f'<rect width="{passo}" height="{passo}" fill="#ffffff"/>'
            f'<rect width="{passo / 2:.1f}" height="{passo}" fill="{cor}"/></pattern></defs>')


def _abre(larg, alt, aria):
    return (f'<svg viewBox="0 0 {larg} {alt:.0f}" width="100%" role="img" aria-label="{esc(aria)}" '
            f'xmlns="http://www.w3.org/2000/svg">')


# ------------------------------------------------------------------ cartões

def kpis(cartoes, larg=MEIA, cols=None):
    """Poucos números, cada um com a régua ao lado: número sozinho aceita vereditos opostos.

    `cartoes` é uma lista de {'rotulo', 'valor', 'regua', 'cor'?}. `cols` quebra os cartões
    em linhas; quatro numa linha de meia coluna viram letra miúda no celular.
    """
    n = len(cartoes)
    cols = cols or n
    cw = larg / cols
    linhas = -(-n // cols)
    util = cw - 30

    def quebra(t):
        """A régua cabe numa linha de 12 px, ou quebra em duas; a letra não encolhe abaixo de 11."""
        t = str(t)
        if larg_texto(t, 12) <= util:
            return [t]
        pal, a = t.split(' '), []
        while pal and larg_texto(' '.join(a + [pal[0]]), 12) <= util:
            a.append(pal.pop(0))
        return [' '.join(a), ' '.join(pal)]
    reguas = [quebra(c['regua']) for c in cartoes]
    duas = any(len(r) > 1 for r in reguas)
    h = 126 if duas else 112
    alt = h * linhas
    p = [_abre(larg, alt, 'Indicadores: ' + ', '.join(c['rotulo'] for c in cartoes))]
    for k, c in enumerate(cartoes):
        x, y0 = (k % cols) * cw, (k // cols) * h
        if k % cols:
            p.append(f'<line x1="{x:.1f}" y1="{y0 + 14}" x2="{x:.1f}" y2="{y0 + h - 14}" stroke="{GRADE}" stroke-width="1"/>')
        fs_v = min(34.0, util / max(len(str(c['valor'])) * 0.62, 1))
        fs_r = max(11.0, min(12.0, util / max(max(len(t) for t in reguas[k]) * 0.55, 1)))
        fs_t = min(11.5, util / max(len(str(c['rotulo'])) * 0.62, 1))
        p.append(f'<text x="{x + 16:.1f}" y="{y0 + 28}" font-size="{fs_t:.1f}" font-weight="600" fill="{TXT}" '
                 f'letter-spacing="0.04em">{esc(c["rotulo"].upper())}</text>')
        p.append(f'<text x="{x + 16:.1f}" y="{y0 + 68}" font-size="{fs_v:.1f}" font-weight="700" '
                 f'fill="{c.get("cor", INK)}" letter-spacing="-0.02em">{esc(c["valor"])}</text>')
        for j, t in enumerate(reguas[k]):
            p.append(f'<text x="{x + 16:.1f}" y="{y0 + 92 + j * 15}" font-size="{fs_r:.1f}" fill="{TXT}">{esc(t)}</text>')
    p.append('</svg>')
    return '\n'.join(p)


# ------------------------------------------------------------------ o que ficou na mesa

def mesa(planejada, realizada, partes, larg=MEIA, formato=None, rot_plan='planejada',
         rot_real='realizada'):
    """Uma barra só contra a margem planejada: o sólido é o que a venda realizou, o hachurado é
    o que ficou na mesa, repartido por quem cedeu (campanha, desconto tático, custo), e a
    linha tracejada é a planejada.

    `partes` é [(nome, valor)] na unidade da margem, e soma planejada − realizada. Parte
    negativa é ganho (venda acima do preço), e aí o que ficou na mesa sai num bloco só. Quando
    a realizada passa da planejada, o sólido passa da linha, e não há hachura.
    """
    fmt = formato or rs
    P, R = float(planejada), float(realizada)
    topo = max(P, R, 1e-9) * 1.03
    esq, dirm = 4, 4
    w = larg - esq - dirm
    X = lambda v: esq + w * max(0.0, min(float(v), topo)) / topo  # noqa: E731
    y, hh = 36, 46
    cor_r, cor_a = paleta.destaque(), paleta.alerta()
    corpo, rotulos = [], []
    corpo.append(f'<rect x="{esq}" y="{y}" width="{w:.1f}" height="{hh}" fill="{GRADE}" rx="2"/>')
    corpo.append(f'<rect x="{esq}" y="{y}" width="{max(X(R) - esq, 1.5):.1f}" height="{hh}" fill="{cor_r}" rx="2"/>')
    na_mesa = P - R
    pos = [(n, float(v)) for n, v in partes if float(v) > 0.005]
    ganho = any(float(v) < -0.005 for _, v in partes)
    if na_mesa > 0.005:
        segs = pos if pos and not ganho else [('ficou na mesa', na_mesa)]
        x = X(R)
        for k, (nome, v) in enumerate(segs):
            sw = max(w * v / topo, 6)
            pid = _novo_id('mesa')
            corpo.append(_hachura(pid, cor_a, 6 if k % 2 == 0 else 4))
            corpo.append(f'<rect x="{x:.1f}" y="{y}" width="{sw:.1f}" height="{hh}" fill="url(#{pid})" '
                         f'stroke="{cor_a}" stroke-width="1"/>')
            rotulos.append((x + sw / 2, nome, fmt(v)))
            x += sw
    xp = X(P)
    corpo.append(f'<line x1="{xp:.1f}" y1="{y - 8}" x2="{xp:.1f}" y2="{y + hh + 6}" stroke="{INK}" '
                 f'stroke-width="1.5" stroke-dasharray="4 3"/>')
    if R > P:  # a linha da planejada cai dentro do sólido: um traço branco por cima, para não sumir
        corpo.append(f'<line x1="{xp:.1f}" y1="{y + 3}" x2="{xp:.1f}" y2="{y + hh - 3}" stroke="#ffffff" '
                     f'stroke-width="1.5" stroke-dasharray="4 3"/>')
    t_plan = f'{rot_plan} {fmt(P)}'
    lp = larg_texto(t_plan, 12)
    ax = min(max(xp, lp / 2 + 2), larg - lp / 2 - 2)
    corpo.append(f'<text x="{ax:.1f}" y="{y - 14}" text-anchor="middle" font-size="12" fill="{TXT}">{esc(t_plan)}</text>')
    t_real = f'{rot_real} {fmt(R)}'
    ocupado = [(esq, esq + larg_texto(t_real, 13, True))]
    yl0 = y + hh + 22
    corpo.append(f'<text x="{esq}" y="{yl0}" font-size="13" font-weight="600" fill="{cor_r}">{esc(t_real)}</text>')
    if R > P + 0.005:
        t = f'acima da planejada: {fmt(R - P)}'
        corpo.append(f'<text x="{larg - dirm}" y="{yl0}" text-anchor="end" font-size="12" fill="{TXT}">{esc(t)}</text>')
    niveis = 0
    usados = [list(ocupado), [], []]
    for cx, nome, val in rotulos:
        meia = max(larg_texto(nome, 12), larg_texto(val, 12, True)) / 2
        cx_ok = min(max(cx, meia + 2), larg - meia - 2)
        for nv, ja in enumerate(usados):
            if all(cx_ok + meia + 8 <= a or cx_ok - meia - 8 >= b for a, b in ja):
                ja.append((cx_ok - meia, cx_ok + meia))
                break
        else:
            nv = 2
        niveis = max(niveis, nv)
        yl = yl0 + nv * 34
        if nv:
            corpo.append(f'<line x1="{cx:.1f}" y1="{y + hh + 2}" x2="{cx:.1f}" y2="{yl - 13}" stroke="{MUTE}" stroke-width="1"/>')
        corpo.append(f'<text x="{cx_ok:.1f}" y="{yl}" text-anchor="middle" font-size="12" fill="{INK}">{esc(nome)}</text>')
        corpo.append(f'<text x="{cx_ok:.1f}" y="{yl + 15}" text-anchor="middle" font-size="12" font-weight="600" '
                     f'fill="{cor_a}">{esc(val)}</text>')
    alt = yl0 + niveis * 34 + (22 if rotulos else 8)
    return '\n'.join([_abre(larg, alt, f'Margem {rot_real} {fmt(R)} contra {rot_plan} {fmt(P)}')] + corpo + ['</svg>'])


# ------------------------------------------------------------------ ponte deitada

def ponte_deitada(passos, larg=MEIA, destaque=(), formato=None, lin_base=36):
    """Ponte de valor com uma linha por degrau: de um total a outro, o que soma e o que tira.

    Deitada porque a ponte do preço tem nove degraus de nome longo, e em pé os nomes não
    cabem embaixo das barras, nem no celular. `passos` é [(rótulo, valor, tipo)], com tipo
    `total`, `mais` ou `menos`; o valor de `mais` e `menos` vem positivo (negativo inverte o
    sentido). Um `total` depois do primeiro é conferido contra a conta corrente, e a
    diferença derruba o desenho: ponte que não fecha é erro de dado.

    Totais em preto, degraus em cinza, e a cor entra nos degraus que a manchete nomeia
    (`destaque`, por rótulo): o que tira vai no alerta, o que soma na primária.
    """
    if not passos:
        return ''
    fmt = formato or (lambda v: br(v))
    linhas, corr = [], 0.0
    for rot, v, tipo in passos:
        v = float(v)
        if tipo == 'total':
            if linhas and abs(v - corr) > 0.006:
                raise ValueError(f'a ponte não fecha em "{rot}": a conta dá {corr:.4f}, o total diz {v:.4f}')
            a, b, corr = 0.0, v, v
            txt = fmt(v)
        else:
            d = v if tipo == 'mais' else -v
            a, b = sorted((corr, corr + d))
            corr += d
            txt = ('+' if d >= 0 else '−') + fmt(abs(d))
            tipo = 'mais' if d >= 0 else 'menos'
        linhas.append((rot, tipo, a, b, txt, corr))
    lo = min(0.0, *(min(l[2], l[3]) for l in linhas))
    hi = max(0.0, *(max(l[2], l[3]) for l in linhas)) or 1.0
    fs = 12.5
    maior = max(larg_texto(r, fs, t == 'total') for r, t, *_ in linhas)
    lw = min(larg * 0.44, maior + 14)
    fs_l = fs if maior + 14 <= lw else fs * (lw - 14) / maior
    vw = max(larg_texto(l[4], 12, True) for l in linhas) + 12
    x0, x1 = lw, larg - vw - 2
    X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)  # noqa: E731
    # ponte curta ganha linhas mais altas: com três degraus, a manchete ocupava mais tela que o desenho
    lin, cima = max(lin_base, lin_base * 5 / len(linhas)), 6
    bh = min(28, lin * 0.56)
    alt = cima + lin * len(linhas) + 6
    p = [_abre(larg, alt, f'Ponte de {linhas[0][0]} a {linhas[-1][0]}, em {len(linhas)} degraus')]
    if lo < 0:
        p.append(f'<line x1="{X(0):.1f}" y1="{cima}" x2="{X(0):.1f}" y2="{alt - 4}" stroke="{MUTE}" stroke-width="1"/>')
    anterior = None
    for k, (rot, tipo, a, b, txt, fim) in enumerate(linhas):
        y = cima + k * lin
        tot = tipo == 'total'
        if tot:
            cor = paleta.alerta() if b < 0 else INK
        elif rot in destaque:
            cor = paleta.alerta() if tipo == 'menos' else paleta.destaque()
        else:
            cor = MUTE
        xa, xb = X(a), X(b)
        p.append(f'<rect x="{xa:.1f}" y="{y + (lin - bh) / 2:.1f}" width="{max(xb - xa, 1.5):.1f}" height="{bh}" '
                 f'fill="{cor}" rx="1.5"/>')
        if anterior is not None:
            p.append(f'<line x1="{X(anterior):.1f}" y1="{y - (lin - bh) / 2 - 1:.1f}" x2="{X(anterior):.1f}" '
                     f'y2="{y + (lin - bh) / 2:.1f}" stroke="#9a9a9a" stroke-width="1" stroke-dasharray="2 2"/>')
        anterior = fim
        p.append(f'<text x="{lw - 12:.1f}" y="{y + lin / 2 + 4.5:.1f}" text-anchor="end" font-size="{fs_l:.1f}" '
                 f'font-weight="{600 if tot else 400}" fill="{INK}">{esc(rot)}</text>')
        cor_t = INK if cor in (MUTE, INK) else cor
        p.append(f'<text x="{larg - 2}" y="{y + lin / 2 + 4.5:.1f}" text-anchor="end" font-size="12" '
                 f'font-weight="{700 if tot else 600}" fill="{cor_t}">{esc(txt)}</text>')
    p.append('</svg>')
    return '\n'.join(p)


# ------------------------------------------------------------------ planejado contra realizado

def pares(itens, larg=MEIA, formato=None, rot_plan='planejada', rot_real='realizada'):
    """Duas barras por item, na ordem de quem deixou mais na mesa: a planejada fina, em cinza,
    e a realizada grossa, na primária quando chega à planejada e no alerta quando não chega.

    `itens` é [(nome, planejado, realizado)] na mesma unidade. O valor vai escrito na ponta,
    com o nome da régua, e por isso a forma não pede legenda.
    """
    fmt = formato or rs
    itens = sorted(itens, key=lambda x: -(float(x[1]) - float(x[2])))
    vals = [float(v) for _, a, b in itens for v in (a, b)]
    lo, hi = min(0.0, *vals), max(0.0, *vals) or 1.0
    textos = [f'{rot_real} {fmt(b)}' for _, _, b in itens] + [f'{rot_plan} {fmt(a)}' for _, a, _ in itens]
    vw = max(larg_texto(t, 12, True) for t in textos) + 12
    x0, x1 = 2, larg - vw
    X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)  # noqa: E731
    # com um ou dois itens, as barras engrossam: fina demais, a forma some ao lado do texto
    poucos = len(itens) <= 2
    lin = 80 if poucos else 58
    h_p, h_r = (12, 24) if poucos else (8, 15)
    alt = lin * len(itens) + 4
    p = [_abre(larg, alt, f'{rot_plan.capitalize()} contra {rot_real}, por item')]
    for k, (nome, a, b) in enumerate(itens):
        a, b = float(a), float(b)
        y = k * lin
        cor = paleta.destaque() if b >= a - 0.005 else paleta.alerta()
        p.append(f'<text x="{x0}" y="{y + 14}" font-size="12.5" font-weight="600" fill="{INK}">{esc(nome)}</text>')
        for (v, yy, h, c, t, peso, ct) in ((a, y + 21, h_p, MUTE, f'{rot_plan} {fmt(a)}', 400, TXT),
                                           (b, y + 21 + h_p + 4, h_r, cor, f'{rot_real} {fmt(b)}', 600, cor)):
            xa, xb = sorted((X(0), X(v)))
            p.append(f'<rect x="{xa:.1f}" y="{yy}" width="{max(xb - xa, 1.5):.1f}" height="{h}" fill="{c}" rx="1.5"/>')
            p.append(f'<text x="{larg - 2}" y="{yy + h - 1}" text-anchor="end" font-size="12" font-weight="{peso}" '
                     f'fill="{ct}">{esc(t)}</text>')
    if lo < 0:
        p.append(f'<line x1="{X(0):.1f}" y1="18" x2="{X(0):.1f}" y2="{alt - 4}" stroke="{INK}" stroke-width="1"/>')
    p.append('</svg>')
    return '\n'.join(p)


# ------------------------------------------------------------------ barras com sinal

def barras_sinal(itens, larg=MEIA, formato=None):
    """Ranking que aceita valor negativo: o nome em cima, a barra sai do zero para a direita
    quando o número é bom e para a esquerda quando é ruim, com a primária e o alerta."""
    fmt = formato or rs
    vals = [float(v) for _, v in itens]
    lo, hi = min(0.0, *vals), max(0.0, *vals)
    if hi == lo:
        hi = lo + 1
    vw = max(larg_texto(fmt(v), 12.5, True) for v in vals) + 12
    x0, x1 = 2, larg - vw
    X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)  # noqa: E731
    lin = max(58, 190 / len(itens))
    alt = lin * len(itens) + 4
    p = [_abre(larg, alt, 'Resultado por cenário')]
    for k, (nome, v) in enumerate(itens):
        v = float(v)
        y = k * lin
        cor = paleta.destaque() if v >= 0 else paleta.alerta()
        xa, xb = sorted((X(0), X(v)))
        p.append(f'<text x="{x0}" y="{y + 14}" font-size="12.5" fill="{INK}">{esc(nome)}</text>')
        p.append(f'<rect x="{xa:.1f}" y="{y + 22:.1f}" width="{max(xb - xa, 1.5):.1f}" height="{lin - 34:.1f}" fill="{cor}" rx="1.5"/>')
        p.append(f'<text x="{larg - 2}" y="{y + 22 + (lin - 34) / 2 + 4.5:.1f}" text-anchor="end" font-size="12.5" font-weight="700" '
                 f'fill="{cor}">{esc(fmt(v))}</text>')
    p.append(f'<line x1="{X(0):.1f}" y1="18" x2="{X(0):.1f}" y2="{alt - 2}" stroke="{INK}" stroke-width="1"/>')
    p.append('</svg>')
    return '\n'.join(p)


# ------------------------------------------------------------------ composição do preço

def slot_estreito(larg, lw, n):
    return lw == 0 and (larg - 4) / n < 55


def _quebra(texto, larg, fs, maximo=2):
    """O texto em até `maximo` linhas que cabem na largura, em negrito; o que sobra vira reticências."""
    pal, linhas = str(texto).split(' '), []
    while pal and len(linhas) < maximo:
        a = [pal.pop(0)]
        while pal and larg_texto(' '.join(a + [pal[0]]), fs, True) <= larg:
            a.append(pal.pop(0))
        linhas.append(' '.join(a))
    if pal:
        ult = linhas[-1]
        while ult and larg_texto(ult + '…', fs, True) > larg:
            ult = ult[:-1].rstrip()
        linhas[-1] = ult + '…'
    return linhas


# Os pedaços do preço, de baixo para cima. O custo em cinza escuro e a margem na cor do
# destaque: é ela que a leitura julga. Tributos, comissão e frete vão clareando.
PEDACOS = (('custo', 'Custo do produto', 'Custo', '#5c5c5c', '#ffffff'),
           ('trib', 'Tributos sobre a venda', 'Tributos', '#8f8f8f', '#0a0a0a'),
           ('com', 'Comissão e despesas variáveis', 'Comissão', '#b8b8b8', '#0a0a0a'),
           ('frete', 'Frete', 'Frete', '#dadada', '#0a0a0a'))
# texto claro sobre a margem: no tema escuro, a tinta vira clara e o texto vira o papel
PAPEL = '#fffffe'


def composicao(colunas, larg=MEIA, nomes=True, titulo=None, alt_plot=None, rot_colunas=None, formato=None,
               linhas_titulo=1):
    """Colunas empilhadas lado a lado, cada uma o preço inteiro de uma venda de uma unidade,
    aberto em custo, tributos, comissão e despesas variáveis, frete e margem de contribuição.

    A altura da coluna é proporcional ao preço, na mesma régua para as três. A margem cedida
    contra a primeira coluna (a venda perfeita) sai hachurada em cima da coluna, na altura do
    que se perdeu; margem ganha não tem hachura e sai escrita na cor do destaque. O preço vai
    no topo de cada coluna e os valores dentro dos pedaços em que cabem.

    `colunas` é [{'preco', 'custo', 'trib', 'com', 'frete', 'mc', 'cedida'}], na unidade do
    preço. `nomes` escreve o nome de cada pedaço ao lado da primeira coluna; os pequenos
    múltiplos saem sem ele, e com `titulo`; `linhas_titulo` reserva a mesma altura de título
    em todos, para as colunas dos múltiplos ficarem na mesma linha de base. Múltiplo estreito
    (coluna com menos de 55 px) sai sem o nome das colunas, que a primeira já mostra na mesma
    ordem, e com a margem cedida só em número.
    """
    fmt = formato or (rs if nomes else (lambda v: br(v)))   # nos pequenos múltiplos, sem o "R$" para caber
    rot_colunas = rot_colunas or ['Preço teto', 'Preço da política', 'Preço negociado']
    n = len(colunas)
    presentes = [k for k, *_ in PEDACOS if any(float(c[k]) > 0.005 for c in colunas)]
    # a coluna dos nomes: o nome inteiro quando cabe, senão o curto
    fs_n = 11.0 if larg >= 600 else 10.0
    lw = 0.0
    curtos = False
    if nomes:
        longos = [p[1] for p in PEDACOS if p[0] in presentes] + ['Margem de contribuição']
        lw = max(larg_texto(t, fs_n) for t in longos) + 14
        if lw > larg * 0.32:
            curtos = True
            lw = max(larg_texto(t, fs_n) for t in [p[2] for p in PEDACOS if p[0] in presentes] + ['Margem']) + 14
    fs_t = 11.5 if nomes else 10.0
    linhas_t = _quebra(titulo, larg - 2, fs_t, 2) if titulo else []
    topo_t = (max(len(linhas_t), linhas_titulo) * (fs_t + 3) + 6) if titulo else 0
    cab = 36 if nomes else 30          # o preço e a margem cedida, em duas linhas
    pe = 22 if nomes else (6 if slot_estreito(larg, lw, n) else 18)
    H = alt_plot or (230 if nomes else 130)
    area = larg - lw - 4
    slot = area / n
    estreito = not nomes and slot < 55
    cw = min(slot * (0.58 if nomes else 0.62), 128)
    alto = max(max(float(c['preco']) + max(float(c['cedida']), 0.0),
                   sum(float(c[k]) for k in presentes)) for c in colunas) or 1.0
    k = H / alto
    y0 = topo_t + cab + H              # a base das colunas
    alt = y0 + pe
    p = [_abre(larg, alt, f'Composição do preço em {n} vendas: ' + ', '.join(
        f'{r} {fmt(c["preco"])}' for r, c in zip(rot_colunas, colunas)))]
    for k_, t in enumerate(linhas_t):
        p.append(f'<text x="0" y="{fs_t + k_ * (fs_t + 3):.1f}" font-size="{fs_t}" font-weight="600" fill="{INK}">{esc(t)}</text>')
    p.append(f'<line x1="{lw:.1f}" y1="{y0:.1f}" x2="{larg - 2:.1f}" y2="{y0:.1f}" stroke="{INK}" stroke-width="1"/>')
    fs_v = 11.0 if nomes else 9.5
    meios = {}
    for j, c in enumerate(colunas):
        cx = lw + slot * j + slot / 2
        x = cx - cw / 2
        y = y0
        for chave, _, _, cor, cor_t in PEDACOS:
            v = float(c[chave])
            if chave not in presentes or v <= 0.005:
                continue
            h = v * k
            p.append(f'<rect x="{x:.1f}" y="{y - h:.1f}" width="{cw:.1f}" height="{h:.1f}" fill="{cor}"/>')
            t = fmt(v)
            if nomes and h >= fs_v + 5 and larg_texto(t, fs_v) <= cw - 6:
                p.append(f'<text x="{cx:.1f}" y="{y - h / 2 + fs_v * 0.36:.1f}" text-anchor="middle" font-size="{fs_v}" '
                         f'fill="{cor_t}">{esc(t)}</text>')
            if j == 0:
                meios[chave] = y - h / 2
            y -= h
        mc = float(c['mc'])
        preco_y = y0 - float(c['preco']) * k
        if mc > 0.005:
            h = mc * k
            p.append(f'<rect x="{x:.1f}" y="{y - h:.1f}" width="{cw:.1f}" height="{h:.1f}" fill="{paleta.destaque()}"/>')
            t = fmt(mc)
            if h >= fs_v + 5 and larg_texto(t, fs_v, True) <= cw - 6:
                p.append(f'<text x="{cx:.1f}" y="{y - h / 2 + fs_v * 0.36:.1f}" text-anchor="middle" font-size="{fs_v}" '
                         f'font-weight="600" fill="{PAPEL}">{esc(t)}</text>')
            if j == 0:
                meios['mc'] = y - h / 2
            y -= h
        elif mc < -0.005:
            # a venda não paga o custo: o que passa do preço é a margem negativa
            p.append(f'<line x1="{x - 3:.1f}" y1="{preco_y:.1f}" x2="{x + cw + 3:.1f}" y2="{preco_y:.1f}" '
                     f'stroke="{paleta.alerta()}" stroke-width="1.5" stroke-dasharray="4 3"/>')
        ced = float(c['cedida'])
        top = min(preco_y, y)
        if ced > 0.005:
            h = max(ced * k, 3)
            pid = _novo_id('ced')
            p.append(_hachura(pid, paleta.alerta(), 6))
            p.append(f'<rect x="{x:.1f}" y="{preco_y - h:.1f}" width="{cw:.1f}" height="{h:.1f}" fill="url(#{pid})" '
                     f'stroke="{paleta.alerta()}" stroke-width="1"/>')
            top = min(top, preco_y - h)
        fs_p = 12.5 if nomes else (9.5 if estreito else 10.5)
        p.append(f'<text x="{cx:.1f}" y="{top - (17 if abs(ced) > 0.005 or mc < -0.005 else 6):.1f}" text-anchor="middle" '
                 f'font-size="{fs_p}" font-weight="700" fill="{INK}">{esc(fmt(c["preco"]))}</text>')
        fs_c = 10.0 if nomes else 9.0
        if mc < -0.005:
            p.append(f'<text x="{cx:.1f}" y="{top - 5:.1f}" text-anchor="middle" font-size="{fs_c}" '
                     f'fill="{paleta.alerta()}">{esc("margem " + fmt(mc))}</text>')
        elif ced > 0.005:
            p.append(f'<text x="{cx:.1f}" y="{top - 5:.1f}" text-anchor="middle" font-size="{fs_c}" '
                     f'fill="{paleta.alerta()}">{esc(("−" if estreito else "cedida ") + fmt(ced))}</text>')
        elif ced < -0.005:
            p.append(f'<text x="{cx:.1f}" y="{top - 5:.1f}" text-anchor="middle" font-size="{fs_c}" '
                     f'fill="{TXT}">{esc(("+" if estreito else "ganha ") + fmt(-ced))}</text>')
        if not estreito:
            p.append(f'<text x="{cx:.1f}" y="{y0 + (15 if nomes else 13):.1f}" text-anchor="middle" '
                     f'font-size="{10.5 if nomes else 9.0}" fill="{TXT}">{esc(rot_colunas[j])}</text>')
    if nomes:
        # os nomes ao lado da primeira coluna, afastados um do outro quando o pedaço é fino
        itens = [(meios[ch], (nc if curtos else nl)) for ch, nl, nc, *_ in PEDACOS if ch in meios]
        if 'mc' in meios:
            itens.append((meios['mc'], 'Margem' if curtos else 'Margem de contribuição'))
        itens.sort(key=lambda t: -t[0])          # de baixo para cima
        passo = fs_n + 3
        ys = []
        for yy, _ in itens:
            ys.append(min(yy, ys[-1] - passo) if ys else min(yy, y0 - 4))
        x_col = lw + slot / 2 - cw / 2
        for (yy, nome), yt in zip(itens, ys):
            p.append(f'<text x="{lw - 12:.1f}" y="{yt + fs_n * 0.36:.1f}" text-anchor="end" font-size="{fs_n}" '
                     f'fill="{INK}">{esc(nome)}</text>')
            if abs(yt - yy) > 2:
                p.append(f'<line x1="{lw - 9:.1f}" y1="{yt:.1f}" x2="{x_col - 2:.1f}" y2="{yy:.1f}" stroke="{MUTE}" '
                         f'stroke-width="1"/>')
    p.append('</svg>')
    return '\n'.join(p)
