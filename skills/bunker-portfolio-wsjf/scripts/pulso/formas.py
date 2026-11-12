"""As formas de gráfico da Bunker, em SVG puro, uma por pergunta.

A forma sai da pergunta, e nunca o contrário (trilha de gráfico da Bunker, g-1.2).
Toda função recebe os dados já contados e a LARGURA em que o desenho vai aparecer, e
devolve o SVG como texto, pronto para entrar no HTML. Nada aqui lê arquivo, API ou banco:
o dado chega pronto, de vendas, preço, margem, financeiro, operação ou CRM.

Regras que valem em todas: eixo do zero (g-1.3), uma cor só para o que a mensagem defende e
o resto em cinza (g-2.1), o nome escrito na ponta em vez de legenda (g-2.1), três marcas no
eixo (g-2.1) e uma régua para o leitor julgar contra (g-2.3).

Texto que aparece dentro do desenho e depende do assunto entra por `textos` (ou por um
parâmetro nomeado), e o padrão é neutro. Quem desenha fila de chamado, pedido ou lead passa
a própria palavra.

O catálogo, com a pergunta de cada forma, está em `references/perguntas-e-formas.md`.
"""
import math

from .paleta import (INK, MUTE, TXT, AZ, AMBAR, ALERTA, VERDE, GRADE, MEIA, CHEIA, TERCO,
                     PRIMARIA, SECUNDARIA, esc, _eixo_y, _cabe, _passo_rotulo)


def _t(padrao, textos):
    """Os textos da forma: o padrão neutro, sobrescrito pelo que quem chama passou."""
    if not textos:
        return padrao
    d = dict(padrao)
    d.update(textos)
    return d


# ---------------------------------------------------------------- 1. cascata (fluxo)

_TXT_CASCATA = {
    'aria': 'Cascata: o saldo partiu de {inicio}, entraram {ent}, saíram {sai}, e parou em {fim}',
    'partida': 'partida: {inicio}, acima da linha tracejada o saldo cresceu',
    'entrada': 'entraram',
    'saida': 'saíram',
    'melhor': 'melhor {uni}: {maior} saídas',
}


def cascata(inicio, entrou, saiu, rotulos, unidade, larg=CHEIA, textos=None):
    """De onde o saldo partiu, quanto entrou e quanto saiu em cada período, e onde parou.

    Serve a qualquer estoque que muda por entrada e saída: fila de chamados, carteira de
    clientes, pedidos em aberto, caixa. `unidade` é o período (hora, dia, semana, mes), e
    `textos` troca as palavras do desenho (chaves de `_TXT_CASCATA`).
    """
    T = _t(_TXT_CASCATA, textos)
    n = len(entrou)
    saldo = sum(entrou) - sum(saiu)
    fim = inicio + saldo
    # Entrada e saída puxam o saldo em sentidos opostos, e a cor diz qual sentido: vermelho
    # empurra para cima, verde puxa para baixo. Quem está do lado bom do saldo fica no
    # cinza, senão a página inteira grita e nenhum degrau se destaca.
    cor_entrada = ALERTA if saldo > 0 else MUTE
    cor_saida = VERDE

    passos = [('total', 'Início', inicio)]
    for k in range(n):
        passos.append(('mais', rotulos[k], entrou[k]))
        passos.append(('menos', '', saiu[k]))
    passos.append(('total', 'Hoje', fim))

    corr, picos = inicio, [inicio, fim]
    for t, _, v in passos[1:-1]:
        corr += v if t == 'mais' else -v
        picos.append(corr)
    topo = max(max(picos), 1) * 1.18

    alt = 348 if larg <= MEIA else 378
    esq, dirm, cima, baixo = 42, (78 if larg > MEIA else 64), 40, 74
    w, h = larg - esq - dirm, alt - cima - baixo
    lb = w / (len(passos) * 1.42)
    vao = (w - lb * len(passos)) / max(len(passos) - 1, 1)
    Y = lambda v: cima + h - (v / topo) * h

    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" aria-label="{T["aria"].format(inicio=inicio, ent=sum(entrou), sai=sum(saiu), fim=fim)}" '
         f'xmlns="http://www.w3.org/2000/svg">']
    _eixo_y(p, esq, larg - dirm, cima, h, topo)

    yr = Y(inicio)
    p.append(f'<line x1="{esq}" y1="{yr:.1f}" x2="{larg-dirm+5}" y2="{yr:.1f}" stroke="{INK}" '
             f'stroke-width="1.25" stroke-dasharray="5 4" opacity=".55"/>')
    # A legenda da linha de partida ficava a direita, e o texto passava da borda do
    # desenho: numa tela de 468 ela comecava em 414 e precisava de 78. Agora ela vive
    # ACIMA da linha, encostada na esquerda, onde o espaco e do tamanho do texto.
    p.append(f'<text x="{esq+4}" y="{cima-14:.0f}" font-size="10" fill="{TXT}">'
             f'{T["partida"].format(inicio=inicio)}</text>')

    salto = _passo_rotulo(n, larg)
    base, x, lig, postos = inicio, esq, None, []
    maior, x_maior = (max(saiu) if saiu else 0), None
    # o nome vai na MAIOR barra de cada metade, e não na primeira: é onde sobra espaço para
    # ele sem encostar no valor nem na barra vizinha
    idx_ent = 1 + 2 * entrou.index(max(entrou)) if entrou and max(entrou) else -1
    idx_sai = 2 + 2 * saiu.index(max(saiu)) if saiu and max(saiu) else -1
    mostra_valor = n <= 10 or larg > MEIA
    for idx, (tipo, rot, val) in enumerate(passos):
        if tipo == 'total':
            y0, y1, cor = Y(val), Y(0), INK
        elif tipo == 'mais':
            y0, y1, cor = Y(base + val), Y(base), cor_entrada
            base += val
        else:
            y0, y1, cor = Y(base), Y(base - val), cor_saida
            if val == maior and maior and x_maior is None:
                x_maior = (x + lb / 2, Y(base - val))
            base -= val
        yy, ht = min(y0, y1), abs(y1 - y0)
        # dia sem movimento não desenha nada. A altura mínima de segurança transformava o
        # zero num traço da cor do degrau, e o desenho passava a afirmar o que não houve.
        if val:
            p.append(f'<rect x="{x:.1f}" y="{yy:.1f}" width="{lb:.1f}" height="{max(ht,2):.1f}" fill="{cor}" rx="1.5"/>')
        if val and (tipo == 'total' or mostra_valor):
            s = '' if tipo == 'total' else ('+' if tipo == 'mais' else '−')
            p.append(f'<text x="{x+lb/2:.1f}" y="{yy-6:.1f}" text-anchor="middle" font-size="11" '
                     f'font-weight="600" fill="{INK if tipo=="total" else cor}">{s}{val}</text>')
        # Os dois nomes ficam PRESOS à área do desenho. Soltos, o de baixo descia sobre a
        # linha de datas do eixo e o de cima subia para fora da tela, e era ali que o
        # operador via texto em cima de texto.
        if idx == idx_ent:
            ye = max(yy - 21, cima + 10)
            p.append(f'<text x="{x+lb/2:.1f}" y="{ye:.1f}" text-anchor="middle" font-size="11" '
                     f'fill="{cor_entrada}" font-weight="600">{T["entrada"]}</text>')
        if idx == idx_sai:
            baixo_bar = yy + max(ht, 2)
            ysa = baixo_bar + 15
            if ysa > cima + h - 3:          # encostaria na linha de datas: vai para cima
                ysa = max(yy - 8, cima + 10)
            p.append(f'<text x="{x+lb/2:.1f}" y="{ysa:.1f}" text-anchor="middle" font-size="11" '
                     f'fill="{cor_saida}" font-weight="600">{T["saida"]}</text>')
        if rot and (tipo == 'total' or ((idx - 1) // 2) % salto == 0) and _cabe(x + lb / 2, rot, postos):
            p.append(f'<text x="{x+lb/2:.1f}" y="{cima+h+18:.1f}" text-anchor="middle" font-size="10" fill="{TXT}">{esc(rot)}</text>')
        if lig is not None:
            p.append(f'<line x1="{lig[0]:.1f}" y1="{lig[1]:.1f}" x2="{x:.1f}" y2="{lig[1]:.1f}" stroke="#D8D8D8" stroke-width="1"/>')
        lig = (x + lb, Y(val if tipo == 'total' and idx == 0 else base))
        x += lb + vao

    if x_maior and maior:
        ax, ay = x_maior
        uni = {'dia': 'dia', 'hora': 'hora', 'mes': 'mês', 'mês': 'mês'}.get(unidade, 'semana')
        # a anotação desce até abaixo do eixo: em cima ela cruzava as barras vizinhas
        yb = cima + h + 38
        tx = min(max(ax, esq + 58), larg - dirm - 58)
        p.append(f'<line x1="{ax:.1f}" y1="{ay+5:.1f}" x2="{ax:.1f}" y2="{yb-10:.1f}" stroke="{TXT}" stroke-width="1" opacity=".45"/>')
        p.append(f'<text x="{tx:.1f}" y="{yb:.1f}" text-anchor="middle" font-size="10.5" fill="{TXT}">{T["melhor"].format(uni=uni, maior=maior)}</text>')
    p.append('</svg>')
    return '\n'.join(p)


# ------------------------------------------------- 2. duas curvas acumuladas (tempo)

_TXT_CURVAS = {'entrada': 'entraram', 'saida': 'saíram', 'vao': 'o vão é o saldo'}


def curvas(acum_ent, acum_sai, rotulos, larg=MEIA, textos=None):
    """Duas linhas do mesmo zero. O vão entre elas É o saldo: quando se aproximam, a saída
    alcançou a entrada. Nome na ponta de cada linha, sem legenda de canto (g-2.1)."""
    T = _t(_TXT_CURVAS, textos)
    ENT, SAI = T['entrada'], T['saida']
    alt = 268
    esq, dirm, cima, baixo = 42, 86, 26, 44
    w, h = larg - esq - dirm, alt - cima - baixo
    n = len(acum_ent)
    topo = max(max(acum_ent + acum_sai), 1) * 1.14
    X = lambda i: esq + (w * i / max(n - 1, 1))
    Y = lambda v: cima + h - (v / topo) * h

    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" aria-label="Curvas acumuladas '
         f'de entradas e saídas" xmlns="http://www.w3.org/2000/svg">']
    _eixo_y(p, esq, larg - dirm, cima, h, topo)

    area = ' '.join(f'{X(i):.1f},{Y(v):.1f}' for i, v in enumerate(acum_ent))
    area += ' ' + ' '.join(f'{X(i):.1f},{Y(v):.1f}' for i, v in reversed(list(enumerate(acum_sai))))
    p.append(f'<polygon points="{area}" fill="{INK}" opacity=".07"/>')

    # Quando as duas curvas terminam perto, os dois rotulos de ponta caem um em cima do
    # outro. Eles sao empurrados para longe do encontro, cada um para o seu lado, mantendo
    # a ordem: o de cima sobe, o de baixo desce.
    ys = {SAI: Y(acum_sai[-1]), ENT: Y(acum_ent[-1])}
    if abs(ys[SAI] - ys[ENT]) < 15:
        meio_y = (ys[SAI] + ys[ENT]) / 2
        alto = SAI if ys[SAI] <= ys[ENT] else ENT
        baixo_n = ENT if alto == SAI else SAI
        ys[alto], ys[baixo_n] = meio_y - 8, meio_y + 8
    for serie, cor, nome in ((acum_sai, VERDE, SAI), (acum_ent, ALERTA, ENT)):
        d = ' '.join(f'{"M" if i==0 else "L"}{X(i):.1f},{Y(v):.1f}' for i, v in enumerate(serie))
        p.append(f'<path d="{d}" fill="none" stroke="{cor}" stroke-width="2.1" stroke-linejoin="round" stroke-linecap="round"/>')
        p.append(f'<circle cx="{X(n-1):.1f}" cy="{Y(serie[-1]):.1f}" r="3.2" fill="{cor}"/>')
        yr = ys[nome]
        if abs(yr - Y(serie[-1])) > 2:
            p.append(f'<line x1="{X(n-1)+3:.1f}" y1="{Y(serie[-1]):.1f}" x2="{X(n-1)+7:.1f}" '
                     f'y2="{yr:.1f}" stroke="{cor}" stroke-width="1" opacity=".55"/>')
        rot_fim = f'{nome} {serie[-1]}'
        if X(n - 1) + 9 + len(rot_fim) * 11.5 * 0.62 > larg:
            p.append(f'<text x="{larg-3}" y="{yr+4:.1f}" text-anchor="end" font-size="11.5" '
                     f'font-weight="600" fill="{cor}">{esc(rot_fim)}</text>')
        else:
            p.append(f'<text x="{X(n-1)+9:.1f}" y="{yr+4:.1f}" font-size="11.5" '
                     f'font-weight="600" fill="{cor}">{esc(rot_fim)}</text>')

    if acum_ent[-1] > acum_sai[-1]:
        meio = n // 2
        ym = (Y(acum_ent[meio]) + Y(acum_sai[meio])) / 2
        p.append(f'<text x="{X(meio):.1f}" y="{ym:.1f}" text-anchor="middle" font-size="10.5" fill="{TXT}">{esc(T["vao"])}</text>')

    salto = _passo_rotulo(n, larg)
    for i, r in enumerate(rotulos):
        if i % salto == 0 or i == n - 1:
            p.append(f'<text x="{X(i):.1f}" y="{cima+h+17:.1f}" text-anchor="middle" font-size="10" fill="{TXT}">{esc(r)}</text>')
    p.append('</svg>')
    return '\n'.join(p)


# ----------------------------------------------------- 3. histograma da idade (distribuição)

FAIXAS_IDADE = [(0, 2, '0-2'), (3, 7, '3-7'), (8, 14, '8-14'),
                (15, 30, '15-30'), (31, 60, '31-60'), (61, 10 ** 6, '60+')]
_TXT_HISTOGRAMA = {'aria': 'Distribuição da idade dos itens em aberto',
                   'corte': 'daqui, envelhece', 'eixo': 'dias em aberto', 'sufixo': 'd'}


def histograma(idades, mediana, p90, larg=MEIA, faixas=None, corte=3, textos=None):
    """A média esconde a forma, então mostre a distribuição (g-3.2). Mediana responde o caso
    típico, P90 responde os piores casos, e as duas entram como régua (g-2.3).

    `faixas` é uma lista de (de, até, rótulo) em inteiros; o padrão é a idade em dias.
    `corte` é o índice da primeira faixa que a mensagem condena (pinta de alerta).
    Devolve (svg, quantos a partir do corte, total).
    """
    T = _t(_TXT_HISTOGRAMA, textos)
    faixas = faixas or FAIXAS_IDADE
    # a idade vem fracionária; sem truncar, quem tem 2,5 dias não cabe em "0 a 2" nem em
    # "3 a 7" e some da contagem. O total do histograma tem de bater com o total de abertas.
    inteiras = [int(d) for d in idades]
    cont = [sum(1 for d in inteiras if a <= d <= b) for a, b, _ in faixas]
    total = max(sum(cont), 1)
    velhas = sum(cont[corte:])

    alt = 268
    esq, dirm, cima, baixo = 42, 18, 38, 46
    w, h = larg - esq - dirm, alt - cima - baixo
    topo = max(max(cont), 1) * 1.2
    lb = w / (len(faixas) * 1.45)
    vao = (w - lb * len(faixas)) / max(len(faixas) - 1, 1)
    Y = lambda v: cima + h - (v / topo) * h

    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" aria-label="{esc(T["aria"])}" xmlns="http://www.w3.org/2000/svg">']
    _eixo_y(p, esq, larg - dirm, cima, h, topo)

    x = esq
    for i, ((a, b, rot), v) in enumerate(zip(faixas, cont)):
        cor = ALERTA if i >= corte and velhas else MUTE
        y0, ht = Y(v), max(Y(0) - Y(v), 1)
        p.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="{lb:.1f}" height="{ht:.1f}" fill="{cor}" rx="1.5"/>')
        if v:
            p.append(f'<text x="{x+lb/2:.1f}" y="{y0-6:.1f}" text-anchor="middle" font-size="11" font-weight="600" fill="{cor}">{v}</text>')
        p.append(f'<text x="{x+lb/2:.1f}" y="{cima+h+17:.1f}" text-anchor="middle" font-size="10" fill="{TXT}">{rot}</text>')
        if i == corte and velhas:
            p.append(f'<line x1="{x-vao/2:.1f}" y1="{cima-6:.1f}" x2="{x-vao/2:.1f}" y2="{cima+h:.1f}" '
                     f'stroke="{ALERTA}" stroke-width="1" stroke-dasharray="3 3" opacity=".5"/>')
            p.append(f'<text x="{x-vao/2+5:.1f}" y="{cima-12:.1f}" font-size="10.5" font-weight="600" fill="{ALERTA}">{esc(T["corte"])}</text>')
        x += lb + vao
    p.append(f'<text x="{esq}" y="{cima+h+35:.1f}" font-size="10" fill="{TXT}">{esc(T["eixo"])}</text>')
    p.append(f'<text x="{larg-dirm}" y="{cima+h+35:.1f}" text-anchor="end" font-size="10.5" fill="{INK}">'
             f'mediana {mediana:.0f}{T["sufixo"]} &#183; P90 {p90:.0f}{T["sufixo"]}</text>')
    p.append('</svg>')
    return '\n'.join(p), velhas, total


# -------------------------------------------------------- 4. dispersão (relação)

_TXT_DISPERSAO = {'vazio': 'Nenhum caso nesta janela.',
                  'aria': 'Dispersão: um ponto por caso, com a régua da mediana',
                  'ponto': 'cada ponto é um caso'}


def dispersao(pontos, mediana, rotulos_x, larg=MEIA, textos=None):
    """Um ponto por caso real (g-0.2). A reta que atravessa a nuvem seria resumo do
    movimento conjunto, nunca prova de causa, então aqui só entra a régua da mediana.

    `pontos` é [(índice do período, valor)], `rotulos_x` nomeia os períodos.
    """
    T = _t(_TXT_DISPERSAO, textos)
    alt = 268
    esq, dirm, cima, baixo = 42, 18, 26, 46
    w, h = larg - esq - dirm, alt - cima - baixo
    if not pontos:
        return (f'<svg viewBox="0 0 {larg} 70" width="100%"><text x="{esq}" y="38" font-size="12.5" '
                f'fill="{TXT}">{esc(T["vazio"])}</text></svg>')
    topo = max(max(y for _, y in pontos), 1) * 1.18
    n = max(max(x for x, _ in pontos), 1)
    X = lambda i: esq + w * i / n
    Y = lambda v: cima + h - (v / topo) * h

    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" aria-label="{esc(T["aria"])}" xmlns="http://www.w3.org/2000/svg">']
    _eixo_y(p, esq, larg - dirm, cima, h, topo)
    ym = Y(mediana)
    p.append(f'<line x1="{esq}" y1="{ym:.1f}" x2="{larg-dirm}" y2="{ym:.1f}" stroke="{INK}" '
             f'stroke-width="1.25" stroke-dasharray="5 4" opacity=".55"/>')
    p.append(f'<text x="{esq+3}" y="{ym-6:.1f}" font-size="10.5" font-weight="600" fill="{INK}">mediana</text>')
    acima = 0
    for xi, yi in pontos:
        longe = mediana and yi > mediana * 3
        acima += 1 if longe else 0
        p.append(f'<circle cx="{X(xi):.1f}" cy="{Y(yi):.1f}" r="3.2" '
                 f'fill="{ALERTA if longe else MUTE}" opacity="{1 if longe else .8}"/>')
    salto = _passo_rotulo(len(rotulos_x), larg)
    for i, r in enumerate(rotulos_x):
        if i % salto == 0 or i == len(rotulos_x) - 1:
            p.append(f'<text x="{X(i):.1f}" y="{cima+h+17:.1f}" text-anchor="middle" font-size="10" fill="{TXT}">{esc(r)}</text>')
    p.append(f'<text x="{esq}" y="{cima+h+35:.1f}" font-size="10" fill="{TXT}">{esc(T["ponto"])}</text>')
    if acima:
        p.append(f'<text x="{larg-dirm}" y="{cima+h+35:.1f}" text-anchor="end" font-size="10.5" fill="{ALERTA}">'
                 f'{acima} bem acima da régua</text>')
    p.append('</svg>')
    return '\n'.join(p)


# ------------------------------------------- 5. painéis pequenos por área (tempo)

def multiplos(series, larg=MEIA, destaque=None):
    """Mesmo intervalo de eixo em todos, painéis ordenados pelo último valor, e o nome da
    série no título de cada painel, que dispensa a legenda (g-3.1, widget `multiplos`).

    `destaque` é QUEM a manchete nomeia. Sem ele, o desenho escolhia sozinho a série que
    mais subiu enquanto o texto falava da maior, e o leitor via a cor num painel que a
    manchete não citava. A cor e o texto têm de apontar para o mesmo painel.
    """
    if not series:
        return ''
    ordem = sorted(series.items(), key=lambda kv: -kv[1][-1])
    topo = max(max(v) for _, v in ordem) or 1
    alta = destaque if destaque in series else max(ordem, key=lambda kv: kv[1][-1] - kv[1][0])[0]
    cols = 2 if larg <= MEIA else 3
    cw, ch = larg / cols, 96
    linhas = (len(ordem) + cols - 1) // cols
    alt = linhas * ch + 6
    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" aria-label="Um painel por '
         f'área, todos no mesmo intervalo de eixo" xmlns="http://www.w3.org/2000/svg">']
    for k, (nome, serie) in enumerate(ordem):
        cx, cy = (k % cols) * cw, (k // cols) * ch
        px, py, pw, ph = cx + 6, cy + 26, cw - 26, ch - 46
        X = lambda i: px + pw * i / max(len(serie) - 1, 1)
        Y = lambda v: py + ph - (v / topo) * ph
        cor = ALERTA if nome == alta else MUTE
        p.append(f'<text x="{cx+6}" y="{cy+15}" font-size="11.5" font-weight="600" fill="{INK}">{esc(nome)}</text>')
        p.append(f'<text x="{cx+cw-18}" y="{cy+15}" text-anchor="end" font-size="11.5" font-weight="600" '
                 f'fill="{ALERTA if nome == alta else INK}">{serie[-1]}</text>')
        p.append(f'<line x1="{px}" y1="{py+ph:.1f}" x2="{px+pw:.1f}" y2="{py+ph:.1f}" stroke="{GRADE}" stroke-width="1"/>')
        area = ' '.join(f'{X(i):.1f},{Y(v):.1f}' for i, v in enumerate(serie))
        p.append(f'<polygon points="{px:.1f},{py+ph:.1f} {area} {px+pw:.1f},{py+ph:.1f}" fill="{cor}" opacity=".14"/>')
        d = ' '.join(f'{"M" if i==0 else "L"}{X(i):.1f},{Y(v):.1f}' for i, v in enumerate(serie))
        p.append(f'<path d="{d}" fill="none" stroke="{cor}" stroke-width="1.7" stroke-linejoin="round"/>')
        p.append(f'<circle cx="{X(len(serie)-1):.1f}" cy="{Y(serie[-1]):.1f}" r="2.6" fill="{cor}"/>')
    p.append('</svg>')
    return '\n'.join(p)


# --------------------------------------------- barras deitadas ordenadas (parte do todo)

def barras_deitadas(itens, larg=MEIA, unidade='itens', destaque=None, cor_destaque=None):
    """Ranking com o nome à esquerda e o valor na ponta da barra.

    A lição g-3.2 manda ler participação em barra ordenada: o olho ordena comprimento com
    precisão e ângulo no chute.

    O denominador continua obrigatório (g-4.1), e ele vive na manchete do bloco, que diz
    "X responde por N das T". Escrever o total também dentro do desenho repetia o mesmo
    número três vezes na mesma tela, contando a linha de fonte.
    """
    itens = sorted(itens, key=lambda kv: -kv[1])
    total = max(sum(v for _, v in itens), 1)
    # `destaque` aceita um indice, um nome, ou uma LISTA de nomes: a resposta da manchete
    # nem sempre cabe numa barra so, e a cor tem de cobrir o que o texto afirma
    if isinstance(destaque, (list, tuple, set)):
        alvos = set(destaque)
    else:
        alvos = {destaque if isinstance(destaque, str) else
                 (itens[destaque][0] if isinstance(destaque, int) and destaque < len(itens)
                  else (itens[0][0] if itens else None))}
    # Empate divide o destaque quando o destaque é o LÍDER (índice ou nada): quem tem
    # exatamente o mesmo valor ganha a mesma cor, senão o desenho afirma uma diferença que
    # o dado não tem. Quando o destaque é uma escolha por nome (urgente é P0 e P1), o
    # empate não conta: P3 com o mesmo número de P1 continua não sendo urgente.
    if not isinstance(destaque, (str, list, tuple, set)):
        valores = {v for n, v in itens if n in alvos}
        alvos |= {n for n, v in itens if v in valores}
    cor_alvo = cor_destaque or AMBAR
    lin, topo_m, base_m = 26, 10, 8
    alt = topo_m + lin * len(itens) + base_m
    esq, dirm = 132, 52  # calha larga o bastante para o nome da frente por extenso
    w = larg - esq - dirm
    maior = max((v for _, v in itens), default=1) or 1

    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="Participação por categoria, em barras ordenadas" '
         f'xmlns="http://www.w3.org/2000/svg">']
    for k, (nome, v) in enumerate(itens):
        y = topo_m + k * lin
        cor = cor_alvo if nome in alvos else MUTE
        bw = max(w * v / maior, 1.5)
        p.append(f'<text x="{esq-10}" y="{y+13:.0f}" text-anchor="end" font-size="11.5" fill="{INK}">{esc(nome)}</text>')
        p.append(f'<rect x="{esq}" y="{y+4:.0f}" width="{bw:.1f}" height="14" fill="{cor}" rx="2"/>')
        pct = f'{v/total*100:.0f}%'
        col_pct = larg - 4 - len(pct) * 10.5 * 0.55
        rotulo = str(v).replace('.', ',')  # número no formato brasileiro
        fim = esq + bw + 7 + len(rotulo) * 11.5 * 0.62
        if fim >= col_pct - 6:
            p.append(f'<text x="{esq+bw-7:.1f}" y="{y+15:.0f}" text-anchor="end" font-size="11.5" '
                     f'font-weight="600" fill="#ffffff">{rotulo}</text>')
        else:
            p.append(f'<text x="{esq+bw+7:.1f}" y="{y+15:.0f}" font-size="11.5" '
                     f'font-weight="600" fill="{INK}">{rotulo}</text>')
        p.append(f'<text x="{larg-4}" y="{y+15:.0f}" text-anchor="end" font-size="10.5" fill="{TXT}">{pct}</text>')
    p.append('</svg>')
    return '\n'.join(p)


