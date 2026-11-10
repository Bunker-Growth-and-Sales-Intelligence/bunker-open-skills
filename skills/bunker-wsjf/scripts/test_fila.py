"""Testes do fila.py, sem rede: o gh é trocado por um dublê."""
import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fila  # noqa: E402


class Conta(unittest.TestCase):
    def test_wsjf(self):
        self.assertEqual(fila.wsjf(8, 5, 3, 2), 8.0)
        self.assertEqual(fila.wsjf(1, 1, 1, 13), 0.23)

    def test_nota_fora_da_regua(self):
        for nota in (0, 4, 6, 21):
            with self.assertRaises(ValueError):
                fila.wsjf(nota, 1, 1, 1)

    def test_fronteiras_da_prioridade(self):
        self.assertEqual(fila.prioridade(8), "P0")
        self.assertEqual(fila.prioridade(7.99), "P1")
        self.assertEqual(fila.prioridade(5), "P1")
        self.assertEqual(fila.prioridade(4.99), "P2")
        self.assertEqual(fila.prioridade(3), "P2")
        self.assertEqual(fila.prioridade(2.99), "P3")

    def test_notas_das_etiquetas(self):
        rotulos = ["bv-8", "tc-5", "rr-3", "sp-2", "P0", "estado: delegado", "bv-x", "sp-4", "bug"]
        self.assertEqual(fila.notas_de(rotulos), {"bv": 8, "tc": 5, "rr": 3, "sp": 2})


class ComGhFalso(unittest.TestCase):
    def rodar(self, respostas, *args):
        chamadas = []

        def gh_falso(*a, simular=False, escreve=False):
            chamadas.append(a)
            if escreve:
                return ""
            return respostas[a[0] + " " + a[1]]

        saida = io.StringIO()
        with mock.patch.object(fila, "gh", side_effect=gh_falso), redirect_stdout(saida):
            fila.main(list(args))
        return chamadas, saida.getvalue()

    def test_nota_troca_so_as_etiquetas_da_regua(self):
        issue = {"state": "OPEN", "labels": [{"name": n} for n in ("bv-3", "tc-5", "P2", "estado: agendado", "bug")]}
        chamadas, saida = self.rodar({"issue view": json.dumps(issue)},
                                     "nota", "dono/repo", "12", "8", "5", "3", "2")
        edicao = chamadas[-1]
        self.assertIn("bv-8", edicao)
        self.assertIn("P0", edicao)
        removidas = [edicao[i + 1] for i, a in enumerate(edicao) if a == "--remove-label"]
        self.assertEqual(sorted(removidas), ["P2", "bv-3"])
        self.assertIn("WSJF 8.0 (P0)", saida)

    def test_nota_recusa_issue_fechada(self):
        issue = {"state": "CLOSED", "labels": []}
        with self.assertRaises(SystemExit):
            self.rodar({"issue view": json.dumps(issue)}, "nota", "dono/repo", "12", "8", "5", "3", "2")

    def test_fila_em_ordem_e_sem_os_que_dormem(self):
        def issue(n, rotulos):
            return {"number": n, "title": f"assunto {n}", "labels": [{"name": r} for r in rotulos]}
        issues = [
            issue(1, ["bv-2", "tc-1", "rr-1", "sp-5"]),
            issue(2, ["bv-13", "tc-8", "rr-5", "sp-2"]),
            issue(3, ["bv-13", "tc-13", "rr-13", "sp-1", "estado: delegado"]),
            issue(4, ["bv-5"]),
        ]
        _, saida = self.rodar({"issue list": json.dumps(issues)}, "fila", "dono/repo")
        linhas = [l for l in saida.splitlines() if "WSJF" in l]
        self.assertEqual(len(linhas), 2)
        self.assertIn("issue 2", linhas[0])
        self.assertIn("issue 1", linhas[1])
        self.assertIn("sem as quatro notas (1): 4", saida)

        _, saida = self.rodar({"issue list": json.dumps(issues)}, "fila", "dono/repo", "--todas")
        self.assertIn("issue 3", saida.splitlines()[0])


if __name__ == "__main__":
    unittest.main()
