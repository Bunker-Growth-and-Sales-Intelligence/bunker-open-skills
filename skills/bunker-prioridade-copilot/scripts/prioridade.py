#!/usr/bin/env python3
"""Prioridade pela conta WSJF: nota, ordem, P0 a P3 e três matrizes de quadrantes.

Entrada: um JSON com as demandas e quatro notas por demanda (valor, urgência, risco e
tamanho), cada uma em 1, 2, 3, 5, 8 ou 13.

    python3 prioridade.py demandas.json --saida pasta

Saída: `prioridade.md` (a fila e as matrizes em texto) e `prioridade.html` (as mesmas
matrizes, com a marca da Bunker, para abrir no navegador ou imprimir em PDF). Só biblioteca
padrão do Python 3.8 ou mais novo.

A conta, a escala e a régua P0 a P3 são o método WSJF. Os CORTES dos quadrantes (a partir de
que nota é "alto") são uma convenção desta skill, e se ajustam.
"""
import argparse
import base64
import html as _html
import json
import os
import sys

NOTAS = (1, 2, 3, 5, 8, 13)
CAMPOS = ('valor', 'urgencia', 'risco', 'tamanho')
ROTULO = {'valor': 'valor', 'urgencia': 'urgência', 'risco': 'risco', 'tamanho': 'tamanho'}
CORTES = {'alto': 8, 'facil': 3, 'wsjf_alto': 5}
AQUI = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------------ a conta

def validar(dem):
    """Levanta ValueError se alguma nota existir e estiver fora da escala. Nota ausente é permitida."""
    for c in CAMPOS:
        v = dem.get(c)
        if v is not None and v not in NOTAS:
            raise ValueError(f'"{dem.get("nome", "?")}": nota de {ROTULO[c]} {v} é inválida. '
                             f'Use 1, 2, 3, 5, 8 ou 13.')


def validar_spec(spec):
    if not spec.get('demandas'):
        raise ValueError('o arquivo não tem demandas')
    for dem in spec['demandas']:
        if not dem.get('nome'):
            raise ValueError('toda demanda precisa de um nome')
        validar(dem)


def completa(dem):
    return all(dem.get(c) is not None for c in CAMPOS)


def wsjf(dem):
    """(valor + urgência + risco) ÷ tamanho, com uma casa. Faltando uma nota, não há conta: None."""
    if not completa(dem):
        return None
    return round((dem['valor'] + dem['urgencia'] + dem['risco']) / dem['tamanho'], 1)


def prioridade(w):
    if w is None:
        return 'Sem nota'
    if w >= 8:
        return 'P0'
    if w >= 5:
        return 'P1'
    if w >= 3:
        return 'P2'
    return 'P3'


def ordenar(demandas):
    """Maior WSJF primeiro; no empate, o mais curto; sem nota, no fim."""
    def chave(d):
        w = wsjf(d)
        return (w is None, -(w or 0), d.get('tamanho') or 99)
    return sorted(demandas, key=chave)


def primeira(demandas):
    com_nota = [d for d in ordenar(demandas) if wsjf(d) is not None]
    return com_nota[0] if com_nota else None


# ------------------------------------------------------------------ os quadrantes

