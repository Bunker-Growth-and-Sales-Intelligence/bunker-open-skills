"""Os exemplos de references/formulas.md, conferidos à mão, e os casos de borda.

Rodar: python3 -m unittest discover -s skills/bunker-pricing/scripts
"""

import argparse
import contextlib
import io
import os
import sys
import tempfile
import unittest
from decimal import Decimal as D

os.environ["BUNKER_PRICING_NAO_ABRIR"] = "1"
sys.path.insert(0, os.path.dirname(__file__))
import preco  # noqa: E402


def premissas(**kw):
    base = dict(
        produto=None, unidade=None, quantidade="1", custo="0", impostos=None, imposto=None,
        comissao="0", comissao_sobre="bruta", frete="0", frete_valor="0", outras="0",
        outras_valor="0", margem=None, por_fora=None, atividade=None, hipotese=None,
    )
    base.update(kw)
    return preco.Premissas(argparse.Namespace(**base))


def fecha(d):
    return (
        d["rb"] - d["deducoes"] == d["rl_contabil"]
        and d["rl_contabil"] - d["desp_total"] == d["rl"]
        and d["rl"] - d["cpv"] == d["mc"]
        and sum(v for _, v in d["impostos"]) == d["deducoes"]
        and sum(d["despesas"].values()) == d["desp_total"]
        and all(x == x.quantize(D("0.0001")) for x in (d["rb"], d["deducoes"], d["rl"], d["cpv"], d["mc"]))
    )


def rodar(*args):
    saida = io.StringIO()
    with contextlib.redirect_stdout(saida):
        preco.main(list(args))
    return saida.getvalue()


QUEIJO = dict(custo="8.12", impostos="13.25", comissao="3", frete="2.5", outras="1", margem="25")
QUEIJO_CLI = ["--custo", "8.12", "--impostos", "13.25", "--comissao", "3", "--frete", "2.5", "--outras", "1"]


class Formula(unittest.TestCase):
    def test_possibilidade_3_da_planilha(self):
        # Planilha "Conceitos de Precificação": custo 8,12, impostos 13,25%, margem 46,25% sobre a receita líquida
        p = premissas(custo="8.12", impostos="13.25", margem="46.25")
        self.assertEqual(preco.formar(p), D("17.41"))
        d = preco.dre(D("17.41"), p)
        self.assertEqual(preco.r2(d["mc_rl"]), D("46.24"))
        # Sem arredondar o preço, a margem sobre a receita líquida é a desejada, exata
        exato = D("8.12") / D("0.5375") / D("0.8675")
        rl = exato * D("0.8675")
        self.assertEqual(round((rl - D("8.12")) / rl * 100, 10), D("46.25"))

    def test_margem_bate_sobre_a_receita_liquida(self):
        casos = [
            dict(custo="8.12", impostos="13.25", comissao="3", frete="2.5", outras="1", margem="25"),
            dict(custo="312", imposto=["ICMS=17", "PIS=1.65", "COFINS=7.6"], comissao="4", frete_valor="18", margem="22"),
            dict(custo="0.9136", impostos="6", comissao="30", outras="3.5", margem="20"),
            dict(custo="58", impostos="15.65", comissao="5", comissao_sobre="liquida", margem="28"),
            dict(custo="1200", impostos="9.25", outras="2", outras_valor="35.50", margem="60"),
        ]
        for kw in casos:
            p = premissas(**kw)
            d = preco.dre(preco.formar(p), p)
            self.assertTrue(fecha(d), kw)
            # sem arredondar, o preço entrega a margem exata sobre a receita líquida
            exato = (p.custo / (1 - p.margem / 100) + p.variaveis_rs()) / (1 - p.variaveis_pct() / 100)
            rl = exato * (1 - p.variaveis_pct() / 100) - p.variaveis_rs()
            self.assertEqual(round((rl - p.custo) / rl * 100, 10), p.margem, kw)
            self.assertEqual(preco.r2(exato), d["preco"], kw)
            # arredondado em 2 casas, a margem fica entre a de um centavo abaixo e a de um centavo acima
            baixo = preco.dre(d["preco"] - D("0.01"), p)["mc_rl"]
            alto = preco.dre(d["preco"] + D("0.01"), p)["mc_rl"]
            self.assertTrue(baixo < p.margem < alto, kw)
            # e sobre a receita bruta a mesma margem vale menos: margem × receita líquida ÷ receita bruta
            self.assertEqual(preco.r4(d["mc_rb"]), preco.r4(d["mc_rl"] * d["rl"] / d["rb"]))


