#!/usr/bin/env python3
"""Régua de preço em níveis e o simulador HTML que abre no navegador.

Lê um cenário em JSON (uma ou mais linhas de venda), forma o preço de cada nível, lê a margem
realizada contra cada régua e grava um HTML autocontido, com o simulador editável dentro.
Só usa a biblioteca padrão do Python 3.8 ou mais novo, e a conta é a de `preco.py`.

Os níveis, do mais largo ao mais específico:
    teto        margem planejada global, o maior preço
    canal       margem planejada menor, combinada antes para um grupo de clientes (não é desconto)
    específico  preço ou margem própria de uma conta, rede ou contrato; ou a tabela de hoje
    tático      o desconto do vendedor sobre o preço do nível usado
Nível usado = o mais específico que existir na linha.

Três leituras de desvio da margem realizada: contra o nível usado (o custo do desconto),
contra o canal (o efeito do preço específico) e contra o teto (o que ficou na mesa).
Cada uma em pontos, relativo e em reais, por linha e no consolidado.

Uso:
    python3 simulador.py cenario.json                      grava cenario.html e abre no navegador
    python3 simulador.py cenario.json --saida painel.html  escolhe o arquivo
    python3 simulador.py cenario.json --nao-abrir          só grava
    python3 simulador.py cenario.json --json               imprime os números em JSON

O formato do cenário está em references/simulador.md.
"""

import argparse
import base64
import datetime as _dt
import html
import json
import os
import shutil
import subprocess
import sys
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import preco  # noqa: E402
from preco import CEM, ZERO, D, r2, r4, dre, formar, margem_maxima, desvio_de  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
MODELO = os.path.join(AQUI, "..", "assets", "simulador.html")
LOGO = os.path.join(AQUI, "..", "assets", "bunker-logo-branco.png")

ROTULOS = {"teto": "Teto", "canal": "Canal", "especifico": "Específico"}


def dec(x):
    if x is None or x == "":
        return None
    return preco.dec(x)


def _num(x):
    """Converte o que vier do JSON para Decimal, pela forma escrita do número."""
    return dec(repr(x) if isinstance(x, float) else x)


def premissas_de(linha, cen):
    """Premissas de uma linha, no formato de preco.Premissas."""
    impostos = linha.get("impostos") or {}
    frete_rs = _num(linha.get("frete_rs", 0)) or ZERO
    if linha.get("frete_rs_kg") is not None:
        frete_rs += _num(linha["frete_rs_kg"]) * _num(linha.get("peso_kg", 1))
    ns = argparse.Namespace(
        produto=linha.get("nome"),
        unidade=cen.get("unidade"),
        quantidade=str(_num(linha.get("quantidade", 1))),
        custo=str(_num(linha["custo"])),
        impostos=None,
        imposto=[f"{k}={_num(v)}" for k, v in impostos.items()] or None,
        comissao=str(_num(linha.get("comissao", 0))),
        comissao_sobre=linha.get("comissao_sobre", "bruta"),
        frete=str(_num(linha.get("frete_pct", 0))),
        frete_valor=str(frete_rs),
        outras=str(_num(linha.get("outras_pct", 0))),
        outras_valor=str(_num(linha.get("outras_rs", 0))),
        margem=None,
        por_fora=[f"{f['nome']}={_num(f['aliq'])}" + (":sem_icms_iss" if f.get("base") == "sem_icms_iss" else "")
                  for f in linha.get("por_fora") or []] or None,
        atividade=cen.get("atividade"),
        hipotese=list(cen.get("hipoteses") or []) + list(linha.get("hipoteses") or []),
    )
    p = preco.Premissas(ns)
    if not impostos:
        p.impostos = {"Impostos sobre a venda": ZERO}
    return p


