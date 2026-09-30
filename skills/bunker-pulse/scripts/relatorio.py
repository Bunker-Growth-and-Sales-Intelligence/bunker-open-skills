#!/usr/bin/env python3
"""O status report em slides, a partir de uma lista de atividades.

A lista chega do jeito que a pessoa tiver (print, planilha, CSV, export do GitHub, do Jira,
do Trello, do Planner, uma lista colada no chat) e a IA a normaliza no formato de
`references/formato.md`. Este script lê só esse formato, e por isso não depende de onde a
lista veio.

    python3 relatorio.py atividades.json --saida relatorio.html
    python3 relatorio.py atividades.json --saida relatorio.html --pdf
    python3 relatorio.py atividades.json --resumo      # só as perguntas e as manchetes

Cada slide só entra quando o dado sustenta: sem prazo não há slide de atraso, sem data de
conclusão não há ritmo de entrega, sem responsável não há carga por pessoa. O terminal diz
o que ficou de fora e por quê.

Só usa a biblioteca padrão do Python. O `--pdf` precisa do Google Chrome; sem ele, o HTML
tem o botão "Salvar em PDF".
"""
import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pulso import paleta  # noqa: E402

BUNKER = ('#0a0a0a', '#b03a2e')
CONCLUIDA, ANDAMENTO, ABERTA, BLOQUEADA, CANCELADA = (
    'concluida', 'andamento', 'aberta', 'bloqueada', 'cancelada')
STATUS_NOME = {CONCLUIDA: 'concluída', ANDAMENTO: 'em andamento', ABERTA: 'não começou',
               BLOQUEADA: 'bloqueada', CANCELADA: 'cancelada'}
TETO_CATEGORIAS = 8
TETO_NOME = 17          # o que cabe na calha do gráfico de barras, no slide


# ------------------------------------------------------------------ leitura e normalização

def _sem_acento(t):
    return ''.join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn')


# O status canônico é decisão da IA que leu a lista, e vem no campo `status`. Esta tabela é
# a rede de segurança para o que chegou cru: ela nunca chuta, e o que não reconhece vira
# "aberta" com aviso no terminal.
_PALAVRAS = [
    (CANCELADA, ('cancel', 'descart', "won't", 'wont do', 'fora de escopo', 'descop')),
    (CONCLUIDA, ('conclu', 'done', 'closed', 'fechad', 'finaliz', 'entregue', 'feito',
                 'complete', 'resolvid', 'ok', 'pronto')),
    (BLOQUEADA, ('bloque', 'blocked', 'impedid', 'aguardando', 'esperando', 'waiting',
                 'on hold', 'parad', 'pausad')),
    (ANDAMENTO, ('andamento', 'progress', 'doing', 'fazendo', 'execu', 'desenvolv',
                 'revis', 'review', 'teste', 'homolog', 'iniciad', 'wip')),
    (ABERTA, ('a fazer', 'to do', 'todo', 'backlog', 'pendente', 'aberta', 'aberto', 'open',
              'novo', 'nova', 'nao iniciad', 'planejad', 'vencid', 'atrasad', 'em risco')),
]


def status_canonico(bruto):
    t = _sem_acento(str(bruto or '')).lower().strip()
    if t in (CONCLUIDA, ANDAMENTO, ABERTA, BLOQUEADA, CANCELADA):
        return t, True
    for canon, chaves in _PALAVRAS:
        if any(re.search(r'(^|\W)' + re.escape(k), t) for k in chaves):
            return canon, True
    return ABERTA, False


def data(v):
    """ISO (2026-04-13), ou dd/mm/aaaa. Qualquer outra coisa vira None."""
    if not v:
        return None
    s = str(v).strip()[:10]
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def ler(caminho):
    with open(caminho, encoding='utf-8') as f:
        base = json.load(f)
    EXIBICAO.clear()
    EXIBICAO.update({str(k): str(v) for k, v in (base.get('exibicao') or {}).items()})
    for k, v in EXIBICAO.items():
        if len(v) > TETO_NOME:
            print(f'aviso: nome curto "{v}" passa de {TETO_NOME} caracteres e pode ser cortado',
                  file=sys.stderr)
    hoje = data(base.get('medido_em')) or dt.date.today()
    avisos, itens = [], []
    for k, a in enumerate(base.get('atividades', []), 1):
        st, reconhecido = status_canonico(a.get('status'))
        if not reconhecido:
            avisos.append(f'status "{a.get("status")}" de "{a.get("titulo", k)}" não '
                          f'reconhecido: contou como aberta')
        itens.append({
            'id': str(a.get('id') or k),
            'titulo': str(a.get('titulo') or f'Atividade {k}').strip(),
            'frente': (str(a.get('frente')).strip() if a.get('frente') else None),
            'status': st,
            'responsavel': (str(a.get('responsavel')).strip() if a.get('responsavel') else None),
            'tipo': (str(a.get('tipo')).strip() if a.get('tipo') else None),
            'prioridade': (str(a.get('prioridade')).strip() if a.get('prioridade') else None),
            'criada_em': data(a.get('criada_em')),
            'inicio': data(a.get('inicio')),
            'prazo': data(a.get('prazo')),
            'concluida_em': data(a.get('concluida_em')),
            'link': a.get('link'),
        })
    return base, hoje, itens, avisos


