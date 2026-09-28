"""A régua em níveis, o consolidado e a conferência do JS do simulador contra o Python.

Rodar: python3 -m unittest discover -s skills/bunker-pricing/scripts
O teste de paridade roda o motor do simulador no node; sem node na máquina, ele é pulado.
"""

import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal as D

os.environ["BUNKER_PRICING_NAO_ABRIR"] = "1"
sys.path.insert(0, os.path.dirname(__file__))
import simulador  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
MODELO = os.path.join(AQUI, "..", "assets", "simulador.html")
EXEMPLOS = os.path.join(AQUI, "..", "..", "..", "exemplos")
SIMULACOES = os.path.join(AQUI, "..", "..", "..", "simulacoes-v2")

NODE = r"""
const fs = require('fs');
const html = fs.readFileSync(process.argv[1], 'utf8');
const motor = html.split('/*MOTOR*/')[1].split('/*FIM-MOTOR*/')[0];
const Motor = new Function(motor + '; return Motor;')();
const cens = JSON.parse(fs.readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(cens.map(c => Motor.numeros(Motor.calcular(c)))));
"""

# O mesmo, mas a partir do arquivo cru: o JS mescla os cenários com Motor.cenarios, como a página faz.
NODE_BRUTO = r"""
const fs = require('fs');
const html = fs.readFileSync(process.argv[1], 'utf8');
const motor = html.split('/*MOTOR*/')[1].split('/*FIM-MOTOR*/')[0];
const Motor = new Function(motor + '; return Motor;')();
const brutos = JSON.parse(fs.readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(brutos.map(b => Motor.cenarios(b).map(c => Motor.numeros(Motor.calcular(c))))));
"""

PROVA_A = {"linha": {"nome": "Prova A", "custo": 11.60, "impostos": {"ICMS": 12}, "frete_rs_kg": 1.7776, "peso_kg": 0.12,
                     "mc_canal": 45, "preco_especifico": 23.00, "desconto": 2}, "mc_teto": 50}
PROVA_B = {"linha": {"nome": "Prova B", "custo": 11.60, "impostos": {"ICMS": 7}, "comissao": 2.5,
                     "frete_rs_kg": 4.0491, "peso_kg": 0.12, "mc_canal": 45, "desconto": 5}, "mc_teto": 50}


def cen(*provas):
    return {"mc_teto": 50, "linhas": [p["linha"] for p in provas]}


def aleatorio(rng):
    linhas = []
    for i in range(rng.randint(1, 4)):
        l = {"nome": f"L{i}", "quantidade": rng.choice([1, 1, 3, 12, 250]),
             "custo": round(rng.uniform(0.5, 900), rng.choice([2, 4])),
             "impostos": {"ICMS": rng.choice([0, 4, 7, 12, 17, 18]), "PIS": rng.choice([0, 0.65, 1.65]),
                          "COFINS": rng.choice([0, 3, 7.6])},
             "comissao": rng.choice([0, 2.5, 3, 5, 10]), "comissao_sobre": rng.choice(["bruta", "liquida"]),
             "frete_pct": rng.choice([0, 0, 1.5, 3]), "frete_rs": rng.choice([0, 0.2133, 1.75, 18]),
             "outras_pct": rng.choice([0, 1, 2.2, 3.5]), "desconto": rng.choice([0, 2, 5, 7.5, 10, 12])}
        if rng.random() < 0.7:
            l["mc_canal"] = rng.choice([10, 18.5, 22, 30, 45])
        r = rng.random()
        if r < 0.35:
            l["preco_especifico"] = round(l["custo"] * rng.uniform(1.05, 2.2), 2)
        elif r < 0.55:
            l["mc_especifica"] = rng.choice([8, 15, 20.25])
        if rng.random() < 0.2:
            l["preco_praticado"] = round(l["custo"] * rng.uniform(0.9, 2.5), 2)
        if rng.random() < 0.2:
            l["preco_mercado"] = round(l["custo"] * rng.uniform(1, 2), 2)
        if rng.random() < 0.15:
            l["custo_real"] = round(l["custo"] * rng.uniform(0.9, 1.2), 2)
        if rng.random() < 0.2:
            l["perda_pct"] = rng.choice([0.5, 2, 5])
        if rng.random() < 0.2 and (l.get("desconto") or l.get("preco_praticado")):
            l["quantidade_sem_desconto"] = rng.choice([1, 10, 80])
        if rng.random() < 0.2:
            l["por_fora"] = [{"nome": "IPI", "aliq": 9.75}, {"nome": "CBS", "aliq": 9.11, "base": "sem_icms_iss"}]
        linhas.append(l)
    c = {"linhas": linhas, "mc_teto": rng.choice([25, 35, 50, 60.5])}
    if rng.random() < 0.3:
        c["custo_fixo_mes"] = rng.choice([800, 4800, 25000])
        c["meta_lucro_pct"] = rng.choice([5, 10, 20])
    return c