class ProvaA(unittest.TestCase):
    """Prova numérica A da errata da fórmula em três blocos (10/09/2026), Atacado SC para RS.

    Custo 11,60; MC global 50%; MC do canal 45%; ICMS 12%; comissão 0; frete 1,7776 R$/kg × 0,12 kg;
    preço específico 23,00; desconto tático 2%.
    """

    def setUp(self):
        self.p = premissas(custo="11.60", imposto=["ICMS=12"], frete_valor=str(D("1.7776") * D("0.12")), margem="50")

    def test_precos_de_referencia(self):
        self.assertEqual(preco.formar(self.p), D("26.61"))            # preço teto
        self.assertEqual(preco.formar(self.p, D("45")), D("24.21"))   # preço do canal

    def test_leitura_da_margem(self):
        tab = preco.dre(D("23.00"), self.p)
        real = preco.dre(preco.r2(D("23.00") * D("0.98")), self.p)
        self.assertEqual(real["preco"], D("22.54"))
        self.assertEqual(real["deducoes"], D("2.7048"))
        self.assertEqual(real["despesas"]["frete"], D("0.2133"))
        self.assertEqual(real["rl"], D("19.6219"))
        self.assertEqual(real["mc"], D("8.0219"))
        self.assertEqual(preco.r4(real["mc_rl"]), D("40.8824"))
        self.assertEqual(preco.r4(tab["mc_rl"]), D("42.0773"))
        self.assertTrue(fecha(real) and fecha(tab))
        pts, rel, em_rs = preco.desvio_de(tab["mc_rl"], real)
        self.assertEqual(pts, D("-1.1949"))
        self.assertEqual(em_rs, preco.r4(D("19.6219") * D("-1.1949") / 100))
        self.assertEqual(preco.r2(preco.desvio_de(D("45"), real)[0]), D("-4.12"))
        pts, rel, _ = preco.desvio_de(D("50"), real)
        self.assertEqual(preco.r2(pts), D("-9.12"))
        self.assertEqual(preco.r2(rel), D("-18.24"))


class ProvaB(unittest.TestCase):
    """Prova B da mesma errata: Varejo GO para PI, ICMS 7%, comissão 2,5%, frete 4,0491 R$/kg × 0,12 kg, desconto 5%."""

    def test_canal_com_comissao(self):
        p = premissas(custo="11.60", imposto=["ICMS=7"], comissao="2.5", frete_valor=str(D("4.0491") * D("0.12")), margem="50")
        self.assertEqual(preco.formar(p), D("26.17"))
        canal = preco.formar(p, D("45"))
        self.assertEqual(canal, D("23.84"))
        real = preco.dre(preco.r2(canal * D("0.95")), p)
        self.assertEqual(real["preco"], D("22.65"))
        self.assertEqual(preco.r2(real["rl"]), D("20.01"))
        self.assertEqual(preco.r2(real["mc"]), D("8.41"))
        self.assertEqual(preco.r2(real["mc_rl"]), D("42.04"))
        self.assertEqual(preco.r2(preco.desvio_de(D("45"), real)[0]), D("-2.96"))
        self.assertEqual(preco.r2(preco.desvio_de(D("50"), real)[0]), D("-7.96"))
        self.assertTrue(fecha(real))


class Identidade(unittest.TestCase):
    def test_no_preco_formado_sem_desconto_realizada_igual_planejada(self):
        casos = [
            dict(custo="11.60", imposto=["ICMS=12"], frete_valor="0.213312", margem="50"),
            dict(custo="11.60", imposto=["ICMS=7"], comissao="2.5", frete_valor=str(D("4.0491") * D("0.12")), margem="45"),
            dict(custo="8.12", impostos="13.25", comissao="3", frete="2.5", outras="1", margem="25"),
        ]
        for kw in casos:
            p = premissas(**kw)
            exato = (p.custo / (1 - p.margem / 100) + p.variaveis_rs()) / (1 - p.variaveis_pct() / 100)
            rl = exato * (1 - p.variaveis_pct() / 100) - p.variaveis_rs()
            self.assertEqual(round((rl - p.custo) / rl * 100, 12), p.margem, kw)
            # no preço arredondado em 2 casas, o desvio é só o do centavo
            d = preco.dre(preco.formar(p), p)
            self.assertLess(abs(preco.desvio_de(p.margem, d)[0]), D("0.02"), kw)