# ------------------------------------------------------------------ português

def n_de(n, sing, plur):
    return f'{n} {sing if n == 1 else plur}'


def lista_nomes(nomes):
    nomes = list(nomes)
    if len(nomes) <= 1:
        return ''.join(nomes)
    return ', '.join(nomes[:-1]) + ' e ' + nomes[-1]


def br_data(d):
    return d.strftime('%d/%m/%Y') if d else ''


_CONECTIVOS = {'e', 'de', 'da', 'do', 'das', 'dos', 'com', 'para', 'a', 'o', 'em', 'no', 'na',
               '-', '–', '/', '&', 'and', 'of', 'the', 'y', 'del'}


EXIBICAO = {}           # nome completo -> nome curto, vindo de `exibicao` no registro


def curto(nome, teto=TETO_NOME):
    """O nome que cabe no espaço, cortado em palavra inteira e sem reticência.

    O corte nunca termina em conectivo nem em pontuação: "Governança e" ou "perfis," dizem
    menos que a palavra seguinte cortada, e parecem erro de quem escreveu.
    """
    nome = ' '.join(str(nome).split())
    if teto == TETO_NOME and nome in EXIBICAO:
        return EXIBICAO[nome]
    if len(nome) <= teto:
        return nome
    palavras = []
    for p in nome.split():
        if len(' '.join(palavras + [p])) > teto:
            break
        palavras.append(p)
    while palavras and (palavras[-1].lower().strip(',;:.') in _CONECTIVOS or not palavras[-1].strip(',;:.-–/')):
        palavras.pop()
    return ' '.join(palavras).rstrip(',;:.-–/ ') or nome[:teto]


def agrupar(pares, rotulo_resto='Outras'):
    """No máximo oito categorias: as sete maiores e o resto somado, com o tamanho escrito."""
    pares = sorted(pares, key=lambda kv: -kv[1])
    if len(pares) <= TETO_CATEGORIAS:
        return pares
    cima, resto = pares[:TETO_CATEGORIAS - 1], pares[TETO_CATEGORIAS - 1:]
    return cima + [(f'{rotulo_resto} ({len(resto)})', sum(v for _, v in resto))]


# ------------------------------------------------------------------ cor

def _hex(c):
    c = c.strip().lstrip('#')
    if len(c) == 3:
        c = ''.join(x * 2 for x in c)
    if not re.fullmatch(r'[0-9a-fA-F]{6}', c):
        raise ValueError(c)
    return '#' + c.lower()


def clarear(c, quanto=.55):
    c = _hex(c)
    r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
    r, g, b = (round(x + (255 - x) * quanto) for x in (r, g, b))
    return f'#{r:02x}{g:02x}{b:02x}'


def definir_cores(base):
    """A cor viva é a de quem recebe o relatório. Sem preferência, preto e vermelho da Bunker,
    com a moldura e o contexto nos cinzas claros da casa."""
    c = base.get('cores') or {}
    try:
        p = _hex(c['primaria']) if c.get('primaria') else BUNKER[0]
        s = _hex(c['secundaria']) if c.get('secundaria') else BUNKER[1]
    except ValueError as e:
        print(f'aviso: cor "{e}" ilegível; saiu com a cor da Bunker', file=sys.stderr)
        p, s = BUNKER
    clara = _hex(c['clara']) if c.get('clara') else clarear(p)
    paleta.definir_marca(p, s, clara)
    return p, s


# ------------------------------------------------------------------ os blocos