def faixa(mantido, mc):
    """Régua de cor: mais de 70% da margem planejada mantida vai bem; de 50 a 70, atenção."""
    if mc is not None and mc <= 0:
        return "critico"
    if mantido is None:
        return "neutro"
    if mantido > 70:
        return "bom"
    if mantido >= 50:
        return "atencao"
    return "critico"


def calcular_linha(linha, cen):
    p = premissas_de(linha, cen)
    rot = dict(ROTULOS, **(cen.get("rotulos") or {}))
    mc_teto = _num(linha.get("mc_teto", cen.get("mc_teto")))
    mc_canal = _num(linha.get("mc_canal"))
    avisos = []
    niveis = []
    if mc_teto is not None:
        pt = formar(p, mc_teto)
        if pt is None:
            avisos.append("Não existe preço no teto: " + " ".join(preco.explicar_impossivel(p)[1:2]))
        else:
            niveis.append({"chave": "teto", "rotulo": rot["teto"], "preco": pt, "mc_plan": mc_teto})
    if mc_canal is not None:
        pc = formar(p, mc_canal)
        if pc is None:
            avisos.append("Não existe preço no canal com essas premissas.")
        else:
            niveis.append({"chave": "canal", "rotulo": linha.get("rotulo_canal") or rot["canal"],
                           "preco": pc, "mc_plan": mc_canal})
    rot_esp = linha.get("rotulo_especifico") or rot["especifico"]
    if linha.get("preco_especifico") is not None:
        pe = r2(_num(linha["preco_especifico"]))
        niveis.append({"chave": "especifico", "rotulo": rot_esp, "preco": pe, "mc_plan": margem_maxima(p, pe)})
    elif linha.get("mc_especifica") is not None:
        me = _num(linha["mc_especifica"])
        pe = formar(p, me)
        if pe is None:
            avisos.append("Não existe preço específico com essas premissas.")
        else:
            niveis.append({"chave": "especifico", "rotulo": rot_esp, "preco": pe, "mc_plan": me})
    if not niveis:
        raise SystemExit(f"Linha {linha.get('nome')!r}: informe mc_teto, mc_canal, mc_especifica ou preco_especifico.")

    usado = niveis[-1]
    desc = _num(linha.get("desconto", 0)) or ZERO
    if linha.get("preco_praticado") is not None:
        negociado = r2(_num(linha["preco_praticado"]))
    else:
        negociado = r2(usado["preco"] * (1 - desc / CEM))
    custo_real = _num(linha.get("custo_real"))
    real = dre(negociado, p, custo=custo_real)
    mesmo_custo = dre(negociado, p) if custo_real is not None else real
    for n in niveis:
        n["dre"] = dre(n["preco"], p)

    por = {n["chave"]: n for n in niveis}
    refs = {"usado": usado["mc_plan"]}
    if "canal" in por:
        refs["canal"] = por["canal"]["mc_plan"]
    elif "teto" in por:
        refs["canal"] = por["teto"]["mc_plan"]
    if "teto" in por:
        refs["teto"] = por["teto"]["mc_plan"]
    leituras = {k: desvio_de(v, real) for k, v in refs.items()}

    # cascata do teto ao realizado: receita bruta e margem em R$, na quantidade da linha
    passos = []
    ant = None
    for n in niveis:
        passos.append((n["chave"], n["rotulo"], n["dre"]["rb"], n["dre"]["mc"]))
    passos.append(("tatico", "Desconto do vendedor", mesmo_custo["rb"], mesmo_custo["mc"]))
    if custo_real is not None:
        passos.append(("custo", "Custo real", real["rb"], real["mc"]))
    cascata = []
    for chave, rotulo, rb, mc in passos:
        cascata.append({"chave": chave, "rotulo": rotulo, "rb": rb, "mc": mc,
                        "delta_rb": None if ant is None else rb - ant[0],
                        "delta_mc": None if ant is None else mc - ant[1]})
        ant = (rb, mc)

    mantido = None
    if usado["mc_plan"] is not None and usado["mc_plan"] > 0 and real["mc_rl"] is not None:
        mantido = real["mc_rl"] / usado["mc_plan"] * CEM
    mercado = None
    if linha.get("preco_mercado") is not None:
        pm = r2(_num(linha["preco_mercado"]))
        mercado = {"preco": pm, "mc_max": margem_maxima(p, pm)}
    return {
        "nome": linha.get("nome") or "Linha",
        "grupo": linha.get("grupo"),
        "p": p,
        "niveis": niveis,
        "usado": usado,
        "negociado": negociado,
        "desconto_rs": usado["preco"] - negociado,
        "real": real,
        "leituras": leituras,
        "refs": refs,
        "cascata": cascata,
        "faixa": faixa(mantido, real["mc"]),
        "mantido": mantido,
        "mercado": mercado,
        "minimo": formar(p, ZERO),
        "avisos": avisos + real["avisos"],
    }


