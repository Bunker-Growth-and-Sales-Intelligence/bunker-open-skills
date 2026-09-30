#!/usr/bin/env python3
"""A entrega da leitura de preço: o painel editável e o PDF A4 para o cliente.

Lê o mesmo cenário do simulador (references/simulador.md), faz a mesma conta
(`simulador.calcular`) e mostra o preço pelo qual cada produto deve ser vendido, em quatro
partes: a composição do preço em três vendas (a perfeita, no preço teto; a da política
comercial; e a negociada), a DRE da venda, a DRE do mês e as conclusões, com as vendas a mais
que os descontos pedem para o mesmo resultado. Fecha com o próximo passo, em escada.

No painel, todo número que é premissa (custo, margem desejada, alíquotas, comissão, frete,
descontos, volume, despesas fixas, resultado financeiro) é um campo dentro da própria célula, e
editar recalcula as duas DREs no navegador, com a mesma conta do Python (`assets/painel.js`,
conferida pelo teste de paridade). As colunas de nome mostram como o Alumni, a skill e o
Pricing Designer chamam cada linha; no painel, o nome escolhido fica gravado no navegador.

Uso, de dentro de qualquer pasta:
    python3 scripts/entrega.py cenario.json                        grava cenario.painel.html
    python3 scripts/entrega.py cenario.json --painel painel.html   escolhe o arquivo do painel
    python3 scripts/entrega.py cenario.json --pdf entrega.pdf      e o PDF A4 para o cliente
    python3 scripts/entrega.py cenario.json --cenario 2            o segundo cenário do arquivo

O PDF sai pelo Chrome headless da máquina. Sem Chrome, o script grava o HTML das folhas A4
ao lado do PDF pedido, para imprimir no navegador (A4, margens: nenhuma, gráficos de fundo
ligados), e avisa. Só usa a biblioteca padrão do Python 3.8 ou mais novo.
"""
import argparse
import datetime as _dt
import json
import os
import re
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import camadas  # noqa: E402
import preco  # noqa: E402
import simulador  # noqa: E402
from preco import CEM, ZERO, D  # noqa: E402
from grafico import formas, marca, pagina, paleta, saida  # noqa: E402
from grafico.paleta import A4, CHEIA, MEIA, esc  # noqa: E402

ASSETS = os.path.join(AQUI, "..", "assets")
CUSTO_MES = {"comercio": "Custo das mercadorias vendidas (CMV)", "industria": "Custo dos produtos vendidos (CPV)",
             "servico": "Custo dos serviços prestados (CSP)", None: "Custo do que foi vendido (CMV, CPV ou CSP)"}
DEGRAUS = [
    ("Poucos itens, um preço por item",
     "Refazer a conta quando custo, imposto ou comissão mudarem, e de novo em janeiro de 2027."),
    ("Muitos itens e nenhum sistema",
     "Começar pelos itens que o cliente compara, uma linha por grupo, e revisar por categoria com o contador."),
    ("Operação grande",
     "Tabela por canal, preço de contrato e desconto em cada pedido: a conta precisa rodar em cada linha de cada pedido."),
]
PD = "É o trabalho do Pricing Designer da Bunker. Conheça em bunkerconsultancy.com"
TITULO = "Leitura de preço e margem"
REFORMA = ("CBS", "IBS")   # os tributos da reforma aparecem sempre, zerados enquanto não valem

# Como o Alumni e o Pricing Designer chamam cada linha que a skill mostra, pela página de
# decisão de nomenclatura (docs/decisao-nomenclatura). None: o termo ainda não existe lá, e a
# célula mostra o nome da skill em vermelho, "a criar".
NOMES = {
    "custo": ("CPV", "Custo"),
    "mc_plan": (None, "margem do nível (MC global)"),
    "base": (None, "preço base da fórmula"),
    "frete_rs": ("“despesas”", "fator frete (R$)"),
    "trib": (None, "fatores em % do preço"),
    "teto": (None, "Level0Price (preço nível 0)"),
    "campanha": (None, "modificador de catálogo (nível 1)"),
    "politica": (None, "Level1Price (preço nível 1)"),
    "tatico": (None, "desconto da linha"),
    "rb": ("receita bruta", "Receita bruta"),
    "deducoes": ("imposto sobre a venda", "somado em “Custos variáveis”"),
    "rlc": ("receita líquida", None),
    "desp": ("“despesas”, junto com as fixas", "somado em “Custos variáveis”"),
    "rlg": (None, "Receita líquida"),
    "cpv": ("CPV", "Custo"),
    "mc": (None, "Margem líquida (R$)"),
    "mc_rl": (None, "Margem sobre a receita líquida"),
    "mc_rb": (None, "Margem líquida (%)"),
    "ced_camp": (None, "desvio do nível 0 contra o 1 (R$)"),
    "ced_tat": (None, "ProfitDeviationLevelUsed (R$)"),
    "rec_teto": (None, "Level0Price × quantidade"),
    "desc_camp": (None, "diferença entre nível 0 e nível 1"),
    "desc_tat": (None, "desconto das linhas"),
    "rb_mes": ("receita bruta", "Receita bruta (soma das linhas)"),
    "mc_mes": (None, "Margem líquida (R$), somada"),
    "mesa_camp": (None, "desvio do nível 0 contra o 1 (R$), somado"),
    "mesa_tat": (None, "ProfitDeviationLevelUsed (R$), somado"),
    "fixas_total": ("despesas", None),
    "ro": ("resultado operacional", None),
    "desp_fin": ("juros", None),
    "ir": ("imposto sobre o lucro", None),
    "ll": ("lucro líquido", None),
    "ml": ("margem líquida (fn-1.2)", None),
}
FIXAS_ALUMNI = (("pessoal", "“equipe”, dentro de despesas"), ("comerciais", "“comercial”, dentro de despesas"),
                ("depreciação", "depreciação"))


# ------------------------------------------------------------------ formato

def br(x, casas=2):
    return "" if x is None else preco.br(D(x), casas)


def rs(x, casas=2):
    return formas.rs(x, casas)


def pc(x, casas=1):
    return "n/d" if x is None else br(x, casas) + "%"


def fmt(x, f):
    """rs: reais em 2 casas; pc: margem em % (o desvio sai em p.p.); pq: variação em % (o desvio
    sai em %)."""
    if x is None:
        return ""
    return br(x, 1) + "%" if f in ("pc", "pq") else br(x, 2)


def _plural(p):
    if p.endswith("ês"):
        return p[:-2] + "eses"
    if p.endswith("s"):
        return p
    if p.endswith("m"):
        return p[:-1] + "ns"
    return p + "s"


def plural(u):
    """Hora, horas; mês de contrato, meses de contrato; km cobrado, km cobrados."""
    ps = u.split(" ")
    if ps[0] == "km":
        return " ".join([ps[0]] + [_plural(p) for p in ps[1:]])
    return " ".join([_plural(ps[0])] + ps[1:])


def unidades(c):
    """A unidade de cada linha, na ordem das linhas; `unidade` na linha manda sobre a do cenário."""
    return [v["unidade"] or "unidade" for v in c["vendas"]]


def uma_unidade(c):
    """A unidade comum a todas as linhas, ou None quando elas se medem em unidades diferentes."""
    us = set(unidades(c))
    return us.pop() if len(us) == 1 else None


def desvio(d, f, s):
    """O desvio com a seta e a classe que julga: `s` é "+" quando subir é bom e "-" quando
    subir é ruim. Devolve (texto, classe)."""
    c = 1 if f in ("pc", "pq") else 2
    if d is None:
        return "", ""
    v = preco.D(d).quantize(D(1).scaleb(-c), rounding=preco.ROUND_HALF_UP)
    if not v:
        return "", ""
    txt = ("▲ " if v > 0 else "▼ ") + br(abs(v), c) + {"pc": " p.p.", "pq": "%"}.get(f, "")
    cls = ("bom" if (v > 0) == (s == "+") else "mau") if s in ("+", "-") else ""
    return txt, cls