def montar(base, hoje, itens):
    from pulso import formas
    from pulso.paleta import MEIA, CHEIA

    fonte_nome = base.get('fonte') or 'lista de atividades enviada'
    quando = br_data(hoje)
    ativos = [a for a in itens if a['status'] != CANCELADA]
    feitos = [a for a in ativos if a['status'] == CONCLUIDA]
    faltam = [a for a in ativos if a['status'] != CONCLUIDA]
    com_prazo = [a for a in ativos if a['prazo']]
    atrasados = [a for a in faltam if a['prazo'] and a['prazo'] < hoje]
    total = len(ativos)
    fora, blocos = [], []

    def fonte(recorte):
        return f'Fonte: {html.escape(fonte_nome)} &#183; {recorte} &#183; medido em {quando}'

    def bloco(chave, grupo, pergunta, manchete, desenho, recorte):
        blocos.append({'chave': chave, 'grupo': grupo, 'pergunta': pergunta,
                       'manchete': manchete, 'desenho': desenho, 'fonte': fonte(recorte)})

    if not total:
        raise SystemExit('nenhuma atividade ativa na lista')

    # 1. quatro números
    pct = round(len(feitos) / total * 100)
    cartoes = [
        {'rotulo': 'ATIVIDADES', 'valor': str(total),
         'regua': f'{n_de(len(itens) - total, "cancelada fora", "canceladas fora")} da conta'
         if len(itens) > total else 'todas as da lista'},
        {'rotulo': 'CONCLUÍDAS', 'valor': f'{pct}%', 'cor': paleta.PRIMARIA,
         'regua': f'{len(feitos)} de {total}'},
        {'rotulo': 'EM ANDAMENTO', 'valor': str(sum(a['status'] == ANDAMENTO for a in ativos)),
         'regua': f'{n_de(sum(a["status"] == BLOQUEADA for a in ativos), "bloqueada", "bloqueadas")} à parte'},
    ]
    if com_prazo:
        cartoes.append({'rotulo': 'ATRASADAS', 'valor': str(len(atrasados)),
                        'cor': paleta.SECUNDARIA if atrasados else paleta.INK,
                        'regua': f'prazo vencido, de {len(faltam)} que faltam'})
    else:
        cartoes.append({'rotulo': 'FALTAM', 'valor': str(len(faltam)),
                        'regua': 'nenhuma atividade tem prazo'})
    if atrasados:
        m = (f'{pct}% concluído: {len(feitos)} de {total} atividades, e '
             f'{n_de(len(atrasados), "está atrasada", "estão atrasadas")}.')
    else:
        m = f'{pct}% concluído: {len(feitos)} de {total} atividades, sem nenhuma atrasada.' \
            if com_prazo else f'{pct}% concluído: {len(feitos)} de {total} atividades.'
    bloco('numeros', 'Onde estamos', 'Como está o projeto, em quatro números?', m,
          formas.kpis(cartoes, MEIA, cols=2), f'{total} atividades ativas')

    # 2. entrou e saiu, por semana
    com_criacao = [a for a in ativos if a['criada_em']]
    if len(com_criacao) >= total * .8 and feitos and all(a['concluida_em'] for a in feitos):
        ini = hoje - dt.timedelta(weeks=8)
        semanas = [ini + dt.timedelta(weeks=k) for k in range(8)]
        inicio = sum(1 for a in ativos if a['criada_em'] < ini
                     and not (a['concluida_em'] and a['concluida_em'] < ini))
        entrou = [sum(1 for a in ativos if s <= a['criada_em'] < s + dt.timedelta(weeks=1)) for s in semanas]
        saiu = [sum(1 for a in feitos if s <= a['concluida_em'] < s + dt.timedelta(weeks=1)) for s in semanas]
        if sum(entrou) + sum(saiu):
            fim = inicio + sum(entrou) - sum(saiu)
            ganho = sum(saiu) >= sum(entrou)
            m = (f'O time concluiu {sum(saiu)} das {sum(entrou)} atividades que chegaram em 8 semanas, '
                 f'e o que falta {"caiu" if fim < inicio else "ficou igual" if fim == inicio else "subiu"} '
                 f'de {inicio} para {fim}.')
            if not ganho and fim > inicio:
                m = (f'Chegou mais do que saiu: {sum(entrou)} atividades entraram e {sum(saiu)} foram '
                     f'concluídas em 8 semanas, e o que falta subiu de {inicio} para {fim}.')
            bloco('cascata', 'Onde estamos', 'Estamos dando conta do trabalho que chega?', m,
                  formas.cascata(inicio, entrou, saiu, [s.strftime('%d/%m') for s in semanas],
                                 'semana', MEIA), 'as últimas 8 semanas, por semana')
    else:
        fora.append('entrou e saiu: falta a data de criação ou a de conclusão na maior parte da lista')

    # 3. frentes
    frentes = {}
    for a in ativos:
        f = frentes.setdefault(a['frente'] or 'Sem frente', [0, 0])
        f[1] += 1
        f[0] += a['status'] == CONCLUIDA
    if len(frentes) >= 2:
        pares = sorted(frentes.items(), key=lambda kv: -(kv[1][0] / kv[1][1]))
        # a manchete leva o nome inteiro; só o desenho precisa do nome curto
        prontas = [n for n, (c, t) in pares if c == t]
        proxima = next(((n, c, t) for n, (c, t) in pares if c < t), None)
        if prontas and proxima:
            m = (f'{n_de(len(prontas), "frente já está concluída", "frentes já estão concluídas")}: '
                 f'{lista_nomes(prontas)}. A próxima é {proxima[0]}, com {proxima[1]} de {proxima[2]}.')
        elif prontas:
            m = f'Todas as {len(prontas)} frentes estão concluídas.'
        elif proxima[1]:
            m = (f'Nenhuma frente concluída ainda. A mais adiantada é {proxima[0]}, '
                 f'com {proxima[1]} de {proxima[2]}.')
        else:
            m = 'Nenhuma frente tem atividade concluída ainda.'
        itens_p = [(curto(n), c, t) for n, (c, t) in pares][:TETO_CATEGORIAS]
        bloco('frentes', 'Onde estamos', 'Quais frentes já estão concluídas?', m,
              formas.progresso(itens_p, MEIA), f'{total} atividades em {len(frentes)} frentes')
    else:
        fora.append('frentes: a lista não separa as atividades em frentes')

    # 4. o que falta, por situação
    if faltam:
        cont = {}
        for a in faltam:
            cont[STATUS_NOME[a['status']]] = cont.get(STATUS_NOME[a['status']], 0) + 1
        pares = sorted(cont.items(), key=lambda kv: -kv[1])
        lider, v = pares[0]
        bloq = cont.get('bloqueada', 0)
        empate = [n for n, x in pares if x == v]
        if len(empate) > 1:
            lider = empate
            frase = {'em andamento': f'{v} em andamento', 'não começou': f'{v} que não começaram',
                     'bloqueada': f'{v} bloqueadas'}
            m = (f'O que falta está dividido por igual: '
                 f'{lista_nomes([frase[x] for x in empate])}.')
            if bloq and 'bloqueada' not in empate:
                m = m[:-1] + f', além de {n_de(bloq, "bloqueada", "bloqueadas")}.'
        elif lider == 'não começou':
            m = f'{v} das {len(faltam)} atividades que faltam ainda não começaram.'
        elif lider == 'bloqueada':
            m = f'O que falta está travado: {v} das {len(faltam)} atividades estão bloqueadas.'
        else:
            m = f'O trabalho está andando: {v} das {len(faltam)} atividades que faltam estão em andamento.'
        if bloq and lider != 'bloqueada' and not isinstance(lider, list):
            m = m[:-1] + f', e {n_de(bloq, "está bloqueada", "estão bloqueadas")}.'
        bloco('situacao', 'O que falta', 'O que falta já está sendo feito?', m,
              formas.barras_deitadas(pares, MEIA, destaque=lider,
                                     cor_destaque=paleta.SECUNDARIA if lider == 'bloqueada' else None)
              if not isinstance(lider, list) else formas.barras_deitadas(pares, MEIA, destaque=lider),
              f'{len(faltam)} atividades não concluídas')

    # 5. atrasos por frente
    if atrasados and len(frentes) >= 2:
        cont = {}
        for a in atrasados:
            k = a['frente'] or 'Sem frente'
            cont[k] = cont.get(k, 0) + 1
        pares = agrupar(cont.items())
        lider, v = pares[0]
        empate = [n for n, x in pares if x == v]
        destaque = [curto(n) for n in empate]
        pares = [(curto(n), x) for n, x in pares]
        if len(empate) > 1:
            m = f'{lista_nomes(empate)} dividem os atrasos: {v} cada, de {len(atrasados)} atrasadas.'
        else:
            m = f'{lider} concentra os atrasos: {v} das {len(atrasados)} atividades atrasadas.'
        bloco('atrasos', 'O que falta', 'Onde estão os atrasos?', m,
              formas.barras_deitadas(pares, MEIA, destaque=destaque, cor_destaque=paleta.SECUNDARIA),
              f'{len(atrasados)} atividades com prazo vencido antes de {quando}')
    elif not com_prazo:
        fora.append('atrasos: nenhuma atividade tem prazo')

    # 6. quanto já passou do prazo
    if len(atrasados) >= 5:
        dias = sorted((hoje - a['prazo']).days for a in atrasados)
        # a mesma mediana que o desenho marca, senão a manchete e a régua discordam
        med = dias[min(int(round((len(dias) - 1) * .5)), len(dias) - 1)]
        pior = max(atrasados, key=lambda a: hoje - a['prazo'])
        m = (f'A atrasada típica passou {med} dias do prazo, e a pior, '
             f'{curto(pior["titulo"], 48)}, está {(hoje - pior["prazo"]).days} dias atrasada.')
        bloco('dias', 'O que falta', 'Os atrasos são de dias ou de semanas?', m,
              formas.tira_pontos(dias, MEIA, 'dias', 'cada ponto é uma atividade atrasada',
                                 posicao='na posição dos dias de atraso em'),
              f'{len(atrasados)} atividades atrasadas')

    # 7. responsável
    tem_dono = [a for a in faltam if a['responsavel']]
    if faltam and (tem_dono or any(a['responsavel'] for a in ativos)):
        cont = {}
        for a in faltam:
            k = curto(a['responsavel'] or 'sem responsável')
            cont[k] = cont.get(k, 0) + 1
        pares = agrupar(cont.items(), 'Outras pessoas')
        sem = cont.get('sem responsável', 0)
        pessoas = [(n, v) for n, v in pares if n != 'sem responsável']
        topo = max((v for _, v in pessoas), default=0)
        lideres = [n for n, v in pessoas if v == topo]
        if sem and sem > topo:
            m = f'{sem} das {len(faltam)} atividades que faltam estão sem responsável.'
            dest, cor = 'sem responsável', paleta.SECUNDARIA
        else:
            dest, cor = lideres, None
            if len(lideres) > 1:
                m = f'{lista_nomes(lideres)} dividem a maior carga, com {topo} atividades cada.'
            else:
                m = f'{lideres[0]} está com {topo} das {len(faltam)} atividades que faltam.'
            if sem:
                m = m[:-1] + f', e {n_de(sem, "está", "estão")} sem responsável.'
        bloco('responsaveis', 'O que falta', 'O trabalho que falta está bem distribuído?', m,
              formas.barras_deitadas(pares, MEIA, destaque=dest, cor_destaque=cor),
              f'{len(faltam)} atividades não concluídas, por responsável')
    else:
        fora.append('responsáveis: a lista não diz quem cuida de cada atividade')

    # 8. ritmo de entrega
    com_fim = [a for a in feitos if a['concluida_em']]
    if len(com_fim) >= 3:
        ini = hoje - dt.timedelta(weeks=8)
        semanas = [ini + dt.timedelta(weeks=k) for k in range(8)]
        por = [(s.strftime('%d/%m'), sum(1 for a in com_fim if s <= a['concluida_em'] < s + dt.timedelta(weeks=1)))
               for s in semanas]
        if sum(v for _, v in por):
            a1, a2 = sum(v for _, v in por[:4]), sum(v for _, v in por[4:])
            if a2 > a1:
                m = f'A entrega acelerou: {a2} atividades nas últimas 4 semanas, contra {a1} nas 4 anteriores.'
            elif a2 < a1:
                m = f'A entrega desacelerou: {a2} atividades nas últimas 4 semanas, contra {a1} nas 4 anteriores.'
            else:
                m = f'A entrega está estável: {a2} atividades nas últimas 4 semanas e {a1} nas 4 anteriores.'
            bloco('ritmo', 'O que foi entregue', 'O ritmo de entrega está aumentando?', m,
                  formas.colunas(por, MEIA), 'atividades concluídas nas últimas 8 semanas')
    else:
        fora.append('ritmo de entrega: menos de 3 atividades têm data de conclusão')

    return blocos, fora, atrasados, faltam