# ------------------------------------------------ pizza como antiexemplo (parte do todo)

def pizza_contra_barra(itens, larg=MEIA):
    """A mesma participação nas duas formas, lado a lado.

    A pizza entra no painel uma vez só, e como antiexemplo: a lição g-0.2 mostra que duas
    fatias de 18% e 17% têm ângulos quase idênticos e o olho não decide qual é maior.
    Trocar cor ou ordem da legenda não resolve, porque a comparação acontece no desenho.
    """
    itens = sorted(itens, key=lambda kv: -kv[1])[:8]
    total = max(sum(v for _, v in itens), 1)
    alt = 250
    r, cx, cy = 74, 92, 118
    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="A mesma participação como pizza e como barras ordenadas" '
         f'xmlns="http://www.w3.org/2000/svg">']
    p.append(f'<text x="8" y="16" font-size="11" font-weight="600" fill="{TXT}">como pizza</text>')
    ang = -math.pi / 2
    tons = ['#d9d9d9', '#cecece', '#c5c5c5', '#bbbbbb', '#b1b1b1', '#a7a7a7', '#9d9d9d', '#939393']
    for k, (nome, v) in enumerate(itens):
        da = 2 * math.pi * v / total
        x1, y1 = cx + r * math.cos(ang), cy + r * math.sin(ang)
        x2, y2 = cx + r * math.cos(ang + da), cy + r * math.sin(ang + da)
        grande = 1 if da > math.pi else 0
        p.append(f'<path d="M{cx},{cy} L{x1:.1f},{y1:.1f} A{r},{r} 0 {grande},1 {x2:.1f},{y2:.1f} Z" '
                 f'fill="{tons[k % len(tons)]}" stroke="#ffffff" stroke-width="1"/>')
        ang += da
    p.append(f'<text x="{cx}" y="{cy+r+22:.0f}" text-anchor="middle" font-size="10.5" fill="{ALERTA}">'
             f'qual é o segundo maior?</text>')

    px, rotulo_w = 210, 74
    barra_x = px + rotulo_w
    pw = larg - barra_x - 40
    p.append(f'<text x="{px}" y="16" font-size="11" font-weight="600" fill="{TXT}">como barras ordenadas</text>')
    if not itens:
        return ''
    maior = max(v for _, v in itens)
    lin = min(22, (alt - 60) / max(len(itens), 1))
    for k, (nome, v) in enumerate(itens):
        y = 32 + k * lin
        bw = max(pw * v / maior, 1.5)
        cor = AMBAR if k == 1 else MUTE
        p.append(f'<text x="{px}" y="{y+9:.0f}" font-size="10.5" fill="{INK}">{esc(nome)}</text>')
        p.append(f'<rect x="{barra_x}" y="{y:.0f}" width="{bw:.1f}" height="11" fill="{cor}" rx="2"/>')
        p.append(f'<text x="{barra_x+bw+6:.1f}" y="{y+9:.0f}" font-size="10.5" font-weight="600" fill="{INK}">{v}</text>')
    p.append(f'<text x="{px}" y="{alt-8}" font-size="10.5" fill="{AZ}">o segundo maior salta aos olhos</text>')
    p.append('</svg>')
    return '\n'.join(p)


# ------------------------------------------------------------- treemap (parte do todo)