# ------------------------------------------------------------------ a conta

def ler(caminho, indice=0):
    raiz, cens = simulador.carregar(caminho)
    if not 0 <= indice < len(cens):
        raise SystemExit(f"O arquivo tem {len(cens)} cenário(s); pedi o {indice + 1}.")
    return raiz, cens, indice


def montar_conta(cen):
    res = simulador.calcular(cen)
    vendas = [camadas.venda(l) for l in res["linhas"]]
    return {"cen": cen, "res": res, "mes": camadas.mes(cen, res), "vendas": vendas,
            "amais": camadas.vendas_a_mais(res, vendas)}


def valores(c):
    """Os números do painel num mapa só, com as mesmas chaves que `assets/painel.js` monta:
    as células levam a chave, e o teste de paridade confere o mapa inteiro nos dois lados."""
    V = {"0": ZERO}

    def dre_(pre, d):
        V[pre + "rb"], V[pre + "deducoes"], V[pre + "rlc"] = d["rb"], d["deducoes"], d["rl_contabil"]
        V[pre + "desp"], V[pre + "rl"], V[pre + "cpv"], V[pre + "mc"] = d["desp_total"], d["rl"], d["cpv"], d["mc"]
        V[pre + "mc_rl"], V[pre + "mc_rb"] = d["mc_rl"], d["mc_rb"]
        if "despesas" in d:
            V[pre + "com"], V[pre + "fre"], V[pre + "out"] = (d["despesas"][k] for k in ("comissao", "frete", "outras"))
            for nome, v in d["impostos"]:
                V[pre + "imp." + nome] = v
            for nome, _, _, v in d["fora"]:
                V[pre + "fora." + nome] = v
            V[pre + "nota"] = d["nota"]
        else:
            V[pre + "com"], V[pre + "fre"], V[pre + "out"] = d["comissao"], d["frete"], d["outras"]
            for nome, v in d["imp"].items():
                V[pre + "imp." + nome] = v
        for k in ("ro", "lair", "ir", "ll", "ml", "peso"):
            if k in d:
                V[pre + k] = d[k]

    for i, (v, l, a) in enumerate(zip(c["vendas"], c["res"]["linhas"], c["amais"]["linhas"])):
        pre = f"v{i}."
        V[pre + "custo"], V[pre + "base"], V[pre + "mcplan"] = v["p"].custo, v["base"], v["base"] - v["p"].custo
        V[pre + "vrs"], V[pre + "trib"] = v["vrs"], v["topo"]["preco"] - v["base"] - v["vrs"]
        V[pre + "teto"], V[pre + "usado"], V[pre + "neg"] = v["topo"]["preco"], v["usado"]["preco"], v["negociado"]
        V[pre + "camp"], V[pre + "tat"] = v["campanha"], v["tatico"]
        V[pre + "ced_camp"], V[pre + "ced_tat"], V[pre + "ced_custo"] = v["cedida_campanha"], v["cedida_tatico"], v["cedida_custo"]
        dre_(pre + "P.", v["plan"])
        dre_(pre + "U.", v["usado_dre"])
        dre_(pre + "R.", v["real"])
        V[pre + "q"], V[pre + "perf"], V[pre + "un"], V[pre + "nec"] = a["q"], a["perf"], a["un"], a["nec"]
        V[pre + "amais"], V[pre + "amais_pct"], V[pre + "esforco"] = a["amais"], a["pct"], a["esforco"]
        V[pre + "minimo"] = l["minimo"]
    m = c["mes"]
    dre_("m.O.", m["orcado"])
    dre_("m.R.", m["realizado"])
    for k in ("rec_teto", "desc_campanha", "desc_tatico", "mesa_campanha", "mesa_tatico", "mesa_custo", "mesa_total"):
        V["m." + k] = m[k]
    if m["tem_fixo"]:
        V["m.fixo"], V["m.rec_fin"], V["m.desp_fin"], V["m.ir_pct"] = m["fixo"], m["rec_fin"], m["desp_fin"], m["ir_pct"]
        for k, (_, v) in enumerate(m["fixas"]):
            V[f"m.fix.{k}"] = v
    t = c["amais"]["total"]
    V["t.q"], V["t.nec"], V["t.amais"], V["t.amais_pct"], V["t.esforco"] = t["q"], t["nec"], t["amais"], t["pct"], t["esforco"]
    return V


def numeros(c):
    """O mapa de `valores` em texto de 4 casas, como o `Camadas.numeros` do JS."""
    return {k: simulador._s(v) for k, v in valores(c).items()}


def porte(cen, res):
    """O degrau da escada: 1 poucos itens, 2 muitos itens sem sistema, 3 operação grande.
    `porte` no cenário manda; sem ele, canal ou contrato mais desconto em duas linhas é grande."""
    dado = str(cen.get("porte") or "").lower()
    if dado in ("1", "pequeno", "poucos"):
        return 1
    if dado in ("2", "muitos", "muitos_itens"):
        return 2
    if dado in ("3", "grande"):
        return 3
    ls = res["linhas"]
    canal = any(any(n["chave"] == "canal" for n in l["niveis"]) for l in ls)
    desc = sum(1 for l in ls if abs(l["desconto_rs"]) > 0)
    if canal and desc >= 2 or len(ls) >= 8:
        return 3
    return 2 if len(ls) >= 3 else 1


def ordem(c):
    """As linhas da maior receita para a menor: a primeira é o produto principal."""
    ls = c["res"]["linhas"]
    return sorted(range(len(ls)), key=lambda i: -ls[i]["real"]["rb"])


# ------------------------------------------------------------------ as linhas da DRE

def L(cls, nome, conceito=None, a=None, b=None, f="rs", s="+", sinal="", prb=True, dv=None, dv_sinal=-1,
      ed_a=None, ed_b=None, extra=None, sb=1):
    """Uma linha da DRE, descrita uma vez e desenhada no painel e no PDF.

    `a` e `b` são chaves de `valores` (planejado e realizado); `dv`, a chave de uma linha que só
    tem desvio (a margem cedida). `ed_a` e `ed_b` fazem da célula um campo: {"campo", "modo",
    ...}. `extra` vai ao lado do nome: a alíquota, a comissão, o frete, o IRPJ. `sb` é o sinal
    do realizado na tela: o acréscimo guarda o valor negativo e mostra o positivo."""
    return dict(cls=cls, nome=nome, conceito=conceito, a=a, b=b, f=f, s=s, sinal=sinal, prb=prb, dv=dv,
                dv_sinal=dv_sinal, ed_a=ed_a, ed_b=ed_b, extra=extra, sb=sb)


def campo(caminho, valor, linha=None, modo="set", k=None, **kw):
    return dict(campo=caminho, valor=valor, linha=linha, modo=modo, k=k, **kw)


