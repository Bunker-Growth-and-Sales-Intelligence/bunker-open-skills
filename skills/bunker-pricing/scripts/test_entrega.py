"""As duas camadas da DRE, as vendas a mais, o painel editável e o PDF de entrega.

Rodar: python3 -m unittest discover -s skills/bunker-pricing/scripts
A paridade da DRE editável roda o JS do painel no node; sem node, é pulada. A edição no
navegador e o PDF usam o Chrome da máquina; sem ele, são pulados, e o teste do HTML para
imprimir roda.
"""
import copy
import io
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from decimal import Decimal as D
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import camadas  # noqa: E402
import entrega  # noqa: E402
import simulador  # noqa: E402
from grafico import conferir, formas, saida  # noqa: E402
from test_simulador import aleatorio  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..", "..", "..")
ASSETS = os.path.join(AQUI, "..", "assets")

# a cafeteira da decisão de nomenclatura: custo 812, meta 25%, frete R$ 34, deduções 13,25%,
# comissão 3%, cartão 1%, campanha de 5% (o preço da política, fechado) e 2% de desconto tático
CAFETEIRA = {"nome": "Cafeteira profissional", "quantidade": 120, "custo": 812, "impostos": {"Deduções": 13.25},
             "comissao": 3, "outras_pct": 1, "frete_rs": 34, "preco_especifico": 1281.98, "desconto": 2}
MES = {"mc_teto": 25, "atividade": "comercio", "unidade": "unidade", "linhas": [CAFETEIRA],
       "despesas_fixas": [{"nome": "Despesas com pessoal e encargos", "valor": 38000},
                          {"nome": "Despesas de ocupação", "valor": 9500}],
       "receitas_financeiras": 1200, "despesas_financeiras": 4300, "irpj_csll_pct": 24}

NODE = r"""
const fs = require('fs');
const sim = fs.readFileSync(process.argv[1], 'utf8'), pj = fs.readFileSync(process.argv[2], 'utf8');
const motor = sim.split('/*MOTOR*/')[1].split('/*FIM-MOTOR*/')[0];
const cam = pj.split('/*CAMADAS*/')[1].split('/*FIM-CAMADAS*/')[0];
const Camadas = new Function(motor + cam + '; return Camadas;')();
const cens = JSON.parse(fs.readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(cens.map(c => Camadas.numeros(c))));
"""


def conta(cen):
    return entrega.montar_conta(simulador.mesclar(cen)[0])


def cenario_arquivo(cen, pasta=None):
    pasta = pasta or tempfile.mkdtemp()
    arq = os.path.join(pasta, "c.json")
    with open(arq, "w", encoding="utf-8") as f:
        json.dump(cen, f, ensure_ascii=False)
    return arq