def treemap(itens, larg=MEIA, alt=250, destaque=None):
    """Muitas categorias de uma vez, com área proporcional (g-0.2).

    É a forma que a lição indica quando as fatias passam do que a pizza aguenta e a lista
    de barras ficaria longa demais para caber na tela.
    """
    itens = [(n, v) for n, v in sorted(itens, key=lambda kv: -kv[1]) if v > 0]
    if not itens:
        return ''
    total = sum(v for _, v in itens)
    alvo = destaque or itens[0][0]
    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="Treemap: cada retângulo é uma categoria, com área proporcional" '
         f'xmlns="http://www.w3.org/2000/svg">']

    def fatiar(dados, x, y, w, h):
        if not dados:
            return
        if len(dados) == 1:
            desenhar(dados[0], x, y, w, h)
            return
        soma = sum(v for _, v in dados)
        acc, corte = 0, 1
        for k, (_, v) in enumerate(dados):
            acc += v
            if acc >= soma / 2:
                corte = max(k + 1, 1)
                break
        a, b = dados[:corte], dados[corte:]
        sa = sum(v for _, v in a)
        if w >= h:
            wa = w * sa / soma
            fatiar(a, x, y, wa, h); fatiar(b, x + wa, y, w - wa, h)
        else:
            ha = h * sa / soma
            fatiar(a, x, y, w, ha); fatiar(b, x, y + ha, w, h - ha)

    def desenhar(item, x, y, w, h):
        nome, v = item
        cor = AMBAR if nome == alvo else MUTE
        p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w-2,1):.1f}" height="{max(h-2,1):.1f}" '
                 f'fill="{cor}" rx="2"/>')
        # o nome so entra se couber DENTRO do retangulo: escrito maior que a caixa, ele
        # invade o retangulo vizinho e os dois nomes se sobrepoem
        if w > 62 and h > 26 and len(nome) * 10.5 * 0.55 <= w - 12:
            p.append(f'<text x="{x+7:.1f}" y="{y+16:.1f}" font-size="10.5" fill="{INK}">{esc(nome)}</text>')
            p.append(f'<text x="{x+7:.1f}" y="{y+29:.1f}" font-size="11" font-weight="600" fill="{INK}">{v}</text>')
        elif w > 30 and h > 15:
            p.append(f'<text x="{x+5:.1f}" y="{y+13:.1f}" font-size="10" font-weight="600" fill="{INK}">{v}</text>')

    fatiar(itens, 0, 0, larg, alt - 18)
    p.append(f'<text x="0" y="{alt-4}" font-size="10.5" fill="{TXT}">'
             f'{len(itens)} categorias</text>')
    p.append('</svg>')
    return '\n'.join(p)


# ------------------------------------------------------------- índice base 100 (tempo)

_TXT_INDICE = {
    'eixo': '&#8593; índice, 100 = a própria série em {base}',
    'janela': 'a janela começa em {ini}, que é a primeira data com valor medível, e vai até {fim}',
}


def indice(series, rotulos, larg=MEIA, destaque=None, unidade='', textos=None):
    """Séries de tamanhos diferentes, todas partindo de 100.

    É o remédio da lição g-3.1 para o gráfico que responde quem é maior e fica calado sobre
    quem variou mais. Feita a conta, a série de 8 casos e a de 5 saem do mesmo ponto, e o
    desenho passa a falar de variação.

    Três coisas que o gráfico tem de dizer sozinho, e que o operador cobrou:

    - o que o eixo Y é, escrito nele: índice, com a base e a data da base;
    - de quando a quando vai o eixo X, sem depender do texto ao redor;
    - o absoluto de cada série na ponta, porque índice sem o número por trás engana.
    """
    T = _t(_TXT_INDICE, textos)
    series = {n: v for n, v in series.items() if v and v[0] > 0}
    if not series:
        return ''
    idx = {n: [x / v[0] * 100 for x in v] for n, v in series.items()}
    ordem = sorted(idx.items(), key=lambda kv: -kv[1][-1])
    alvo = destaque if destaque in idx else max(idx, key=lambda n: abs(idx[n][-1] - 100))
    topo = max(max(v) for _, v in ordem) * 1.12
    alt = 292
    esq, dirm, cima, baixo = 52, 134, 40, 56
    w, h = larg - esq - dirm, alt - cima - baixo
    n = len(rotulos)
    X = lambda i: esq + w * i / max(n - 1, 1)
    Y = lambda v: cima + h - (v / topo) * h

    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="Índice base 100: variação de cada série sobre a própria base" '
         f'xmlns="http://www.w3.org/2000/svg">']
    base_em = esc(rotulos[0]) if rotulos else ''
    p.append(f'<text x="{esq-40}" y="{cima-18}" font-size="10" fill="{TXT}">'
             f'{T["eixo"].format(base=base_em)}</text>')
    _eixo_y(p, esq, larg - dirm, cima, h, topo)
    y100 = Y(100)
    p.append(f'<line x1="{esq}" y1="{y100:.1f}" x2="{larg-dirm}" y2="{y100:.1f}" stroke="{INK}" '
             f'stroke-width="1.25" stroke-dasharray="5 4" opacity=".55"/>')
    p.append(f'<text x="{esq+3}" y="{y100-6:.1f}" font-size="10.5" font-weight="600" fill="{INK}">'
             f'100, o tamanho de partida</text>')
    # Cada rotulo de ponta ocupa DUAS linhas, o nome e o absoluto. Quando duas series
    # terminam perto, os dois blocos se sobrepoem. Sao empurrados para caber, na ordem em
    # que terminam, com uma haste ligando cada um ao seu ponto.
    fins = sorted(range(len(ordem)), key=lambda k: Y(ordem[k][1][-1]))
    teto, piso, folga = cima + 6, cima + h - 6, 30
    brutos = [Y(ordem[k][1][-1]) for k in fins]
    # desce empilhando, e depois SOBE de volta o que passou do piso. Sem a segunda passada,
    # as series que terminam juntas no rodape eram todas espremidas contra o limite, e os
    # rótulos voltavam a se encostar.
    for i in range(1, len(brutos)):
        brutos[i] = max(brutos[i], brutos[i - 1] + folga)
    for i in range(len(brutos) - 1, -1, -1):
        brutos[i] = min(brutos[i], piso)
        if i < len(brutos) - 1:
            brutos[i] = min(brutos[i], brutos[i + 1] - folga)
        brutos[i] = max(brutos[i], teto)
    ys = {ordem[k][0]: brutos[i] for i, k in enumerate(fins)}
    for nome, v in ordem:
        eh = nome == alvo
        cor = ALERTA if eh else MUTE
        d = ' '.join(f'{"M" if i==0 else "L"}{X(i):.1f},{Y(x):.1f}' for i, x in enumerate(v))
        p.append(f'<path d="{d}" fill="none" stroke="{cor}" stroke-width="{2.1 if eh else 1.4}" stroke-linejoin="round"/>')
        p.append(f'<circle cx="{X(len(v)-1):.1f}" cy="{Y(v[-1]):.1f}" r="3" fill="{cor}"/>')
        bruto = series[nome]
        yr = ys[nome]
        if abs(yr - Y(v[-1])) > 2:
            p.append(f'<line x1="{X(len(v)-1)+3:.1f}" y1="{Y(v[-1]):.1f}" x2="{X(len(v)-1)+7:.1f}" '
                     f'y2="{yr:.1f}" stroke="{cor}" stroke-width="1" opacity=".5"/>')
        p.append(f'<text x="{X(len(v)-1)+9:.1f}" y="{yr+1:.1f}" font-size="11" '
                 f'font-weight="{600 if eh else 400}" fill="{cor if eh else INK}">{esc(nome)}</text>')
        p.append(f'<text x="{X(len(v)-1)+9:.1f}" y="{yr+13:.1f}" font-size="9.5" fill="{TXT}">'
                 f'{v[-1]:.0f} &#183; {bruto[0]} &#8594; {bruto[-1]}{(" " + esc(unidade)) if unidade else ""}</text>')
    salto = max(1, n // 6)
    for i, r in enumerate(rotulos):
        if i % salto == 0 or i == n - 1:
            p.append(f'<text x="{X(i):.1f}" y="{cima+h+17:.1f}" text-anchor="middle" font-size="10" fill="{TXT}">{esc(r)}</text>')
    if rotulos:
        p.append(f'<text x="{esq}" y="{alt-8}" font-size="10" fill="{TXT}">'
                 f'{T["janela"].format(ini=esc(rotulos[0]), fim=esc(rotulos[-1]))}</text>')
    p.append('</svg>')
    return '\n'.join(p)


# ------------------------------------------------------------------- bolhas (relação)

def bolhas(pontos, larg=MEIA, rotx='esforço', roty='valor', rott='criticidade'):
    """Duas medidas na posição e uma terceira no tamanho do ponto (g-0.2).

    Andar junto não é causar, então não entra reta nenhuma: entram as duas réguas da
    mediana, que dividem o desenho em quadrantes e deixam o leitor julgar.
    """
    if not pontos:
        return ''
    alt = 290
    esq, dirm, cima, baixo = 46, 24, 30, 50
    w, h = larg - esq - dirm, alt - cima - baixo
    tx = max(x for x, _, _, _ in pontos) * 1.18
    ty = max(y for _, y, _, _ in pontos) * 1.18
    tt = max(t for _, _, t, _ in pontos) or 1
    X = lambda v: esq + w * v / tx
    Y = lambda v: cima + h - (v / ty) * h
    med = lambda vs: sorted(vs)[len(vs) // 2]
    mx, my = med([x for x, _, _, _ in pontos]), med([y for _, y, _, _ in pontos])

    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="Bolhas: {rotx} contra {roty}, com {rott} no tamanho" '
         f'xmlns="http://www.w3.org/2000/svg">']
    _eixo_y(p, esq, larg - dirm, cima, h, ty)
    p.append(f'<line x1="{X(mx):.1f}" y1="{cima}" x2="{X(mx):.1f}" y2="{cima+h:.1f}" stroke="{INK}" '
             f'stroke-width="1" stroke-dasharray="4 4" opacity=".4"/>')
    p.append(f'<line x1="{esq}" y1="{Y(my):.1f}" x2="{larg-dirm}" y2="{Y(my):.1f}" stroke="{INK}" '
             f'stroke-width="1" stroke-dasharray="4 4" opacity=".4"/>')
    for x, y, t, rot in pontos:
        r = 3.5 + 7 * math.sqrt(t / tt)
        # o quadrante que a mensagem defende: muito valor por pouco esforço
        alvo = x <= mx and y >= my
        p.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="{r:.1f}" fill="{AMBAR if alvo else MUTE}" '
                 f'opacity="{0.85 if alvo else 0.6}" stroke="{INK if alvo else "none"}" stroke-width="0.6"/>')
    p.append(f'<text x="{esq+4}" y="{cima+12}" font-size="10.5" font-weight="600" fill="{AMBAR}">'
             f'muito {roty}, pouco {rotx}</text>')
    p.append(f'<text x="{larg-dirm}" y="{cima+h+17:.1f}" text-anchor="end" font-size="10" fill="{TXT}">{esc(rotx)} &#8594;</text>')
    p.append(f'<text x="{esq}" y="{cima+h+17:.1f}" font-size="10" fill="{TXT}">&#8593; {esc(roty)}</text>')
    p.append(f'<text x="{esq}" y="{cima+h+34:.1f}" font-size="10" fill="{TXT}">'
             f'o tamanho da bolha é a {esc(rott)}</text>')
    p.append('</svg>')
    return '\n'.join(p)


# --------------------------------------------- barra 100% empilhada (comparação)

def empilhada100(grupos, categorias, cores, larg=MEIA, total_rot='itens'):
    """Uma barra por grupo, todas do mesmo comprimento, para comparar MISTURA.

    A lição g-3.2 prefere barra ordenada para participação dentro de um total. Esta forma
    serve a outra pergunta: como a mesma mistura muda de um grupo para o outro. O valor
    absoluto vai escrito ao lado, senão 100% de 15 parece igual a 100% de 84 (g-4.1).
    """
    if not grupos:
        return ''
    lin, esp = 34, 20
    alt = 26 + len(grupos) * (lin + esp)
    esq, dirm = 156, 54
    w = larg - esq - dirm
    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="Mistura de categorias por grupo, em barras de 100 por cento" '
         f'xmlns="http://www.w3.org/2000/svg">']
    for k, (nome, valores) in enumerate(grupos):
        y = 16 + k * (lin + esp)
        total = max(sum(valores), 1)
        p.append(f'<text x="{esq-10}" y="{y+14:.0f}" text-anchor="end" font-size="11.5" fill="{INK}">{esc(nome)}</text>')
        p.append(f'<text x="{esq-10}" y="{y+27:.0f}" text-anchor="end" font-size="10" fill="{TXT}">{total} {esc(total_rot)}</text>')
        x = esq
        for cat, v, cor in zip(categorias, valores, cores):
            if not v:
                continue
            bw = w * v / total
            p.append(f'<rect x="{x:.1f}" y="{y:.0f}" width="{bw:.1f}" height="20" fill="{cor}"/>')
            if bw > 34:
                p.append(f'<text x="{x+bw/2:.1f}" y="{y+14:.0f}" text-anchor="middle" font-size="10" '
                         f'font-weight="600" fill="{INK}">{v/total*100:.0f}%</text>')
            x += bw
        # o nome de cada faixa vai na primeira barra, o que dispensa a legenda de canto
        if k == 0:
            x = esq
            for cat, v in zip(categorias, valores):
                if v:
                    bw = w * v / total
                    if bw > 44:
                        p.append(f'<text x="{x+bw/2:.1f}" y="{y-5:.0f}" text-anchor="middle" font-size="10" '
                                 f'fill="{TXT}">{esc(cat)}</text>')
                    x += bw
    p.append('</svg>')
    return '\n'.join(p)


# ------------------------------------------------------ faixa de quartis (distribuição)

def quartis(linhas, larg=MEIA, unidade='dias'):
    """P25 a P75 na caixa, mediana no traço, P90 na ponta.

    Cada pergunta tem o seu número (g-3.2): mediana para o caso típico, P90 para os piores
    casos, e a faixa P25 a P75 para o que se pode esperar. A média ficaria de fora de todas
    as três.
    """
    linhas = [l for l in linhas if l[1]]
    if not linhas:
        return ''
    lin = 30
    alt = 30 + lin * len(linhas) + 38  # 38: a nota de leitura ocupa duas linhas
    esq, dirm = 138, 30  # a calha acompanha o nome do grupo por extenso
    w = larg - esq - dirm
    perc = lambda vs, k: sorted(vs)[min(int(round((len(vs) - 1) * k)), len(vs) - 1)]
    # O eixo vai até o MAIOR valor medido, e o que passa do P90 vira ponto solto. Antes o
    # eixo parava no maior P90: cerca de um em cada dez casos de cada área nunca era
    # desenhado, e o operador perguntou, com razão, o que mais estava fora do desenho.
    # Nenhum dado sai do desenho calado.
    topo = max(max(v) for _, v in linhas) * 1.05 or 1
    X = lambda v: esq + w * v / topo

    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="Faixa de quartis por categoria" xmlns="http://www.w3.org/2000/svg">']
    for t in range(3):
        v = topo * t / 2
        p.append(f'<line x1="{X(v):.1f}" y1="22" x2="{X(v):.1f}" y2="{22+lin*len(linhas):.0f}" stroke="{GRADE}" stroke-width="1"/>')
        p.append(f'<text x="{X(v):.1f}" y="16" text-anchor="middle" font-size="10" fill="{TXT}">{v:.0f}</text>')
    pior = max(linhas, key=lambda l: perc(l[1], .5))[0]
    for k, (nome, vs) in enumerate(sorted(linhas, key=lambda l: -perc(l[1], .5))):
        y = 30 + k * lin
        q1, q2, q3, q9 = perc(vs, .25), perc(vs, .5), perc(vs, .75), perc(vs, .9)
        cor = ALERTA if nome == pior else MUTE
        p.append(f'<text x="{esq-10}" y="{y+13:.0f}" text-anchor="end" font-size="11.5" fill="{INK}">{esc(nome)}</text>')
        p.append(f'<line x1="{X(q3):.1f}" y1="{y+8:.0f}" x2="{X(q9):.1f}" y2="{y+8:.0f}" stroke="{cor}" stroke-width="1.2"/>')
        p.append(f'<line x1="{X(q9):.1f}" y1="{y+3:.0f}" x2="{X(q9):.1f}" y2="{y+13:.0f}" stroke="{cor}" stroke-width="1.2"/>')
        # A caixa e a PEÇA principal desta forma, e ela vinha a 45% de opacidade, o que
        # desbotava a cor da marca e deixava o destaque mais fraco que o cinza vizinho.
        # A caixa em cheio, e a régua de trás em cinza, resolve sem perder a distinção.
        p.append(f'<rect x="{X(q1):.1f}" y="{y+1:.0f}" width="{max(X(q3)-X(q1),2):.1f}" height="14" fill="{cor}" rx="2"/>')
        # com a caixa em cheio, o traço da mediana vira branco na linha destacada: preto
        # sobre laranja some, e a mediana é o número que a forma existe para mostrar
        p.append(f'<line x1="{X(q2):.1f}" y1="{y:.0f}" x2="{X(q2):.1f}" y2="{y+16:.0f}" '
                 f'stroke="{"#ffffff" if nome == pior else INK}" stroke-width="2"/>')
        for x in (x for x in vs if x > q9):
            p.append(f'<circle cx="{X(x):.1f}" cy="{y+8:.0f}" r="2.6" fill="{cor}"/>')
        ult = X(max(vs))
        p.append(f'<text x="{ult+8:.1f}" y="{y+12:.0f}" font-size="10" fill="{TXT}">n={len(vs)}</text>')
    # A nota ensina a FORMA, e não este desenho: ela vale igual em qualquer slide que use
    # caixas, e por isso não carrega número nenhum.
    nota1 = 'como ler: cada linha é um grupo, e a caixa mostra onde cai a metade dos casos'
    nota2 = ('o traço dentro da caixa é o valor típico (a mediana); a linha vai até o P90, '
             'abaixo do qual ficam 9 em cada 10 casos; cada ponto além dela é um caso isolado; '
             'o número ao lado (n) diz quantos casos entraram na conta')
    p.append(f'<text class="leitura" x="{esq}" y="{alt-19}" font-size="10.5" fill="{TXT}">{nota1}</text>')
    p.append(f'<text class="leitura" x="{esq}" y="{alt-5}" font-size="10.5" fill="{TXT}">{nota2}</text>')
    p.append('</svg>')
    return '\n'.join(p)