def quadrantes(demandas, cortes=None):
    """As três matrizes. Cada demanda cai em exatamente um quadrante de cada matriz.

    Ordem dos quadrantes, como num plano cartesiano: alto-x alto-y, baixo-x alto-y, alto-x
    baixo-y, baixo-x baixo-y. `destaque` é o quadrante de onde sai a primeira tarefa.
    """
    c = dict(CORTES, **(cortes or {}))
    alto = c['alto']
    fila = ordenar(demandas)

    def monta(titulo, pergunta, eixo_x, eixo_y, destaque, nomes, leituras, pertence, precisa):
        qs = {n: {'leitura': l, 'itens': []} for n, l in zip(nomes, leituras)}
        for dem in fila:
            if all(dem.get(k) is not None for k in precisa):
                qs[nomes[pertence(dem)]]['itens'].append(dem)
        return {'titulo': titulo, 'pergunta': pergunta, 'eixo_x': eixo_x, 'eixo_y': eixo_y,
                'destaque': destaque, 'quadrantes': qs}

    def idx(x_alto, y_alto):
        return {(True, True): 0, (False, True): 1, (True, False): 2, (False, False): 3}[(x_alto, y_alto)]

    return {
        'valor_urgencia': monta(
            'Valor × urgência', 'O que sai agora?', 'Valor', 'Urgência', 'Fazer agora',
            ['Fazer agora', 'Armadilha', 'Agendar', 'Estacionar'],
            ['Valor alto e urgente', 'Urgente e de pouco valor', 'Valor alto, pode esperar', 'Nem valor nem urgência'],
            lambda d: idx(d['valor'] >= alto, d['urgencia'] >= alto), ('valor', 'urgencia')),
        'esforco_wsjf': monta(
            'Esforço × WSJF', 'O que sai rápido e rende?', 'Facilidade', 'WSJF', 'Rápido e rende',
            ['Rápido e rende', 'Projeto grande', 'Se sobrar tempo', 'Vale a pena?'],
            ['WSJF alto e pouco esforço', 'WSJF alto e muito trabalho', 'Pouco esforço e WSJF baixo',
             'Muito trabalho e WSJF baixo'],
            lambda d: idx(d['tamanho'] <= c['facil'], wsjf(d) >= c['wsjf_alto']), CAMPOS),
        'valor_risco': monta(
            'Valor × risco', 'O que protege o negócio?', 'Valor', 'Risco reduzido', 'Estratégico',
            ['Estratégico', 'Manutenção', 'Novidade', 'Pouco valor'],
            ['Valor alto e risco grande evitado', 'Tira um risco grande, com pouco valor direto',
             'Traz valor, não reduz risco', 'Não merece lugar na fila'],
            lambda d: idx(d['valor'] >= alto, d['risco'] >= alto), ('valor', 'risco')),
        'sem_nota': [d for d in fila if not completa(d)],
        'cortes': c,
    }


# ------------------------------------------------------------------ a saída

def minuscula_inicial(texto):
    """'Valor alto' vira 'valor alto', mas 'WSJF alto' fica como está."""
    primeira_palavra = texto.split(' ', 1)[0]
    return texto if primeira_palavra.isupper() and len(primeira_palavra) > 1 else texto[:1].lower() + texto[1:]


def fmt(w):
    return '—' if w is None else f'{w:.1f}'.replace('.', ',')


def relatorio_md(spec, cortes=None):
    dem = spec['demandas']
    fila = ordenar(dem)
    q = quadrantes(dem, cortes)
    c = q['cortes']
    out = [f'# {spec.get("titulo", "Minha fila")}', '']
    p = primeira(dem)
    if p:
        out += [f'**A primeira da fila:** {p["nome"]} (WSJF {fmt(wsjf(p))}, {prioridade(wsjf(p))}). '
                f'Ordenou? Faça a primeira até terminar. Só então a segunda.', '']
    out += ['## A fila', '', '| # | Demanda | Valor | Urgência | Risco | Tamanho | WSJF | Prioridade |',
            '|---|---|---|---|---|---|---|---|']
    for i, d in enumerate(fila, 1):
        out.append(f'| {i} | {d["nome"]} | {d.get("valor", "—")} | {d.get("urgencia", "—")} | {d.get("risco", "—")} | '
                   f'{d.get("tamanho", "—")} | {fmt(wsjf(d))} | {prioridade(wsjf(d))} |')
    for chave in ('valor_urgencia', 'esforco_wsjf', 'valor_risco'):
        m = q[chave]
        out += ['', f'## {m["titulo"]}: {m["pergunta"].lower()}', '',
                f'Eixos: {m["eixo_x"]} para a direita, {m["eixo_y"]} para cima. Destaque: **{m["destaque"]}**.', '']
        for nome, qd in m['quadrantes'].items():
            marca = ' (destaque)' if nome == m['destaque'] else ''
            itens = '; '.join(f'{x["nome"]} ({fmt(wsjf(x))})' for x in qd['itens']) or 'nada neste quadrante'
            out.append(f'- **{nome}**{marca}, {minuscula_inicial(qd["leitura"])}: {itens}')
    if q['sem_nota']:
        out += ['', '## Sem nota', '', 'Estas demandas ficaram fora da conta porque falta alguma das quatro notas:', '']
        out += [f'- {x["nome"]}' for x in q['sem_nota']]
    out += ['', '---', '',
            f'Régua: P0 é WSJF 8 ou mais, P1 de 5 a 7,9, P2 de 3 a 4,9 e P3 abaixo de 3. Cortes dos quadrantes '
            f'(convenção da skill, ajustável): nota {c["alto"]} ou mais é alta; tamanho {c["facil"]} ou menos é pouco '
            f'esforço; WSJF {c["wsjf_alto"]} ou mais é alto. As notas são sugestão: quem decide é quem executa.']
    return '\n'.join(out) + '\n'