class DreDaVenda(unittest.TestCase):
    def test_cafeteira_da_decisao(self):
        v = conta(MES)["vendas"][0]
        self.assertEqual(v["topo"]["preco"], D("1349.45"))
        self.assertEqual(v["usado"]["preco"], D("1281.98"))
        self.assertEqual(v["negociado"], D("1256.34"))
        self.assertEqual(round(v["plan"]["mc"], 2), D("270.67"))
        self.assertEqual(round(v["real"]["mc"], 2), D("193.62"))
        self.assertEqual(round(v["cedida_campanha"], 2), D("55.83"))
        self.assertEqual(round(v["cedida_tatico"], 2), D("21.22"))
        self.assertEqual(v["cedida_campanha"] + v["cedida_tatico"], v["plan"]["mc"] - v["real"]["mc"])

    def test_formacao_fecha_no_negociado(self):
        v = conta(MES)["vendas"][0]
        corr = D(0)
        for chave, tipo, valor in v["formacao"]:
            if tipo in ("custo", "total"):
                if chave != "CMV":
                    self.assertEqual(corr, valor, chave)
                corr = valor
            else:
                corr += valor if tipo == "mais" else -valor
        self.assertEqual(corr, v["negociado"])

    def test_piso_usa_a_tabela_como_preco_teto(self):
        c = {"mc_teto": 50, "regra_margem": "piso", "linhas": [
            {"nome": "Hora", "custo": 67.5, "impostos": {"ISS": 5}, "preco_especifico": 330, "desconto": 10}]}
        l = conta(c)["res"]["linhas"][0]
        self.assertEqual(camadas.topo(l)["chave"], "especifico")

    def test_composicao_das_tres_vendas(self):
        v = conta(MES)["vendas"][0]
        teto, pol, neg = camadas.composicao(v)
        for col in (teto, pol, neg):
            self.assertEqual(col["custo"] + col["trib"] + col["com"] + col["frete"] + col["mc"], col["preco"])
        self.assertEqual(teto["cedida"], 0)
        self.assertEqual(pol["cedida"], v["cedida_campanha"])
        self.assertEqual(neg["cedida"], v["cedida_campanha"] + v["cedida_tatico"])
        self.assertGreater(teto["preco"], pol["preco"])
        self.assertGreater(pol["preco"], neg["preco"])
        svg = formas.composicao([teto, pol, neg], entrega.A4)
        self.assertEqual(conferir.geometria(svg), [])
        self.assertEqual(conferir.sobreposicao(svg), [])
        self.assertEqual(conferir.texto_cortado(svg), [])
        self.assertIn("cedida R$ 77,05", svg)

    def test_tributos_da_reforma_sempre_aparecem(self):
        tab = entrega.tabela_venda(conta(MES), 0)
        for nome in ("Deduções", "CBS", "IBS"):
            self.assertIn(f'data-padrao="{nome}"', tab)
        self.assertIn('data-campo="linhas.0.impostos.CBS"', tab)


class DreDoMes(unittest.TestCase):
    def test_mesa_soma_campanha_e_tatico(self):
        m = conta(MES)["mes"]
        self.assertEqual(m["mesa_total"], m["orcado"]["mc"] - m["realizado"]["mc"])
        self.assertEqual(m["mesa_campanha"] + m["mesa_tatico"] + m["mesa_custo"], m["mesa_total"])
        self.assertEqual(m["rec_teto"] - m["desc_campanha"] - m["desc_tatico"], m["realizado"]["rb"])

    def test_despesas_fixas_financeiro_e_ir(self):
        m = conta(MES)["mes"]
        r = m["realizado"]
        self.assertEqual(m["fixo"], D(47500))
        self.assertEqual(r["ro"], r["mc"] - D(47500))
        self.assertEqual(r["lair"], r["ro"] + D(1200) - D(4300))
        self.assertEqual(r["ir"], (r["lair"] * D("0.24")).quantize(D("0.01")) if r["lair"] > 0 else D(0))
        self.assertEqual(r["ll"], r["lair"] - r["ir"])
        self.assertEqual(r["peso"], D(47500) / r["rb"] * 100)

    def test_real_zera_com_prejuizo_e_presumido_sai_da_receita(self):
        prejuizo = dict(MES, despesas_fixas=[{"nome": "Pessoal", "valor": 90000}])
        m = conta(prejuizo)["mes"]
        self.assertLess(m["realizado"]["lair"], 0)
        self.assertEqual(m["realizado"]["ir"], 0)
        pres = dict(prejuizo, regime="presumido", irpj_csll_pct=8.54)
        m = conta(pres)["mes"]
        for d in (m["orcado"], m["realizado"]):
            self.assertEqual(d["ir"], (d["rb"] * D("8.54") / 100).quantize(D("0.01")))
            self.assertGreater(d["ir"], 0)
            self.assertEqual(d["ll"], d["lair"] - d["ir"])
        tab = entrega.tabela_mes(conta(pres))
        self.assertIn("IRPJ e CSLL, Lucro Presumido, sobre a receita", tab)
        self.assertNotIn("do lucro", tab)

    def test_uma_despesa_fixa_sem_total_repetido(self):
        c = dict(MES, despesas_fixas=[{"nome": "Despesas operacionais fixas", "valor": 47500}])
        self.assertNotIn("Total das despesas operacionais fixas", entrega.tabela_mes(conta(c)))
        self.assertIn("Total das despesas operacionais fixas", entrega.tabela_mes(conta(MES)))

    def test_sem_fixo_para_na_margem(self):
        c = dict(MES)
        for k in ("despesas_fixas", "receitas_financeiras", "despesas_financeiras", "irpj_csll_pct"):
            c.pop(k)
        ct = conta(c)
        self.assertFalse(ct["mes"]["tem_fixo"])
        self.assertNotIn("Resultado operacional", entrega.tabela_mes(ct))