# ------------------------------------------------------------ colunas (comparação)

def colunas(itens, larg=MEIA, unidade=''):
    """Colunas em pé: poucas categorias, com ordem própria que não é a do tamanho.

    A lição g-0.1 separa as barras deitadas, boas para ranking com nome longo, das colunas
    em pé, boas quando a categoria tem ordem natural, como dia da semana.
    """
    if not itens:
        return ''
    alt = 240
    esq, dirm, cima, baixo = 40, 18, 34, 44
    w, h = larg - esq - dirm, alt - cima - baixo
    topo = max(v for _, v in itens) * 1.2 or 1
    lb = w / (len(itens) * 1.5)
    vao = (w - lb * len(itens)) / max(len(itens) - 1, 1)
    Y = lambda v: cima + h - (v / topo) * h
    alvo = max(itens, key=lambda kv: kv[1])[0]
    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="Colunas por categoria de ordem natural" xmlns="http://www.w3.org/2000/svg">']
    _eixo_y(p, esq, larg - dirm, cima, h, topo)
    x = esq
    for nome, v in itens:
        cor = AMBAR if nome == alvo else MUTE
        p.append(f'<rect x="{x:.1f}" y="{Y(v):.1f}" width="{lb:.1f}" height="{max(Y(0)-Y(v),1):.1f}" fill="{cor}" rx="1.5"/>')
        if v:
            p.append(f'<text x="{x+lb/2:.1f}" y="{Y(v)-6:.1f}" text-anchor="middle" font-size="11" '
                     f'font-weight="600" fill="{cor}">{v}</text>')
        p.append(f'<text x="{x+lb/2:.1f}" y="{cima+h+17:.1f}" text-anchor="middle" font-size="10" fill="{TXT}">{esc(nome)}</text>')
        x += lb + vao
    if unidade:
        p.append(f'<text x="{esq}" y="{cima+h+34:.1f}" font-size="10" fill="{TXT}">{esc(unidade)}</text>')
    p.append('</svg>')
    return '\n'.join(p)


def _rotulo_valor(p, x, y, v, cor=INK, anc='middle', tam=11):
    p.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anc}" font-size="{tam}" '
             f'font-weight="600" fill="{cor}">{v}</text>')


# ----------------------------------------------------------- inclinação (slope), tempo

def inclinacao(itens, rot_antes, rot_depois, larg=MEIA, unidade=''):
    """Dois pontos e uma linha por categoria: a inclinação entrega direção e tamanho.

    A lição g-0.1 coloca esta forma no lugar das colunas lado a lado quando a pergunta é
    antes contra depois: colunas agrupadas obrigam o leitor a medir alturas de pares
    espalhados pelo eixo, e a inclinação diz tudo de uma vez.
    """
    itens = [(n, a, b) for n, a, b in itens]
    if not itens:
        return ''
    alt = 306
    cima, baixo = 40, 48
    h = alt - cima - baixo
    xa, xb = 132, larg - 132
    topo = max(max(a, b) for _, a, b in itens) * 1.12 or 1
    Y = lambda v: cima + h - (v / topo) * h
    subiu = max(itens, key=lambda t: t[2] - t[1])

    teto, piso = cima - 2, alt - 8

    def sem_colisao(vals, minimo=13):
        """Empurra rótulos que cairiam em cima uns dos outros, mantendo a ordem.

        A descida empilha, e com rótulos próximos o último saía por baixo da tela. Por isso
        vem a segunda passada, de baixo para cima, que prende a pilha entre o teto e o piso.
        """
        ordem = sorted(range(len(vals)), key=lambda k: vals[k])
        saida = list(vals)
        for pos, k in enumerate(ordem):
            if pos and saida[k] - saida[ordem[pos - 1]] < minimo:
                saida[k] = saida[ordem[pos - 1]] + minimo
        for pos in range(len(ordem) - 1, -1, -1):
            k = ordem[pos]
            saida[k] = min(saida[k], piso)
            if pos < len(ordem) - 1 and saida[ordem[pos + 1]] - saida[k] < minimo:
                saida[k] = saida[ordem[pos + 1]] - minimo
            saida[k] = max(saida[k], teto)
        return saida

    ordenados = sorted(itens, key=lambda t: -t[2])
    ya = sem_colisao([Y(a) for _, a, _ in ordenados])
    yb = sem_colisao([Y(b) for _, _, b in ordenados])

    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="Antes e depois, uma linha por categoria" xmlns="http://www.w3.org/2000/svg">']
    p.append(f'<line x1="{xa}" y1="{cima-10}" x2="{xa}" y2="{cima+h+6:.0f}" stroke="{GRADE}" stroke-width="1"/>')
    p.append(f'<line x1="{xb}" y1="{cima-10}" x2="{xb}" y2="{cima+h+6:.0f}" stroke="{GRADE}" stroke-width="1"/>')
    p.append(f'<text x="{xa}" y="{cima-18}" text-anchor="middle" font-size="11" fill="{TXT}">{esc(rot_antes)}</text>')
    p.append(f'<text x="{xb}" y="{cima-18}" text-anchor="middle" font-size="11" fill="{TXT}">{esc(rot_depois)}</text>')
    for k, (nome, a, b) in enumerate(ordenados):
        cor = ALERTA if nome == subiu[0] else MUTE
        peso = 2.2 if nome == subiu[0] else 1.4
        p.append(f'<line x1="{xa}" y1="{Y(a):.1f}" x2="{xb}" y2="{Y(b):.1f}" stroke="{cor}" stroke-width="{peso}"/>')
        p.append(f'<circle cx="{xa}" cy="{Y(a):.1f}" r="3" fill="{cor}"/>')
        p.append(f'<circle cx="{xb}" cy="{Y(b):.1f}" r="3" fill="{cor}"/>')
        # a haste liga o rótulo deslocado ao ponto de verdade, senão o leitor associa errado
        if abs(ya[k] - Y(a)) > 2:
            p.append(f'<line x1="{xa-6}" y1="{ya[k]-3:.1f}" x2="{xa-2}" y2="{Y(a):.1f}" stroke="{GRADE}" stroke-width="1"/>')
        if abs(yb[k] - Y(b)) > 2:
            p.append(f'<line x1="{xb+2}" y1="{Y(b):.1f}" x2="{xb+6}" y2="{yb[k]-3:.1f}" stroke="{GRADE}" stroke-width="1"/>')
        p.append(f'<text x="{xa-9}" y="{ya[k]:.1f}" text-anchor="end" font-size="10.5" fill="{INK}">{esc(nome)} {a}</text>')
        p.append(f'<text x="{xb+9}" y="{yb[k]:.1f}" font-size="10.5" font-weight="{600 if nome==subiu[0] else 400}" '
                 f'fill="{cor if nome==subiu[0] else INK}">{b}</text>')
    if unidade:
        # o rodape ficava na mesma faixa do rotulo mais baixo da esquerda; agora ele vive
        # abaixo da moldura, numa linha propria
        p.append(f'<text x="0" y="{alt-4}" font-size="10" fill="{TXT}">{esc(unidade)}</text>')
    p.append('</svg>')
    return '\n'.join(p)


# ------------------------------------------------------------- área empilhada, tempo

def _suave(pts):
    """Liga os pontos com curva, e não com quina, sem nunca passar dos pontos medidos.

    É a interpolação monótona de Fritsch e Carlson: entre dois pontos a curva fica dentro
    do intervalo deles. A versão anterior zerava a tangente só no extremo local, e ainda
    estourava num salto como 56, 103, 22: a faixa de baixo descia abaixo de zero, que é
    saldo negativo, e o operador viu no relatório de 28/09/2026.
    """
    n = len(pts)
    if n < 3:
        return 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    h = [xs[i + 1] - xs[i] for i in range(n - 1)]
    s = [(ys[i + 1] - ys[i]) / h[i] if h[i] else 0 for i in range(n - 1)]
    m = [s[0]] + [0 if s[i - 1] * s[i] <= 0 else (s[i - 1] + s[i]) / 2
                  for i in range(1, n - 1)] + [s[-1]]
    for i in range(n - 1):
        if s[i] == 0:
            m[i] = m[i + 1] = 0
            continue
        a_, b_ = m[i] / s[i], m[i + 1] / s[i]
        if a_ < 0:
            m[i] = 0
        if b_ < 0:
            m[i + 1] = 0
        r = a_ * a_ + b_ * b_
        if r > 9:
            k = 3 / r ** .5
            m[i], m[i + 1] = k * a_ * s[i], k * b_ * s[i]
    d = [f'M{xs[0]:.1f},{ys[0]:.1f}']
    for i in range(n - 1):
        dx = h[i] / 3
        d.append(f'C{xs[i] + dx:.1f},{ys[i] + m[i] * dx:.1f} '
                 f'{xs[i + 1] - dx:.1f},{ys[i + 1] - m[i + 1] * dx:.1f} '
                 f'{xs[i + 1]:.1f},{ys[i + 1]:.1f}')
    return ' '.join(d)