def bruto_com_cenarios(rng):
    """Um arquivo com campos de topo (margens, hipóteses, custo fixo, linhas) e cenários que sobrepõem só parte deles."""
    base = aleatorio(rng)
    base["hipoteses"] = ["outras"]
    base["rotulos"] = {"teto": "Planejado", "desconto": "Promoção"}
    base["custo_fixo_mes"] = rng.choice([800, 4800])
    base["meta_lucro_pct"] = rng.choice([5, 20])
    cens = []
    for i in range(rng.randint(2, 4)):
        c = {"nome_cenario": f"C{i}"}
        r = rng.random()
        if r < 0.4:
            c["linhas"] = aleatorio(rng)["linhas"]  # linhas próprias, margens e fixo herdados
        elif r < 0.7:
            c["mc_teto"] = rng.choice([18, 28, 40])   # só a margem muda, as linhas vêm do topo
        # senão: o cenário não traz nada e herda tudo
        cens.append(c)
    base["cenarios"] = cens
    return base


class Regua(unittest.TestCase):
    def test_prova_a_tres_leituras(self):
        r = simulador.calcular(cen(PROVA_A))
        l = r["linhas"][0]
        self.assertEqual([(n["chave"], n["preco"]) for n in l["niveis"]],
                         [("teto", D("26.61")), ("canal", D("24.21")), ("especifico", D("23.00"))])
        self.assertEqual(l["usado"]["chave"], "especifico")
        self.assertEqual(l["negociado"], D("22.54"))
        self.assertEqual(simulador.r4(l["real"]["mc_rl"]), D("40.8824"))
        self.assertEqual(l["leituras"]["usado"][0], D("-1.1949"))
        self.assertEqual(simulador.r2(l["leituras"]["canal"][0]), D("-4.12"))
        self.assertEqual(simulador.r2(l["leituras"]["teto"][0]), D("-9.12"))
        self.assertEqual(l["leituras"]["usado"][2], simulador.r4(D("19.6219") * D("-1.1949") / 100))

    def test_prova_b_canal_e_nivel_usado(self):
        l = simulador.calcular(cen(PROVA_B))["linhas"][0]
        self.assertEqual(l["usado"]["chave"], "canal")
        self.assertEqual(l["negociado"], D("22.65"))
        self.assertEqual(simulador.r2(l["leituras"]["usado"][0]), D("-2.96"))
        self.assertEqual(l["leituras"]["usado"], l["leituras"]["canal"])
        self.assertEqual(simulador.r2(l["leituras"]["teto"][0]), D("-7.96"))

    def test_sem_desconto_realizada_igual_ao_nivel(self):
        for mc in (45, 30, 22.5):
            linha = dict(PROVA_B["linha"], desconto=0, mc_canal=mc)
            l = simulador.calcular({"mc_teto": 50, "linhas": [linha]})["linhas"][0]
            self.assertLess(abs(l["leituras"]["usado"][0]), D("0.02"))

    def test_cascata_do_teto_ao_realizado(self):
        l = simulador.calcular(cen(PROVA_A))["linhas"][0]
        chaves = [c["chave"] for c in l["cascata"]]
        self.assertEqual(chaves, ["teto", "canal", "especifico", "tatico"])
        self.assertEqual(l["cascata"][-1]["mc"], l["real"]["mc"])
        soma = l["cascata"][0]["mc"] + sum(c["delta_mc"] for c in l["cascata"][1:])
        self.assertEqual(soma, l["real"]["mc"])

    def test_consolidado_pondera_pela_receita_liquida(self):
        r = simulador.calcular(cen(PROVA_A, PROVA_B))
        t, (a, b) = r["total"], r["linhas"]
        self.assertEqual(t["mc"], a["real"]["mc"] + b["real"]["mc"])
        plan = (a["real"]["rl"] * a["refs"]["teto"] + b["real"]["rl"] * b["refs"]["teto"]) / t["rl"]
        self.assertEqual(t["leituras"]["teto"]["plan"], plan)
        self.assertEqual(t["leituras"]["teto"]["pts"], simulador.r4(t["mc_rl"] - plan))
        self.assertEqual(t["leituras"]["teto"]["rs"], simulador.r4(t["rl"] * t["leituras"]["teto"]["pts"] / 100))
        # uma linha só: o consolidado é a própria linha
        so = simulador.calcular(cen(PROVA_A))
        self.assertEqual(so["total"]["leituras"]["usado"]["pts"], so["linhas"][0]["leituras"]["usado"][0])
        self.assertEqual([c["chave"] for c in r["total"]["cascata"]], ["teto", "canal", "especifico", "tatico"])

    def test_tabela_de_hoje_como_nivel_especifico(self):
        c = {"mc_teto": 25, "rotulos": {"teto": "Planejado"}, "linhas": [{
            "nome": "Queijo", "custo": 8.12, "impostos": {"Impostos": 13.25}, "comissao": 3, "frete_pct": 2.5,
            "outras_pct": 1, "preco_especifico": 13.20, "rotulo_especifico": "Tabela de hoje", "desconto": 10}]}
        l = simulador.calcular(c)["linhas"][0]
        self.assertEqual(l["niveis"][0]["preco"], D("13.49"))
        self.assertEqual(l["negociado"], D("11.88"))
        self.assertEqual(l["real"]["mc"], D("1.4137"))
        self.assertEqual(simulador.r2(l["leituras"]["usado"][0]), D("-8.52"))
        self.assertEqual(simulador.r2(l["leituras"]["teto"][0]), D("-10.17"))
        self.assertEqual(l["cascata"][0]["mc"] - l["cascata"][-1]["mc"], D("1.2920"))

    def test_custo_fixo_e_lucro_depois_dele(self):
        c = {"mc_teto": 30, "custo_fixo_mes": 4800, "meta_lucro_pct": 20, "linhas": [{
            "nome": "km", "quantidade": 6000, "custo": 0.9136, "impostos": {"DAS": 6}, "comissao": 30,
            "outras_pct": 2.1, "preco_praticado": 3.80}]}
        r = simulador.calcular(c)
        e = r["equilibrio"]
        self.assertEqual(e["lucro"], r["total"]["mc"] - 4800)
        self.assertIsNotNone(e["unidades_pe"])
        p = r["linhas"][0]["p"]
        esperado = simulador.r2((p.custo + D(4800) / 6000) / ((100 - p.variaveis_pct() - 20) / D(100)))
        self.assertEqual(e["preco_meta"], esperado)

    def test_margem_negativa_sem_ponto_de_equilibrio(self):
        c = {"custo_fixo_mes": 1000, "linhas": [{"nome": "x", "custo": 100, "impostos": {"ICMS": 17},
                                                  "preco_especifico": 90, "quantidade": 10}]}
        e = simulador.calcular(c)["equilibrio"]
        self.assertIsNone(e["receita_pe"])
        self.assertIsNone(e["unidades_pe"])

    def test_meta_e_a_margem_desejada_e_nao_o_preco_de_hoje(self):
        # o preço de hoje é o nível usado, mas a leitura principal é contra a meta de 30%
        c = {"mc_teto": 30, "linhas": [{"nome": "Arroz", "custo": 22.40, "impostos": {"DAS": 7.3}, "outras_pct": 1.32,
                                        "preco_especifico": 29.12}]}
        l = simulador.calcular(c)["linhas"][0]
        self.assertEqual(l["usado"]["chave"], "especifico")
        self.assertEqual(l["meta"], D(30))
        self.assertEqual(simulador.r2(l["leituras"]["meta"][0]), D("-14.18"))
        self.assertEqual(l["faixa"], "atencao")  # 15,82 ÷ 30 = 53% mantido
        # canal é a meta da linha quando existe
        l = simulador.calcular(cen(PROVA_A))["linhas"][0]
        self.assertEqual(l["meta"], D(45))
        # sem meta: neutro, mesmo com margem boa
        c = {"linhas": [{"nome": "x", "custo": 10, "preco_especifico": 30}]}
        l = simulador.calcular(c)["linhas"][0]
        self.assertIsNone(l["meta"])
        self.assertEqual(l["faixa"], "neutro")

    def test_custo_fixo_com_varias_linhas(self):
        c = {"custo_fixo_mes": 4800, "meta_lucro_pct": 20, "linhas": [
            {"nome": "Avulsa", "quantidade": 2952, "custo": 1.3052, "impostos": {"DAS": 6}, "comissao": 30,
             "outras_pct": 1.75, "preco_especifico": 3.80},
            {"nome": "Contrato", "quantidade": 2952, "custo": 1.3052, "impostos": {"DAS": 6}, "comissao": 30,
             "outras_pct": 1.75, "preco_especifico": 3.20}]}
        r = simulador.calcular(c)
        e = r["equilibrio"]
        self.assertIsNotNone(e["unidades_pe"])
        self.assertEqual(len(e["precos_meta"]), 2)
        # vendendo cada linha no preço da meta, o lucro depois do fixo é 20% da receita, a menos do arredondamento
        for l, pm in zip(c["linhas"], e["precos_meta"]):
            l["preco_especifico"] = float(pm)
        r2 = simulador.calcular(c)
        lucro = r2["total"]["mc"] - 4800
        self.assertLess(abs(lucro / r2["total"]["rb"] * 100 - 20), D("0.1"))

    def test_desconto_que_vende_mais(self):
        l = simulador.calcular({"mc_teto": 30, "linhas": [{
            "nome": "Promo", "quantidade": 90, "quantidade_sem_desconto": 30, "custo": 22.40,
            "impostos": {"DAS": 7.3}, "outras_pct": 1.32, "preco_especifico": 29.12, "preco_praticado": 26.90}]})["linhas"][0]
        self.assertEqual(l["sem_desconto"]["mc"], D("126.2957"))
        self.assertGreater(l["real"]["mc"], l["sem_desconto"]["mc"])

    def test_perda_entra_no_custo(self):
        l = simulador.calcular({"mc_teto": 30, "linhas": [{"nome": "x", "custo": 22.40, "perda_pct": 0.5,
                                                           "preco_especifico": 29.12}]})["linhas"][0]
        self.assertEqual(l["p"].custo, D("22.5126"))

    def test_avisos_de_nivel(self):
        base = {"custo": 284, "impostos": {"ICMS": 18, "PIS": 1.65, "COFINS": 7.6}, "comissao": 4, "frete_rs": 18}
        r = simulador.calcular({"mc_teto": 22, "linhas": [
            dict(base, nome="Revenda", grupo="Revenda", mc_canal=18),
            dict(base, nome="Grande", grupo="Grande", preco_especifico=489),
            dict(base, nome="Pequeno", grupo="Pequeno", mc_canal=28)]})
        self.assertTrue(any("Revenda: o preço do canal" in a for a in r["avisos"]))
        self.assertTrue(any("Pequeno: a margem" in a and "passa do teto" in a for a in r["avisos"]))
        # rede com meta menor e contrato mais barato é o esperado: sem aviso
        r = simulador.calcular({"mc_teto": 50, "linhas": [
            dict(base, nome="Varejo", grupo="Varejo", mc_canal=45),
            dict(base, nome="Rede", grupo="Rede", mc_canal=30, preco_especifico=420)]})
        self.assertEqual(r["avisos"], [])

    def test_cenarios_herdam_o_topo(self):
        bruto = {"mc_teto": 30, "hipoteses": ["outras"], "custo_fixo_mes": 100,
                 "linhas": [{"nome": "x", "custo": 10, "preco_especifico": 20}],
                 "cenarios": [{"nome_cenario": "a"}, {"nome_cenario": "b", "mc_teto": 40}]}
        a, b = simulador.mesclar(bruto)
        self.assertEqual((a["mc_teto"], b["mc_teto"]), (30, 40))
        self.assertEqual(a["linhas"], bruto["linhas"])
        self.assertEqual(b["custo_fixo_mes"], 100)
        self.assertNotIn("cenarios", a)

    def test_apendice_um_por_cenario(self):
        bruto = {"mc_teto": 30, "linhas": [{"nome": "x", "custo": 10, "impostos": {"PIS": 0.65}, "preco_especifico": 20}],
                 "cenarios": [{"nome_cenario": "2026"},
                              {"nome_cenario": "2027", "linhas": [{"nome": "x", "custo": 10, "preco_especifico": 20,
                                                                   "por_fora": [{"nome": "CBS", "aliq": 9.11}]}]}]}
        h = simulador.gerar_html(bruto)
        self.assertIn('data-cen="0"', h)
        self.assertIn('data-cen="1" hidden', h)
        c0, c1 = h.split('data-cen="0"')[1].split('data-cen="1"')
        self.assertNotIn("CBS", c0)
        self.assertIn("CBS", c1)

    def test_pagina_usa_o_merge_do_motor(self):
        with open(MODELO, encoding="utf-8") as f:
            h = f.read()
        self.assertIn("Motor.cenarios(BRUTO)", h.split("/*FIM-MOTOR*/")[1])

    def test_html_leva_o_cenario_e_o_apendice(self):
        with tempfile.TemporaryDirectory() as tmp:
            arq = os.path.join(tmp, "s.html")
            simulador.gravar(cen(PROVA_A, PROVA_B), arq, nao_abrir=True)
            with open(arq, encoding="utf-8") as f:
                h = f.read()
        self.assertIn('"preco_especifico": 23.0', h)
        self.assertIn("Receita líquida gerencial", h)
        self.assertIn("data:image/png;base64,", h)
        self.assertNotIn("<!--APENDICE-->", h)
        self.assertNotIn("http://", h.replace("http://www.w3.org", ""))