def tabela(faltam, hoje):
    """O que segue em aberto, com o atrasado primeiro e o prazo mais antigo no topo."""
    ordem = sorted(faltam, key=lambda a: (a['prazo'] is None, a['prazo'] or dt.date.max))
    cab = '<thead><tr><th>Atividade</th><th>Frente</th><th>Responsável</th><th>Prazo</th><th>Situação</th></tr></thead>'
    linhas = []
    for a in ordem:
        atras = a['prazo'] and a['prazo'] < hoje
        sit = (f'atrasada {(hoje - a["prazo"]).days} dias' if atras else STATUS_NOME[a['status']])
        titulo = html.escape(a['titulo'])
        if a['link']:
            titulo = f'<a href="{html.escape(a["link"])}">{titulo}</a>'
        linhas.append(f'<tr><td>{titulo}</td><td class="nd">{html.escape(a["frente"] or "")}</td>'
                      f'<td class="nd">{html.escape(a["responsavel"] or "sem responsável")}</td>'
                      f'<td class="num">{br_data(a["prazo"])}</td><td>{sit}</td></tr>')
    return f'<table class="abertas">{cab}<tbody>{"".join(linhas)}</tbody></table>'


# ------------------------------------------------------------------ o deck

def deck_html(base, hoje, blocos, faltam, atrasados):
    from pulso import deck
    deck.JA_EXPLICADO.clear()
    manchetes = base.get('manchetes') or {}
    cliente = base.get('cliente') or ''
    projeto = base.get('projeto') or 'Projeto'
    quando = br_data(hoje)
    rot = ' · '.join(x for x in ('STATUS REPORT', html.escape(cliente.upper()),
                                 html.escape(projeto.upper()), quando) if x)
    slides = [deck.capa(
        rot, html.escape(base.get('titulo') or 'Onde o projeto está hoje'),
        html.escape(base.get('subtitulo') or
                    'O que já foi entregue, o que segue em aberto e onde estão os atrasos.'),
        f'Números calculados a partir de {html.escape(base.get("fonte") or "lista de atividades")}, '
        f'sem digitação à mão')]
    pag = 1
    for b in blocos:
        pag += 1
        manchete = manchetes.get(b['chave'], b['manchete'])
        slides.append(deck.slide(b['grupo'], b['pergunta'], manchete, b['desenho'], b['fonte'], pag))
    if faltam:
        apoio = ('As atrasadas primeiro, e depois o que vence antes.' if atrasados
                 else 'Em ordem de prazo, do que vence antes para o que vence depois.')
        mais, pag = deck.slides_tabela(
            tabela(faltam, hoje), pag, por_slide=6, teto=12, titulo='O que continua em aberto',
            rotulo='O que segue aberto', apoio=apoio,
            sobra='Outras {n} atividades, com prazo mais distante, ficaram fora desta lista.',
            fonte=f'Fonte: {html.escape(base.get("fonte") or "lista de atividades")} &#183; medido em {quando}')
        slides += mais
    slides.append(deck.fecho(f'{html.escape(cliente or projeto)} · {quando}'))
    return deck.render(f'Status report · {html.escape(cliente or projeto)}', slides)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('atividades')
    ap.add_argument('--saida', default='relatorio.html')
    ap.add_argument('--pdf', action='store_true', help='gera o PDF pelo Google Chrome')
    ap.add_argument('--resumo', action='store_true', help='só imprime perguntas e manchetes')
    a = ap.parse_args(argv)

    base, hoje, itens, avisos = ler(a.atividades)
    definir_cores(base)
    blocos, fora, atrasados, faltam = montar(base, hoje, itens)
    for x in avisos:
        print('aviso:', x, file=sys.stderr)
    print(f'{len(blocos)} gráficos, medido em {br_data(hoje)}')
    for b in blocos:
        m = (base.get('manchetes') or {}).get(b['chave'], b['manchete'])
        print(f'  [{b["chave"]}] {b["pergunta"]}\n      {m}')
    for x in fora:
        print(f'  fora: {x}')
    if a.resumo:
        return 0
    open(a.saida, 'w', encoding='utf-8').write(deck_html(base, hoje, blocos, faltam, atrasados))
    print(f'relatório: {os.path.abspath(a.saida)}')
    if a.pdf:
        pdf = os.path.splitext(a.saida)[0] + '.pdf'
        try:
            from pulso import saida
            saida.para_pdf(a.saida, pdf)
            print(f'pdf: {os.path.abspath(pdf)}')
        except Exception as e:  # noqa: BLE001
            print(f'aviso: o PDF não saiu ({e.__class__.__name__}). Abra o HTML no Chrome e '
                  f'clique em "Salvar em PDF".', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