def linhas_venda(c, i):
    v, l = c["vendas"][i], c["res"]["linhas"][i]
    cen, p = c["cen"], v["p"]
    bruta = cen["linhas"][i]
    pre = f"v{i}."
    custo_rot = preco.ROTULO_CUSTO.get(cen.get("atividade"), preco.ROTULO_CUSTO[None])[0]
    R = []
    R.append(L("grp", "Formação do preço"))
    R.append(L("mov", custo_rot, "custo", pre + "custo", pre + "custo", s="-", prb=False,
               ed_a=campo(f"linhas.{i}.custo", p.custo, i)))
    R.append(L("mov", "Margem de contribuição planejada", "mc_plan", pre + "mcplan", pre + "mcplan", sinal="(+) ", prb=False))
    R.append(L("sub", "Preço base", "base", pre + "base", pre + "base", sinal="(=) ", prb=False))
    if v["vrs"]:
        ed = campo(f"linhas.{i}.frete_rs", p.frete_valor, i) if not p.outras_valor else None
        R.append(L("mov", "Frete e despesas em R$", "frete_rs", pre + "vrs", pre + "vrs", sinal="(+) ", s="-", prb=False, ed_a=ed))
    R.append(L("mov", "Tributos e comissão por dentro", "trib", pre + "trib", pre + "trib", sinal="(+) ", s="-", prb=False))
    ed_teto = None
    if v["topo"]["chave"] == "especifico" and bruta.get("preco_especifico") is not None:
        ed_teto = campo(f"linhas.{i}.preco_especifico", v["topo"]["preco"], i, modo="esp")
    R.append(L("sub", "Preço teto", "teto", pre + "teto", pre + "teto", sinal="(=) ", prb=False, ed_a=ed_teto))
    if v["campanha"]:
        ed = None if l["piso"] else campo(f"linhas.{i}.preco_especifico", abs(v["campanha"]), i, modo="camp",
                                          k=pre + "camp", teto=v["topo"]["preco"])
        sc = 1 if v["campanha"] > 0 else -1
        if ed:
            ed["sinal"] = sc
        R.append(L("mov", "Desconto de campanha" if sc > 0 else "Acréscimo da política comercial", "campanha",
                   "0", pre + "camp", sinal="(−) " if sc > 0 else "(+) ", s="-" if sc > 0 else "+", prb=False, ed_b=ed, sb=sc))
        R.append(L("sub", "Preço da política comercial", "politica", pre + "teto", pre + "usado", sinal="(=) ", prb=False))
    sinal_tat = 1 if v["tatico"] >= 0 else -1
    R.append(L("mov", "Desconto tático" if sinal_tat > 0 else "Acréscimo tático", "tatico", "0", pre + "tat",
               sinal="(−) " if sinal_tat > 0 else "(+) ", s="-" if sinal_tat > 0 else "+", prb=False, sb=sinal_tat,
               ed_b=campo(f"linhas.{i}.preco_praticado", abs(v["tatico"]), i, modo="tat", k=pre + "tat",
                          usado=v["usado"]["preco"], sinal=sinal_tat)))
    R.append(L("grp", "Resultado da venda"))
    R.append(L("tot", "Receita bruta da venda", "rb", pre + "P.rb", pre + "R.rb"))
    R.append(L("mov", "Deduções da receita bruta", "deducoes", pre + "P.deducoes", pre + "R.deducoes", sinal="(−) ", s="-"))
    for nome, aliq in _tributos(p.impostos):
        R.append(L("ind", nome, "imp:" + nome, pre + "P.imp." + nome, pre + "R.imp." + nome, s="-",
                   extra=campo(f"linhas.{i}.impostos.{nome}", aliq, i, pct=True)))
    R.append(L("sub", "Receita líquida contábil", "rlc", pre + "P.rlc", pre + "R.rlc", sinal="(=) "))
    R.append(L("mov", "Despesas variáveis de venda", "desp", pre + "P.desp", pre + "R.desp", sinal="(−) ", s="-"))
    R.append(L("ind", "Comissão", "comissao", pre + "P.com", pre + "R.com", s="-",
               extra=campo(f"linhas.{i}.comissao", p.comissao, i, pct=True)))
    # frete e outras despesas entram em % do preço ou em R$ por unidade: o campo segue o que a linha usa
    if p.frete_valor and not p.frete and not p.outras_valor:
        ed = campo(f"linhas.{i}.frete_rs", p.frete_valor, i, reais=True)
    else:
        ed = campo(f"linhas.{i}.frete_pct", p.frete, i, pct=True)
    R.append(L("ind", "Frete", "frete", pre + "P.fre", pre + "R.fre", s="-", extra=ed))
    if p.outras or p.outras_valor:
        if p.outras_valor and not p.outras:
            ed = campo(f"linhas.{i}.outras_rs", p.outras_valor, i, reais=True)
        else:
            ed = campo(f"linhas.{i}.outras_pct", p.outras, i, pct=True)
        R.append(L("ind", "Outras despesas variáveis", "outras", pre + "P.out", pre + "R.out", s="-", extra=ed))
    R.append(L("sub", "Receita líquida gerencial", "rlg", pre + "P.rl", pre + "R.rl", sinal="(=) "))
    R.append(L("mov", custo_rot, "cpv", pre + "P.cpv", pre + "R.cpv", sinal="(−) ", s="-"))
    R.append(L("tot", "Margem de contribuição da venda", "mc", pre + "P.mc", pre + "R.mc", sinal="(=) "))
    ed_meta = None
    if v["topo"]["chave"] == "teto":
        caminho = f"linhas.{i}.mc_teto" if "mc_teto" in bruta else "mc_teto"
        ed_meta = campo(caminho, v["topo"]["mc_plan"], i if "mc_teto" in bruta else None, pct=True)
    R.append(L("ind", "Margem de contribuição sobre a receita líquida gerencial", "mc_rl", pre + "P.mc_rl", pre + "R.mc_rl",
               f="pc", prb=False, ed_a=ed_meta))
    R.append(L("ind", "Margem de contribuição sobre a receita bruta", "mc_rb", pre + "P.mc_rb", pre + "R.mc_rb", f="pc", prb=False))
    for chave, nome, ganho, conc in (("cedida_campanha", "Margem de contribuição cedida na campanha",
                                      "Margem de contribuição ganha na política comercial", "ced_camp"),
                                     ("cedida_tatico", "Margem de contribuição cedida no desconto tático",
                                      "Margem de contribuição ganha acima da tabela", "ced_tat"),
                                     ("cedida_custo", "Margem de contribuição perdida no custo acima do planejado",
                                      "Margem de contribuição ganha no custo abaixo do planejado", "ced_custo")):
        if v[chave]:
            R.append(L("des", nome if v[chave] > 0 else ganho, conc, prb=False, dv=pre + conc))
    if v["plan"]["fora"]:
        R.append(L("grp", "Fora da receita bruta, somado na nota"))
        for nome, aliq, _, _ in v["plan"]["fora"]:
            R.append(L("mov", f"{nome} {pc(aliq, 2)}", "fora:" + nome, pre + "P.fora." + nome, pre + "R.fora." + nome,
                       sinal="(+) ", s="-", prb=False))
        R.append(L("tot", "Total da nota", "nota", pre + "P.nota", pre + "R.nota", sinal="(=) ", prb=False))
    return R


def _tributos(impostos):
    """Os tributos da regra de hoje e os da reforma, CBS e IBS, mesmo zerados."""
    out = list(impostos.items())
    tem = {n.strip().upper() for n, _ in out}
    out += [(n, ZERO) for n in REFORMA if n not in tem]
    return out