@unittest.skipUnless(shutil.which("node"), "node não está instalado")
class Paridade(unittest.TestCase):
    """O JS do simulador e o Python dão os mesmos números, na mesma escala."""

    def rodar_js(self, cens):
        out = subprocess.run(["node", "-e", NODE, MODELO], input=json.dumps(cens), capture_output=True,
                             text=True, check=True)
        return json.loads(out.stdout)

    def conferir(self, cens):
        js = self.rodar_js(cens)
        for c, j in zip(cens, js):
            py = json.loads(json.dumps(simulador.numeros(simulador.calcular(c))))
            self.assertEqual(py, j, json.dumps(c, ensure_ascii=False))

    def test_provas_e_exemplos(self):
        cens = [cen(PROVA_A), cen(PROVA_B), cen(PROVA_A, PROVA_B)]
        if os.path.isdir(EXEMPLOS):
            for nome in sorted(os.listdir(EXEMPLOS)):
                if nome.endswith(".json"):
                    raiz, lista = simulador.carregar(os.path.join(EXEMPLOS, nome))
                    cens += lista
        self.conferir(cens)

    def test_cenarios_multiplos_js_herda_como_python(self):
        """O bug da v2: com `cenarios`, o JS não herdava mc_teto, hipóteses, linhas e custo fixo do topo."""
        rng = random.Random(20260929)
        brutos = [bruto_com_cenarios(rng) for _ in range(300)]
        if os.path.isdir(SIMULACOES):
            for caso in sorted(os.listdir(SIMULACOES)):
                arq = os.path.join(SIMULACOES, caso, "cenario.json")
                if os.path.exists(arq):
                    with open(arq, encoding="utf-8") as f:
                        brutos.append(json.load(f))
        out = subprocess.run(["node", "-e", NODE_BRUTO, MODELO], input=json.dumps(brutos), capture_output=True,
                             text=True, check=True)
        js = json.loads(out.stdout)
        for b, j in zip(brutos, js):
            py = [json.loads(json.dumps(simulador.numeros(simulador.calcular(c)))) for c in simulador.mesclar(b)]
            self.assertEqual(py, j, json.dumps(b, ensure_ascii=False)[:400])

    def test_mil_casos_aleatorios(self):
        rng = random.Random(20260928)
        self.conferir([aleatorio(rng) for _ in range(1000)])


if __name__ == "__main__":
    unittest.main()