def _logo():
    caminho = os.path.join(AQUI, '..', 'assets', 'bunker-logo-preto.png')
    if not os.path.exists(caminho):
        return ''
    with open(caminho, 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()


CSS = '''
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"Schibsted Grotesk","Helvetica Neue",Arial,sans-serif;color:#0a0a0a;background:#fff;
 max-width:1100px;margin:0 auto;padding:40px 32px 80px;-webkit-font-smoothing:antialiased}
header{display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #0a0a0a;padding-bottom:18px}
header img{height:30px}header .rot{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:#555;font-weight:600}
h1{font-size:44px;line-height:1.05;font-weight:900;letter-spacing:-.03em;margin:34px 0 10px}
.primeira{background:#0a0a0a;color:#fff;padding:22px 28px;margin:22px 0 8px}
.primeira .k{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:#bdbdbd;font-weight:600}
.primeira .v{font-size:28px;font-weight:800;margin-top:6px;letter-spacing:-.01em}
.primeira .s{color:#cecece;margin-top:4px}
h2{font-size:26px;font-weight:800;letter-spacing:-.02em;margin:46px 0 6px}
.perg{color:#555;margin-bottom:14px}
table{width:100%;border-collapse:collapse;font-size:14px;margin-top:12px}
th{text-align:left;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#969696;padding:6px 8px;border-bottom:2px solid #0a0a0a}
td{padding:9px 8px;border-bottom:1px solid #dddddd;vertical-align:top}td.n{text-align:right;font-variant-numeric:tabular-nums}
.matriz{margin-top:8px}
.wrap{display:grid;grid-template-columns:34px 1fr;grid-template-rows:auto 34px;gap:0 12px}
.grade{grid-column:2;display:grid;grid-template-columns:1fr 1fr;gap:8px}
.q{background:#f4f4f4;padding:16px 20px;min-height:140px}
.q.viva{background:#0a0a0a;color:#fff}
.q .n{font-size:20px;font-weight:900;letter-spacing:-.01em}
.q .l{font-size:12px;color:#969696;margin-top:3px}.q.viva .l{color:#bdbdbd}
.q ul{list-style:none;margin-top:10px}.q li{font-size:14px;line-height:1.35;padding:3px 0 3px 16px;position:relative}
.q li::before{content:"";position:absolute;left:0;top:.62em;width:6px;height:6px;background:#0a0a0a}
.q.viva li::before{background:#fff}.q .vazio{font-size:13px;color:#969696;margin-top:10px}
.eixo-y{grid-column:1;writing-mode:vertical-rl;transform:rotate(180deg);display:flex;align-items:center;justify-content:center}
.eixo-x{grid-column:2;display:flex;align-items:center;justify-content:center}
.eixo-x,.eixo-y{font-size:12px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#555}
.nota{margin-top:34px;font-size:12px;color:#969696;line-height:1.5}
@media print{body{padding:0}.matriz{break-inside:avoid}h2{break-after:avoid}@page{size:A4;margin:16mm}}
'''


def _e(x):
    return _html.escape(str(x), quote=False)


def relatorio_html(spec, cortes=None):
    dem = spec['demandas']
    fila = ordenar(dem)
    q = quadrantes(dem, cortes)
    c = q['cortes']
    logo = _logo()
    p = primeira(dem)
    topo = (f'<div class="primeira"><div class="k">A primeira da fila</div><div class="v">{_e(p["nome"])}</div>'
            f'<div class="s">WSJF {fmt(wsjf(p))} · {prioridade(wsjf(p))}. Ordenou? Faça a primeira até terminar. '
            f'Só então a segunda.</div></div>') if p else ''
    linhas = ''.join(
        f'<tr><td class="n">{i}</td><td>{_e(d["nome"])}</td><td class="n">{d.get("valor", "—")}</td>'
        f'<td class="n">{d.get("urgencia", "—")}</td><td class="n">{d.get("risco", "—")}</td>'
        f'<td class="n">{d.get("tamanho", "—")}</td><td class="n"><b>{fmt(wsjf(d))}</b></td>'
        f'<td>{prioridade(wsjf(d))}</td></tr>' for i, d in enumerate(fila, 1))
    matrizes = []
    for chave in ('valor_urgencia', 'esforco_wsjf', 'valor_risco'):
        m = q[chave]
        caixas = []
        for nome, qd in m['quadrantes'].items():
            itens = ''.join(f'<li>{_e(x["nome"])} <span class="l">WSJF {fmt(wsjf(x))}</span></li>' for x in qd['itens'])
            corpo = f'<ul>{itens}</ul>' if itens else '<p class="vazio">Nada neste quadrante.</p>'
            viva = ' viva' if nome == m['destaque'] else ''
            caixas.append(f'<div class="q{viva}"><div class="n">{_e(nome)}</div><div class="l">{_e(qd["leitura"])}</div>{corpo}</div>')
        # na tela: superior direito, superior esquerdo, inferior direito, inferior esquerdo
        a, b, c3, d4 = caixas
        matrizes.append(
            f'<section class="matriz"><h2>{_e(m["titulo"])}</h2><p class="perg">{_e(m["pergunta"])}</p>'
            f'<div class="wrap"><div class="eixo-y"><span>{_e(m["eixo_y"])} &rarr;</span></div>'
            f'<div class="grade">{b}{a}{d4}{c3}</div>'
            f'<div class="eixo-x"><span>{_e(m["eixo_x"])} &rarr;</span></div></div></section>')
    sem = ''
    if q['sem_nota']:
        sem = ('<h2>Sem nota</h2><p class="perg">Ficaram fora da conta porque falta alguma das quatro notas: '
               + _e('; '.join(x['nome'] for x in q['sem_nota'])) + '.</p>')
    rodape = (f'Régua: P0 é WSJF 8 ou mais, P1 de 5 a 7,9, P2 de 3 a 4,9 e P3 abaixo de 3. Cortes dos quadrantes '
              f'(convenção da skill, ajustável): nota {c["alto"]} ou mais é alta; tamanho {c["facil"]} ou menos é pouco '
              f'esforço; WSJF {c["wsjf_alto"]} ou mais é alto. As notas são sugestão: quem decide é quem executa.')
    img = f'<img src="{logo}" alt="Bunker">' if logo else '<b>Bunker</b>'
    return (f'<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{_e(spec.get("titulo", "Minha fila"))}</title><style>{CSS}</style></head><body>'
            f'<header>{img}<span class="rot">Growth &amp; Sales Intelligence</span></header>'
            f'<h1>{_e(spec.get("titulo", "Minha fila"))}</h1>{topo}'
            f'<h2>A fila</h2><table><thead><tr><th>#</th><th>Demanda</th><th>Valor</th><th>Urgência</th><th>Risco</th>'
            f'<th>Tamanho</th><th>WSJF</th><th>Prioridade</th></tr></thead><tbody>{linhas}</tbody></table>'
            f'{"".join(matrizes)}{sem}<p class="nota">{_e(rodape)}</p></body></html>')


# ------------------------------------------------------------------ linha de comando

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('json')
    ap.add_argument('--saida', default='.')
    ap.add_argument('--corte-alto', type=int, help='nota a partir da qual valor, urgência e risco são altos (padrão 8)')
    ap.add_argument('--corte-facil', type=int, help='tamanho até o qual o esforço é pouco (padrão 3)')
    ap.add_argument('--corte-wsjf', type=float, help='WSJF a partir do qual é alto (padrão 5)')
    a = ap.parse_args()
    try:
        with open(a.json, encoding='utf-8') as f:
            spec = json.load(f)
        validar_spec(spec)
    except (ValueError, OSError) as e:
        print(f'erro: {e}', file=sys.stderr)
        return 2
    cortes = {k: v for k, v in (('alto', a.corte_alto), ('facil', a.corte_facil), ('wsjf_alto', a.corte_wsjf))
              if v is not None}
    os.makedirs(a.saida, exist_ok=True)
    md = relatorio_md(spec, cortes)
    with open(os.path.join(a.saida, 'prioridade.md'), 'w', encoding='utf-8') as f:
        f.write(md)
    with open(os.path.join(a.saida, 'prioridade.html'), 'w', encoding='utf-8') as f:
        f.write(relatorio_html(spec, cortes))
    print(md)
    print(f'Gravado em {os.path.join(a.saida, "prioridade.md")} e {os.path.join(a.saida, "prioridade.html")}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