def area_empilhada(series, rotulos, cores, larg=MEIA, anotar_pico=True,
                   aria='Área empilhada: composição do total ao longo do tempo'):
    """Composição ao longo do tempo, com o total lido na altura da pilha.

    Serve quando a pergunta junta duas: quanto no total, e de que esse total é feito. Cada
    faixa recebe o nome dentro dela, o que dispensa a legenda de canto (g-2.1).

    Com `anotar_pico`, a virada da série ganha a camada de anotação que a trilha pede: um
    ponto no máximo, uma haste e um texto curto com o valor e a data, mais a queda até
    hoje. O leitor não deveria precisar medir o desenho com o olho para achar a virada.
    """
    nomes = list(series.keys())
    if not nomes:
        return ''
    n = len(rotulos)
    alt = 282
    esq, dirm, cima, baixo = 42, 96, 26, 44
    w, h = larg - esq - dirm, alt - cima - baixo
    totais = [sum(series[k][i] for k in nomes) for i in range(n)]
    topo = max(totais) * 1.1 or 1
    X = lambda i: esq + w * i / max(n - 1, 1)
    Y = lambda v: cima + h - (v / topo) * h

    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="{esc(aria)}" '
         f'xmlns="http://www.w3.org/2000/svg">']
    _eixo_y(p, esq, larg - dirm, cima, h, topo)
    base = [0] * n
    for k, nome in enumerate(nomes):
        v = series[nome]
        topo_s = [base[i] + v[i] for i in range(n)]
        caminho = (_suave([(X(i), Y(topo_s[i])) for i in range(n)])
                   + ' L' + _suave([(X(i), Y(base[i])) for i in reversed(range(n))])[1:]
                   + ' Z')
        p.append(f'<path d="{caminho}" fill="{cores[k % len(cores)]}"/>')
        meio = (Y(topo_s[-1]) + Y(base[-1])) / 2
        rot_faixa = f'{nome} {v[-1]}'
        if Y(base[-1]) - Y(topo_s[-1]) > 13 and len(rot_faixa) * 10.5 * 0.55 <= dirm - 10:
            p.append(f'<text x="{X(n-1)+8:.1f}" y="{meio+4:.1f}" font-size="10.5" fill="{INK}">{esc(rot_faixa)}</text>')
        base = topo_s
    # a camada de anotação vai por cima das faixas, senão o polígono seguinte a cobre
    if anotar_pico and n > 2:
        ipico = max(range(n), key=lambda i: totais[i])
        pico, hoje = totais[ipico], totais[-1]
        if pico > hoje and ipico < n - 1:
            xp, yp = X(ipico), Y(pico)
            queda = (pico - hoje) / pico * 100
            p.append(f'<circle cx="{xp:.1f}" cy="{yp:.1f}" r="4" fill="none" stroke="{INK}" stroke-width="1.5"/>')
            p.append(f'<line x1="{xp:.1f}" y1="{yp-6:.1f}" x2="{xp:.1f}" y2="{cima+4:.1f}" '
                     f'stroke="{INK}" stroke-width="1" opacity=".45"/>')
            anc = 'start' if xp < esq + w * .6 else 'end'
            dx = 6 if anc == 'start' else -6
            p.append(f'<text x="{xp+dx:.1f}" y="{cima:.1f}" text-anchor="{anc}" font-size="10.5" '
                     f'font-weight="600" fill="{INK}">pico de {pico} em {esc(rotulos[ipico])}</text>')
            p.append(f'<text x="{xp+dx:.1f}" y="{cima+12:.1f}" text-anchor="{anc}" font-size="9.5" '
                     f'fill="{ALERTA}">caiu {queda:.0f}% até hoje, para {hoje}</text>')
            p.append(f'<circle cx="{X(n-1):.1f}" cy="{Y(hoje):.1f}" r="3.5" fill="{INK}"/>')
            p.append(f'<text x="{X(n-1)-8:.1f}" y="{Y(hoje)-9:.1f}" text-anchor="end" '
                     f'font-size="10.5" font-weight="600" fill="{INK}">hoje: {hoje}</text>')

    salto, postos = max(1, n // 6), []
    for i, r in enumerate(rotulos):
        if (i % salto == 0 or i == n - 1) and _cabe(X(i), r, postos):
            p.append(f'<text x="{X(i):.1f}" y="{cima+h+17:.1f}" text-anchor="middle" font-size="10" fill="{TXT}">{esc(r)}</text>')
    p.append('</svg>')
    return '\n'.join(p)


# ----------------------------------------------- barra empilhada única, parte do todo

def empilhada_unica(itens, cores, larg=MEIA, total_rot='itens'):
    """Uma barra só, com poucas fatias, para um total que se reparte.

    A lição g-3.2 aceita esta forma quando as fatias são poucas: o comprimento continua
    sendo comparado sobre uma base comum, ao contrário do ângulo da pizza.
    """
    itens = [(n, v) for n, v in itens if v > 0]
    if not itens:
        return ''
    total = sum(v for _, v in itens)
    alt, y, hh = 132, 44, 34
    esq, dirm = 4, 4
    w = larg - esq - dirm
    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="Uma barra repartida entre as categorias" xmlns="http://www.w3.org/2000/svg">']
    x = esq
    for k, (nome, v) in enumerate(itens):
        bw = w * v / total
        p.append(f'<rect x="{x:.1f}" y="{y}" width="{bw:.1f}" height="{hh}" fill="{cores[k % len(cores)]}"/>')
        if bw > 46:
            p.append(f'<text x="{x+bw/2:.1f}" y="{y+21:.0f}" text-anchor="middle" font-size="11" '
                     f'font-weight="600" fill="{INK}">{v}</text>')
            p.append(f'<text x="{x+bw/2:.1f}" y="{y-8:.0f}" text-anchor="middle" font-size="10" fill="{TXT}">{esc(nome)}</text>')
        x += bw

    p.append('</svg>')
    return '\n'.join(p)


# ------------------------------------------------ pontos num eixo só, comparação

def pontos_eixo(itens, larg=MEIA, unidade='', referencia=None, rot_ref='média do grupo'):
    """Posição num eixo comum, que é a leitura mais precisa depois do comprimento.

    Com a média do grupo desenhada atrás, cada ponto ganha sentido contra os pares, que é a
    régua da lição g-2.3.
    """
    itens = sorted(itens, key=lambda kv: -kv[1])
    if not itens:
        return ''
    lin = 26
    alt = 34 + lin * len(itens) + 26
    esq, dirm = 108, 42
    w = larg - esq - dirm
    topo = max(v for _, v in itens) * 1.15 or 1
    X = lambda v: esq + w * v / topo
    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="Um ponto por categoria, num eixo comum" xmlns="http://www.w3.org/2000/svg">']
    for t in range(3):
        v = topo * t / 2
        p.append(f'<line x1="{X(v):.1f}" y1="26" x2="{X(v):.1f}" y2="{26+lin*len(itens):.0f}" stroke="{GRADE}" stroke-width="1"/>')
        p.append(f'<text x="{X(v):.1f}" y="18" text-anchor="middle" font-size="10" fill="{TXT}">{v:.0f}</text>')
    if referencia is not None:
        p.append(f'<line x1="{X(referencia):.1f}" y1="22" x2="{X(referencia):.1f}" y2="{26+lin*len(itens)+4:.0f}" '
                 f'stroke="{INK}" stroke-width="1.25" stroke-dasharray="5 4" opacity=".55"/>')
        p.append(f'<text x="{X(referencia)+5:.1f}" y="{26+lin*len(itens)+16:.0f}" font-size="10" '
                 f'font-weight="600" fill="{INK}">{esc(rot_ref)}: {referencia:.0f}</text>')
    for k, (nome, v) in enumerate(itens):
        y = 34 + k * lin
        acima = referencia is not None and v > referencia
        cor = ALERTA if acima else MUTE
        p.append(f'<line x1="{esq}" y1="{y+5:.0f}" x2="{X(v):.1f}" y2="{y+5:.0f}" stroke="{GRADE}" stroke-width="1"/>')
        p.append(f'<circle cx="{X(v):.1f}" cy="{y+5:.0f}" r="5" fill="{cor}"/>')
        p.append(f'<text x="{esq-10}" y="{y+9:.0f}" text-anchor="end" font-size="11.5" fill="{INK}">{esc(nome)}</text>')
        p.append(f'<text x="{X(v)+11:.1f}" y="{y+9:.0f}" font-size="11" font-weight="600" fill="{INK}">{v:.0f}</text>')
    if unidade:
        p.append(f'<text x="{esq}" y="{alt-4}" font-size="10" fill="{TXT}">{esc(unidade)}</text>')
    p.append('</svg>')
    return '\n'.join(p)


# --------------------------------------------------- mapa de calor, comparação

def mapa_calor(linhas, colunas, matriz, larg=MEIA):
    """Intensidade de cor para duas categorias cruzadas.

    A cor aqui carrega quantidade, e não identidade, então ela vai de um tom só, do claro
    ao escuro. O tom é o verde da marca do cliente, e a rampa continua sendo de uma cor
    única: escala sequencial com duas matizes faria o leitor procurar diferença de
    categoria onde só existe diferença de tamanho.

    O número vai escrito dentro da célula, porque intensidade se compara mal entre tons
    vizinhos, e o desenho não pode depender só disso.
    """
    if not linhas or not colunas:
        return ''
    # Linha ou coluna inteiramente vazia sai do desenho, pela mesma razão que a etapa
    # `Validado` saiu do funil: célula que só pode dar zero ocupa espaço e não informa.
    vivas_c = [j for j in range(len(colunas)) if any(l[j] for l in matriz)]
    vivas_l = [i for i, l in enumerate(matriz) if any(l)]
    if not vivas_c or not vivas_l:
        return ''
    colunas = [colunas[j] for j in vivas_c]
    linhas = [linhas[i] for i in vivas_l]
    matriz = [[matriz[i][j] for j in vivas_c] for i in vivas_l]
    cw = (larg - 108) / len(colunas)
    ch = 30
    alt = 46 + ch * len(linhas) + 22
    topo = max((max(l) for l in matriz), default=1) or 1
    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="Mapa de calor cruzando duas categorias" xmlns="http://www.w3.org/2000/svg">']
    for j, c in enumerate(colunas):
        p.append(f'<text x="{108+cw*j+cw/2:.1f}" y="36" text-anchor="middle" font-size="10" fill="{TXT}">{esc(c)}</text>')
    for i, nome in enumerate(linhas):
        y = 46 + i * ch
        p.append(f'<text x="98" y="{y+19:.0f}" text-anchor="end" font-size="11" fill="{INK}">{esc(nome)}</text>')
        for j in range(len(colunas)):
            v = matriz[i][j]
            op = 0.06 + 0.84 * (v / topo) if v else 0.04
            x = 108 + cw * j
            p.append(f'<rect x="{x:.1f}" y="{y}" width="{cw-2:.1f}" height="{ch-2}" fill="{AMBAR}" opacity="{op:.2f}"/>')
            if v:
                claro = op > 0.45
                p.append(f'<text x="{x+cw/2-1:.1f}" y="{y+19:.0f}" text-anchor="middle" font-size="10.5" '
                         f'font-weight="600" fill="{"#ffffff" if claro else INK}">{v}</text>')
    p.append(f'<text class="leitura" x="108" y="{alt-6}" font-size="10" fill="{TXT}">cada quadrado cruza uma linha com uma coluna, e quanto mais escuro, mais itens</text>')
    p.append('</svg>')
    return '\n'.join(p)


# ------------------------------------------------- top 5 mais Outros, comparação

def top_mais_outros(itens, larg=MEIA, n=5, unidade='itens'):
    """As cinco maiores, e o resto somado numa barra de Outros.

    A lição g-2.2 aceita o corte no top 5 desde que o que ficou de fora apareça: top 5
    limpo, sem mencionar as demais, esconde o tamanho do que foi cortado. Se a barra de
    Outros ficar maior que a primeira, o corte está errado, e o desenho denuncia isso.
    """
    itens = sorted(itens, key=lambda kv: -kv[1])
    cima, resto = itens[:n], itens[n:]
    soma_resto = sum(v for _, v in resto)
    linhas = cima + ([('Outros ({} categorias)'.format(len(resto)), soma_resto)] if resto else [])
    total = sum(v for _, v in itens)
    lin = 26
    alt = 10 + lin * len(linhas) + 28
    esq, dirm = 150, 46
    w = larg - esq - dirm
    maior = max(v for _, v in linhas)
    alerta = soma_resto > (cima[0][1] if cima else 0)

    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="As maiores categorias, e o resto somado" xmlns="http://www.w3.org/2000/svg">']
    for k, (nome, v) in enumerate(linhas):
        y = 10 + k * lin
        ehoutros = resto and k == len(linhas) - 1
        cor = (ALERTA if alerta else '#b8b8b8') if ehoutros else (AMBAR if k == 0 else MUTE)
        bw = max(w * v / maior, 1.5)
        p.append(f'<text x="{esq-10}" y="{y+13:.0f}" text-anchor="end" font-size="11" fill="{INK}">{esc(nome)}</text>')
        p.append(f'<rect x="{esq}" y="{y+4:.0f}" width="{bw:.1f}" height="14" fill="{cor}" rx="2"/>')
        p.append(f'<text x="{esq+bw+7:.1f}" y="{y+15:.0f}" font-size="11" font-weight="600" fill="{INK}">{v}</text>')
    nota = ('Outros passou a primeira: o corte esconde o assunto'
            if alerta else f'{total} {unidade} no total, nada escondido')
    p.append(f'<text x="{esq}" y="{alt-8}" font-size="10.5" fill="{ALERTA if alerta else TXT}">{nota}</text>')
    p.append('</svg>')
    return '\n'.join(p)


# --------------------------------------------- barra divergente, comparação

def divergente(itens, referencia, larg=MEIA, unidade='dias', rot_ref='mediana do grupo'):
    """Desvio com sinal a partir de uma referência: quem passou e quem ficou abaixo.

    A lição g-1.2 pede uma referência declarada para esta forma, e a g-2.3 lista a média do
    grupo entre as três réguas que resolvem quase tudo.
    """
    itens = sorted(((n, v - referencia) for n, v in itens), key=lambda kv: -kv[1])
    if not itens:
        return ''
    lin = 26
    alt = 30 + lin * len(itens) + 26
    esq, dirm = 108, 34
    w = larg - esq - dirm
    amp = max(abs(v) for _, v in itens) * 1.2 or 1
    zero = esq + w / 2
    X = lambda v: zero + (w / 2) * v / amp
    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="Desvio de cada categoria contra a referência do grupo" '
         f'xmlns="http://www.w3.org/2000/svg">']
    p.append(f'<line x1="{zero:.1f}" y1="22" x2="{zero:.1f}" y2="{30+lin*len(itens):.0f}" stroke="{INK}" stroke-width="1.25" opacity=".6"/>')
    p.append(f'<text x="{zero:.1f}" y="16" text-anchor="middle" font-size="10" font-weight="600" fill="{INK}">{esc(rot_ref)}</text>')
    for k, (nome, v) in enumerate(itens):
        y = 30 + k * lin
        cor = ALERTA if v > 0 else AZ
        x0, x1 = (zero, X(v)) if v > 0 else (X(v), zero)
        p.append(f'<rect x="{x0:.1f}" y="{y+3:.0f}" width="{max(x1-x0,1.5):.1f}" height="14" fill="{cor}" rx="2"/>')
        p.append(f'<text x="{esq-10}" y="{y+14:.0f}" text-anchor="end" font-size="11.5" fill="{INK}">{esc(nome)}</text>')
        anc, xt = ('start', X(v) + 7) if v > 0 else ('end', X(v) - 7)
        p.append(f'<text x="{xt:.1f}" y="{y+14:.0f}" text-anchor="{anc}" font-size="10.5" font-weight="600" '
                 f'fill="{cor}">{v:+.0f}</text>')
    p.append(f'<text x="{esq}" y="{alt-6}" font-size="10" fill="{TXT}">{esc(unidade)} acima ou abaixo da referência</text>')
    p.append('</svg>')
    return '\n'.join(p)


# ================================ ANTIEXEMPLOS, sempre ao lado da forma correta ========

def eixo_cortado(itens, larg=CHEIA):
    """O mesmo dado com o eixo cortado e com o eixo do zero.

    Quem mente é a régua, e não a barra: os valores estão certos nos dois desenhos. É o
    caso da lição g-1.3, em que 42 contra 38 parece quase o dobro com o eixo começando em 28.
    """
    itens = sorted(itens, key=lambda kv: -kv[1])[:5]
    if len(itens) < 2:
        return ''
    alt = 250
    meia = larg / 2
    maior, menor = itens[0][1], itens[-1][1]
    corte = max(menor - max(1, (maior - menor) * 0.15), 0)

    def painel(x0, base, titulo, cor_titulo):
        esq, cima, baixo, dirm = x0 + 44, 42, 40, 24
        w, h = meia - 44 - dirm, alt - cima - baixo
        lb = w / (len(itens) * 1.5)
        vao = (w - lb * len(itens)) / max(len(itens) - 1, 1)
        span = (maior * 1.08 - base) or 1
        Y = lambda v: cima + h - ((v - base) / span) * h
        out = [f'<text x="{x0+8}" y="20" font-size="11" font-weight="600" fill="{cor_titulo}">{titulo}</text>']
        out.append(f'<line x1="{esq-6}" y1="{cima+h:.1f}" x2="{esq+w:.1f}" y2="{cima+h:.1f}" stroke="{GRADE}" stroke-width="1"/>')
        out.append(f'<text x="{esq-10}" y="{cima+h+4:.1f}" text-anchor="end" font-size="10" fill="{TXT}">{base:.0f}</text>')
        x = esq
        for nome, v in itens:
            y = Y(v)
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{lb:.1f}" height="{max(cima+h-y,1):.1f}" fill="{MUTE}" rx="1.5"/>')
            out.append(f'<text x="{x+lb/2:.1f}" y="{y-6:.1f}" text-anchor="middle" font-size="10.5" font-weight="600" fill="{INK}">{v}</text>')
            out.append(f'<text x="{x+lb/2:.1f}" y="{cima+h+15:.1f}" text-anchor="middle" font-size="9.5" fill="{TXT}">{esc(nome[:9])}</text>')
            x += lb + vao
        return out

    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="O mesmo dado com eixo cortado e com eixo no zero" xmlns="http://www.w3.org/2000/svg">']
    p += painel(0, corte, f'eixo cortado em {corte:.0f}', ALERTA)
    p += painel(meia, 0, 'eixo no zero', AZ)
    p.append(f'<line x1="{meia:.1f}" y1="8" x2="{meia:.1f}" y2="{alt-28}" stroke="{GRADE}" stroke-width="1"/>')
    p.append(f'<text x="8" y="{alt-8}" font-size="10.5" fill="{ALERTA}">o degrau parece enorme</text>')
    p.append(f'<text x="{meia+8:.0f}" y="{alt-8}" font-size="10.5" fill="{AZ}">o degrau real, proporcional ao dado</text>')
    p.append('</svg>')
    return '\n'.join(p)