def consolidar(linhas):
    """Soma as linhas. A margem planejada de cada régua é ponderada pela receita líquida realizada."""
    rb = sum((l["real"]["rb"] for l in linhas), ZERO)
    rl = sum((l["real"]["rl"] for l in linhas), ZERO)
    mc = sum((l["real"]["mc"] for l in linhas), ZERO)
    mc_rl = mc / rl * CEM if rl > 0 and rb > 0 else None
    leituras = {}
    for k in ("usado", "canal", "teto"):
        if not all(k in l["refs"] and l["refs"][k] is not None for l in linhas) or mc_rl is None:
            continue
        plan = sum((l["real"]["rl"] * l["refs"][k] for l in linhas), ZERO) / rl
        pts = r4(mc_rl - plan)
        rel = None if plan == 0 else r4((mc_rl / plan - 1) * CEM)
        leituras[k] = {"plan": plan, "pts": pts, "rel": rel, "rs": r4(rl * pts / CEM)}
    # cascata: cada linha entra com o preço de cada nível; sem canal, o canal é o teto; sem específico, é o canal
    ordem = ["teto", "canal", "especifico", "tatico"]
    tem = {k: any(any(c["chave"] == k for c in l["cascata"]) for l in linhas) for k in ordem}
    tem["tatico"] = True
    cascata = []
    for k in ordem:
        if not tem[k]:
            continue
        srb = smc = ZERO
        for l in linhas:
            c = _valor_no_nivel(l["cascata"], k, ordem)
            srb += c["rb"]
            smc += c["mc"]
        cascata.append({"chave": k, "rb": srb, "mc": smc})
    if any(any(c["chave"] == "custo" for c in l["cascata"]) for l in linhas):
        cascata.append({"chave": "custo", "rb": rb, "mc": mc})
    return {"rb": rb, "rl": rl, "mc": mc, "mc_rl": mc_rl, "mc_rb": mc / rb * CEM if rb > 0 else None,
            "leituras": leituras, "cascata": cascata}


def _valor_no_nivel(cascata, chave, ordem):
    """O valor da linha num nível; se a linha não tem esse nível, vale o nível de cima."""
    por = {c["chave"]: c for c in cascata}
    if chave in por:
        return por[chave]
    i = ordem.index(chave)
    for k in reversed(ordem[:i]):
        if k in por:
            return por[k]
    return cascata[0]


def equilibrio(cen, linhas, total):
    """Outra conta, fora da margem de contribuição: o custo fixo do mês e o lucro que sobra."""
    fixo = _num(cen.get("custo_fixo_mes"))
    if fixo is None:
        return None
    out = {"fixo": fixo, "lucro": total["mc"] - fixo}
    out["lucro_pct_rb"] = out["lucro"] / total["rb"] * CEM if total["rb"] > 0 else None
    if total["mc"] > 0 and total["rb"] > 0:
        out["receita_pe"] = r2(fixo / (total["mc"] / total["rb"]))
    else:
        out["receita_pe"] = None
    if len(linhas) == 1:
        l = linhas[0]
        q = l["p"].qtd
        mc_un = l["real"]["mc"] / q if q else ZERO
        out["unidades_pe"] = (fixo / mc_un) if mc_un > 0 else None
        meta = _num(cen.get("meta_lucro_pct"))
        if meta is not None:
            p = l["p"]
            div = CEM - p.variaveis_pct() - meta
            out["meta_lucro_pct"] = meta
            out["preco_meta"] = r2((p.custo + p.variaveis_rs() + fixo / q) / (div / CEM)) if div > 0 and q else None
    return out