class Exemplos(unittest.TestCase):
    def test_1_formacao_normal(self):
        p = premissas(**QUEIJO)
        self.assertEqual(preco.formar(p), D("13.49"))
        d = preco.dre(D("13.49"), p)
        self.assertEqual(d["deducoes"], D("1.7874"))
        self.assertEqual(d["rl_contabil"], D("11.7026"))
        self.assertEqual(d["desp_total"], D("0.8769"))
        self.assertEqual(d["rl"], D("10.8257"))
        self.assertEqual(d["mc"], D("2.7057"))
        self.assertEqual(preco.r2(d["mc_rl"]), D("24.99"))
        self.assertEqual(preco.r2(d["mc_rb"]), D("20.06"))
        self.assertTrue(fecha(d))
        mult = preco.dre(preco.r2(D("8.12") * D("1.25")), p)
        self.assertEqual(mult["mc"], D("0.0253"))

    def test_2_tabela_e_desconto_separados(self):
        p = premissas(**QUEIJO)
        plan = preco.dre(D("13.49"), p)
        tab = preco.dre(D("13.20"), p)
        real = preco.dre(preco.r2(D("13.20") * D("0.90")), p)
        self.assertEqual(real["preco"], D("11.88"))
        for d in (plan, tab, real):
            self.assertTrue(fecha(d))
        self.assertEqual(tab["mc"], D("2.4730"))
        self.assertEqual(real["mc"], D("1.4137"))
        # efeito da tabela, contra o planejado
        self.assertEqual(plan["mc"] - tab["mc"], D("0.2327"))
        # efeito do desconto, contra a tabela: desconto × (1 − 19,75%)
        self.assertEqual(tab["mc"] - real["mc"], D("1.0593"))
        self.assertEqual(D("1.32") * (1 - D("0.1975")), D("1.0593"))
        out = rodar(*QUEIJO_CLI, "--margem", "25", "--preco-atual", "13.20", "--desconto", "10")
        self.assertIn("DRE NO PREÇO DE TABELA", out)
        self.assertIn("10,00% sobre o preço de tabela, R$ 13,20", out)
        self.assertIn("Desse valor, R$ 1,0593 saíram da margem", out)
        self.assertIn("Margem da tabela contra a planejada (25,0000%): −1,65 p.p.", out)
        self.assertIn("Margem realizada contra a da tabela (23,3456%): −8,52 p.p.", out)
        self.assertIn("Margem realizada contra a planejada (25,0000%): −10,17 p.p.", out)
        self.assertIn("ficam R$ 1,2920 na mesa", out)

    def test_3_preco_acima_do_formado(self):
        p = premissas(**QUEIJO)
        real = preco.dre(D("15.90"), p)
        self.assertTrue(fecha(real))
        self.assertEqual(real["mc"], D("4.6397"))
        self.assertEqual(preco.r2(real["mc_rl"]), D("36.36"))
        out = rodar(*QUEIJO_CLI, "--margem", "25", "--preco-praticado", "15.90")
        self.assertNotIn("caiu", out)
        self.assertNotIn("saíram da margem", out)
        self.assertNotIn("−R$", out.split("COMPARAÇÃO")[1].split("Margem de contribuição não")[0])
        self.assertIn("ficou R$ 2,4100 acima do preço formado", out)
        self.assertIn("R$ 1,9340 entraram na margem", out)
        self.assertIn("+11,36 p.p., +45,45% relativo, +R$ 1,4498", out)


class Bordas(unittest.TestCase):
    def test_auditoria_sem_margem(self):
        out = rodar("--custo", "22.40", "--impostos", "7.3", "--outras", "2.2", "--preco-atual", "29.12")
        self.assertNotIn("PLANEJADO", out)
        self.assertIn("Margem no preço de tabela: R$ 3,9536, ou 15,00% da receita líquida, 13,58% da receita bruta", out)

    def test_sem_margem_nem_preco_recusa(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            preco.main(["--custo", "10"])

    def test_despesas_acima_de_100(self):
        p = premissas(custo="50", impostos="60", comissao="45", margem="30")
        self.assertIsNone(preco.formar(p))
        self.assertIn("105,00%", "\n".join(preco.explicar_impossivel(p)))

    def test_margem_de_100_ou_mais(self):
        p = premissas(custo="50", impostos="10", margem="100")
        self.assertIsNone(preco.formar(p))
        texto = "\n".join(preco.explicar_impossivel(p, D("100")))
        self.assertIn("44,44%", texto)
        d = preco.dre(D("100"), p)
        self.assertEqual(preco.r2(d["mc_rl"]), D("44.44"))

    def test_receita_zero_nao_calcula_percentual(self):
        p = premissas(custo="10", impostos="10", margem="20")
        d = preco.dre(D("0"), p)
        self.assertIsNone(d["mc_rl"])
        self.assertTrue(d["avisos"])

    def test_html_marca_hipotese_ipi_e_rotulos(self):
        with tempfile.TemporaryDirectory() as tmp:
            arq = os.path.join(tmp, "dre.html")
            rodar("--custo", "58", "--atividade", "industria", "--imposto", "ICMS=12", "--imposto", "PIS=0.65",
                  "--imposto", "COFINS=3", "--comissao", "5", "--margem", "28", "--preco-atual", "109",
                  "--por-fora", "IPI=9.75", "--hipotese", "custo", "--hipotese", "comissao", "--html", arq)
            with open(arq, encoding="utf-8") as f:
                h = f.read()
        self.assertIn("Deduções da receita bruta", h)
        self.assertIn("Custo do produto vendido (CPV) <span class='hip'>hipótese</span>", h)
        self.assertIn("Comissão <span class='hip'>hipótese</span>", h)
        self.assertIn("(+) IPI 9,75%", h)
        self.assertIn("R$ 119,6275", h)
        self.assertIn("Margem em % da receita líquida", h)
        self.assertIn("Margem em % da receita bruta", h)


if __name__ == "__main__":
    unittest.main()
