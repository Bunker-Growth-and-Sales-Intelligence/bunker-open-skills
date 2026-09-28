#!/usr/bin/env python3
"""Forma ou audita o preço de um produto ou serviço e emite o DRE da linha.

Só usa a biblioteca padrão do Python 3.8 ou mais novo.

Regras da conta:
- A margem planejada é medida sobre a receita líquida: o preço menos impostos sobre a
  venda, comissão, frete e outras despesas variáveis. É a mesma conta do nível 0 do
  Pricing Designer da Bunker.
- Preço formado em duas etapas:
    Preço = (Custo ÷ (1 − margem %) + despesas variáveis em R$) ÷ (1 − (impostos % + comissão % + frete % + outras %))
- Preço arredonda em 2 casas. Cada linha do DRE arredonda em 4 casas, e as linhas de
  total saem da subtração das linhas já arredondadas. Assim o DRE fecha exato.
- Percentuais entram em pontos: 18 quer dizer 18%.
- A margem planejada é opcional. Sem ela, o script só audita o preço informado.

Exemplos:
    python3 preco.py --custo 8.12 --impostos 13.25 --comissao 3 --frete 2.5 --outras 1 --margem 25
    python3 preco.py --custo 8.12 --impostos 13.25 --comissao 3 --frete 2.5 --outras 1 --margem 25 --preco-atual 13.20 --desconto 10
    python3 preco.py --custo 22.40 --impostos 7.3 --outras 2.2 --preco-atual 29.12 --atividade comercio --hipotese outras
"""

import argparse
import html
import sys
from decimal import Decimal, ROUND_HALF_UP

D = Decimal
CEM = D(100)
ZERO = D(0)

ROTULO_CUSTO = {
    "comercio": ("Custo da mercadoria vendida (CMV)", "o que você pagou pela mercadoria que vendeu"),
    "industria": ("Custo do produto vendido (CPV)", "o que custou fabricar o que você vendeu"),
    "servico": ("Custo do serviço prestado (CSP)", "o que custou prestar o serviço"),
    None: ("Custo do que foi vendido (CMV, CPV ou CSP)", "o que custou a mercadoria, o produto ou o serviço vendido"),
}


def r2(x):
    return x.quantize(D("0.01"), rounding=ROUND_HALF_UP)


def r4(x):
    return x.quantize(D("0.0001"), rounding=ROUND_HALF_UP)


def br(x, casas=2):
    """Formata número no padrão brasileiro: 1.234,56."""
    q = D(1).scaleb(-casas)
    x = x.quantize(q, rounding=ROUND_HALF_UP)
    sinal = "−" if x < 0 else ""
    inteiro, _, frac = f"{abs(x):f}".partition(".")
    grupos = []
    while len(inteiro) > 3:
        grupos.insert(0, inteiro[-3:])
        inteiro = inteiro[:-3]
    grupos.insert(0, inteiro)
    texto = ".".join(grupos)
    if casas:
        texto += "," + frac.ljust(casas, "0")
    return sinal + texto


def rs(x, casas=2):
    if x < 0:
        return "−R$ " + br(-x, casas)
    return "R$ " + br(x, casas)


def pct(x, casas=2):
    return br(x, casas) + "%"


def pp(x):
    """Diferença em pontos percentuais, com sinal nos dois sentidos."""
    return ("+" if x > 0 else "") + br(x) + " p.p."


def rs_sinal(x, casas=4):
    return ("+" if x > 0 else "") + rs(x, casas)


def dec(texto):
    try:
        return D(str(texto).replace(",", "."))
    except Exception:
        raise SystemExit(f"Número inválido: {texto!r}")


def ler_pares(lista):
    """Lê itens NOME=PCT[:base] em um dicionário ordenado."""
    saida = {}
    for item in lista or []:
        if "=" not in item:
            raise SystemExit(f"Use NOME=PERCENTUAL, recebi {item!r}")
        nome, valor = item.split("=", 1)
        base = "preco"
        if ":" in valor:
            valor, base = valor.split(":", 1)
        saida[nome.strip()] = (dec(valor), base.strip())
    return saida


def chave(nome):
    return nome.strip().lower().replace("_", "-")