def calcular(cen):
    linhas = [calcular_linha(l, cen) for l in cen["linhas"]]
    total = consolidar(linhas)
    return {"linhas": linhas, "total": total, "equilibrio": equilibrio(cen, linhas, total)}


# ------------------------------------------------------------------ números para conferir com o JS

def _s(x, casas=4):
    if x is None:
        return None
    q = x.quantize(D(1).scaleb(-casas), rounding=preco.ROUND_HALF_UP)
    if q == 0:
        q = abs(q)
    return f"{q:f}"


def numeros(res):
    """Os números que o simulador mostra, na escala em que ele mostra: preço em 2, leitura em 4."""
    out = {"linhas": []}
    for l in res["linhas"]:
        d = l["real"]
        out["linhas"].append({
            "niveis": [[n["chave"], _s(n["preco"], 2), _s(n["mc_plan"])] for n in l["niveis"]],
            "negociado": _s(l["negociado"], 2),
            "rb": _s(d["rb"]), "deducoes": _s(d["deducoes"]),
            "impostos": [_s(v) for _, v in d["impostos"]],
            "comissao": _s(d["despesas"]["comissao"]), "frete": _s(d["despesas"]["frete"]),
            "outras": _s(d["despesas"]["outras"]), "rl": _s(d["rl"]), "cpv": _s(d["cpv"]),
            "mc": _s(d["mc"]), "mc_rl": _s(d["mc_rl"]), "mc_rb": _s(d["mc_rb"]), "nota": _s(d["nota"]),
            "leituras": {k: (None if v is None else [_s(v[0]), _s(v[1]), _s(v[2])]) for k, v in l["leituras"].items()},
            "cascata": [[c["chave"], _s(c["rb"]), _s(c["mc"])] for c in l["cascata"]],
            "faixa": l["faixa"],
            "minimo": _s(l["minimo"], 2),
            "mercado": None if not l["mercado"] else [_s(l["mercado"]["preco"], 2), _s(l["mercado"]["mc_max"])],
        })
    t = res["total"]
    out["total"] = {
        "rb": _s(t["rb"]), "rl": _s(t["rl"]), "mc": _s(t["mc"]), "mc_rl": _s(t["mc_rl"]),
        "leituras": {k: [_s(v["plan"]), _s(v["pts"]), _s(v["rel"]), _s(v["rs"])] for k, v in t["leituras"].items()},
        "cascata": [[c["chave"], _s(c["rb"]), _s(c["mc"])] for c in t["cascata"]],
    }
    e = res["equilibrio"]
    out["equilibrio"] = None if not e else {
        "lucro": _s(e["lucro"]), "receita_pe": _s(e.get("receita_pe"), 2),
        "unidades_pe": _s(e.get("unidades_pe"), 2), "preco_meta": _s(e.get("preco_meta"), 2),
    }
    return out


# ------------------------------------------------------------------ texto do resumo

