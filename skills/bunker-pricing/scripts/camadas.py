"""As duas camadas da leitura de preço, no padrão de DRE da skill.

1. DRE da venda, venda a venda: do custo ao preço negociado e à margem de contribuição, por
   unidade. Sem despesa fixa nem resultado financeiro: nada disso se divide por unidade.
2. DRE do mês, da empresa: orçado contra realizado. A receita parte do preço teto, tira os
   descontos de campanha e os táticos em totais, chega à margem de contribuição e ao que dela
   ficou na mesa, e desce pelas despesas fixas abertas por natureza, pelo resultado
   financeiro (receitas e despesas separadas) e pelo IRPJ e a CSLL até o lucro líquido. No
   Lucro Real, IRPJ e CSLL são % do lucro antes deles e zeram com prejuízo; com
   `regime: "presumido"`, são % da receita bruta e pesam mesmo com prejuízo.

Daqui sai também a conclusão das vendas a mais: com o time vendendo sempre com os descontos,
quantas unidades a mais o mês precisa para deixar a mesma margem de contribuição da venda
perfeita, no preço teto.

Os níveis do simulador entram assim na DRE:
    preço teto        o primeiro nível da linha (o teto; com a margem como piso, a tabela)
    campanha          do preço teto ao nível usado: canal, contrato, tabela de outro grupo
    desconto tático   do nível usado ao negociado: o que o vendedor deu na hora
Orçado é a mesma venda no preço teto; realizado, no negociado. As mesmas unidades nos dois.

Cada parcela da DRE sai em 4 casas e os totais por subtração, como em `preco.dre`, então as
duas camadas fecham exato e `mesa_total == orcado.mc − realizado.mc`.
"""
import copy

from preco import CEM, ZERO, D, r2, dre

CHAVES = ("rb", "deducoes", "rl_contabil", "desp_total", "rl", "cpv", "mc")


def topo(l):
    """O nível do preço teto da linha. Com a margem como piso, o piso é a menor margem aceita, e
    o preço que o dono planeja cobrar é o do primeiro nível acima dele (a tabela)."""
    if l.get("piso"):
        acima = [n for n in l["niveis"] if n["chave"] != "teto"]
        if acima:
            return acima[0]
    return l["niveis"][0]


def _tatico(l):
    return next(c for c in l["cascata"] if c["chave"] == "tatico")


def _unitario(p):
    u = copy.copy(p)
    u.qtd = D(1)
    return u


def venda(l):
    """A DRE da venda de uma linha, por unidade: a formação do preço e o resultado da venda,
    planejado no preço teto e realizado no negociado."""
    p = _unitario(l["p"])
    t, u = topo(l), l["usado"]
    plan = dre(t["preco"], p)
    usado = dre(u["preco"], p)
    mesmo = dre(l["negociado"], p)
    real = dre(l["negociado"], p, custo=l.get("custo_real"))
    vrs = p.variaveis_rs()
    # a formação do preço fecha na receita líquida gerencial do preço teto: é a conta que a DRE
    # de baixo mostra, e por isso a margem planejada é a mesma nas duas partes da tabela
    base = plan["rl"]
    formacao = [
        ("CMV", "custo", p.custo),
        ("MC", "mais", base - p.custo),
        ("BASE", "total", base),
    ]
    if vrs:
        formacao.append(("FRETE", "mais", vrs))
    formacao.append(("TRIB", "mais", t["preco"] - base - vrs))
    formacao.append(("TETO", "total", t["preco"]))
    campanha = t["preco"] - u["preco"]
    tatico = u["preco"] - l["negociado"]
    if campanha:
        formacao.append(("CAMP", "menos", campanha))
        formacao.append(("POL", "total", u["preco"]))
    if tatico:
        formacao.append(("TAT", "menos", tatico))
    formacao.append(("NEG", "total", l["negociado"]))
    return {
        "nome": l["nome"], "unidade": p.unidade, "topo": t, "usado": u, "negociado": l["negociado"],
        "plan": plan, "real": real, "vrs": vrs, "base": base,
        "campanha": campanha, "tatico": tatico,
        "cedida_campanha": plan["mc"] - usado["mc"], "cedida_tatico": usado["mc"] - mesmo["mc"],
        "cedida_custo": mesmo["mc"] - real["mc"],
        "formacao": formacao, "p": p, "usado_dre": usado, "mesmo": mesmo,
    }


def composicao(v):
    """As três vendas de uma unidade, para o desenho da composição do preço: a perfeita, no
    preço teto; a da política comercial; e a negociada, com o desconto tático. Cada uma com o
    preço aberto em custo, tributos, comissão e despesas variáveis, frete e margem, e a margem
    cedida contra a venda perfeita."""
    out = []
    for chave, d in (("teto", v["plan"]), ("politica", v["usado_dre"]), ("negociado", v["real"])):
        out.append({"chave": chave, "preco": d["rb"], "custo": d["cpv"], "trib": d["deducoes"],
                    "com": d["despesas"]["comissao"] + d["despesas"]["outras"], "frete": d["despesas"]["frete"],
                    "mc": d["mc"], "cedida": v["plan"]["mc"] - d["mc"]})
    return out