class Premissas:
    def __init__(self, a):
        self.produto = getattr(a, "produto", None) or "Produto"
        self.unidade = getattr(a, "unidade", None) or "unidade"
        self.qtd = dec(getattr(a, "quantidade", "1"))
        self.custo = dec(a.custo)
        partes = ler_pares(getattr(a, "imposto", None))
        if partes:
            self.impostos = {k: v for k, (v, _) in partes.items()}
        else:
            self.impostos = {"Impostos sobre a venda": dec(getattr(a, "impostos", None) or 0)}
        self.comissao = dec(getattr(a, "comissao", "0"))
        self.comissao_sobre = getattr(a, "comissao_sobre", "bruta")
        self.frete = dec(getattr(a, "frete", "0"))
        self.frete_valor = dec(getattr(a, "frete_valor", "0"))
        self.outras = dec(getattr(a, "outras", "0"))
        self.outras_valor = dec(getattr(a, "outras_valor", "0"))
        m = getattr(a, "margem", None)
        self.margem = None if m in (None, "") else dec(m)
        self.por_fora = ler_pares(getattr(a, "por_fora", None))
        self.atividade = getattr(a, "atividade", None)
        self.hipoteses = {chave(h) for h in (getattr(a, "hipotese", None) or [])}

    @property
    def imposto_total(self):
        return sum(self.impostos.values(), ZERO)

    def comissao_efetiva(self):
        """Comissão em % do preço. Sobre a receita sem ICMS, PIS e Cofins ela encolhe junto com os impostos."""
        if self.comissao_sobre == "liquida":
            return self.comissao * (CEM - self.imposto_total) / CEM
        return self.comissao

    def variaveis_pct(self):
        """Tudo o que sai do preço em %: impostos por dentro, comissão, frete e outras."""
        return self.imposto_total + self.comissao_efetiva() + self.frete + self.outras

    def variaveis_rs(self):
        return self.frete_valor + self.outras_valor

    def hip(self, *nomes):
        return any(chave(n) in self.hipoteses for n in nomes)


def dre(preco, p, custo=None, comissao=None, frete=None, frete_valor=None):
    """DRE da linha a um preço dado. Cada parcela em 4 casas; totais por subtração."""
    q = p.qtd
    custo = p.custo if custo is None else custo
    comissao = p.comissao if comissao is None else comissao
    frete = p.frete if frete is None else frete
    frete_valor = p.frete_valor if frete_valor is None else frete_valor

    rb = r4(preco * q)
    impostos = [(nome, r4(rb * aliq / CEM)) for nome, aliq in p.impostos.items()]
    deducoes = sum((v for _, v in impostos), ZERO)
    rl_contabil = rb - deducoes
    base_com = rl_contabil if p.comissao_sobre == "liquida" else rb
    despesas = [
        ("comissao", r4(base_com * comissao / CEM)),
        ("frete", r4(rb * frete / CEM + frete_valor * q)),
        ("outras", r4(rb * p.outras / CEM + p.outras_valor * q)),
    ]
    desp_total = sum((v for _, v in despesas), ZERO)
    rl = rl_contabil - desp_total
    cpv = r4(custo * q)
    mc = rl - cpv

    avisos = []
    mc_rl = mc_rb = None
    if rb <= 0:
        avisos.append("A receita bruta é zero ou negativa. Não há base para calcular margem em %.")
    elif rl <= 0:
        avisos.append(
            "A receita líquida é zero ou negativa: impostos, comissão e frete levam o preço inteiro. "
            "Margem em % perde sentido nessa situação, então ela não é calculada. "
            "Confira as alíquotas antes de seguir."
        )
    else:
        mc_rl = mc / rl * CEM
        mc_rb = mc / rb * CEM

    fora = []
    icms_iss = sum((v for n, v in impostos if n.strip().upper() in ("ICMS", "ISS")), ZERO)
    for nome, (aliq, base) in p.por_fora.items():
        b = rb - icms_iss if base == "sem_icms_iss" else rb
        fora.append((nome, aliq, base, r4(b * aliq / CEM)))
    nota = rb + sum((v for *_, v in fora), ZERO)

    # Conferência do fechamento em 4 casas
    assert rb - deducoes == rl_contabil
    assert rl_contabil - desp_total == rl
    assert rl - cpv == mc
    assert sum((v for _, v in impostos), ZERO) == deducoes
    assert sum((v for _, v in despesas), ZERO) == desp_total

    return {
        "preco": preco,
        "rb": rb,
        "impostos": impostos,
        "deducoes": deducoes,
        "rl_contabil": rl_contabil,
        "despesas": dict(despesas),
        "desp_total": desp_total,
        "rl": rl,
        "cpv": cpv,
        "mc": mc,
        "mc_rl": mc_rl,
        "mc_rb": mc_rb,
        "fora": fora,
        "nota": nota,
        "avisos": avisos,
    }


def formar(p, margem=None):
    """Preço formado com a margem sobre a receita líquida. None se não existe preço."""
    m = p.margem if margem is None else margem
    if m is None or m >= CEM or p.variaveis_pct() >= CEM:
        return None
    alvo_rl = p.custo / ((CEM - m) / CEM)
    return r2((alvo_rl + p.variaveis_rs()) / ((CEM - p.variaveis_pct()) / CEM))