class VendasAMais(unittest.TestCase):
    def test_conta_das_vendas_a_mais(self):
        c = conta(MES)
        a = c["amais"]["linhas"][0]
        v, l = c["vendas"][0], c["res"]["linhas"][0]
        perf = camadas.topo(l)["dre"]["mc"]
        self.assertEqual(a["perf"], perf)
        self.assertEqual(a["nec"], perf / v["real"]["mc"])
        self.assertEqual(a["amais"], a["nec"] - 120)
        self.assertEqual(a["pct"], a["amais"] / 120 * 100)
        self.assertEqual(a["esforco"], a["amais"] * v["negociado"])
        # vendendo as necessárias com desconto, a margem do mês volta à da venda perfeita
        self.assertAlmostEqual(float(a["nec"] * v["real"]["mc"]), float(perf), places=6)
        self.assertEqual(round(a["nec"], 2), D("167.75"))
        self.assertIn("47,75 unidades a mais", entrega.frase_a_mais(c))

    def test_margem_com_desconto_negativa_nenhum_volume_compensa(self):
        c = conta({"mc_teto": 30, "linhas": [{"nome": "Queima", "quantidade": 10, "custo": 100,
                                               "impostos": {"ICMS": 18}, "desconto": 40}]})
        a = c["amais"]
        self.assertIsNone(a["linhas"][0]["nec"])
        self.assertIsNone(a["total"]["nec"])
        self.assertIn("nenhum volume compensa", entrega.frase_a_mais(c))
        self.assertIn("nenhum volume compensa", entrega.bloco_a_mais(c)["html"])

    def test_unidades_diferentes_nao_se_somam(self):
        base = {"custo": 10, "impostos": {"ISS": 2}, "desconto": 10}
        c = conta({"mc_teto": 50, "regra_margem": "piso", "linhas": [dict(base, nome="Contrato", unidade="mês de contrato", quantidade=2,
                                                  custo=20000, preco_especifico=59200),
                                             dict(base, nome="Hora", unidade="hora", quantidade=150)]})
        self.assertIsNone(entrega.uma_unidade(c))
        frase = entrega.frase_a_mais(c)
        self.assertIn("meses de contrato a mais em Contrato", frase)
        self.assertIn("horas a mais em Hora", frase)
        html = entrega.bloco_a_mais(c)["html"]
        self.assertNotIn('data-k="t.q"', html)
        self.assertIn('data-k="t.esforco"', html)


class Setas(unittest.TestCase):
    def test_sentido_de_cada_linha(self):
        self.assertEqual(entrega.desvio(D("5"), "rs", "+"), ("▲ 5,00", "bom"))
        self.assertEqual(entrega.desvio(D("-5"), "rs", "+"), ("▼ 5,00", "mau"))
        self.assertEqual(entrega.desvio(D("5"), "rs", "-"), ("▲ 5,00", "mau"))     # mais custo é ruim
        self.assertEqual(entrega.desvio(D("-5"), "rs", "-"), ("▼ 5,00", "bom"))    # menos dedução é bom
        self.assertEqual(entrega.desvio(D("1.26"), "pc", "+"), ("▲ 1,3 p.p.", "bom"))
        self.assertEqual(entrega.desvio(D("22.4"), "pq", "-"), ("▲ 22,4%", "mau"))
        self.assertEqual(entrega.desvio(D("0.004"), "rs", "+"), ("", ""))

    def test_setas_na_dre(self):
        tab = entrega.tabela_venda(conta(MES), 0)
        linha = lambda nome: re.search(r'<tr[^>]*>(?:(?!</tr>).)*data-padrao="' + re.escape(nome) + r'".*?</tr>', tab, re.S).group(0)  # noqa: E731
        self.assertIn('class="dsv mau"', linha("Receita bruta da venda"))          # a receita caiu
        self.assertIn('class="dsv bom"', linha("Deduções da receita bruta"))        # a dedução caiu junto
        self.assertIn('class="dsv mau"', linha("Margem de contribuição da venda"))
        self.assertIn('class="dsv mau"', linha("Desconto tático"))                  # desconto a mais é ruim
        self.assertNotIn("<b>", tab)

    def test_duas_casas_na_tela(self):
        tab = entrega.tabela_venda(conta(MES), 0)
        self.assertIn(">1.349,45<", tab)
        self.assertNotRegex(tab, r">\d+,\d{3,}<")