def resumo(cen, res):
    br, rs, pct = preco.br, preco.rs, preco.pct
    u = cen.get("unidade") or "unidade"
    out = [cen.get("titulo") or "Simulação de preço"]
    for l in res["linhas"]:
        out.append("")
        out.append(f"{l['nome']}" + (f" ({l['grupo']})" if l.get("grupo") else ""))
        for n in l["niveis"]:
            mc = "" if n["mc_plan"] is None else f", margem {pct(n['mc_plan'])} da receita líquida"
            out.append(f"  {n['rotulo']}: {rs(n['preco'])} por {u}{mc}")
        d = l["real"]
        out.append(f"  Nível usado: {l['usado']['rotulo']}. Negociado: {rs(l['negociado'])}"
                   + (f", desconto de {rs(l['desconto_rs'])}" if l["desconto_rs"] > 0 else ""))
        if d["mc_rl"] is None:
            out.append(f"  Margem realizada: {rs(d['mc'], 4)}; em % não se calcula, a receita líquida é zero ou negativa.")
        else:
            out.append(f"  Margem realizada: {rs(d['mc'], 4)}, {pct(d['mc_rl'])} da receita líquida, {pct(d['mc_rb'])} da receita bruta")
        nomes = {"usado": "contra o nível usado", "canal": "contra o canal", "teto": "contra o teto"}
        for k, v in l["leituras"].items():
            if v is None:
                continue
            if k == "canal" and "canal" not in {n["chave"] for n in l["niveis"]}:
                continue
            if k != "usado" and l["usado"]["chave"] == k:
                continue
            out.append(f"  Desvio {nomes[k]}: {preco.fmt_desvio(v)}")
        if d["mc"] < 0:
            out.append(f"  Cada venda tira {rs(-d['mc'], 4)} do caixa. Preço mínimo, com margem zero: {rs(l['minimo'])}.")
        if l["mercado"]:
            m = l["mercado"]
            if m["mc_max"] is None:
                out.append(f"  No preço de mercado, {rs(m['preco'])}, a venda não cobre o custo e as despesas.")
            else:
                out.append(f"  No preço de mercado, {rs(m['preco'])}, cabe no máximo {pct(m['mc_max'])} de margem.")
        for a in l["avisos"]:
            out.append("  Atenção: " + a)
    t = res["total"]
    if len(res["linhas"]) > 1 and t["mc_rl"] is not None:
        out.append("")
        out.append(f"Consolidado das {len(res['linhas'])} linhas: margem {rs(t['mc'], 4)}, {pct(t['mc_rl'])} da receita líquida")
        nomes_t = {"usado": "contra o nível usado", "canal": "contra o canal", "teto": "contra o teto"}
        for k, v in t["leituras"].items():
            out.append(f"  Desvio {nomes_t[k]}: {preco.pp(v['pts'])} contra {pct(v['plan'])}, "
                       + ("" if v["rel"] is None else f"{br(v['rel'])}% relativo, ") + preco.rs_sinal(v["rs"]))
    e = res["equilibrio"]
    if e:
        out.append("")
        out.append(f"Outra conta, abaixo da margem: custo fixo de {rs(e['fixo'])} no mês. Sobra {rs(e['lucro'], 2)} depois dele.")
        if e.get("receita_pe"):
            out.append(f"  Receita que paga o custo fixo: {rs(e['receita_pe'])} no mês.")
        if e.get("preco_meta"):
            out.append(f"  Preço para {pct(e['meta_lucro_pct'])} de lucro depois do custo fixo: {rs(e['preco_meta'])}.")
    out.append("")
    out.append("Margem de contribuição não é lucro. Números fiscais são hipótese até o contador confirmar.")
    return out


# ------------------------------------------------------------------ HTML

def apendice(cen, res):
    """DRE contábil de cada linha, estático, nos números da conversa."""
    partes = []
    for l in res["linhas"]:
        colunas = [(n["rotulo"], f"{preco.rs(n['preco'])} por {cen.get('unidade') or 'unidade'}", n["dre"]) for n in l["niveis"]]
        colunas.append(("Realizado", f"negociado, {preco.rs(l['negociado'])}", l["real"]))
        partes.append(f"<h3>{html.escape(l['nome'])}</h3>" + preco.tabela_dre(l["p"], colunas))
    return "".join(partes)