def margem_maxima(p, preco):
    """A maior margem sobre a receita líquida que cabe num preço dado."""
    rl = preco * (CEM - p.variaveis_pct()) / CEM - p.variaveis_rs()
    if rl <= 0:
        return None
    return (CEM - p.custo / rl * CEM)


def explicar_impossivel(p, preco_ref=None):
    out = ["NÃO EXISTE PREÇO POSSÍVEL COM ESSAS PREMISSAS"]
    v = p.variaveis_pct()
    if v >= CEM:
        comp = [
            ("Impostos sobre a venda", p.imposto_total),
            ("Comissão", p.comissao_efetiva()),
            ("Frete", p.frete),
            ("Outras despesas variáveis", p.outras),
        ]
        comp = sorted((c for c in comp if c[1] > 0), key=lambda c: c[1], reverse=True)
        out.append(
            f"Impostos, comissão, frete e outras despesas somam {pct(v)} do preço. Eles levam o preço inteiro "
            "e não sobra nada para pagar o custo, por mais alto que seja o preço. Nem com margem zero existe preço."
        )
        out.append("Do maior para o menor:")
        for nome, x in comp:
            out.append(f"  {nome}: {pct(x)}")
        out.append(
            f"A soma precisa cair mais de {br(v - CEM)} pontos, e na prática bem mais: perto de 100% o preço "
            "cresce sem limite. Quase sempre é alíquota lançada errada."
        )
    if p.margem is not None and p.margem >= CEM:
        out.append(
            f"A margem planejada é {pct(p.margem)} da receita líquida. Margem de 100% quer dizer custo zero, "
            "então ela tem que ficar abaixo de 100%."
        )
        if v < CEM:
            out.append("Veja o preço com margens menores:")
            for m in (D(50), D(40), D(30)):
                out.append(f"  margem {pct(m)}: preço {rs(formar(p, m))}")
    if preco_ref is not None and preco_ref > 0:
        m_max = margem_maxima(p, preco_ref)
        if m_max is not None and m_max > 0:
            out.append(f"No preço de {rs(preco_ref)}, a maior margem que cabe é {pct(m_max)} da receita líquida.")
        else:
            out.append(f"No preço de {rs(preco_ref)}, a venda não cobre nem o custo e as despesas variáveis.")
    return out


def fmt_margens(d):
    if d["mc_rl"] is None:
        return "% não calculada"
    return f"{pct(d['mc_rl'])} da receita líquida, {pct(d['mc_rb'])} da receita bruta"


def rotulos(p):
    """Rótulo contábil da linha de custo e a explicação simples que vai ao lado."""
    custo_rot, custo_exp = ROTULO_CUSTO.get(p.atividade, ROTULO_CUSTO[None])
    return custo_rot, custo_exp


DESPESAS = [
    ("comissao", "Comissão", "despesa variável de venda", ("comissao",)),
    ("frete", "Frete de entrega", "despesa variável de venda", ("frete", "frete-valor")),
    ("outras", "Outras despesas variáveis de venda", "taxa de cartão, marketplace, embalagem de entrega", ("outras", "outras-valor")),
]


def despesas_visiveis(p, colunas):
    """Esconde a despesa que é zero em todas as colunas (frete zero num serviço, por exemplo)."""
    return [x for x in DESPESAS if any(d["despesas"][x[0]] != 0 for _, _, d in colunas)]


def marca(p, *nomes):
    return " (hipótese)" if p.hip(*nomes) else ""


def bloco_dre(titulo, d, p, visiveis):
    rb = d["rb"]

    def perc(v):
        return "" if rb <= 0 else f"  ({pct(v / rb * CEM)} da RB)"

    custo_rot, _ = rotulos(p)
    qtd = br(p.qtd, 0) if p.qtd == p.qtd.to_integral() else br(p.qtd, 4)
    out = [titulo, f"  Preço por {p.unidade}: {rs(d['preco'])}   Quantidade: {qtd}"]
    w = 58
    out.append(f"  {'Receita bruta':<{w}}{rs(rb, 4)}{perc(rb)}")
    out.append(f"  {'(−) Deduções da receita bruta (impostos sobre a venda)' + marca(p, 'impostos'):<{w}}{rs(d['deducoes'], 4)}{perc(d['deducoes'])}")
    if len(d["impostos"]) > 1:
        for nome, v in d["impostos"]:
            out.append(f"        {nome + marca(p, nome, 'impostos'):<{w - 6}}{rs(v, 4)}")
    out.append(f"  {'(=) Receita líquida contábil (depois das deduções)':<{w}}{rs(d['rl_contabil'], 4)}{perc(d['rl_contabil'])}")
    for k, nome, _, hips in visiveis:
        out.append(f"  {'(−) ' + nome + marca(p, *hips):<{w}}{rs(d['despesas'][k], 4)}{perc(d['despesas'][k])}")
    out.append(f"  {'(=) Receita líquida, base da margem':<{w}}{rs(d['rl'], 4)}{perc(d['rl'])}")
    out.append(f"  {'(−) ' + custo_rot + marca(p, 'custo'):<{w}}{rs(d['cpv'], 4)}{perc(d['cpv'])}")
    out.append(f"  {'(=) Margem de contribuição':<{w}}{rs(d['mc'], 4)}")
    if d["mc_rl"] is not None:
        out.append(f"      em % da receita líquida (base da margem): {pct(d['mc_rl'])}")
        out.append(f"      em % da receita bruta: {pct(d['mc_rb'])}")
    for nome, aliq, base, v in d["fora"]:
        rot = "base sem ICMS e ISS" if base == "sem_icms_iss" else "base no preço"
        out.append(f"  {'(+) ' + nome + ' ' + pct(aliq) + ', por fora (' + rot + ')' + marca(p, nome):<{w}}{rs(v, 4)}")
    if d["fora"]:
        out.append(f"  {'(=) Total da nota':<{w}}{rs(d['nota'], 4)}")
    for a in d["avisos"]:
        out.append("  Atenção: " + a)
    return out