@unittest.skipUnless(shutil.which("node"), "node não está instalado")
class Paridade(unittest.TestCase):
    """O JS do painel refaz a DRE editável com os mesmos números do Python, em 4 casas."""

    def conferir(self, cens):
        out = subprocess.run(["node", "-e", NODE, os.path.join(ASSETS, "simulador.html"), os.path.join(ASSETS, "painel.js")],
                             input=json.dumps(cens), capture_output=True, text=True, check=True)
        js = json.loads(out.stdout)
        self.assertEqual(len(js), len(cens))
        for c, j in zip(cens, js):
            py = entrega.numeros(entrega.montar_conta(c))
            self.assertEqual(py, j, json.dumps(c, ensure_ascii=False)[:500])

    def arquivos(self):
        cens = [simulador.mesclar(MES)[0]]
        pastas = [os.path.join(RAIZ, "exemplos"), os.path.join(RAIZ, "simulacoes-bunker")]
        sim = os.path.join(RAIZ, "simulacoes-v2")
        if os.path.isdir(sim):
            pastas += [os.path.join(sim, p) for p in sorted(os.listdir(sim))]
        for pasta in pastas:
            if not os.path.isdir(pasta):
                continue
            for nome in sorted(os.listdir(pasta)):
                if nome.endswith(".json") and nome.startswith(("cenario", "industria", "pequeno", "servico")):
                    cens += simulador.carregar(os.path.join(pasta, nome))[1]
        return cens

    def test_cenarios_dos_exemplos_e_das_simulacoes(self):
        self.conferir(self.arquivos())

    def test_trezentos_casos_aleatorios_com_o_mes_inteiro(self):
        rng = random.Random(20260929)
        cens = []
        for _ in range(300):
            c = aleatorio(rng)
            if rng.random() < 0.6:
                c["despesas_fixas"] = [{"nome": "Pessoal", "valor": rng.choice([800, 4800, 25000])},
                                       {"nome": "Ocupação", "valor": rng.choice([0, 1200.5])}]
                c["receitas_financeiras"] = rng.choice([0, 150.25])
                c["despesas_financeiras"] = rng.choice([0, 320.81])
                c["irpj_csll_pct"] = rng.choice([None, 24, 34, 8.54])
                if rng.random() < 0.4:
                    c["regime"] = "presumido"
            cens.append(simulador.mesclar(c)[0])
        self.conferir(cens)