def espaguete_contra_paineis(series, rotulos, larg=CHEIA):
    """As mesmas séries num gráfico só e em painéis pequenos.

    O espaguete da lição g-3.1: linhas que se cruzam continuam cruzadas com mais cores, e a
    legenda de canto obriga o olho a decorar a cor e voltar.
    """
    nomes = list(series.keys())
    if not nomes:
        return ''
    alt = 250
    meia = larg / 2
    n = len(rotulos)
    topo = max(max(v) for v in series.values()) * 1.12 or 1
    tons = ['#b03a2e', '#1f618d', '#1e8449', '#b9770e', '#7d3c98', '#117a65']

    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="As mesmas séries como espaguete e como painéis pequenos" '
         f'xmlns="http://www.w3.org/2000/svg">']
    esq, cima, h, w = 40, 40, alt - 40 - 52, meia - 40 - 90
    X = lambda i: esq + w * i / max(n - 1, 1)
    Y = lambda v: cima + h - (v / topo) * h
    p.append(f'<text x="8" y="20" font-size="11" font-weight="600" fill="{ALERTA}">tudo num gráfico só</text>')
    for k, nome in enumerate(nomes):
        d = ' '.join(f'{"M" if i==0 else "L"}{X(i):.1f},{Y(v):.1f}' for i, v in enumerate(series[nome]))
        p.append(f'<path d="{d}" fill="none" stroke="{tons[k % len(tons)]}" stroke-width="1.8"/>')
    ly = cima + 4
    for k, nome in enumerate(nomes):
        p.append(f'<rect x="{esq+w+14:.0f}" y="{ly+k*15:.0f}" width="9" height="9" fill="{tons[k % len(tons)]}"/>')
        p.append(f'<text x="{esq+w+28:.0f}" y="{ly+k*15+8:.0f}" font-size="9.5" fill="{TXT}">{esc(nome)}</text>')
    p.append(f'<text x="8" y="{alt-8}" font-size="10.5" fill="{ALERTA}">seis cores e uma legenda no canto</text>')

    cols, cw, chh = 3, (meia - 16) / 3, (alt - 70) / 2
    p.append(f'<text x="{meia+8:.0f}" y="20" font-size="11" font-weight="600" fill="{AZ}">um painel por série</text>')
    for k, nome in enumerate(sorted(nomes, key=lambda x: -series[x][-1])):
        cx, cy = meia + 8 + (k % cols) * cw, 30 + (k // cols) * chh
        px, py, pw, ph = cx + 2, cy + 16, cw - 12, chh - 34
        XX = lambda i: px + pw * i / max(n - 1, 1)
        YY = lambda v: py + ph - (v / topo) * ph
        p.append(f'<text x="{cx+2:.0f}" y="{cy+11:.0f}" font-size="9.5" fill="{INK}">{esc(nome)} {series[nome][-1]}</text>')
        d = ' '.join(f'{"M" if i==0 else "L"}{XX(i):.1f},{YY(v):.1f}' for i, v in enumerate(series[nome]))
        p.append(f'<path d="{d}" fill="none" stroke="{AZ}" stroke-width="1.5"/>')
        p.append(f'<line x1="{px:.1f}" y1="{py+ph:.1f}" x2="{px+pw:.1f}" y2="{py+ph:.1f}" stroke="{GRADE}" stroke-width="1"/>')
    p.append(f'<line x1="{meia:.1f}" y1="8" x2="{meia:.1f}" y2="{alt-28}" stroke="{GRADE}" stroke-width="1"/>')
    p.append(f'<text x="{meia+8:.0f}" y="{alt-8}" font-size="10.5" fill="{AZ}">mesmo eixo, nome no título, zero legenda</text>')
    p.append('</svg>')
    return '\n'.join(p)


def radar_contra_barras(itens, larg=CHEIA):
    """O mesmo dado em radar e em barras ordenadas.

    O radar aparece na trilha como antiexemplo: a área do polígono muda conforme a ordem
    dos eixos, e o olho compara área com muito menos precisão do que comprimento.
    """
    itens = list(itens)
    if len(itens) < 3:
        return ''
    alt = 260
    meia = larg / 2
    if not itens:
        return ''
    maior = max(v for _, v in itens) or 1
    cx, cy, r = meia / 2, alt / 2 + 6, 74
    k = len(itens)
    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="O mesmo dado em radar e em barras ordenadas" xmlns="http://www.w3.org/2000/svg">']
    p.append(f'<text x="8" y="20" font-size="11" font-weight="600" fill="{ALERTA}">como radar</text>')
    for anel in (0.5, 1.0):
        pts = ' '.join(f'{cx + r*anel*math.cos(-math.pi/2 + 2*math.pi*i/k):.1f},'
                       f'{cy + r*anel*math.sin(-math.pi/2 + 2*math.pi*i/k):.1f}' for i in range(k))
        p.append(f'<polygon points="{pts}" fill="none" stroke="{GRADE}" stroke-width="1"/>')
    pts = []
    for i, (nome, v) in enumerate(itens):
        ang = -math.pi / 2 + 2 * math.pi * i / k
        rr = r * v / maior
        pts.append(f'{cx + rr*math.cos(ang):.1f},{cy + rr*math.sin(ang):.1f}')
        p.append(f'<text x="{cx + (r+14)*math.cos(ang):.1f}" y="{cy + (r+14)*math.sin(ang)+3:.1f}" '
                 f'text-anchor="middle" font-size="9" fill="{TXT}">{esc(nome[:8])}</text>')
    p.append(f'<polygon points="{" ".join(pts)}" fill="{ALERTA}" opacity=".18" stroke="{ALERTA}" stroke-width="1.5"/>')
    p.append(f'<text x="8" y="{alt-8}" font-size="10.5" fill="{ALERTA}">a área muda se os eixos trocarem de ordem</text>')

    px, pw = meia + 96, meia - 96 - 44
    p.append(f'<text x="{meia+8:.0f}" y="20" font-size="11" font-weight="600" fill="{AZ}">como barras ordenadas</text>')
    lin = min(26, (alt - 70) / k)
    for i, (nome, v) in enumerate(sorted(itens, key=lambda kv: -kv[1])):
        y = 34 + i * lin
        bw = max(pw * v / maior, 1.5)
        p.append(f'<text x="{px-10:.0f}" y="{y+11:.0f}" text-anchor="end" font-size="10.5" fill="{INK}">{esc(nome)}</text>')
        p.append(f'<rect x="{px:.0f}" y="{y+1:.0f}" width="{bw:.1f}" height="13" fill="{AMBAR if i==0 else MUTE}" rx="2"/>')
        p.append(f'<text x="{px+bw+6:.1f}" y="{y+12:.0f}" font-size="10.5" font-weight="600" fill="{INK}">{v}</text>')
    p.append(f'<line x1="{meia:.1f}" y1="8" x2="{meia:.1f}" y2="{alt-28}" stroke="{GRADE}" stroke-width="1"/>')
    p.append(f'<text x="{meia+8:.0f}" y="{alt-8}" font-size="10.5" fill="{AZ}">o ranking se lê sem ninguém medir área</text>')
    p.append('</svg>')
    return '\n'.join(p)


def alfabetica_contra_ordenada(itens, larg=CHEIA):
    """O mesmo dado em ordem alfabética e em ordem de tamanho.

    A ordem alfabética seduz porque parece neutra, mas ninguém pediu lista telefônica: ela
    joga fora a leitura mais fácil que o gráfico tinha para oferecer (g-2.2).
    """
    if len(itens) < 3:
        return ''
    alt = 34 + 26 * len(itens) + 30
    meia = larg / 2
    if not itens:
        return ''
    maior = max(v for _, v in itens) or 1
    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="O mesmo dado em ordem alfabética e em ordem de tamanho" '
         f'xmlns="http://www.w3.org/2000/svg">']

    def lado(x0, dados, titulo, cor_titulo, destacar):
        px, pw = x0 + 104, meia - 104 - 44
        out = [f'<text x="{x0+8}" y="20" font-size="11" font-weight="600" fill="{cor_titulo}">{titulo}</text>']
        for i, (nome, v) in enumerate(dados):
            y = 34 + i * 26
            bw = max(pw * v / maior, 1.5)
            cor = AMBAR if (destacar and i == 0) else MUTE
            out.append(f'<text x="{px-10:.0f}" y="{y+13:.0f}" text-anchor="end" font-size="11" fill="{INK}">{esc(nome)}</text>')
            out.append(f'<rect x="{px:.0f}" y="{y+2:.0f}" width="{bw:.1f}" height="14" fill="{cor}" rx="2"/>')
            out.append(f'<text x="{px+bw+6:.1f}" y="{y+14:.0f}" font-size="10.5" font-weight="600" fill="{INK}">{v}</text>')
        return out

    p += lado(0, sorted(itens, key=lambda kv: kv[0].lower()), 'em ordem alfabética', ALERTA, False)
    p += lado(meia, sorted(itens, key=lambda kv: -kv[1]), 'em ordem de tamanho', AZ, True)
    p.append(f'<line x1="{meia:.1f}" y1="8" x2="{meia:.1f}" y2="{alt-26}" stroke="{GRADE}" stroke-width="1"/>')
    p.append(f'<text x="8" y="{alt-8}" font-size="10.5" fill="{ALERTA}">cada leitor monta o ranking sozinho</text>')
    p.append(f'<text x="{meia+8:.0f}" y="{alt-8}" font-size="10.5" fill="{AZ}">a ordem já responde a pergunta</text>')
    p.append('</svg>')
    return '\n'.join(p)


# ------------------------------------------------------------------ quatro indicadores