def gerar_html(cen, res=None, apendice_html=None):
    base = dict({k: v for k, v in cen.items() if k != "cenarios"}, **cen["cenarios"][0]) if "cenarios" in cen else cen
    res = res or calcular(base)
    with open(MODELO, encoding="utf-8") as f:
        pagina = f.read()
    dados = json.dumps(cen, ensure_ascii=False, indent=1).replace("</", "<\\/")
    ini = pagina.index('<script id="cenario" type="application/json">') + len('<script id="cenario" type="application/json">')
    fim = pagina.index("</script>", ini)
    pagina = pagina[:ini] + "\n" + dados + "\n" + pagina[fim:]
    if os.path.exists(LOGO):
        with open(LOGO, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        pagina = pagina.replace('<span class="marca-txt">Bunker</span>',
                                f'<img class="marca-img" alt="Bunker" src="data:image/png;base64,{b64}">', 1)
    pagina = pagina.replace("<!--APENDICE-->", apendice_html or apendice(base, res), 1)
    if cen.get("titulo"):
        pagina = pagina.replace("<title>Simulador de preço</title>",
                                f"<title>{html.escape(cen['titulo'])}</title>", 1)
    return pagina


def abrir(caminho):
    """Abre o HTML no navegador padrão: open no macOS, start no Windows, xdg-open no Linux."""
    if os.environ.get("BUNKER_PRICING_NAO_ABRIR"):
        return False
    caminho = os.path.abspath(caminho)
    try:
        if sys.platform == "darwin":
            subprocess.Popen(["open", caminho])
        elif sys.platform.startswith("win"):
            os.startfile(caminho)  # noqa: equivale a "start"
        elif shutil.which("xdg-open"):
            subprocess.Popen(["xdg-open", caminho], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            return False
    except OSError:
        return False
    return True


def gravar(cen, saida, nao_abrir=False, res=None, apendice_html=None):
    cen = dict(cen)
    cen.setdefault("data", _dt.datetime.now().strftime("%d/%m/%Y %H:%M"))
    with open(saida, "w", encoding="utf-8") as f:
        f.write(gerar_html(cen, res, apendice_html))
    aberto = False if nao_abrir else abrir(saida)
    if aberto:
        print(f"\nSimulador gravado em {saida} e aberto no navegador.")
    else:
        print(f"\nSimulador gravado em {saida}. Abra o arquivo no navegador.")
    return saida


def carregar(caminho):
    with open(caminho, encoding="utf-8") as f:
        cen = json.load(f)
    if "cenarios" in cen:
        herda = {k: v for k, v in cen.items() if k != "cenarios"}
        return cen, [dict(herda, **c) for c in cen["cenarios"]]
    return cen, [cen]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Régua de preço em níveis e simulador HTML.")
    ap.add_argument("cenario", help="arquivo JSON do cenário (veja references/simulador.md)")
    ap.add_argument("--saida", help="HTML a gravar; o padrão é o nome do cenário com .html")
    ap.add_argument("--nao-abrir", action="store_true", help="grava o HTML sem abrir o navegador")
    ap.add_argument("--json", action="store_true", help="imprime os números calculados em JSON")
    a = ap.parse_args(argv)
    raiz, cenarios = carregar(a.cenario)
    resultados = [calcular(c) for c in cenarios]
    if a.json:
        print(json.dumps([numeros(r) for r in resultados], ensure_ascii=False, indent=1))
    else:
        for c, r in zip(cenarios, resultados):
            if len(cenarios) > 1:
                print(f"\n=== {c.get('nome_cenario') or c.get('titulo')}")
            print("\n".join(resumo(c, r)))
    saida = a.saida or os.path.splitext(a.cenario)[0] + ".html"
    gravar(raiz, saida, a.nao_abrir, resultados[0] if len(cenarios) == 1 else None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