def vendas_a_mais(res, vendas):
    """Quantas unidades a mais o mês precisa, vendendo com os descontos (política e tático),
    para deixar a mesma margem de contribuição da venda perfeita, no preço teto.

        necessárias = margem total da venda perfeita ÷ margem unitária com desconto
        a mais      = necessárias − vendidas

    Com a mesma margem de contribuição e as mesmas despesas fixas, o lucro líquido também fica
    igual. Margem unitária com desconto zero ou negativa: nenhum volume compensa (None)."""
    linhas = []
    for l, v in zip(res["linhas"], vendas):
        q = l["p"].qtd
        perf = topo(l)["dre"]["mc"]
        un = v["real"]["mc"]
        nec = perf / un if un > 0 else None
        amais = None if nec is None else nec - q
        linhas.append({"nome": l["nome"], "q": q, "perf": perf, "un": un, "nec": nec, "amais": amais,
                       "pct": None if amais is None or not q else amais / q * CEM,
                       "esforco": None if amais is None else amais * v["negociado"]})
    ok = all(x["nec"] is not None for x in linhas)
    q = sum((x["q"] for x in linhas), ZERO)
    tot = {"q": q, "nec": None, "amais": None, "pct": None, "esforco": None}
    if ok:
        tot["nec"] = sum((x["nec"] for x in linhas), ZERO)
        tot["amais"] = tot["nec"] - q
        tot["pct"] = tot["amais"] / q * CEM if q else None
        tot["esforco"] = sum((x["esforco"] for x in linhas), ZERO)
    return {"linhas": linhas, "total": tot}


def _soma(dres):
    out = {k: sum((d[k] for d in dres), ZERO) for k in CHAVES}
    # os tributos e as despesas variáveis, abertos, para a DRE do mês mostrar cada um
    imp = {}
    for d in dres:
        for nome, v in d["impostos"]:
            imp[nome] = imp.get(nome, ZERO) + v
    out["imp"] = imp
    for k in ("comissao", "frete", "outras"):
        out[k] = sum((d["despesas"][k] for d in dres), ZERO)
    return out


def fixas_de(cen):
    """As despesas fixas do mês, abertas por natureza quando vêm abertas; senão, uma linha só."""
    if cen.get("despesas_fixas"):
        return [(d["nome"], D(repr(d["valor"]) if isinstance(d["valor"], float) else str(d["valor"])))
                for d in cen["despesas_fixas"]]
    if cen.get("custo_fixo_mes") not in (None, ""):
        v = cen["custo_fixo_mes"]
        return [("Despesas operacionais fixas", D(repr(v) if isinstance(v, float) else str(v)))]
    return []


def _dec(cen, k):
    v = cen.get(k)
    if v in (None, ""):
        return None
    return D(repr(v) if isinstance(v, float) else str(v))


def presumido_de(cen):
    """`regime: "presumido"` no cenário: `irpj_csll_pct` é % da receita bruta, e não do lucro."""
    return str(cen.get("regime") or "").strip().lower() in ("presumido", "lucro presumido")


def mes(cen, res):
    """A DRE do mês, orçado contra realizado, e o que ficou na mesa por quem cedeu."""
    ls = res["linhas"]
    orc = _soma([topo(l)["dre"] for l in ls])
    rea = _soma([l["real"] for l in ls])
    out = {
        "orcado": orc, "realizado": rea,
        "rec_teto": orc["rb"],
        "desc_campanha": sum((topo(l)["dre"]["rb"] - l["usado"]["dre"]["rb"] for l in ls), ZERO),
        "desc_tatico": sum((l["usado"]["dre"]["rb"] - l["real"]["rb"] for l in ls), ZERO),
        "mesa_campanha": sum((topo(l)["dre"]["mc"] - l["usado"]["dre"]["mc"] for l in ls), ZERO),
        "mesa_tatico": sum((l["usado"]["dre"]["mc"] - _tatico(l)["mc"] for l in ls), ZERO),
        "mesa_custo": sum((_tatico(l)["mc"] - l["real"]["mc"] for l in ls), ZERO),
        "por_linha": [(l["nome"], topo(l)["dre"]["mc"], l["real"]["mc"]) for l in ls],
    }
    out["mesa_total"] = orc["mc"] - rea["mc"]
    assert out["mesa_campanha"] + out["mesa_tatico"] + out["mesa_custo"] == out["mesa_total"]
    for d in (orc, rea):
        d["mc_rl"] = d["mc"] / d["rl"] * CEM if d["rl"] > 0 else None
        d["mc_rb"] = d["mc"] / d["rb"] * CEM if d["rb"] > 0 else None
    fixas = fixas_de(cen)
    out["fixas"] = fixas
    out["tem_fixo"] = bool(fixas)
    if fixas:
        tot = sum((v for _, v in fixas), ZERO)
        rf = _dec(cen, "receitas_financeiras") or ZERO
        df = _dec(cen, "despesas_financeiras") or ZERO
        ir = _dec(cen, "irpj_csll_pct")
        presumido = presumido_de(cen)
        out.update(fixo=tot, rec_fin=rf, desp_fin=df, ir_pct=ir, presumido=presumido,
                   tem_fin=bool(rf or df), tem_ir=ir is not None)
        for d in (orc, rea):
            d["fixo"] = tot
            d["ro"] = d["mc"] - tot
            d["lair"] = d["ro"] + rf - df
            if ir is None:
                d["ir"] = ZERO
            elif presumido:
                # no Lucro Presumido, IRPJ e CSLL saem da receita bruta e pesam mesmo com prejuízo
                d["ir"] = r2(d["rb"] * ir / CEM) if d["rb"] > 0 else ZERO
            else:
                d["ir"] = r2(d["lair"] * ir / CEM) if d["lair"] > 0 else ZERO
            d["ll"] = d["lair"] - d["ir"]
            d["final"] = d["ll"] if ir is not None else d["lair"]
            d["ml"] = d["ll"] / d["rl_contabil"] * CEM if ir is not None and d["rl_contabil"] > 0 else None
            d["peso"] = tot / d["rb"] * CEM if d["rb"] > 0 else None
    return out