def linhas_mes(c):
    m, cen = c["mes"], c["cen"]
    R = [L("grp", "Receita")]
    R.append(L("sub", "Receita bruta no preço teto", "rec_teto", "m.rec_teto", "m.rec_teto"))
    for chave, nome, alt, conc in (("desc_campanha", "Descontos de campanha e política comercial",
                                    "Acréscimos da política comercial", "desc_camp"),
                                   ("desc_tatico", "Descontos táticos", "Acréscimos táticos", "desc_tat")):
        if m[chave]:
            sm = 1 if m[chave] > 0 else -1
            R.append(L("mov", nome if sm > 0 else alt, conc, "0", "m." + chave,
                       sinal="(−) " if sm > 0 else "(+) ", s="-" if sm > 0 else "+", sb=sm))
    R.append(L("tot", "Receita bruta de vendas", "rb_mes", "m.O.rb", "m.R.rb", sinal="(=) "))
    R.append(L("mov", "Deduções da receita bruta", "deducoes", "m.O.deducoes", "m.R.deducoes", sinal="(−) ", s="-"))
    aliqs = {}
    for l in c["res"]["linhas"]:
        for n, a in _tributos(l["p"].impostos):
            aliqs.setdefault(n, set()).add(a)
    for n, a in aliqs.items():
        R.append(L("ind", n, "imp:" + n, "m.O.imp." + n, "m.R.imp." + n, s="-",
                   extra={"texto": pc(next(iter(a)), 2)} if len(a) == 1 else None))
    R.append(L("sub", "Receita líquida contábil", "rlc", "m.O.rlc", "m.R.rlc", sinal="(=) "))
    R.append(L("grp", "Margem de contribuição"))
    R.append(L("mov", "Despesas variáveis de venda", "desp", "m.O.desp", "m.R.desp", sinal="(−) ", s="-"))
    o, r = m["orcado"], m["realizado"]
    for k, nome, conc in (("comissao", "Comissão", "comissao"), ("frete", "Frete", "frete"),
                          ("outras", "Outras despesas variáveis", "outras")):
        if k == "comissao" or o[k] or r[k]:
            R.append(L("ind", nome, conc, "m.O." + k[:3].replace("fre", "fre"), "m.R." + k[:3], s="-"))
    R.append(L("sub", "Receita líquida gerencial", "rlg", "m.O.rl", "m.R.rl", sinal="(=) "))
    R.append(L("mov", CUSTO_MES.get(cen.get("atividade"), CUSTO_MES[None]), "cpv", "m.O.cpv", "m.R.cpv", sinal="(−) ", s="-"))
    R.append(L("tot", "Margem de contribuição do mês", "mc_mes", "m.O.mc", "m.R.mc", sinal="(=) "))
    R.append(L("ind", "Margem de contribuição sobre a receita líquida gerencial", "mc_rl", "m.O.mc_rl", "m.R.mc_rl", f="pc", prb=False))
    for chave, nome, ganho, conc in (("mesa_campanha", "campanha", "política comercial", "mesa_camp"),
                                     ("mesa_tatico", "desconto tático", "acima da tabela", "mesa_tat"),
                                     ("mesa_custo", "custo acima do planejado", "custo abaixo do planejado", "mesa_custo")):
        if m[chave]:
            R.append(L("des", f"Margem de contribuição que ficou na mesa: {nome}" if m[chave] > 0
                       else f"Margem de contribuição ganha: {ganho}", conc, prb=False, dv="m." + chave))
    R.append(L("des", "Margem de contribuição que ficou na mesa: total" if m["mesa_total"] >= 0
               else "Margem de contribuição acima da planejada: total", "mesa_total", prb=False, dv="m.mesa_total"))
    if m["tem_fixo"]:
        R.append(L("grp", "Despesas operacionais fixas"))
        brutas = cen.get("despesas_fixas") or []
        for k, (nome, v) in enumerate(m["fixas"]):
            caminho = f"despesas_fixas.{k}.valor" if brutas else "custo_fixo_mes"
            R.append(L("mov", nome.replace("(−) ", ""), "fixa:" + nome, f"m.fix.{k}", f"m.fix.{k}", sinal="(−) ", s="-",
                       ed_a=campo(caminho, v)))
        if len(m["fixas"]) > 1:  # com uma natureza só, o total repetiria a linha
            R.append(L("sub", "Total das despesas operacionais fixas", "fixas_total", "m.fixo", "m.fixo", sinal="(=) ", s="-"))
        R.append(L("tot", "Resultado operacional", "ro", "m.O.ro", "m.R.ro", sinal="(=) "))
        if m["tem_fin"] or m["tem_ir"]:
            R.append(L("grp", "Resultado financeiro e tributos sobre o lucro"))
            R.append(L("mov", "Receitas financeiras", "rec_fin", "m.rec_fin", "m.rec_fin", sinal="(+) ",
                       ed_a=campo("receitas_financeiras", m["rec_fin"])))
            R.append(L("mov", "Despesas financeiras", "desp_fin", "m.desp_fin", "m.desp_fin", sinal="(−) ", s="-",
                       ed_a=campo("despesas_financeiras", m["desp_fin"])))
            R.append(L("sub", "Lucro antes do IRPJ e da CSLL", "lair", "m.O.lair", "m.R.lair", sinal="(=) "))
        if m["tem_ir"]:
            if m["presumido"]:
                R.append(L("mov", "IRPJ e CSLL, Lucro Presumido, sobre a receita", "ir", "m.O.ir", "m.R.ir", sinal="(−) ",
                           s="-", extra=campo("irpj_csll_pct", m["ir_pct"], pct=True)))
            else:
                R.append(L("mov", "IRPJ e CSLL", "ir", "m.O.ir", "m.R.ir", sinal="(−) ", s="-",
                           extra=campo("irpj_csll_pct", m["ir_pct"], pct=True, depois="do lucro")))
            R.append(L("tot", "Lucro líquido do período", "ll", "m.O.ll", "m.R.ll", sinal="(=) "))
            R.append(L("ind", "Margem líquida", "ml", "m.O.ml", "m.R.ml", f="pc", prb=False))
        R.append(L("ind", "Peso das despesas operacionais fixas na receita bruta", "peso", "m.O.peso", "m.R.peso",
                   f="pc", s="-", prb=False))
    return R


# ------------------------------------------------------------------ desenho da tabela

def _nomes(conceito, skill):
    if conceito and conceito.startswith("fixa:"):
        low = conceito.lower()
        al = next((t for chave, t in FIXAS_ALUMNI if chave in low), "despesas")
        return al, None
    return NOMES.get(conceito, (None, None))


def _input(ed, V, pdf, larg_pct=False):
    """Um campo sem borda, na própria célula, no tamanho da letra dela. No PDF, só o número."""
    if ed.get("texto"):
        return esc(ed["texto"])
    if ed.get("k"):
        v = V.get(ed["k"])
        if v is not None and ed.get("sinal", 1) != 1:
            v = v * ed["sinal"]
    else:
        v = ed["valor"]
    txt = br(v if v is not None else ZERO, 2)
    if pdf:
        return esc(txt)
    at = [f'data-campo="{esc(ed["campo"])}"', f'data-modo="{ed["modo"]}"']
    if ed.get("linha") is not None:
        at.append(f'data-linha="{ed["linha"]}"')
    if ed.get("k"):
        at.append(f'data-k="{esc(ed["k"])}"')
    for chave in ("teto", "usado", "sinal"):
        if ed.get(chave) is not None:
            at.append(f'data-{chave}="{ed[chave]}"')
    return (f'<input class="ed" type="text" inputmode="decimal" value="{esc(txt)}" size="{max(len(txt), 3)}" '
            f'aria-label="editar" {" ".join(at)}>')


def _extra(ed, V, pdf):
    if ed is None:
        return ""
    if ed.get("texto"):
        return f' <span class="al">{esc(ed["texto"])}</span>'
    depois = f' {esc(ed["depois"])}' if ed.get("depois") else ""
    if ed.get("reais"):
        return f' <span class="al">R$ {_input(ed, V, pdf)}</span>'
    return f' <span class="al">{_input(ed, V, pdf)}%{depois}</span>'


def _celula_nome(src, texto, skill, pdf):
    falta = texto is None
    mostra = skill if falta else texto
    cls = ("nm" + (" falta" if falta else "") + (" sk" if src == "skill" else ""))
    if pdf:
        # o vermelho basta; a legenda "em vermelho, a criar" vai no cabeçalho da coluna
        return f'<td class="nmc {cls}">{esc(mostra)}</td>'
    dica = ' title="a criar"' if falta else ""
    return (f'<td class="nmc"><button type="button" class="{cls}" data-src="{src}" data-nome="{esc(mostra)}"{dica} '
            f'aria-pressed="false">{esc(mostra)}</button></td>')