def tabela_dre(p, colunas):
    """A tabela do DRE da linha, uma coluna por preço, com o % da receita bruta ao lado."""
    def e(s):
        return html.escape(str(s))

    hip_tag = "<span class='hip'>hipótese</span>"
    custo_rot, custo_exp = rotulos(p)
    visiveis = despesas_visiveis(p, colunas)
    varias = len(colunas) > 1

    def cel_rs(d, v):
        rb = d["rb"]
        p_ = "" if rb <= 0 else pct(v / rb * CEM)
        return f"<td class='n'>{e(rs(v, 4))}</td><td class='n p'>{e(p_)}</td>"

    linhas = []

    def rot(rotulo, explica, hip):
        r = e(rotulo) + (" " + hip_tag if hip else "")
        if explica:
            r += f"<small>{e(explica)}</small>"
        return r

    def linha(rotulo, pega, cls="", explica="", hip=False):
        tds = "".join(cel_rs(d, pega(d)) for _, _, d in colunas)
        extra = ""
        if varias:
            extra = f"<td class='n'>{e(rs_sinal(pega(colunas[-1][2]) - pega(colunas[0][2])))}</td>"
        linhas.append(f"<tr class='{cls}'><th>{rot(rotulo, explica, hip)}</th>{tds}{extra}</tr>")

    def linha_pct(rotulo, pega, explica=""):
        tds = ""
        for _, _, d in colunas:
            v = pega(d)
            tds += f"<td class='n'>{e('' if v is None else pct(v))}</td><td></td>"
        extra = ""
        if varias:
            a, b = pega(colunas[0][2]), pega(colunas[-1][2])
            extra = f"<td class='n'>{e('' if a is None or b is None else pp(b - a))}</td>"
        linhas.append(f"<tr class='mcp'><th>{rot(rotulo, explica, False)}</th>{tds}{extra}</tr>")

    linha("Receita bruta", lambda d: d["rb"], "tot", "o valor da venda, sem os tributos por fora")
    linha("(−) Deduções da receita bruta", lambda d: d["deducoes"], "",
          "impostos sobre a venda, que vêm dentro do preço", p.hip("impostos"))
    base = colunas[0][2]
    if len(base["impostos"]) > 1:
        for i, (nome, _) in enumerate(base["impostos"]):
            linha(nome, lambda d, i=i: d["impostos"][i][1], "sub", "", p.hip(nome, "impostos"))
    linha("(=) Receita líquida contábil", lambda d: d["rl_contabil"], "tot", "receita bruta menos as deduções")
    for k, nome, explica, hips in visiveis:
        linha("(−) " + nome, lambda d, k=k: d["despesas"][k], "", explica, p.hip(*hips))
    linha("(=) Receita líquida, base da margem", lambda d: d["rl"], "tot",
          "o que sobra do preço depois de impostos, comissão e frete")
    linha("(−) " + custo_rot, lambda d: d["cpv"], "", custo_exp, p.hip("custo"))
    linha("(=) Margem de contribuição", lambda d: d["mc"], "tot mc",
          "o que a venda deixa para as despesas fixas e o lucro; não é lucro")
    linha_pct("Margem em % da receita líquida", lambda d: d["mc_rl"], "a base em que a margem é planejada")
    linha_pct("Margem em % da receita bruta", lambda d: d["mc_rb"], "a mesma margem, medida sobre o preço")
    if base["fora"]:
        linhas.append(f"<tr class='sec'><th colspan='{1 + 2 * len(colunas) + (1 if varias else 0)}'>Fora da receita bruta, somado na nota</th></tr>")
        for i, (nome, aliq, b, _) in enumerate(base["fora"]):
            expl = "base sem ICMS e ISS" if b == "sem_icms_iss" else "sobre o preço"
            linha(f"(+) {nome} {pct(aliq)}", lambda d, i=i: d["fora"][i][3], "", "tributo por fora, " + expl, p.hip(nome))
        linha("(=) Total da nota", lambda d: d["nota"], "tot", "o que o cliente paga")

    cab = "".join(
        f"<th colspan='2'>{e(n)}<br><small>{e(sub)}</small></th>" for n, sub, _ in colunas
    )
    if varias:
        cab += f"<th>{e(colunas[-1][0])} − {e(colunas[0][0].lower())}</th>"
    return (f"<div class='wrap'><table class='dre'><thead><tr><th></th>{cab}</tr></thead><tbody>"
            f"{''.join(linhas)}</tbody></table></div>")