def kpis(cartoes, larg=CHEIA, cols=None):
    """Quatro números, e só quatro.

    Cada um vem com a régua ao lado, porque número sozinho aceita vereditos opostos (g-2.3),
    e com o denominador escrito, porque quem lê decide em cinco segundos (g-4.1). O quinto
    indicador sempre parece útil e é o que faz ninguém olhar para nenhum.
    """
    n = len(cartoes)
    # `cols` quebra os cartões em linhas: quatro numa linha de meia coluna viram letra miúda
    # no celular. Sem ele, todos numa linha só, como sempre foi.
    cols = cols or n
    cw = larg / cols
    linhas = -(-n // cols)
    alt = 128 * linhas
    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="Quatro indicadores macro" xmlns="http://www.w3.org/2000/svg">']
    for k, c in enumerate(cartoes):
        x, y0 = (k % cols) * cw, (k // cols) * 128
        if k % cols:
            p.append(f'<line x1="{x:.1f}" y1="{y0+14}" x2="{x:.1f}" y2="{y0+128-14}" stroke="{GRADE}" stroke-width="1"/>')
        cor = c.get('cor', INK)
        p.append(f'<text x="{x+22:.1f}" y="{y0+34}" font-size="11" fill="{TXT}" '
                 f'text-transform="uppercase">{esc(c["rotulo"])}</text>')
        p.append(f'<text x="{x+22:.1f}" y="{y0+78}" font-size="38" font-weight="700" fill="{cor}" '
                 f'letter-spacing="-0.02em">{esc(c["valor"])}</text>')
        if c.get('unidade'):
            p.append(f'<text x="{x+26+len(str(c["valor"]))*21:.1f}" y="{y0+78}" font-size="14" fill="{TXT}">{esc(c["unidade"])}</text>')
        p.append(f'<text x="{x+22:.1f}" y="{y0+102}" font-size="11.5" fill="{TXT}">{esc(c["regua"])}</text>')
    p.append('</svg>')
    return '\n'.join(p)


# --------------------------------------------------------------- painel de pizzas

def _fatias(cx, cy, r, itens, tons, p, destaque=0):
    ang = -math.pi / 2
    total = max(sum(v for _, v in itens), 1)
    for k, (nome, v) in enumerate(itens):
        da = 2 * math.pi * v / total
        if da <= 0:
            continue
        x1, y1 = cx + r * math.cos(ang), cy + r * math.sin(ang)
        x2, y2 = cx + r * math.cos(ang + da), cy + r * math.sin(ang + da)
        grande = 1 if da > math.pi else 0
        cor = AMBAR if k == destaque else tons[k % len(tons)]
        if abs(da - 2 * math.pi) < 1e-9:
            p.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{cor}"/>')
        else:
            p.append(f'<path d="M{cx:.1f},{cy:.1f} L{x1:.1f},{y1:.1f} A{r},{r} 0 {grande},1 '
                     f'{x2:.1f},{y2:.1f} Z" fill="{cor}" stroke="#ffffff" stroke-width="1.5"/>')
        ang += da


def pizzas(perspectivas, larg=CHEIA, cols=3):
    """Uma pizza por pergunta, cada uma com poucas fatias e uma dominante.

    É o único desenho de pizza que a trilha aprova: a lição g-0.2 delimita o uso dela a
    poucas fatias com uma claramente dominante, e é justamente isso que cada recorte aqui
    entrega. Acima de cinco fatias, ou sem dominante, a forma certa é a barra ordenada.

    O nome e o valor vão ao lado da própria pizza, o que dispensa a legenda de canto, e a
    fatia que a pergunta defende leva a cor.
    """
    tons = ['#cecece', '#bdbdbd', '#bdbdbd', '#969696', '#969696']
    linhas = -(-len(perspectivas) // cols)
    cw, ch = larg / cols, 176
    alt = linhas * ch + 26
    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="Uma pizza por recorte, cada uma com poucas fatias" '
         f'xmlns="http://www.w3.org/2000/svg">']
    for k, persp in enumerate(perspectivas):
        itens = [(n, v) for n, v in persp['itens'] if v > 0]
        if not itens:
            continue
        cx0, cy0 = (k % cols) * cw, (k // cols) * ch
        total = sum(v for _, v in itens)
        r, cx, cy = 42, cx0 + 56, cy0 + 88
        p.append(f'<text x="{cx0+12:.1f}" y="{cy0+24:.0f}" font-size="11.5" font-weight="600" fill="{INK}">{esc(persp["titulo"])}</text>')
        _fatias(cx, cy, r, itens, tons, p, persp.get('destaque', 0))
        ty = cy - (len(itens) - 1) * 8 - 2
        for j, (nome, v) in enumerate(itens):
            cor = AMBAR if j == persp.get('destaque', 0) else MUTE
            p.append(f'<rect x="{cx+r+12:.1f}" y="{ty+j*16-8:.1f}" width="8" height="8" fill="{cor}"/>')
            p.append(f'<text x="{cx+r+25:.1f}" y="{ty+j*16:.1f}" font-size="10.5" fill="{INK}">'
                     f'{esc(nome)} <tspan font-weight="600">{v}</tspan> '
                     f'<tspan fill="{TXT}">{v/total*100:.0f}%</tspan></text>')
    p.append(f'<text x="0" y="{alt-6}" font-size="10.5" fill="{TXT}">'
             f'cada recorte tem poucas fatias e uma dominante, que é o uso estreito que a pizza aguenta</text>')
    p.append('</svg>')
    return '\n'.join(p)


def fora_da_faixa(valores, k=1.5):
    """Separa o corpo dos dados dos pontos extremos, pela regra de Tukey.

    Corte em Q3 mais `k` vezes o intervalo entre quartis, que é a regra publicada e não um
    número escolhido para o desenho ficar bonito. Devolve (corpo, extremos, corte).

    **O extremo não some.** Ele sai do eixo e é contado na nota, porque um ponto de 63 dias
    numa série de mediana 8 é a informação mais cara do gráfico. O que a regra evita é o
    eixo inteiro se esticar para caber um caso e achatar os outros cento e poucos.
    """
    if len(valores) < 8:
        return list(valores), [], None
    v = sorted(valores)
    q = lambda f: v[min(int(round((len(v) - 1) * f)), len(v) - 1)]
    q1, q3 = q(.25), q(.75)
    corte = q3 + k * (q3 - q1)
    corpo = [x for x in v if x <= corte]
    extremos = [x for x in v if x > corte]
    if not corpo:
        return list(v), [], None
    return corpo, extremos, corte


# --------------------------------------------------- tira de pontos (distribuição)

def tira_pontos(valores, larg=MEIA, unidade='dias', rotulo='cada ponto é um caso',
                posicao='na posição do seu valor em'):
    """Um ponto por caso, num eixo só, com as réguas da mediana e do P90.

    A faixa do histograma decide por quem lê: dois casos de 14,9 e 15,1 dias caem em
    baldes diferentes e parecem distantes. A tira mostra onde os casos se amontoam de
    verdade, e é a forma honesta quando o dado se concentra.
    """
    if not valores:
        return ''
    todos = sorted(valores)
    perc_t = lambda k: todos[min(int(round((len(todos) - 1) * k)), len(todos) - 1)]
    # mediana e P90 saem de TODOS os casos, inclusive os extremos: quem sai é o eixo, e
    # não o dado. Tirar o extremo da estatística mentiria sobre a cauda da distribuição.
    mediana, p90 = perc_t(.5), perc_t(.9)
    v, extremos, _corte = fora_da_faixa(todos)
    esq, dirm, cima = 42, 30, 56
    w = larg - esq - dirm
    # o eixo tem de caber as DUAS réguas, senão a mediana ou o P90 são desenhados fora da
    # tela: elas saem de todos os casos, e o eixo sai só do corpo
    topo = max(max(v), mediana, p90) * 1.08 or 1
    X = lambda x: esq + w * x / topo

    # A pilha é medida ANTES de desenhar: com os casos nascidos quase todos no mesmo dia,
    # uma coluna sozinha pode ter dezenas de pontos e transbordar a tela. O espaçamento e a
    # altura saem da pilha mais alta, e não de um número escolhido a esmo.
    passo = max(topo / 60, 1e-9)
    pilhas = {}
    for x in v:
        k = int(x / passo)
        pilhas[k] = pilhas.get(k, 0) + 1
    mais_alta = max(pilhas.values())
    espaco = min(6.5, max(2.2, 150 / mais_alta))
    alt = int(cima + 46 + 40 + min(mais_alta * espaco, 160))
    eixo_y = alt - 54

    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="Uma tira de pontos: cada ponto é um caso, na posição do seu valor" '
         f'xmlns="http://www.w3.org/2000/svg">']
    p.append(f'<line x1="{esq}" y1="{eixo_y}" x2="{esq+w:.1f}" y2="{eixo_y}" stroke="{GRADE}" stroke-width="1"/>')
    for t in range(3):
        x = topo * t / 2
        p.append(f'<line x1="{X(x):.1f}" y1="{eixo_y-4}" x2="{X(x):.1f}" y2="{eixo_y+4}" stroke="{GRADE}" stroke-width="1"/>')
        p.append(f'<text x="{X(x):.1f}" y="{eixo_y+18}" text-anchor="middle" font-size="10" fill="{TXT}">{x:.0f}</text>')

    raio = min(3.0, espaco / 2)
    coluna = {}
    for x in v:
        k = int(x / passo)
        coluna[k] = coluna.get(k, 0) + 1
        cy = eixo_y - 5 - (coluna[k] - 1) * espaco
        cor = ALERTA if x >= p90 else MUTE
        p.append(f'<circle cx="{X(x):.1f}" cy="{cy:.1f}" r="{raio:.1f}" fill="{cor}" opacity=".8"/>')

    for valor, nome, dy in ((mediana, 'mediana', 0), (p90, 'P90', 14)):
        p.append(f'<line x1="{X(valor):.1f}" y1="{18+dy}" x2="{X(valor):.1f}" y2="{eixo_y:.1f}" '
                 f'stroke="{INK}" stroke-width="1.25" stroke-dasharray="5 4" opacity=".5"/>')
        anc = 'end' if X(valor) > larg - 120 else 'start'
        dx = -6 if anc == 'end' else 6
        p.append(f'<text x="{X(valor)+dx:.1f}" y="{26+dy}" text-anchor="{anc}" font-size="10.5" '
                 f'font-weight="600" fill="{INK}">{nome} {valor:.0f} {unidade}</text>')
    nota = f'{esc(rotulo)}, {esc(posicao)} {unidade}'
    if extremos:
        nota += (f' &#183; {len(extremos)} fora da faixa de Tukey, de {min(extremos):.0f} a '
                 f'{max(extremos):.0f} {unidade}, ficaram fora do eixo e dentro da conta')
    # nota longa passava da borda; quebra em duas linhas na virgula mais proxima do meio
    # a nota quebra em quantas linhas precisar, sempre comecando na margem esquerda, e o
    # desenho ja nasceu com 14px a mais de rodape para elas caberem
    cabe = int((larg - 4) / (10 * 0.55))
    linhas_nota, atual = [], ''
    for palavra in nota.split(' '):
        if atual and len(atual) + len(palavra) + 1 > cabe:
            linhas_nota.append(atual)
            atual = palavra
        else:
            atual = f'{atual} {palavra}'.strip()
    if atual:
        linhas_nota.append(atual)
    for k, ln in enumerate(linhas_nota[-2:]):
        y_n = alt - 8 - (len(linhas_nota[-2:]) - 1 - k) * 12
        p.append(f'<text x="0" y="{y_n}" font-size="10" fill="{TXT}">{ln}</text>')
    p.append('</svg>')
    return '\n'.join(p)


# ------------------------------------------------- dispersão de duas medidas (relação)

def dispersao_xy(pontos, rotx, roty, larg=MEIA, nota='', rot_alvo='alto nos dois eixos'):
    """Cada ponto é um caso, posicionado por duas medidas que variam de verdade.

    Sem reta: ela resumiria o movimento conjunto e seria lida como causa. Entram as duas
    medianas, que cortam o desenho em quadrantes e deixam o leitor julgar.
    """
    if not pontos:
        return ''
    alt = 282
    esq, dirm, cima, baixo = 44, 22, 30, 52
    w, h = larg - esq - dirm, alt - cima - baixo
    tx = max(x for x, _ in pontos) * 1.12 or 1
    ty = max(y for _, y in pontos) * 1.12 or 1
    X = lambda v: esq + w * v / tx
    Y = lambda v: cima + h - (v / ty) * h
    med = lambda vs: sorted(vs)[len(vs) // 2]
    mx, my = med([x for x, _ in pontos]), med([y for _, y in pontos])

    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="Dispersão: {esc(rotx)} contra {esc(roty)}" xmlns="http://www.w3.org/2000/svg">']
    _eixo_y(p, esq, larg - dirm, cima, h, ty)
    p.append(f'<line x1="{X(mx):.1f}" y1="{cima}" x2="{X(mx):.1f}" y2="{cima+h:.1f}" stroke="{INK}" '
             f'stroke-width="1" stroke-dasharray="4 4" opacity=".35"/>')
    p.append(f'<line x1="{esq}" y1="{Y(my):.1f}" x2="{larg-dirm}" y2="{Y(my):.1f}" stroke="{INK}" '
             f'stroke-width="1" stroke-dasharray="4 4" opacity=".35"/>')
    caro = 0
    for x, y in pontos:
        alvo = x > mx and y > my
        caro += 1 if alvo else 0
        p.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="3.4" '
                 f'fill="{ALERTA if alvo else MUTE}" opacity="{1 if alvo else .75}"/>')
    p.append(f'<text x="{larg-dirm}" y="{cima+12}" text-anchor="end" font-size="10.5" font-weight="600" '
             f'fill="{ALERTA}">{esc(rot_alvo)}: {caro}</text>')
    for t in range(3):
        v = tx * t / 2
        p.append(f'<text x="{X(v):.1f}" y="{cima+h+17:.1f}" text-anchor="middle" font-size="10" fill="{TXT}">{v:.0f}</text>')
    p.append(f'<text x="{larg-dirm}" y="{cima+h+34:.1f}" text-anchor="end" font-size="10" fill="{TXT}">{esc(rotx)} &#8594;</text>')
    p.append(f'<text x="{esq}" y="{cima+h+34:.1f}" font-size="10" fill="{TXT}">&#8593; {esc(roty)}</text>')
    if nota:
        p.append(f'<text x="{esq}" y="{alt-6}" font-size="10" fill="{TXT}">{esc(nota)}</text>')
    p.append('</svg>')
    return '\n'.join(p)


# ------------------------------------------------------------ linha de taxa (tempo)

def linha_taxa(taxas, rotulos, larg=MEIA, meta=100, rot_meta='empate: fecha o que entra'):
    """Uma taxa ao longo do tempo, com a linha do empate atravessando o desenho.

    As curvas acumuladas respondem quanto. Esta responde em que ritmo, que é outra
    pergunta: acima da linha o time ganha terreno no dia, abaixo dela perde.
    """
    validos = [(i, t) for i, t in enumerate(taxas) if t is not None]
    if not validos:
        return ''
    alt = 268
    esq, dirm, cima, baixo = 44, 70, 28, 44
    w, h = larg - esq - dirm, alt - cima - baixo
    n = len(taxas)
    topo = max([t for _, t in validos] + [meta]) * 1.15 or 1
    X = lambda i: esq + w * i / max(n - 1, 1)
    Y = lambda v: cima + h - (v / topo) * h

    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="Taxa de resolução por período, com a linha do empate" '
         f'xmlns="http://www.w3.org/2000/svg">']
    _eixo_y(p, esq, larg - dirm, cima, h, topo)
    ym = Y(meta)
    p.append(f'<line x1="{esq}" y1="{ym:.1f}" x2="{larg-dirm+4}" y2="{ym:.1f}" stroke="{INK}" '
             f'stroke-width="1.25" stroke-dasharray="5 4" opacity=".55"/>')
    p.append(f'<text x="{larg-dirm+8}" y="{ym-4:.1f}" font-size="10.5" font-weight="600" fill="{INK}">{meta:.0f}%</text>')
    p.append(f'<text x="{larg-dirm+8}" y="{ym+10:.1f}" font-size="9.5" fill="{TXT}">{esc(rot_meta)}</text>')
    for i, t in validos:
        cor = AZ if t >= meta else ALERTA
        p.append(f'<rect x="{X(i)-4:.1f}" y="{min(Y(t),ym):.1f}" width="8" '
                 f'height="{max(abs(Y(t)-ym),1.5):.1f}" fill="{cor}" opacity=".75" rx="1.5"/>')
        p.append(f'<circle cx="{X(i):.1f}" cy="{Y(t):.1f}" r="3" fill="{cor}"/>')
    salto = max(1, n // 6)
    for i, r in enumerate(rotulos):
        if i % salto == 0 or i == n - 1:
            p.append(f'<text x="{X(i):.1f}" y="{cima+h+17:.1f}" text-anchor="middle" font-size="10" fill="{TXT}">{esc(r)}</text>')
    p.append(f'<text x="{esq}" y="{alt-6}" font-size="10" fill="{TXT}">'
             f'dia parado fica de fora: sem entrada nem saída, a taxa não existe</text>')
    p.append('</svg>')
    return '\n'.join(p)


# ------------------------------------------------- matriz de quadrantes (priorização)

_COMO_LER_QUAD = ('cada ponto é um item, posto pelas duas notas escritas nos eixos; as linhas '
                  'tracejadas são a mediana de cada eixo e dividem o gráfico em quatro '
                  'quadrantes; o nome de cada quadrante diz o que fazer com os itens dele')


def matriz_quadrantes(pontos, rotx, roty, nomes, larg=MEIA, alvo=0, nota=''):
    """Dispersão com os quatro quadrantes nomeados, que é a matriz de priorização.

    A dispersão sozinha mostra onde os casos caem; a matriz diz o que fazer com cada canto.
    `nomes` vem na ordem em que se lê um plano cartesiano: [alto-x alto-y, baixo-x alto-y,
    alto-x baixo-y, baixo-x baixo-y]. `alvo` é o índice do quadrante que a pergunta defende,
    e é o único que leva cor.

    O corte é a mediana de cada eixo, e não um valor redondo escolhido a esmo: com nota em
    Fibonacci, um corte fixo em 5 jogaria metade da carteira num canto só.
    """
    if not pontos:
        return ''
    alt = 300
    esq, dirm, cima, baixo = 40, 20, 24, 56
    w, h = larg - esq - dirm, alt - cima - baixo
    tx = max(x for x, _ in pontos) * 1.1 or 1
    ty = max(y for _, y in pontos) * 1.1 or 1
    X = lambda v: esq + w * v / tx
    Y = lambda v: cima + h - (v / ty) * h
    med = lambda vs: sorted(vs)[len(vs) // 2]
    mx, my = med([x for x, _ in pontos]), med([y for _, y in pontos])
    quad = lambda x, y: (0 if x > mx else 1) if y > my else (2 if x > mx else 3)

    contas = [0, 0, 0, 0]
    for x, y in pontos:
        contas[quad(x, y)] += 1

    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="Matriz de priorização: {esc(rotx)} contra {esc(roty)}, quatro quadrantes nomeados" '
         f'xmlns="http://www.w3.org/2000/svg">']
    p.append(f'<rect x="{esq}" y="{cima}" width="{w:.1f}" height="{h:.1f}" fill="none" stroke="{GRADE}" stroke-width="1"/>')
    p.append(f'<line x1="{X(mx):.1f}" y1="{cima}" x2="{X(mx):.1f}" y2="{cima+h:.1f}" stroke="{INK}" '
             f'stroke-width="1" stroke-dasharray="4 4" opacity=".3"/>')
    p.append(f'<line x1="{esq}" y1="{Y(my):.1f}" x2="{esq+w:.1f}" y2="{Y(my):.1f}" stroke="{INK}" '
             f'stroke-width="1" stroke-dasharray="4 4" opacity=".3"/>')

    # o rótulo de cada canto fica NO canto, e não numa legenda: assim o olho lê o nome
    # do quadrante no mesmo movimento em que vê os pontos dele
    cantos = [(esq + w - 6, cima + 14, 'end'), (esq + 6, cima + 14, 'start'),
              (esq + w - 6, cima + h - 8, 'end'), (esq + 6, cima + h - 8, 'start')]
    # so ha destaque quando o quadrante que a pergunta defende tem ponto dentro: laranja
    # sobre um canto vazio aponta para lugar nenhum, e ai o desenho inteiro fica verde
    ha_destaque = contas[alvo] > 0
    for k, (nome, (cx, cy, anc)) in enumerate(zip(nomes, cantos)):
        cor = ALERTA if (k == alvo and ha_destaque) else TXT
        p.append(f'<text x="{cx:.1f}" y="{cy:.1f}" text-anchor="{anc}" font-size="10" '
                 f'font-weight="{700 if (k == alvo and ha_destaque) else 600}" fill="{cor}" letter-spacing=".04em">'
                 f'{esc(nome)} <tspan font-weight="400">{contas[k]}</tspan></text>')

    for x, y in pontos:
        k = quad(x, y)
        eh = k == alvo and ha_destaque
        p.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="3.4" '
                 f'fill="{ALERTA if eh else VERDE}" opacity="{1 if eh else .6}"/>')

    p.append(f'<text x="{esq+w:.1f}" y="{cima+h+18:.1f}" text-anchor="end" font-size="10" fill="{TXT}">{esc(rotx)} &#8594;</text>')
    p.append(f'<text x="{esq}" y="{cima+h+18:.1f}" font-size="10" fill="{TXT}">&#8593; {esc(roty)}</text>')
    p.append(f'<text class="leitura" x="{esq}" y="{alt-8}" font-size="10" fill="{TXT}">'
             f'{esc(nota) if nota else _COMO_LER_QUAD}</text>')
    p.append('</svg>')
    return '\n'.join(p)


# ------------------------------------------------------ progresso por frente (parte do todo)

def _conta_progresso(fe, tot):
    return f'{fe} concluídas de {tot}, {tot-fe} em aberto'


_TXT_PROGRESSO = {'aria': 'Progresso de cada frente: parte concluída sobre o total',
                  'conta': _conta_progresso, 'vazio': 'sem item ainda'}


def progresso(itens, larg=CHEIA, alvo=100, textos=None):
    """Uma barra por frente: a pista clara é o total, a parte cheia é o que já concluiu.

    É a forma de bullet: valor medido contra um alvo, na mesma linha. A pista inteira dá o
    denominador, que é o que falta numa barra de porcentagem solta, e a linha do alvo
    ancora a comparação entre frentes de tamanhos muito diferentes.

    `itens` vem como (nome, fechadas, total), e a ordem do desenho é a do percentual.
    """
    T = _t(_TXT_PROGRESSO, textos)
    if not itens:
        return ''
    # frente sem item fica, com a pista vazia: ele e uma frente que existe e nao comecou
    itens = sorted(itens, key=lambda x: -(x[1] / x[2]) if x[2] else 1)
    # A moldura cresce para ocupar a altura que o cartão reserva. Com três frentes e passo
    # fixo o desenho terminava em 176 de altura dentro de uma caixa de 300, e sobrava uma
    # faixa vazia embaixo maior que o próprio gráfico.
    esq = 150 if larg <= MEIA else 190
    dirm, cima = 74, 26
    alvo_alt = 300 if larg <= MEIA else 360
    passo = max(40, (alvo_alt - cima - 30) / max(len(itens), 1))
    altb = min(28, max(17, passo - 22))
    w = larg - esq - dirm
    alt = cima + len(itens) * passo + 16
    # Empate divide o destaque: se três frentes estão em 100%, os três ganham a cor. Pintar
    # só o primeiro diria que ele se destaca dos outros, e o dado diz que não.
    com_total = [k for k in range(len(itens)) if itens[k][2]]
    top = max(com_total, key=lambda k: itens[k][1] / itens[k][2], default=None)
    # compara em inteiros: 38/38 e 11/11 empatam sem depender de arredondamento
    lideres = {k for k in com_total
               if itens[k][1] * itens[top][2] == itens[top][1] * itens[k][2]}

    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="{esc(T["aria"])}" '
         f'xmlns="http://www.w3.org/2000/svg">']
    p.append(f'<line x1="{esq+w:.1f}" y1="{cima-8}" x2="{esq+w:.1f}" y2="{alt-26}" '
             f'stroke="{INK}" stroke-width="1" stroke-dasharray="4 3" opacity=".45"/>')
    p.append(f'<text x="{esq+w:.1f}" y="{cima-14}" text-anchor="middle" font-size="10" '
             f'fill="{TXT}">{alvo}%</text>')
    for k, (nome, fe, tot) in enumerate(itens):
        y = cima + k * passo
        pct = fe / tot * 100 if tot else 0
        cor = AMBAR if k in lideres else MUTE
        # nome maior que a goteira era desenhado para fora da tela, pela esquerda
        cabe = int((esq - 16) / (11 * 0.55))
        curto = nome if len(nome) <= cabe else nome[:cabe - 1].rstrip() + '…'
        p.append(f'<text x="{esq-12}" y="{y+altb-4:.0f}" text-anchor="end" font-size="11" '
                 f'fill="{INK}">{esc(curto)}</text>')
        p.append(f'<rect x="{esq}" y="{y:.0f}" width="{w:.1f}" height="{altb:.0f}" fill="{GRADE}" rx="2"/>')
        if fe:
            p.append(f'<rect x="{esq}" y="{y:.0f}" width="{w*pct/100:.1f}" height="{altb:.0f}" fill="{cor}" rx="2"/>')
        p.append(f'<text x="{esq+w+10:.1f}" y="{y+altb-4:.0f}" font-size="11" font-weight="600" '
                 f'fill="{INK}">{pct:.0f}%</text>')
        p.append(f'<text x="{esq}" y="{y+altb+13}" font-size="9.5" fill="{TXT}">'
                 f'{T["conta"](fe, tot) if tot else T["vazio"]}</text>')
    # sem legenda embaixo: "N concluídas de T" já diz o que é a pista, e com nove frentes a
    # linha a mais empurrava o desenho para baixo do rodapé do slide
    p.append('</svg>')
    return '\n'.join(p)