def tabela(linhas, V, rb_key, cab_a, cab_b, prefixo, pdf=False):
    """A DRE: nome, planejado, realizado, desvio, % da receita bruta e as três colunas de nome."""
    rb = V.get(rb_key)
    corpo = []
    for r in linhas:
        if r["cls"] == "grp":
            corpo.append(f'<tr class="grp"><td colspan="8">{esc(r["nome"])}</td></tr>')
            continue
        al, pd = _nomes(r["conceito"], r["nome"])
        nome = (f'<td class="n0"><span class="sinal">{esc(r["sinal"])}</span><span class="nome" data-padrao="{esc(r["nome"])}">'
                f'{esc(r["nome"])}</span>{_extra(r["extra"], V, pdf)}</td>')
        cels = []
        for chave, ed in (("a", r["ed_a"]), ("b", r["ed_b"])):
            k = r[chave]
            if ed is not None:
                cels.append(f'<td class="v">{_input(ed, V, pdf)}</td>')
            elif k is None:
                cels.append('<td class="v"></td>')
            else:
                sg = r["sb"] if chave == "b" else 1
                v = V.get(k, ZERO)
                at = f' data-sinal="{sg}"' if sg != 1 else ""
                cels.append(f'<td class="v" data-k="{esc(k)}" data-f="{r["f"]}"{at}>'
                            f'{esc(fmt(None if v is None else v * sg, r["f"]))}</td>')
        if r["dv"]:
            val = V.get(r["dv"])
            txt, cls = desvio(None if val is None else val * r["dv_sinal"], r["f"], r["s"])
            dsv = (f'<td class="dsv {cls}" data-dv="{esc(r["dv"])}" data-sinal="{r["dv_sinal"]}" data-f="{r["f"]}" '
                   f'data-s="{r["s"]}">{txt}</td>')
        elif r["a"] is not None and r["b"] is not None:
            a, b = V.get(r["a"], ZERO), V.get(r["b"], ZERO)
            txt, cls = desvio(None if a is None or b is None else b * r["sb"] - a, r["f"], r["s"])
            dsv = (f'<td class="dsv {cls}" data-da="{esc(r["a"])}" data-db="{esc(r["b"])}" data-sinal="{r["sb"]}" '
                   f'data-f="{r["f"]}" data-s="{r["s"]}">{txt}</td>')
        else:
            dsv = '<td class="dsv"></td>'
        if r["prb"] and r["b"] is not None:
            b = V.get(r["b"], ZERO)
            b = None if b is None else b * r["sb"]
            txt = "" if not rb or b is None else pc(b / rb * CEM, 1)
            prb = (f'<td class="prb" data-pn="{esc(r["b"])}" data-pd="{esc(rb_key)}" data-sinal="{r["sb"]}">{txt}</td>')
        else:
            prb = '<td class="prb"></td>'
        nm = "".join(_celula_nome(src, t, r["nome"], pdf) for src, t in (("alumni", al), ("skill", r["nome"]), ("pd", pd)))
        corpo.append(f'<tr class="{r["cls"]}" data-nm="{prefixo}:{esc(r["conceito"] or r["nome"])}">{nome}{"".join(cels)}'
                     f'{dsv}{prb}{nm}</tr>')
    leg = '<small class="falta">em vermelho, a criar</small>'
    cab = (f'<thead><tr><th class="n0"></th><th>{cab_a}</th><th>{cab_b}</th><th>Desvio</th>'
           f'<th class="prb">% da receita bruta</th><th class="nmc">Alumni chama de{leg}</th>'
           f'<th class="nmc sk">Skill chama de</th><th class="nmc">Pricing Designer grava como{leg}</th></tr></thead>')
    return f'<div class="tw"><table class="dre">{cab}<tbody>{"".join(corpo)}</tbody></table></div>'


def tabela_venda(c, i, pdf=False):
    return tabela(linhas_venda(c, i), valores(c), f"v{i}.R.rb", "Planejado<br>no preço teto", "Realizado<br>no negociado",
                  "v", pdf)


def tabela_mes(c, pdf=False):
    return tabela(linhas_mes(c), valores(c), "m.R.rb", "Orçado<br>no mês", "Realizado<br>no mês", "m", pdf)


# ------------------------------------------------------------------ os blocos

def _duplo(desenhar):
    """Um bloco de largura cheia leva dois desenhos, um nascido em 980 e outro em 468, e o CSS
    mostra o da largura da tela: encolher o de 980 no celular deixaria a letra com 4 px."""
    return (f'<div class="so-largo">{desenhar(CHEIA)}</div>'
            f'<div class="so-estreito">{desenhar(MEIA)}</div>')


ROT_CURTO = ["Teto", "Política", "Negociado"]