def html_saida(p, colunas, texto, cards):
    """Página só de texto, para quando não existe preço e o simulador não tem o que mostrar."""
    corpo = html.escape(chr(10).join(texto))
    return ("<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'><title>DRE da linha</title>"
            "<style>body{font:15px/1.45 system-ui,sans-serif;margin:0;padding:24px 16px;background:#fff;color:#141414}"
            "@media (prefers-color-scheme: dark){body{background:#121212;color:#eee}}"
            "pre{white-space:pre-wrap;max-width:880px;margin:0 auto}</style></head>"
            f"<body><pre>{corpo}</pre></body></html>")


def cenario_de_args(a, p, preco_atual):
    """Leva os argumentos da linha de comando para o formato de cenário do simulador."""
    linha = {
        "nome": p.produto,
        "quantidade": float(p.qtd),
        "custo": float(p.custo),
        "impostos": {k: float(v) for k, v in p.impostos.items()},
        "comissao": float(p.comissao),
        "comissao_sobre": p.comissao_sobre,
        "frete_pct": float(p.frete),
        "frete_rs": float(p.frete_valor),
        "outras_pct": float(p.outras),
        "outras_rs": float(p.outras_valor),
        "hipoteses": sorted(p.hipoteses),
    }
    if p.por_fora:
        linha["por_fora"] = [{"nome": n, "aliq": float(al), "base": b} for n, (al, b) in p.por_fora.items()]
    if preco_atual is not None:
        linha["preco_especifico"] = float(preco_atual)
        linha["rotulo_especifico"] = "Tabela de hoje"
    if a.desconto:
        linha["desconto"] = float(dec(a.desconto))
    if a.preco_praticado:
        linha["preco_praticado"] = float(dec(a.preco_praticado))
    if a.custo_real:
        linha["custo_real"] = float(dec(a.custo_real))
    cen = {"titulo": p.produto, "unidade": p.unidade, "atividade": p.atividade,
           "rotulos": {"teto": "Planejado"}, "linhas": [linha]}
    if p.margem is not None:
        cen["mc_teto"] = float(p.margem)
    return cen


def comparar(texto, p, de, para, rotulo_de, rotulo_para):
    """Explica a diferença de margem entre dois preços, com o sentido certo."""
    dif = para["rb"] - de["rb"]
    dmc = para["mc"] - de["mc"]
    if dif == 0:
        return
    resto = dif - dmc
    if dif < 0:
        texto.append(
            f"  {rotulo_para} ficou {rs(-dif, 4)} abaixo do {rotulo_de}. Desse valor, {rs(-dmc, 4)} saíram da margem "
            f"({pct(dmc / dif * CEM)}). O resto, {rs(-resto, 4)}, deixou de ir para imposto, comissão e frete, "
            "que caem junto com o preço."
        )
    else:
        texto.append(
            f"  {rotulo_para} ficou {rs(dif, 4)} acima do {rotulo_de}. Desse valor, {rs(dmc, 4)} entraram na margem "
            f"({pct(dmc / dif * CEM)}). O resto, {rs(resto, 4)}, foi para imposto, comissão e frete, "
            "que sobem junto com o preço."
        )


def desvio_de(ref_pct, d):
    """Desvio da margem realizada contra uma margem de referência, como no Pricing Designer.

    Pontos = realizada − referência. Relativo = realizada ÷ referência − 1.
    Em R$ = receita líquida realizada × pontos ÷ 100.
    """
    if ref_pct is None or d["mc_rl"] is None:
        return None
    pts = r4(d["mc_rl"] - ref_pct)
    rel = None if ref_pct == 0 else r4((d["mc_rl"] / ref_pct - 1) * CEM)
    em_rs = r4(d["rl"] * pts / CEM)
    return pts, rel, em_rs