# ============================== formas de valor: preço, margem, DRE ==============

def br(v, casas=0):
    """Número no jeito brasileiro: 1.234,5. Preço vai em 2 casas, leitura de fator em 4."""
    s = f'{v:,.{casas}f}'
    return s.replace(',', '§').replace('.', ',').replace('§', '.')


def _hachura(pid, cor, fundo='#ffffff', passo=6):
    """Hachura de 45 graus: distingue o que foi CEDIDO do que foi realizado, sem competir
    com o sólido. O padrão vai dentro do próprio SVG, porque o desenho é autocontido."""
    return (f'<defs><pattern id="{pid}" patternUnits="userSpaceOnUse" width="{passo}" '
            f'height="{passo}" patternTransform="rotate(45)">'
            f'<rect width="{passo}" height="{passo}" fill="{fundo}"/>'
            f'<rect width="{passo/2:.1f}" height="{passo}" fill="{cor}"/></pattern></defs>')


def composicao(partes, larg=CHEIA, destaque=None, formato=None, total_rot='do total'):
    """Uma barra só, de 100%, repartida nas linhas que compõem um total.

    É a forma do preço decomposto em custo, despesas, tributos e margem, ou da receita
    decomposta nas linhas da DRE: o comprimento de cada bloco é a parte dele no total, e a
    ordem é a ordem do raciocínio, e não a do tamanho.

    `partes` é uma lista de dicionários com `nome`, `valor` e, opcionais, `hachura` (o
    pedaço FINAL do bloco que foi cedido, na mesma unidade do valor) e `cor`. O bloco que
    a mensagem defende (`destaque`, por nome) leva a cor primária; o resto fica em cinza.
    A parte hachurada tem piso de 6 pixels: sem ele ela desaparece justo no caso pequeno
    que alguém pediu para enxergar.
    """
    partes = [p for p in partes if p.get('valor', 0) > 0]
    if not partes:
        return ''
    fmt = formato or (lambda v: br(v))
    total = sum(p['valor'] for p in partes)
    esq, dirm, y, hh = 4, 4, 34, 38
    w = larg - esq - dirm
    tons = ['#d6d6d6', '#c4c4c4', '#b2b2b2', '#a0a0a0', '#8e8e8e', '#7c7c7c']
    alvo = destaque if destaque is not None else partes[-1]['nome']
    p = [f'<svg viewBox="0 0 {larg} {{ALT}}" width="100%" role="img" '
         f'aria-label="Composição de um total em {len(partes)} partes, numa barra de 100 por cento" '
         f'xmlns="http://www.w3.org/2000/svg">']
    x, rot_linhas = esq, [[], [], []]
    for k, parte in enumerate(partes):
        bw = w * parte['valor'] / total
        eh = parte['nome'] == alvo
        cor = parte.get('cor') or (AMBAR if eh else tons[k % len(tons)])
        ced = min(parte.get('hachura') or 0, parte['valor'])
        cw = max(w * ced / total, 6) if ced else 0
        cw = min(cw, bw)
        if cw:
            pid = f'hach{k}'
            p.append(_hachura(pid, cor))
            p.append(f'<rect x="{x:.1f}" y="{y}" width="{max(bw - cw, 0):.1f}" height="{hh}" fill="{cor}"/>')
            p.append(f'<rect x="{x + bw - cw:.1f}" y="{y}" width="{cw:.1f}" height="{hh}" '
                     f'fill="url(#{pid})" stroke="{cor}" stroke-width="1"/>')
        else:
            p.append(f'<rect x="{x:.1f}" y="{y}" width="{bw:.1f}" height="{hh}" fill="{cor}"/>')
        if k:
            p.append(f'<line x1="{x:.1f}" y1="{y}" x2="{x:.1f}" y2="{y+hh}" stroke="#ffffff" stroke-width="1.5"/>')
        cx = x + bw / 2
        pct = f'{parte["valor"] / total * 100:.1f}%'.replace('.', ',')
        # o nome vai na primeira linha livre abaixo da barra onde ele não encosta no vizinho
        for nivel, ja in enumerate(rot_linhas):
            larg_txt = max(len(parte['nome']) * 11 * 0.55, len(pct) * 11 * 0.62) / 2
            if all(abs(cx - xo) >= larg_txt + mo + 8 for xo, mo in ja):
                ja.append((cx, larg_txt))
                break
        else:
            nivel = 2
        yl = y + hh + 20 + nivel * 34
        if nivel:
            p.append(f'<line x1="{cx:.1f}" y1="{y+hh+2}" x2="{cx:.1f}" y2="{yl-12:.0f}" stroke="{GRADE}" stroke-width="1"/>')
        ax = min(max(cx, esq + larg_txt), larg - dirm - larg_txt)
        p.append(f'<text x="{ax:.1f}" y="{yl:.0f}" text-anchor="middle" font-size="11" '
                 f'fill="{INK}" font-weight="{600 if eh else 400}">{esc(parte["nome"])}</text>')
        p.append(f'<text x="{ax:.1f}" y="{yl+14:.0f}" text-anchor="middle" font-size="11" '
                 f'font-weight="600" fill="{cor if eh else TXT}">{pct}</text>')
        if ced:
            p.append(f'<text x="{min(x + bw, larg - dirm):.1f}" y="{y-8}" text-anchor="end" font-size="10.5" '
                     f'fill="{TXT}">hachurado: {esc(fmt(ced))} cedido</text>')
        x += bw
    niveis = 1 + max((k for k, ja in enumerate(rot_linhas) if ja), default=0)
    alt = y + hh + 20 + niveis * 34 + 8
    p.append(f'<text x="{esq}" y="{y-8}" font-size="10.5" fill="{TXT}">100% = {esc(fmt(total))} {esc(total_rot)}</text>')
    p.append('</svg>')
    return '\n'.join(p).replace('{ALT}', str(alt), 1)


def desempenho(realizado, cedido=0, meta=100, larg=MEIA, unidade='%', rot_realizado='realizado',
               rot_cedido='cedido', rot_meta='meta'):
    """Uma barra contra a meta: o sólido é o que se realizou, o hachurado é o que foi cedido
    até a meta, e a linha tracejada é a própria meta.

    É a forma da margem realizada contra a planejada: sólido e hachurado juntos fecham na
    meta quando tudo que faltou foi desconto. Sólido que passa da linha é sobrepreço, e
    ganha a cor primária; sólido curto sem hachura é perda que não veio de desconto, e leva
    o alerta.
    """
    topo = max(meta, realizado + cedido, 1) * 1.12
    esq, dirm, y, hh = 4, 70, 40, 56
    w = larg - esq - dirm
    X = lambda v: esq + w * v / topo
    alt = y + hh + 52
    cor = AMBAR if realizado + cedido >= meta * 0.995 else ALERTA
    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="{esc(rot_realizado)} {br(realizado, 1)}{unidade} contra {esc(rot_meta)} de '
         f'{br(meta, 0)}{unidade}" xmlns="http://www.w3.org/2000/svg">']
    p.append(_hachura('hach-ced', cor))
    p.append(f'<rect x="{esq}" y="{y}" width="{w:.1f}" height="{hh}" fill="{GRADE}" rx="2"/>')
    p.append(f'<rect x="{esq}" y="{y}" width="{max(X(realizado) - esq, 1.5):.1f}" height="{hh}" fill="{cor}" rx="2"/>')
    if cedido > 0:
        cw = max(X(realizado + cedido) - X(realizado), 6)
        p.append(f'<rect x="{X(realizado):.1f}" y="{y}" width="{cw:.1f}" height="{hh}" '
                 f'fill="url(#hach-ced)" stroke="{cor}" stroke-width="1"/>')
    xm = X(meta)
    p.append(f'<line x1="{xm:.1f}" y1="{y-10}" x2="{xm:.1f}" y2="{y+hh+8}" stroke="{INK}" '
             f'stroke-width="1.25" stroke-dasharray="4 3" opacity=".6"/>')
    p.append(f'<text x="{xm:.1f}" y="{y-14}" text-anchor="middle" font-size="10.5" fill="{TXT}">'
             f'{esc(rot_meta)} {br(meta, 0)}{unidade}</text>')
    p.append(f'<text x="{esq}" y="{y+hh+24}" font-size="13" font-weight="600" fill="{cor}">'
             f'{esc(rot_realizado)} {br(realizado, 1)}{unidade}</text>')
    if cedido > 0:
        p.append(f'<text x="{min(X(realizado + cedido), larg - 4):.1f}" y="{y+hh+24}" text-anchor="end" '
                 f'font-size="13" fill="{TXT}">{esc(rot_cedido)} {br(cedido, 1)}{unidade}</text>')
    p.append('</svg>')
    return '\n'.join(p)


def ponte(passos, larg=CHEIA, destaque=None, formato=None):
    """Cascata de ponte: de um total a outro, passando pelo que soma e pelo que subtrai.

    É a cascata do preço (preço cheio, menos desconto, menos impostos, igual líquido), da
    DRE (receita bruta até o resultado) ou de uma variação de margem entre dois períodos.
    `passos` é uma lista de (rótulo, valor, tipo), com tipo `total`, `mais` ou `menos`; o
    valor de `menos` vem positivo. Um `total` depois do primeiro é conferido contra a conta
    corrente, e a diferença derruba o desenho: ponte que não fecha é erro de dado.

    Totais em preto, degraus em cinza, e a cor entra uma vez, no degrau que a mensagem
    defende (`destaque`, por rótulo).
    """
    if not passos:
        return ''
    fmt = formato or (lambda v: br(v))
    corr, picos, alturas = 0, [0], []
    for rot, v, tipo in passos:
        if tipo == 'total':
            if alturas and abs(v - corr) > max(abs(corr), 1) * 1e-6:
                raise ValueError(f'a ponte não fecha em "{rot}": a conta dá {corr}, o total diz {v}')
            base, topo_b, corr = 0, v, v
        elif tipo == 'mais':
            base, topo_b, corr = corr, corr + v, corr + v
        else:
            base, topo_b, corr = corr - v, corr, corr - v
        alturas.append((rot, v, tipo, base, topo_b))
        picos += [base, topo_b]
    topo = max(max(picos), 1) * 1.16
    alt = 300
    esq, dirm, cima, baixo = 52, 12, 30, 52
    w, h = larg - esq - dirm, alt - cima - baixo
    n = len(alturas)
    lb = w / (n * 1.45)
    vao = (w - lb * n) / max(n - 1, 1)
    Y = lambda v: cima + h - (v / topo) * h
    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" '
         f'aria-label="Ponte de {esc(alturas[0][0])} a {esc(alturas[-1][0])}, em {n} passos" '
         f'xmlns="http://www.w3.org/2000/svg">']
    _eixo_y(p, esq, larg - dirm, cima, h, topo)
    x, lig, postos = esq, None, []
    for rot, v, tipo, b, t_ in alturas:
        eh = rot == destaque
        cor = INK if tipo == 'total' else (AMBAR if eh and tipo == 'mais' else
                                            ALERTA if eh else MUTE)
        yy, ht = Y(t_), max(Y(b) - Y(t_), 1.5)
        p.append(f'<rect x="{x:.1f}" y="{yy:.1f}" width="{lb:.1f}" height="{ht:.1f}" fill="{cor}" rx="1.5"/>')
        sinal = '' if tipo == 'total' else ('+' if tipo == 'mais' else '−')
        p.append(f'<text x="{x+lb/2:.1f}" y="{yy-6:.1f}" text-anchor="middle" font-size="11" '
                 f'font-weight="600" fill="{cor if cor != MUTE else INK}">{sinal}{esc(fmt(v))}</text>')
        if _cabe(x + lb / 2, rot, postos, 10):
            p.append(f'<text x="{x+lb/2:.1f}" y="{cima+h+17:.1f}" text-anchor="middle" font-size="10" '
                     f'fill="{TXT}">{esc(rot)}</text>')
        if lig is not None:
            p.append(f'<line x1="{lig[0]:.1f}" y1="{lig[1]:.1f}" x2="{x:.1f}" y2="{lig[1]:.1f}" '
                     f'stroke="#D8D8D8" stroke-width="1"/>')
        lig = (x + lb, Y(t_ if tipo != 'menos' else b))
        x += lb + vao
    p.append('</svg>')
    return '\n'.join(p)