def bloco_composicao(c, pdf=False):
    """O preço de uma unidade em três vendas: a perfeita, a da política e a negociada. O
    produto principal sai grande, com o nome de cada pedaço; os outros, em pequenos múltiplos."""
    ords = ordem(c)
    un = uma_unidade(c)
    vs = c["vendas"]
    principal = vs[ords[0]]
    tit = principal["nome"] + ("" if un else f", por {principal['unidade']}")

    def grande(larg):
        # na folha, mais baixo: a composição e a DRE da venda dividem a mesma folha
        return formas.composicao(camadas.composicao(principal), larg, titulo=tit if len(vs) > 1 else None,
                                 alt_plot=104 if larg == A4 else (240 if larg >= CHEIA else 220))
    outros = [vs[i] for i in ords[1:]]
    if pdf:
        # na folha, uma fileira só de pequenos múltiplos, até cinco: a composição divide a folha com a DRE da venda
        corpo = grande(A4)
        por_fila = min(max(len(outros), 3), 5)
        larg_p, alt_p = int((A4 - 15 * (por_fila - 1)) // por_fila), 58 if por_fila <= 3 else 52
    else:
        corpo = _duplo(grande)
        larg_p, alt_p = 300, 130
    if outros:
        nl = max(len(formas._quebra(v["nome"], larg_p - 2, 10.0, 2)) for v in outros)
        peq = "".join(f'<div>{formas.composicao(camadas.composicao(v), larg_p, nomes=False, titulo=v["nome"], rot_colunas=ROT_CURTO, alt_plot=alt_p, linhas_titulo=nl)}</div>'
                      for v in outros)
        cols = f' style="grid-template-columns:repeat({por_fila},1fr);gap:4mm"' if pdf else ""
        corpo += f'<div class="multiplos"{cols}>{peq}</div>'
    cada = f"cada {un}" if un else "cada venda"
    return {"id": "composicao", "pergunta": f"Para onde vai o preço de {cada}: na venda perfeita, com a política e com o desconto tático",
            "manchete": "", "html": f'<div class="estatico">{corpo}</div>'}


def bloco_dre_venda(c, pdf=False):
    ords = ordem(c)
    un = uma_unidade(c)
    if pdf:
        i = ords[0]
        v = c["vendas"][i]
        return {"id": "dre_venda", "pergunta": f"DRE da venda · por {v['unidade']} de {v['nome']}", "manchete": "",
                "html": tabela_venda(c, i, pdf=True)}
    abas = ""
    if len(ords) > 1:
        abas = '<div class="abas" role="tablist">' + "".join(
            f'<button type="button" role="tab" data-aba="{i}" aria-selected="{"true" if k == 0 else "false"}">'
            f'{esc(c["vendas"][i]["nome"])}</button>' for k, i in enumerate(ords)) + "</div>"
    corpo = "".join(f'<div class="dre-venda" data-i="{i}"{"" if k == 0 else " hidden"}>'
                    + ("" if un else f'<p class="un">Por {esc(c["vendas"][i]["unidade"])}</p>')
                    + f'{tabela_venda(c, i)}</div>' for k, i in enumerate(ords))
    return {"id": "dre_venda", "pergunta": f"DRE da venda · por {un}" if un else "DRE da venda · uma unidade de cada produto",
            "manchete": "", "html": abas + corpo}


def bloco_dre_mes(c, pdf=False):
    m = c["mes"]
    o, r = m["orcado"], m["realizado"]
    manch = f"Orçado {rs(o['mc'])}, realizado {rs(r['mc'])} de margem de contribuição"
    if m["tem_fixo"]:
        nome = "lucro líquido" if m["tem_ir"] else "resultado"
        manch += f"; o {nome} fica em {rs(r['final'])}, contra {rs(o['final'])} orçados."
    else:
        manch += "."
    return {"id": "dre_mes", "pergunta": "DRE do mês · orçado no preço teto contra realizado", "manchete": "",
            "html": tabela_mes(c, pdf)}


def _cel(V, k, f="rs", pdf=False, ed=None, s=None):
    """Uma célula de número das conclusões, com a chave para o painel recalcular."""
    if ed is not None:
        return f'<td class="v">{_input(ed, V, pdf)}</td>'
    v = V.get(k)
    if s:
        txt, cls = desvio(v, f, s)
        return f'<td class="dsv {cls}" data-dv="{esc(k)}" data-sinal="1" data-f="{f}" data-s="{s}">{txt}</td>'
    return f'<td class="v" data-k="{esc(k)}" data-f="{f}">{esc(fmt(v, f))}</td>'


def _produto(v, un):
    """O nome do produto na tabela; com unidades diferentes, a unidade vai junto."""
    return esc(v["nome"]) + ("" if un else f'<small>por {esc(v["unidade"])}</small>')


def bloco_precos(c, pdf=False):
    """O preço pelo qual cada produto deve ser vendido, contra o que foi negociado."""
    V = valores(c)
    m = c["mes"]
    un = uma_unidade(c)
    corpo = []
    for i in ordem(c):
        v = c["vendas"][i]
        dsv_txt, cls = desvio(v["negociado"] - v["topo"]["preco"], "rs", "+")
        corpo.append(f'<tr><td class="n0">{_produto(v, un)}</td>{_cel(V, f"v{i}.teto")}{_cel(V, f"v{i}.usado")}'
                     f'{_cel(V, f"v{i}.neg")}<td class="dsv {cls}" data-da="v{i}.teto" data-db="v{i}.neg" data-f="rs" '
                     f'data-s="+">{dsv_txt}</td>{_cel(V, f"v{i}.minimo")}</tr>')
    cab = f"Por {esc(un)}" if un else "Produto"
    tab = (f'<div class="tw"><table class="dre conc"><thead><tr><th class="n0">{cab}</th><th>Preço teto</th>'
           f'<th>Preço da política</th><th>Preço negociado</th><th>Desvio</th><th>Preço mínimo<br>margem zero</th></tr></thead>'
           f'<tbody>{"".join(corpo)}</tbody></table></div>')
    manch = (f"No preço teto, a margem de contribuição do mês seria {rs(m['orcado']['mc'])}; "
             f"nos preços negociados, foi {rs(m['realizado']['mc'])}.")
    return {"id": "precos", "pergunta": "Por quanto vender cada produto", "manchete": manch, "html": tab}


def _q(x):
    return br(x, 2)


def _junta(itens):
    return itens[0] if len(itens) == 1 else ", ".join(itens[:-1]) + " e " + itens[-1]


def frase_a_mais(c):
    """A conclusão das vendas a mais em uma frase, na unidade de cada linha."""
    a = c["amais"]
    un = uma_unidade(c)
    nunca = [x["nome"] for x in a["linhas"] if x["nec"] is None]
    t = a["total"]
    uns = {x["nome"]: plural(v["unidade"] or "unidade") for x, v in zip(a["linhas"], c["vendas"])}
    nada = (f" Em {_junta(nunca)}, nenhum volume compensa: com os descontos, a venda não deixa margem de contribuição."
            if nunca else "")
    if t["amais"] is None:
        return nada.strip()
    # a mais que some no arredondamento do preço (menos de 0,05% do volume) não é esforço: é ruído
    mais = [x for x in a["linhas"] if x["amais"] is not None and x["amais"] > D("0.005") and x["pct"] >= D("0.05")]
    if un is None:
        # unidades diferentes não se somam: a frase fala de cada linha, e o total vai em reais
        if not mais:
            return ("Nos preços negociados, nenhum produto precisa vender mais para deixar a margem de contribuição da "
                    "venda perfeita." + nada)
        partes = [f"{_q(x['amais'])} {uns[x['nome']]} a mais em {x['nome']} ({pc(x['pct'])})" for x in mais]
        frase = f"Com os descontos de hoje, a mesma margem da venda perfeita pede {_junta(partes)}."
        if t["esforco"] > D("0.005"):
            frase += f" No mês, são {rs(t['esforco'])} de receita a mais para o mesmo lucro líquido."
        return frase + nada
    uns_ = plural(un)
    if t["amais"] > D("0.005") and t["pct"] >= D("0.05"):
        frase = (f"Com os descontos de hoje, o mês precisa de {_q(t['amais'])} {uns_} a mais "
                 f"({pc(t['pct'])} do volume, {rs(t['esforco'])} de receita) para a mesma margem e o mesmo lucro "
                 "líquido da venda perfeita.")
    elif t["amais"] < -D("0.005") and t["pct"] <= -D("0.05"):
        frase = (f"Nos preços negociados, o mês já deixa mais margem que a venda perfeita: bastariam {_q(-t['amais'])} "
                 f"{uns_} a menos para o mesmo lucro líquido.")
        if mais:
            x = max(mais, key=lambda y: y["pct"])
            frase += f" {x['nome']} é a exceção: precisa de {_q(x['amais'])} {uns_} a mais ({pc(x['pct'])})."
    else:
        frase = "Sem desconto a compensar: o volume de hoje já deixa a margem de contribuição da venda perfeita."
    return frase + nada


def bloco_a_mais(c, pdf=False):
    V = valores(c)
    a = c["amais"]
    un = uma_unidade(c)
    corpo = []
    for i in ordem(c):
        x, v = a["linhas"][i], c["vendas"][i]
        ed = campo(f"linhas.{i}.quantidade", x["q"], i)
        if x["nec"] is None:
            resto = '<td class="v" colspan="4">nenhum volume compensa</td>'
        else:
            resto = (_cel(V, f"v{i}.nec") + _cel(V, f"v{i}.amais", s="-") + _cel(V, f"v{i}.amais_pct", "pq", s="-")
                     + _cel(V, f"v{i}.esforco"))
        nome = esc(x["nome"]) + ("" if un else f'<small>em {esc(plural(v["unidade"] or "unidade"))}</small>')
        corpo.append(f'<tr><td class="n0">{nome}</td>{_cel(V, None, pdf=pdf, ed=ed)}{resto}</tr>')
    if len(a["linhas"]) > 1:
        t = a["total"]
        if t["nec"] is None:
            resto = '<td class="v" colspan="4"></td>'
        elif un:
            resto = _cel(V, "t.nec") + _cel(V, "t.amais", s="-") + _cel(V, "t.amais_pct", "pq", s="-") + _cel(V, "t.esforco")
        else:
            resto = '<td class="v"></td><td class="dsv"></td><td class="dsv"></td>' + _cel(V, "t.esforco")
        q = _cel(V, "t.q") if un else '<td class="v"></td>'
        corpo.append(f'<tr class="tot"><td class="n0">Total</td>{q}{resto}</tr>')
    cab = f"No mês, em {esc(plural(un))}" if un else "No mês"
    tab = (f'<div class="tw"><table class="dre conc"><thead><tr><th class="n0">{cab}</th>'
           f'<th>Vendidas</th><th>Necessárias</th><th>A mais</th><th>% a mais</th><th>Esforço em R$</th></tr></thead>'
           f'<tbody>{"".join(corpo)}</tbody></table></div>')
    ok = [a["linhas"][i] for i in ordem(c) if a["linhas"][i]["nec"] is not None]
    if un:
        itens, f_, rp, rr = [(x["nome"], x["nec"], x["q"]) for x in ok], _q, "necessárias", "vendidas"
    else:
        # em unidades diferentes, a régua comum é o volume de hoje: vendidas é 100%
        itens = [(x["nome"], x["nec"] / x["q"] * CEM, CEM) for x in ok if x["q"]]
        f_, rp, rr = (lambda y: br(y, 1) + "%"), "necessárias", "vendidas"

    def graf(larg):
        return formas.pares(itens, larg, formato=f_, rot_plan=rp, rot_real=rr)
    desenho = ""
    if itens:
        desenho = graf(A4) if pdf else _duplo(graf)
        desenho = f'<div class="estatico">{desenho}</div>'
    return {"id": "a_mais", "pergunta": "Quantas vendas a mais para o mesmo resultado no bolso",
            "manchete": frase_a_mais(c), "html": desenho + tab}


def blocos(c, pdf=False):
    # por ora a entrega é só as duas DREs: sem gráfico, manchete, conclusão nem próximo passo
    return [bloco_dre_venda(c, pdf), bloco_dre_mes(c, pdf)]


SECAO = {"composicao": "Como o preço se compõe", "dre_venda": "DRE da venda", "dre_mes": "DRE do mês",
         "precos": "Conclusões", "a_mais": "Conclusões"}


# ------------------------------------------------------------------ o painel

def fonte_de(cen):
    return cen.get("fonte") or "números da conversa"


def e_bunker(cen):
    return str(cen.get("cliente") or "").strip().lower() == "bunker"


def titulos(cen):
    """O título e o subtítulo. Quando o cliente é a própria Bunker, a logo já diz a marca e o
    título é o da análise; o prefixo "cliente · " do título do cenário não se repete."""
    cliente = cen.get("cliente")
    tit = cen.get("titulo") or ""
    if cliente and tit.lower().startswith(cliente.lower() + " · "):
        tit = tit[len(cliente) + 3:]
    if e_bunker(cen) or not cliente:
        h1 = TITULO if e_bunker(cen) or not tit else tit
        sub = [tit if h1 != tit else None, cen.get("subtitulo")]
    else:
        h1 = cliente
        sub = [tit, cen.get("subtitulo")]
    return h1, [s for s in sub if s]


def rodape(cen, c, extra=""):
    partes = [f"Fonte: {esc(fonte_de(cen))}"]
    if cen.get("nome_cenario"):
        partes.append(f"cenário: {esc(cen['nome_cenario'])}")
    partes.append("valores em 2 casas; a conta roda em 4")
    if not c["mes"]["tem_fixo"]:
        partes.append("sem despesas fixas informadas, a DRE do mês para na margem de contribuição")
    partes.append(esc(cen.get("data") or ""))
    return " · ".join(p for p in partes if p) + extra


def css_duplo():
    return '.so-estreito{display:none}@media(max-width:860px){.so-largo{display:none}.so-estreito{display:block}}\n'


def _motor_js():
    with open(os.path.join(ASSETS, "simulador.html"), encoding="utf-8") as f:
        s = f.read()
    return s.split("/*MOTOR*/")[1].split("/*FIM-MOTOR*/")[0]


def _painel_js():
    with open(os.path.join(ASSETS, "painel.js"), encoding="utf-8") as f:
        return f.read()


def _cenario_json(cen):
    """O cenário do painel, para o navegador recalcular. Decimal vira número do JSON."""
    def conv(x):
        if isinstance(x, D):
            return float(x)
        raise TypeError(type(x))
    limpo = {k: v for k, v in cen.items() if k != "cenarios"}
    return json.dumps(limpo, ensure_ascii=False, default=conv).replace("</", "<\\/")


def painel(caminho, indice=0, agora=None):
    raiz, cens, i = ler(caminho, indice)
    cen = dict(cens[i])
    agora = agora or _dt.datetime.now()
    cen.setdefault("data", agora.strftime("%d/%m/%Y"))
    _marca(cen)
    c = montar_conta(cen)
    html_blocos = [pagina.secao(x["pergunta"], x["manchete"], x["html"], larga=True, classe=x["id"]) for x in blocos(c)]
    h1, sub = titulos(cen)
    if cen.get("nome_cenario"):
        sub.append(cen["nome_cenario"])
    barra = ('<div class="editado" hidden><span>Números editados. Os gráficos seguem o cenário original.</span>'
             '<button type="button">Voltar ao cenário</button></div>')
    script = (f'<script id="cenario-painel" type="application/json">{_cenario_json(cen)}</script>\n'
              f'<script>{_motor_js()}\n{_painel_js()}</script>')
    doc = pagina.documento(h1, html_blocos, sub=" · ".join(sub), quando=cen["data"],
                           rodape=rodape(cen, c, " · Método da Bunker de formação e leitura de preço · bunkerconsultancy.com"),
                           fim=barra + script)
    return doc.replace("</style>", css_duplo() + "</style>", 1), cen, c, cens


def _marca(cen):
    m = cen.get("marca") or {}
    if m.get("primaria") and m.get("secundaria"):
        paleta.definir_marca(m["primaria"], m["secundaria"])
    else:
        paleta.definir_marca(*paleta.BUNKER)


# ------------------------------------------------------------------ o PDF

def _escada(degrau, alt=250):
    """Os três degraus do próximo passo, em escada, com o degrau do cliente aceso."""
    larg = A4 + 24
    p = [f'<svg viewBox="0 0 {larg} {alt}" width="100%" role="img" aria-label="Três degraus do próximo passo; o do cliente é o {degrau}" '
         'xmlns="http://www.w3.org/2000/svg">']
    w = (larg - 24) / 3
    for k in range(3):
        h = alt * (0.28 + k * 0.24)
        x, y = k * (w + 12), alt - h
        aceso = k + 1 == degrau
        cor = paleta.destaque() if aceso and paleta.destaque() != "#0a0a0a" else ("#ffffff" if aceso else "#2a2a2a")
        txt = "#0a0a0a" if aceso and cor == "#ffffff" else "#ffffff"
        p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{cor}" rx="3"/>')
        p.append(f'<text x="{x + 16:.1f}" y="{y + 34:.1f}" font-size="26" font-weight="900" fill="{txt}">{k + 1}</text>')
        if aceso:
            p.append(f'<text x="{x + w - 14:.1f}" y="{y + 30:.1f}" text-anchor="end" font-size="10.5" font-weight="700" '
                     f'fill="{txt}" letter-spacing="0.08em">VOCÊ ESTÁ AQUI</text>')
    p.append('</svg>')
    return ''.join(p)


def folhas(cen, c, agora):
    fonte_txt = fonte_de(cen)
    h1, sub = titulos(cen)
    data = cen.get("data") or agora.strftime("%d/%m/%Y")
    pe = esc(f"Fonte: {fonte_txt}" + (f" · cenário: {cen['nome_cenario']}" if cen.get("nome_cenario") else ""))
    seq = [(SECAO[x["id"]], pagina.bloco_folha(x["pergunta"], x["manchete"], x["html"])) for x in blocos(c, pdf=True)]
    degrau = porte(cen, c["res"])
    itens = []
    for k, (tit, txt) in enumerate(DEGRAUS, start=1):
        extra_txt = f" {PD}" if k == 3 and degrau == 3 else ""
        cls = ' style="color:#ffffff"' if k == degrau else ' style="color:#9a9a9a"'
        itens.append(f'<div{cls}><b style="display:block;font-size:12px;margin-bottom:3px">{k}. {esc(tit)}</b>'
                     f'<span style="font-size:10.5px;line-height:1.45">{esc(txt + extra_txt)}</span></div>')
    grade = f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:5mm;position:relative">{"".join(itens)}</div>'
    # o fecho entra como um bloco escuro no fim da última folha, quando cabe; senão, ganha a folha preta dele
    caixa = (f'<div class="bloco fecho-caixa"><h3>O próximo passo</h3><p>Proporcional ao tamanho da operação. '
             f'O degrau aceso é o desta operação.</p>{_escada(degrau, 150)}{grade}</div>')
    conteudo = compor(seq, pe)
    fecho_proprio = False
    total = len(conteudo) + 1
    out = []
    # capa: com o título da análise no h1, o rótulo de cima fica só com a data
    rot = esc(data) if h1 == TITULO else f"{TITULO} · {esc(data)}"
    out.append(f'''<section class="folha capa"><img class="b" src="{marca.b_outline(branco=True)}" alt="">
<img class="logo" src="{marca.logo_branco()}" alt="Bunker">
<div class="rot">{rot}</div>
<h1>{esc(h1)}</h1>
<p class="sub">{esc(" · ".join(sub))}</p>
<div class="pe"><span>Método da Bunker · {marca.CASA} · {marca.SITE}</span><span>Confidencial · uso do cliente</span></div></section>''')
    for n, (tits, bls) in enumerate(conteudo, start=2):
        out.append(pagina.folha("".join(bls), " · ".join(dict.fromkeys(tits)), pe, n, total))
    if fecho_proprio:
        out.append(f'''<section class="folha fecho"><img class="b" src="{marca.b_outline(branco=True)}" alt="">
<img class="logo" src="{marca.logo_branco()}" alt="Bunker">
<h1>O próximo passo</h1>
<p class="sub">Proporcional ao tamanho da operação. O degrau aceso é o desta operação.</p>
{_escada(degrau)}
{grade}
<div class="pe"><span>Método da Bunker · {marca.CASA} · {marca.SITE}</span><span>{total} / {total}</span></div></section>''')
    return pagina.documento_folhas(f"{h1} · leitura de preço", out), total


_MEDIR_BLOCOS = r"""<script>
addEventListener('load', function () { setTimeout(function () {
  var f = document.querySelector('.folha'), pe = f.querySelector('.pe'), ini = document.getElementById('ini');
  var r = {livre: pe.getBoundingClientRect().top - ini.getBoundingClientRect().top, blocos: []};
  document.querySelectorAll('#medir > .bloco').forEach(function (b) {
    r.blocos.push(b.getBoundingClientRect().height + parseFloat(getComputedStyle(b).marginBottom)); });
  var p = document.createElement('pre'); p.id = 'medida'; p.textContent = JSON.stringify(r); document.body.appendChild(p);
}, 200); });
</script>"""


def _medir_blocos(blocos_, pe):
    """A altura de cada bloco na coluna da A4 e o espaço livre de uma folha, medidos no Chrome."""
    exe = saida.achar_chrome()
    if not exe:
        return None
    folha = pagina.folha('<div id="ini"></div>', "medida", pe, 1, 1)
    medir = ('<div id="medir" style="position:absolute;left:0;top:0;width:174mm;visibility:hidden">'
             + "".join(blocos_) + "</div>")
    html = pagina.documento_folhas("medida", [folha]).replace("</body>", medir + _MEDIR_BLOCOS + "</body>")
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        tmp = f.name
    try:
        r = subprocess.run([exe, "--headless=new", "--disable-gpu", "--window-size=794,1123", "--virtual-time-budget=8000",
                            "--dump-dom", "file://" + tmp], capture_output=True, text=True)
    finally:
        os.remove(tmp)
    m = re.search(r'<pre id="medida">(.*?)</pre>', r.stdout, re.S)
    return json.loads(m.group(1).replace("&quot;", '"')) if m else None


def compor(seq, pe):
    """Distribui os blocos pelas folhas sem deixar folha meio vazia: cada bloco vai para a
    primeira folha aberta em que ele cabe, na ordem da leitura. Sem Chrome para medir, uma
    seção por folha."""
    med = _medir_blocos([h for _, h in seq], pe)
    if not med:
        folhas_ = []
        for t, h in seq:
            if not folhas_ or folhas_[-1][0][-1] != t:
                folhas_.append(([t], []))
            folhas_[-1][1].append(h)
        return folhas_
    livre = med["livre"] - 4
    folhas_ = []   # [titulos, blocos, usado]
    for (t, h), alto in zip(seq, med["blocos"]):
        # a leitura segue em ordem: o bloco só entra na última folha aberta, nunca volta
        f = folhas_[-1] if folhas_ else None
        if f and f[2] + alto <= livre:
            f[0].append(t)
            f[1].append(h)
            f[2] += alto
        else:
            folhas_.append([[t], [h], alto])
    return [(f[0], f[1]) for f in folhas_]


_MEDIR_FOLHAS = r"""<script>
addEventListener('load', function () { setTimeout(function () {
  var r = []; document.querySelectorAll('.folha').forEach(function (f, k) {
    var pe = f.querySelector('.pe'), ult = null;
    Array.prototype.forEach.call(f.children, function (e) { if (e !== pe && !e.classList.contains('b')) ult = e; });
    var sobra = pe && ult ? pe.getBoundingClientRect().top - ult.getBoundingClientRect().bottom : 0;
    var fb = f.getBoundingClientRect().bottom, pb = pe ? pe.getBoundingClientRect().bottom : fb;
    r.push({k: k + 1, passa: Math.round(pb - fb), sobra: Math.round(sobra)}); });
  var p = document.createElement('pre'); p.id = 'medida'; p.textContent = JSON.stringify(r); document.body.appendChild(p);
}, 200); });
</script>"""


def transbordo(html_path):
    """As folhas cujo conteúdo não cabe na A4: com `overflow:hidden`, o Chrome cortaria calado."""
    exe = saida.achar_chrome()
    if not exe:
        return []
    with open(html_path, encoding="utf-8") as f:
        fonte = f.read().replace("</body>", _MEDIR_FOLHAS + "</body>")
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, dir=os.path.dirname(os.path.abspath(html_path)),
                                     encoding="utf-8") as f:
        f.write(fonte)
        tmp = f.name
    try:
        r = subprocess.run([exe, "--headless=new", "--disable-gpu", "--window-size=794,1123", "--virtual-time-budget=8000",
                            "--dump-dom", "file://" + tmp], capture_output=True, text=True)
    finally:
        os.remove(tmp)
    m = re.search(r'<pre id="medida">(.*?)</pre>', r.stdout, re.S)
    if not m:
        return []
    return [x for x in json.loads(m.group(1).replace("&quot;", '"')) if x["passa"] > 1 or x["sobra"] < 0]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Painel editável e PDF A4 da leitura de preço.")
    ap.add_argument("cenario", help="o JSON do cenário (references/simulador.md)")
    ap.add_argument("--painel", help="HTML do painel; o padrão é o nome do cenário com .painel.html")
    ap.add_argument("--pdf", help="grava também o PDF A4 de entrega nesse caminho")
    ap.add_argument("--cenario", dest="indice", type=int, default=1, help="qual cenário do arquivo, a partir de 1")
    a = ap.parse_args(argv)
    agora = _dt.datetime.now()
    doc, cen, c, _ = painel(a.cenario, a.indice - 1, agora)
    destino = a.painel or os.path.splitext(a.cenario)[0] + ".painel.html"
    with open(destino, "w", encoding="utf-8") as f:
        f.write(doc)
    m = c["mes"]
    print(f"Painel gravado em {destino}.")
    print(f"Margem planejada {rs(m['orcado']['mc'])}, realizada {rs(m['realizado']['mc'])}.")
    if a.pdf:
        html_folhas, total = folhas(cen, c, agora)
        base = os.path.splitext(a.pdf)[0]
        imprimir = base + ".imprimir.html"
        with open(imprimir, "w", encoding="utf-8") as f:
            f.write(html_folhas)
        if not saida.achar_chrome():
            print(f"Sem Chrome nesta máquina: o HTML das folhas A4 está em {imprimir}. Abra no navegador e imprima em A4, "
                  "margens: nenhuma, com os gráficos de fundo ligados.")
            return 0
        ruins = transbordo(imprimir)
        if ruins:
            raise SystemExit(f"Folhas que não cabem na A4: {ruins}. Nada foi gravado em {a.pdf}.")
        saida.para_pdf(imprimir, a.pdf, esperadas=total)
        os.remove(imprimir)
        print(f"PDF gravado em {a.pdf}: {total} folhas A4.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
