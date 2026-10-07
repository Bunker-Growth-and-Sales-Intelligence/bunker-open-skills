#!/usr/bin/env python3
"""Testes da bunker-prioridade-copilot. Rodar: python3 -m unittest discover -s skills/bunker-prioridade-copilot/scripts"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
EXEMPLO = os.path.join(AQUI, '..', 'exemplos', 'demandas.json')


def d(nome, v, u, r, t):
    return {'nome': nome, 'valor': v, 'urgencia': u, 'risco': r, 'tamanho': t}


CONTRATO = d('Contrato', 13, 13, 8, 3)
BACKUP = d('Backup', 8, 5, 13, 2)
LOGO = d('Logo', 1, 1, 1, 2)
LOGIN = d('Login', 2, 1, 1, 5)


class TestConta(unittest.TestCase):
    def test_wsjf_dos_exemplos_do_encontro(self):
        import prioridade as p
        self.assertEqual(p.wsjf(CONTRATO), 11.3)
        self.assertEqual(p.wsjf(BACKUP), 13.0)
        self.assertEqual(p.wsjf(LOGO), 1.5)
        self.assertEqual(p.wsjf(LOGIN), 0.8)

    def test_nota_fora_da_escala_levanta_erro_que_diz_a_escala(self):
        import prioridade as p
        with self.assertRaises(ValueError) as e:
            p.validar(d('X', 9, 1, 1, 1))
        self.assertIn('1, 2, 3, 5, 8 ou 13', str(e.exception))
        self.assertIn('X', str(e.exception))

    def test_nota_ausente_deixa_o_wsjf_nulo_e_nao_inventa(self):
        import prioridade as p
        self.assertIsNone(p.wsjf({'nome': 'Sem tamanho', 'valor': 5, 'urgencia': 5, 'risco': 5}))
        self.assertIsNone(p.wsjf({'nome': 'Sem valor', 'urgencia': 5, 'risco': 5, 'tamanho': 2}))

    def test_prioridade_p0_a_p3_nas_fronteiras(self):
        import prioridade as p
        casos = [(13.0, 'P0'), (8.0, 'P0'), (7.9, 'P1'), (5.0, 'P1'), (4.9, 'P2'), (3.0, 'P2'), (2.9, 'P3'), (0.8, 'P3')]
        for w, esperado in casos:
            self.assertEqual(p.prioridade(w), esperado, w)
        self.assertEqual(p.prioridade(None), 'Sem nota')

    def test_ordem_maior_wsjf_primeiro(self):
        import prioridade as p
        ordem = [x['nome'] for x in p.ordenar([LOGO, CONTRATO, LOGIN, BACKUP])]
        self.assertEqual(ordem, ['Backup', 'Contrato', 'Logo', 'Login'])

    def test_empate_o_mais_curto_vai_primeiro(self):
        import prioridade as p
        a = d('Longa', 5, 5, 5, 5)   # 3,0
        b = d('Curta', 2, 2, 2, 2)   # 3,0
        self.assertEqual([x['nome'] for x in p.ordenar([a, b])], ['Curta', 'Longa'])

    def test_sem_nota_vai_para_o_fim(self):
        import prioridade as p
        ordem = p.ordenar([{'nome': 'Vaga', 'valor': 5}, LOGO, CONTRATO])
        self.assertEqual(ordem[-1]['nome'], 'Vaga')


class TestQuadrantes(unittest.TestCase):
    def setUp(self):
        import prioridade as p
        self.q = p.quadrantes([CONTRATO, BACKUP, LOGO, LOGIN])

    def nomes(self, matriz, quadrante):
        return [x['nome'] for x in self.q[matriz]['quadrantes'][quadrante]['itens']]

    def test_matriz_1_valor_x_urgencia(self):
        self.assertEqual(self.nomes('valor_urgencia', 'Fazer agora'), ['Contrato'])
        self.assertEqual(self.nomes('valor_urgencia', 'Agendar'), ['Backup'])
        self.assertEqual(self.nomes('valor_urgencia', 'Armadilha'), [])
        self.assertEqual(self.nomes('valor_urgencia', 'Estacionar'), ['Logo', 'Login'])

    def test_matriz_2_esforco_x_wsjf(self):
        self.assertEqual(self.nomes('esforco_wsjf', 'Rápido e rende'), ['Backup', 'Contrato'])
        self.assertEqual(self.nomes('esforco_wsjf', 'Projeto grande'), [])
        self.assertEqual(self.nomes('esforco_wsjf', 'Se sobrar tempo'), ['Logo'])
        self.assertEqual(self.nomes('esforco_wsjf', 'Vale a pena?'), ['Login'])

    def test_matriz_3_valor_x_risco(self):
        self.assertEqual(self.nomes('valor_risco', 'Estratégico'), ['Backup', 'Contrato'])
        self.assertEqual(self.nomes('valor_risco', 'Pouco valor'), ['Logo', 'Login'])

    def test_cada_item_fica_em_exatamente_um_quadrante_por_matriz(self):
        for chave in ('valor_urgencia', 'esforco_wsjf', 'valor_risco'):
            m = self.q[chave]
            todos = [x['nome'] for qd in m['quadrantes'].values() for x in qd['itens']]
            self.assertEqual(sorted(todos), ['Backup', 'Contrato', 'Login', 'Logo'], chave)

    def test_cada_matriz_destaca_um_quadrante(self):
        self.assertEqual(self.q['valor_urgencia']['destaque'], 'Fazer agora')
        self.assertEqual(self.q['esforco_wsjf']['destaque'], 'Rápido e rende')
        self.assertEqual(self.q['valor_risco']['destaque'], 'Estratégico')

    def test_dentro_do_quadrante_a_ordem_e_a_do_wsjf(self):
        import prioridade as p
        q = p.quadrantes([LOGO, LOGIN, d('Outra', 2, 2, 1, 1)])
        itens = [x['nome'] for x in q['valor_urgencia']['quadrantes']['Estacionar']['itens']]
        self.assertEqual(itens, ['Outra', 'Logo', 'Login'])

    def test_corte_ajustavel(self):
        import prioridade as p
        q = p.quadrantes([BACKUP], cortes={'alto': 5})
        nomes = [x['nome'] for x in q['valor_urgencia']['quadrantes']['Fazer agora']['itens']]
        self.assertEqual(nomes, ['Backup'])  # urgência 5 passa a ser alta

    def test_item_sem_nota_fica_fora_e_e_listado(self):
        import prioridade as p
        q = p.quadrantes([CONTRATO, {'nome': 'Vaga', 'valor': 5}])
        todos = [x['nome'] for qd in q['valor_urgencia']['quadrantes'].values() for x in qd['itens']]
        self.assertEqual(todos, ['Contrato'])
        self.assertEqual([x['nome'] for x in q['sem_nota']], ['Vaga'])

    def test_a_primeira_da_fila(self):
        import prioridade as p
        self.assertEqual(p.primeira([CONTRATO, BACKUP, LOGO, LOGIN])['nome'], 'Backup')
        self.assertIsNone(p.primeira([]))


class TestSaida(unittest.TestCase):
    def spec(self):
        return json.load(open(EXEMPLO, encoding='utf-8'))

    def test_exemplo_valido(self):
        import prioridade as p
        p.validar_spec(self.spec())

    def test_relatorio_em_texto_lista_a_fila_e_os_quadrantes(self):
        import prioridade as p
        md = p.relatorio_md(self.spec())
        for trecho in ('A primeira da fila', 'Testar o backup do banco', 'Fazer agora', 'Rápido e rende',
                       'Estratégico', 'P0', '13,0'):
            self.assertIn(trecho, md)

    def test_sigla_nao_vira_minuscula_no_texto(self):
        import prioridade as p
        md = p.relatorio_md(self.spec())
        self.assertNotIn('wsjf alto', md)
        self.assertIn('WSJF alto e pouco esforço', md)

    def test_html_tem_as_tres_matrizes_e_todas_as_demandas(self):
        import prioridade as p
        html = p.relatorio_html(self.spec())
        self.assertEqual(html.count('class="matriz"'), 3)
        for dm in self.spec()['demandas']:
            self.assertIn(dm['nome'].split(',')[0], html)

    def test_html_escapa_o_texto_do_usuario(self):
        import prioridade as p
        spec = {'titulo': '<b>x</b>', 'demandas': [d('<img src=x onerror=y()>', 5, 5, 5, 2)]}
        html = p.relatorio_html(spec)
        self.assertNotIn('<img src=x', html)
        self.assertNotIn('<b>x</b>', html)

    def test_html_e_monocromatico(self):
        import prioridade as p
        html = p.relatorio_html(self.spec())
        cores = set(re.findall(r'#[0-9a-fA-F]{6}\b', html))
        vivas = [c for c in cores if len({c[1:3].lower(), c[3:5].lower(), c[5:7].lower()}) > 1]
        self.assertEqual(vivas, [], vivas)

    def test_linha_de_comando_grava_md_e_html(self):
        with tempfile.TemporaryDirectory() as t:
            r = subprocess.run([sys.executable, os.path.join(AQUI, 'prioridade.py'), EXEMPLO, '--saida', t],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(os.path.exists(os.path.join(t, 'prioridade.md')))
            self.assertTrue(os.path.exists(os.path.join(t, 'prioridade.html')))

    def test_linha_de_comando_com_nota_invalida_sai_com_erro_legivel(self):
        with tempfile.TemporaryDirectory() as t:
            ruim = os.path.join(t, 'ruim.json')
            json.dump({'demandas': [d('X', 9, 1, 1, 1)]}, open(ruim, 'w'))
            r = subprocess.run([sys.executable, os.path.join(AQUI, 'prioridade.py'), ruim, '--saida', t],
                               capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn('1, 2, 3, 5, 8 ou 13', r.stderr)
            self.assertNotIn('Traceback', r.stderr)


if __name__ == '__main__':
    unittest.main()