@unittest.skipUnless(saida.achar_chrome(), "sem Chrome na máquina")
class EdicaoNoNavegador(unittest.TestCase):
    """Editar um campo no painel dá, célula por célula, o mesmo texto que o Python escreve para o
    cenário já editado."""

    EDITAR = r"""<script>
addEventListener('load', function () { setTimeout(function () {
  EDICOES.forEach(function (e) {
    var el = document.querySelector('input.ed[data-campo="' + e[0] + '"]');
    el.value = e[1]; el.dispatchEvent(new Event('input', {bubbles: true})); el.blur();
  });
  var p = document.createElement('pre'); p.id = 'fim'; document.body.appendChild(p);
}, 300); });
</script>"""

    def celulas(self, html):
        corpo = html.split('<main>')[1].split('</main>')[0]
        return re.findall(r'<td class="([^"]*)" (data-(?:k|da|dv|pn)="[^"]*")[^>]*>([^<]*)</td>', corpo)

    def rodar(self, cen, edicoes, esperado):
        with tempfile.TemporaryDirectory() as tmp:
            doc = entrega.painel(cenario_arquivo(cen, tmp))[0]
            script = self.EDITAR.replace("EDICOES", json.dumps(edicoes))
            arq = os.path.join(tmp, "p.html")
            with open(arq, "w", encoding="utf-8") as f:
                f.write(doc.replace("</body>", script + "</body>"))
            r = subprocess.run([saida.achar_chrome(), "--headless=new", "--disable-gpu", "--virtual-time-budget=6000",
                                "--dump-dom", "file://" + arq], capture_output=True, text=True)
            self.assertIn('<pre id="fim">', r.stdout)
            antes = self.celulas(doc)
            depois = self.celulas(r.stdout)
            alvo = self.celulas(entrega.painel(cenario_arquivo(esperado, tmp))[0])
        self.assertNotEqual(antes, alvo)
        self.assertEqual(len(depois), len(alvo))
        for d, a in zip(depois, alvo):
            self.assertEqual((d[0].strip(), d[1], d[2]), (a[0].strip(), a[1], a[2]))

    def test_custo_aliquota_e_despesa_fixa(self):
        esperado = copy.deepcopy(MES)
        esperado["linhas"][0]["custo"] = 830.5
        esperado["linhas"][0]["impostos"] = {"Deduções": 12, "CBS": 0.9}
        esperado["despesas_fixas"][1]["valor"] = 10000
        self.rodar(MES, [["linhas.0.custo", "830,50"], ["linhas.0.impostos.Deduções", "12"],
                         ["linhas.0.impostos.CBS", "0,9"], ["despesas_fixas.1.valor", "10.000,00"]], esperado)

    def test_desconto_tatico_em_reais(self):
        esperado = copy.deepcopy(MES)
        esperado["linhas"][0].pop("desconto")
        esperado["linhas"][0]["preco_praticado"] = 1231.98
        self.rodar(MES, [["linhas.0.preco_praticado", "50,00"]], esperado)