def fmt_desvio(dv):
    pts, rel, em_rs = dv
    rel_txt = "" if rel is None else f", {('+' if rel > 0 else '') + br(rel)}% relativo"
    return f"{pp(pts)}{rel_txt}, {rs_sinal(em_rs)}"


def desvio(texto, rotulo, ref_pct, ref_nome, d):
    dv = desvio_de(ref_pct, d)
    if dv is None:
        texto.append(f"  {rotulo}: em pontos não se calcula, veja o aviso acima.")
        return None
    texto.append(f"  {rotulo} ({pct(ref_pct, 4)}): {fmt_desvio(dv)} na receita líquida realizada")
    return dv


def main(argv=None):
    ap = argparse.ArgumentParser(description="Forma ou audita preço e emite o DRE da linha.")
    ap.add_argument("--produto")
    ap.add_argument("--unidade")
    ap.add_argument("--quantidade", default="1")
    ap.add_argument("--atividade", choices=["comercio", "industria", "servico"],
                    help="dá o nome certo à linha de custo: CMV, CPV ou CSP")
    ap.add_argument("--custo", required=True, help="custo por unidade em R$, já sem os créditos de imposto")
    ap.add_argument("--impostos", help="soma dos impostos sobre a venda, em %%")
    ap.add_argument("--imposto", action="append", help="imposto separado, NOME=PCT (repita)")
    ap.add_argument("--comissao", default="0")
    ap.add_argument("--comissao-sobre", choices=["bruta", "liquida"], default="bruta",
                    help="bruta: sobre a receita bruta (o preço sem IPI). liquida: sobre o preço sem ICMS, PIS e Cofins")
    ap.add_argument("--frete", default="0", help="frete em %% do preço")
    ap.add_argument("--frete-valor", default="0", help="frete em R$ por unidade")
    ap.add_argument("--outras", default="0", help="outras despesas variáveis em %% do preço")
    ap.add_argument("--outras-valor", default="0", help="outras despesas variáveis em R$ por unidade")
    ap.add_argument("--margem", help="margem de contribuição planejada, em %% da receita líquida. Sem ela, só audita")
    ap.add_argument("--preco-atual", help="preço de tabela, o que a pessoa cobra hoje antes do desconto")
    ap.add_argument("--desconto", help="desconto em %% sobre o preço de tabela (ou sobre o formado, sem tabela)")
    ap.add_argument("--preco-praticado", help="preço efetivamente cobrado, já com desconto")
    ap.add_argument("--custo-real")
    ap.add_argument("--comissao-real")
    ap.add_argument("--frete-real")
    ap.add_argument("--frete-valor-real")
    ap.add_argument("--por-fora", action="append", help="tributo por fora, NOME=PCT ou NOME=PCT:sem_icms_iss")
    ap.add_argument("--hipotese", action="append",
                    help="premissa estimada, marcada no texto e na tabela: custo, impostos, NOME do imposto, comissao, frete, outras, margem, desconto, preco-atual (repita)")
    ap.add_argument("--html", help="grava o simulador em HTML nesse caminho e abre no navegador")
    ap.add_argument("--nao-abrir", action="store_true", help="grava o HTML sem abrir o navegador")
    a = ap.parse_args(argv)
    p = Premissas(a)

    preco_atual = dec(a.preco_atual) if a.preco_atual else None
    if p.margem is None and preco_atual is None and not a.preco_praticado:
        ap.error("informe --margem para formar o preço, ou --preco-atual ou --preco-praticado para auditar")

    texto = [f"{p.produto}, por {p.unidade}"]
    texto.append(
        f"Premissas: custo {rs(p.custo, 4)}{marca(p, 'custo')}; impostos por dentro {pct(p.imposto_total)}{marca(p, 'impostos')}; "
        f"comissão {pct(p.comissao)}{marca(p, 'comissao')}"
        + (" sobre o preço sem ICMS, PIS e Cofins" if p.comissao_sobre == "liquida" else "")
        + f"; frete {pct(p.frete)}"
        + (f" + {rs(p.frete_valor)}" if p.frete_valor else "") + marca(p, "frete", "frete-valor")
        + f"; outras {pct(p.outras)}"
        + (f" + {rs(p.outras_valor)}" if p.outras_valor else "") + marca(p, "outras", "outras-valor")
        + ("; sem margem planejada, só auditoria." if p.margem is None
           else f"; margem planejada {pct(p.margem)} da receita líquida{marca(p, 'margem')}.")
    )

    # Planejado
    plan = None
    preco_plan = None
    if p.margem is not None:
        preco_plan = formar(p)
        if preco_plan is None:
            texto += explicar_impossivel(p, preco_atual)
        else:
            v = p.variaveis_pct()
            alvo = p.custo / ((CEM - p.margem) / CEM)
            texto.append("")
            texto.append("FORMAÇÃO DO PREÇO (margem sobre a receita líquida)")
            texto.append(
                f"  1. Receita líquida que o preço precisa deixar: custo ÷ (1 − margem) = "
                f"{rs(p.custo, 4)} ÷ {br((CEM - p.margem) / CEM, 4)} = {rs(r4(alvo), 4)}"
            )
            soma_rs = f" + frete e outras em R$, {rs(p.variaveis_rs(), 4)}" if p.variaveis_rs() else ""
            texto.append(
                f"  2. Preço: (receita líquida{soma_rs}) ÷ (1 − impostos, comissão e frete de {pct(v)}) = "
                f"{rs(r4(alvo + p.variaveis_rs()), 4)} ÷ {br((CEM - v) / CEM, 4)} = {rs(preco_plan)}"
            )
            plan = dre(preco_plan, p)

    # Tabela e realizado
    tab = dre(preco_atual, p) if preco_atual is not None else None
    ref_preco = preco_atual if preco_atual is not None else preco_plan
    ref_nome = "preço de tabela" if preco_atual is not None else "preço formado"
    ref_dre = tab if tab is not None else plan

    reais = {
        "custo": dec(a.custo_real) if a.custo_real else None,
        "comissao": dec(a.comissao_real) if a.comissao_real else None,
        "frete": dec(a.frete_real) if a.frete_real else None,
        "frete_valor": dec(a.frete_valor_real) if a.frete_valor_real else None,
    }
    tem_real = any(x is not None for x in reais.values())
    preco_real = None
    if a.preco_praticado:
        preco_real = r2(dec(a.preco_praticado))
    elif a.desconto:
        if ref_preco is None:
            ap.error("--desconto precisa de um preço de referência: --preco-atual ou --margem")
        preco_real = r2(ref_preco * (1 - dec(a.desconto) / CEM))
    elif tem_real and ref_preco is not None:
        preco_real = ref_preco
    real = dre(preco_real, p, **reais) if preco_real is not None else None

    colunas = []
    if plan:
        colunas.append(("Planejado", f"preço formado, {rs(plan['preco'])} por {p.unidade}", plan))
    if tab:
        colunas.append(("Tabela", f"preço de hoje, {rs(tab['preco'])} por {p.unidade}" + marca(p, "preco-atual"), tab))
    if real:
        sub = f"cobrado, {rs(real['preco'])} por {p.unidade}"
        if a.desconto:
            sub = f"com {pct(dec(a.desconto))} de desconto, {rs(real['preco'])}" + marca(p, "desconto")
        colunas.append(("Realizado", sub, real))
    visiveis = despesas_visiveis(p, colunas)

    for nome, _, d in colunas:
        texto.append("")
        titulo = {"Planejado": "DRE PLANEJADO (preço formado)", "Tabela": "DRE NO PREÇO DE TABELA",
                  "Realizado": "DRE REALIZADO"}[nome]
        texto += bloco_dre(titulo, d, p, visiveis)
        if nome == "Planejado" and d["mc_rl"] is not None and r2(d["mc_rl"]) != r2(p.margem):
            texto.append("  A margem no preço formado fica a centésimos da planejada porque o preço é arredondado em 2 casas.")

    if plan:
        mult = r2((p.custo + p.variaveis_rs()) * (1 + p.margem / CEM))
        dm = dre(mult, p)
        texto.append("")
        texto.append("POR QUE NÃO USAR CUSTO × (1 + MARGEM)")
        texto.append(
            f"  {rs(p.custo + p.variaveis_rs(), 4)} × {br(1 + p.margem / CEM, 4)} = {rs(mult)}. Nesse preço a margem de contribuição "
            f"seria {rs(dm['mc'], 4)} {'por ' + p.unidade if p.qtd == 1 else 'no total'}, ou {fmt_margens(dm)}, "
            f"e não {pct(p.margem)} da receita líquida."
        )
        texto.append(
            "  O multiplicador põe a margem em cima do custo. Impostos, comissão e frete são cobrados "
            "sobre o preço e comem essa margem por dentro."
        )

    # Comparações
    cards = []
    if p.margem is not None:
        cards.append(("Margem planejada", f"{pct(p.margem)} da receita líquida"))
    if plan:
        cards.append(("Preço formado", rs(plan["preco"])))
        cards.append(("Margem no preço formado", fmt_margens(plan)))
    if tab:
        cards.append(("Margem na tabela", fmt_margens(tab)))
    if real:
        cards.append(("Margem realizada", fmt_margens(real)))

    if tab or real:
        texto.append("")
        texto.append("COMPARAÇÃO")
        if plan and tab:
            comparar(texto, p, plan, tab, "preço formado", "O preço de tabela")
            desvio(texto, "Margem da tabela contra a planejada", p.margem, None, tab)
        if real and ref_dre is not None:
            mesmo_custo = dre(preco_real, p)
            desc_rs = ref_preco - preco_real
            if desc_rs > 0:
                texto.append(
                    f"  Desconto: {rs(desc_rs)} por {p.unidade} ({pct(desc_rs / ref_preco * CEM)} sobre o {ref_nome}, {rs(ref_preco)})."
                )
                if a.desconto and r2(desc_rs / ref_preco * CEM) != r2(dec(a.desconto)):
                    texto.append(f"  O desconto pedido foi {pct(dec(a.desconto))}; a diferença vem do preço arredondado em 2 casas.")
                comparar(texto, p, ref_dre, mesmo_custo, ref_nome, "O preço com desconto")
                cards.append(("Desconto que saiu da margem", rs(ref_dre["mc"] - mesmo_custo["mc"], 4)))
            elif desc_rs < 0:
                texto.append(
                    f"  Não houve desconto: o preço cobrado ficou {pct(-desc_rs / ref_preco * CEM)} acima do {ref_nome}, {rs(ref_preco)}."
                )
                comparar(texto, p, ref_dre, mesmo_custo, ref_nome, "O preço cobrado")
            efeito_custo = real["mc"] - mesmo_custo["mc"]
            if efeito_custo < 0:
                texto.append(f"  Os custos reais, diferentes dos planejados, tiraram mais {rs(-efeito_custo, 4)} da margem.")
            elif efeito_custo > 0:
                texto.append(f"  Os custos reais, diferentes dos planejados, acrescentaram {rs(efeito_custo, 4)} à margem.")
            if tab and plan:
                desvio(texto, "Margem realizada contra a da tabela", tab["mc_rl"], None, real)
        final = real or tab
        if plan:
            dv = None
            if real:
                dv = desvio(texto, "Margem realizada contra a planejada", p.margem, None, real)
            else:
                dv = desvio_de(p.margem, tab)
            if dv is not None:
                cards.append(("Desvio contra a planejada", fmt_desvio(dv)))
        else:
            if tab:
                texto.append(f"  Margem no preço de tabela: {rs(tab['mc'], 4)}, ou {fmt_margens(tab)}.")
            if real:
                texto.append(f"  Margem realizada: {rs(real['mc'], 4)}, ou {fmt_margens(real)}.")
            if tab and real:
                desvio(texto, "Margem realizada contra a da tabela", tab["mc_rl"], None, real)

    # Onde vende abaixo do custo real e quanto fica na mesa
    for nome, d in (("preço de tabela", tab), ("preço realizado", real)):
        if d is not None and d["mc"] < 0:
            minimo = formar(p, ZERO)
            texto.append(
                f"  No {nome} cada venda tira {rs(-d['mc'], 4)} do caixa: o preço não cobre o custo e as despesas variáveis."
                + (f" O preço mínimo, com margem zero, é {rs(minimo)}." if minimo is not None else "")
            )
    final = real or tab
    if plan and final is not None and final["mc"] < plan["mc"]:
        na_mesa = plan["mc"] - final["mc"]
        texto.append(
            f"  Contra o preço formado, ficam {rs(na_mesa, 4)} na mesa "
            + (f"por {p.unidade}." if p.qtd == 1 else "na quantidade informada.")
        )
        cards.append(("Deixado na mesa", rs(na_mesa, 4)))

    fora_d = real or tab or plan
    if fora_d and fora_d["fora"]:
        cards.append(("Total da nota", rs(fora_d["nota"])))

    if p.hipoteses:
        texto.append("")
        texto.append("Premissas marcadas como hipótese: " + ", ".join(sorted(p.hipoteses)) + ". Confirme antes de decidir.")
    texto.append("")
    texto.append("A margem é medida sobre a receita líquida: o preço menos impostos, comissão e frete. "
                 "Na DRE contábil, receita líquida é só a receita bruta menos as deduções.")
    texto.append("Margem de contribuição não é lucro: dela ainda saem as despesas fixas, o IRPJ e a CSLL.")
    texto.append("Impostos informados são hipótese até o contador confirmar.")

    print("\n".join(texto))
    if a.html:
        if not colunas:
            with open(a.html, "w", encoding="utf-8") as f:
                f.write(html_saida(p, colunas, texto, cards))
            print(f"\nHTML gravado em {a.html}")
            return 0
        import simulador
        cen = cenario_de_args(a, p, preco_atual)
        simulador.gravar(cen, a.html, a.nao_abrir, apendice_html=tabela_dre(p, colunas))
    return 0


if __name__ == "__main__":
    sys.exit(main())