class Painel(unittest.TestCase):
    def cenario_bunker(self):
        return os.path.join(RAIZ, "simulacoes-bunker", "cenario.json")

    def test_painel_passa_nas_conferencias_do_html(self):
        arq = self.cenario_bunker()
        if not os.path.exists(arq):
            self.skipTest("sem o cenário de teste")
        doc = entrega.painel(arq)[0]
        for nome, achados, _ in conferir.conferir(doc):
            self.assertEqual(achados, [], nome)
        self.assertNotIn("https://", doc.replace("http://www.w3.org", ""))
        # a logo já diz a marca: o título é o da análise, e a entrega é só as duas DREs
        self.assertIn("<h1>Leitura de preço e margem</h1>", doc)
        self.assertNotIn("<h1>Bunker</h1>", doc)
        main = doc.split("<main>")[1]
        self.assertLess(main.index("DRE da venda"), main.index("DRE do mês"))
        for fora in ("hipótese", "Da margem de contribuição planejada", "Ficaram", "Cada hora de", "Premissas",
                     "Para onde vai o preço", "Quantas vendas a mais", "Por quanto vender cada produto"):
            self.assertNotIn(fora, main.split("<footer>")[0], fora)

    def test_colunas_de_nome_e_campos(self):
        doc = entrega.painel(cenario_arquivo(MES))[0]
        for trecho in ("Alumni chama de", "Skill chama de", "Pricing Designer grava como", 'data-src="alumni"',
                       'data-src="pd"', 'data-nome="Level0Price (preço nível 0)"', 'data-nome="CPV"', 'title="a criar"',
                       'data-campo="linhas.0.custo"', 'data-campo="mc_teto"', 'data-campo="linhas.0.comissao"',
                       'data-campo="linhas.0.frete_rs"', 'data-campo="despesas_fixas.0.valor"',
                       'data-campo="receitas_financeiras"', 'data-campo="despesas_financeiras"',
                       'data-campo="irpj_csll_pct"', 'data-modo="tat"',
                       'data-modo="camp"', 'localStorage', 'id="cenario-painel"'):
            self.assertIn(trecho, doc)
        self.assertNotIn("não ensina", doc)

    def test_blocos_das_duas_camadas(self):
        doc = entrega.painel(cenario_arquivo(MES))[0]
        for trecho in ("Receita bruta no preço teto", "Descontos de campanha e política comercial",
                       "Descontos táticos", "Margem de contribuição que ficou na mesa: total",
                       "Despesas com pessoal e encargos", "Receitas financeiras", "Despesas financeiras",
                       "Lucro líquido do período", "Preço teto", "Desconto tático"):
            self.assertIn(trecho, doc)
        for fora in ("Quantas vendas a mais", "Por quanto vender cada produto", "O próximo passo"):
            self.assertNotIn(fora, doc)

    def test_folhas_so_com_capa_e_dres(self):
        # por ora a entrega não tem o próximo passo nem o convite ao Pricing Designer
        g = conta(dict(MES, porte="grande"))
        html, total = entrega.folhas(g["cen"], g, entrega._dt.datetime(2026, 9, 29))
        self.assertNotIn("Pricing Designer da Bunker", html)
        self.assertNotIn("O próximo passo", html)
        self.assertIn("DRE da venda", html)
        self.assertIn("DRE do mês", html)

    def test_folhas_sem_campo_e_sem_a_marca_repetida(self):
        c = conta(dict(MES, cliente="Bunker", titulo="Bunker · teste"))
        html, _ = entrega.folhas(c["cen"], c, entrega._dt.datetime(2026, 9, 29))
        self.assertNotIn("<input", html)
        self.assertNotIn("<button", html)
        for rot in re.findall(r'<div class="cab"><img[^>]*><span>([^<]*)</span>', html):
            self.assertFalse(rot.startswith("Bunker"), rot)
        self.assertIn("<h1>Leitura de preço e margem</h1>", html)
        self.assertNotIn("hipótese", html)

    def test_sem_chrome_entrega_o_html_para_imprimir(self):
        with tempfile.TemporaryDirectory() as tmp:
            cen = cenario_arquivo(MES, tmp)
            with mock.patch.object(saida, "achar_chrome", return_value=None), redirect_stdout(io.StringIO()) as out:
                entrega.main([cen, "--painel", os.path.join(tmp, "p.html"), "--pdf", os.path.join(tmp, "e.pdf")])
            self.assertTrue(os.path.exists(os.path.join(tmp, "e.imprimir.html")))
            self.assertFalse(os.path.exists(os.path.join(tmp, "e.pdf")))
            self.assertIn("Sem Chrome", out.getvalue())

    @unittest.skipUnless(saida.achar_chrome(), "sem Chrome na máquina")
    def test_pdf_a4_com_as_folhas_contadas(self):
        with tempfile.TemporaryDirectory() as tmp:
            cen = cenario_arquivo(MES, tmp)
            pdf = os.path.join(tmp, "e.pdf")
            with redirect_stdout(io.StringIO()):
                entrega.main([cen, "--painel", os.path.join(tmp, "p.html"), "--pdf", pdf])
            with open(pdf, "rb") as f:
                self.assertEqual(f.read(5), b"%PDF-")
            n = saida.paginas(pdf)
            self.assertGreaterEqual(n, 3)
            self.assertLessEqual(n, 6)
            self.assertFalse(os.path.exists(os.path.join(tmp, "e.imprimir.html")))


class Formas(unittest.TestCase):
    def test_ponte_que_nao_fecha_derruba(self):
        with self.assertRaises(ValueError):
            formas.ponte_deitada([("A", 10, "total"), ("B", 3, "menos"), ("C", 8, "total")])

    def test_numero_brasileiro(self):
        self.assertEqual(formas.br(-1234.5), "−1.234,50")
        self.assertEqual(formas.rs(D("21968.16")), "R$ 21.968,16")
        self.assertEqual(entrega.plural("mês de contrato"), "meses de contrato")
        self.assertEqual(entrega.plural("km cobrado"), "km cobrados")


if __name__ == "__main__":
    unittest.main()
