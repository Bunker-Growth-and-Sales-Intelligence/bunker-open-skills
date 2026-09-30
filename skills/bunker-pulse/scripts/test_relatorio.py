"""Testes do status report: leitura, status, nomes curtos, manchetes e slides que entram.

    python3 -m unittest discover -s skills/bunker-pulse/scripts
"""
import datetime as dt
import json
import os
import re
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relatorio as R  # noqa: E402

HOJE = '2026-09-30'


def registro(atividades, **extra):
    base = {'projeto': 'Teste', 'cliente': 'Cliente', 'medido_em': HOJE,
            'fonte': 'lista de teste', 'atividades': atividades}
    base.update(extra)
    f = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8')
    json.dump(base, f, ensure_ascii=False)
    f.close()
    return f.name


def rodar(atividades, **extra):
    base, hoje, itens, avisos = R.ler(registro(atividades, **extra))
    R.definir_cores(base)
    blocos, fora, atrasados, faltam = R.montar(base, hoje, itens)
    return {b['chave']: b for b in blocos}, fora, avisos, base, hoje, faltam, atrasados


class Status(unittest.TestCase):
    def test_palavras_comuns(self):
        casos = {'Concluído': 'concluida', 'Done': 'concluida', 'Em andamento': 'andamento',
                 'In Progress': 'andamento', 'A fazer': 'aberta', 'To Do': 'aberta',
                 'Bloqueado': 'bloqueada', 'Aguardando cliente': 'bloqueada',
                 'Cancelado': 'cancelada', 'Pendente': 'aberta', 'Vencido': 'aberta',
                 'concluida': 'concluida'}
        for bruto, canon in casos.items():
            self.assertEqual(R.status_canonico(bruto), (canon, True), bruto)

    def test_desconhecido_vira_aberta_com_aviso(self):
        self.assertEqual(R.status_canonico('xyz'), ('aberta', False))
        avisos = rodar([{'titulo': 'a', 'status': 'xyz'}])[2]
        self.assertTrue(any('xyz' in a for a in avisos))


class Datas(unittest.TestCase):
    def test_formatos(self):
        self.assertEqual(R.data('2026-04-13'), dt.date(2026, 4, 13))
        self.assertEqual(R.data('13/04/2026'), dt.date(2026, 4, 13))
        self.assertEqual(R.data('2026-04-13T10:00:00Z'), dt.date(2026, 4, 13))
        self.assertIsNone(R.data('13/abr'))
        self.assertIsNone(R.data(None))


class NomeCurto(unittest.TestCase):
    def test_nao_termina_em_conectivo_nem_virgula(self):
        self.assertEqual(R.curto('Governança e Descoberta'), 'Governança')
        self.assertEqual(R.curto('Definição de perfis, papéis e alçadas', 24), 'Definição de perfis')
        self.assertNotIn('…', R.curto('Um nome muito comprido demais para a calha'))

    def test_exibicao_vence_o_corte(self):
        R.EXIBICAO.clear()
        R.EXIBICAO['Construção Sales Cloud'] = 'Construção'
        self.assertEqual(R.curto('Construção Sales Cloud'), 'Construção')
        R.EXIBICAO.clear()


class Manchetes(unittest.TestCase):
    def lista(self):
        # 10 atividades: 4 concluídas, 3 atrasadas, frentes A e B
        a = []
        for k in range(4):
            a.append({'titulo': f'feita {k}', 'frente': 'Frente A', 'status': 'concluida',
                      'responsavel': 'Ana', 'prazo': '2026-09-01'})
        for k in range(3):
            a.append({'titulo': f'atrasada {k}', 'frente': 'Frente B', 'status': 'aberta',
                      'prazo': f'2026-09-{10 + k}'})
        for k in range(3):
            a.append({'titulo': f'no prazo {k}', 'frente': 'Frente B', 'status': 'andamento',
                      'responsavel': 'Bruno', 'prazo': '2026-10-15'})
        return a

    def test_numeros(self):
        b, *_ = rodar(self.lista())
        self.assertEqual(b['numeros']['manchete'],
                         '40% concluído: 4 de 10 atividades, e 3 estão atrasadas.')

    def test_frente_concluida_e_proxima(self):
        b, *_ = rodar(self.lista())
        self.assertEqual(b['frentes']['manchete'],
                         '1 frente já está concluída: Frente A. A próxima é Frente B, com 0 de 6.')

    def test_empate_de_situacao_nao_elege_lider(self):
        b, *_ = rodar(self.lista())
        self.assertIn('dividido por igual', b['situacao']['manchete'])

    def test_sem_responsavel_so_lidera_quando_passa_de_todos(self):
        b, *_ = rodar(self.lista())
        # 3 sem responsável contra 3 do Bruno: empate, então quem lidera é o Bruno
        self.assertTrue(b['responsaveis']['manchete'].startswith('Bruno está com 3'))

    def test_mediana_da_manchete_e_a_do_desenho(self):
        a = [{'titulo': f'x{k}', 'status': 'aberta', 'frente': 'F' + str(k % 2),
              'prazo': (dt.date(2026, 9, 30) - dt.timedelta(days=d)).isoformat()}
             for k, d in enumerate([1, 2, 3, 20, 30, 40])]
        b, *_ = rodar(a)
        n = re.search(r'típica passou (\d+) dias', b['dias']['manchete']).group(1)
        self.assertIn(f'mediana {n} dias', b['dias']['desenho'])


class SlidesQueEntram(unittest.TestCase):
    def test_sem_prazo_sem_slide_de_atraso(self):
        b, fora, *_ = rodar([{'titulo': 'a', 'status': 'aberta', 'frente': 'X'},
                             {'titulo': 'b', 'status': 'concluida', 'frente': 'Y'}])
        self.assertNotIn('atrasos', b)
        self.assertTrue(any('prazo' in x for x in fora))

    def test_cancelada_fica_fora_da_conta(self):
        b, *_ = rodar([{'titulo': 'a', 'status': 'concluida'},
                       {'titulo': 'b', 'status': 'cancelada'}])
        self.assertTrue(b['numeros']['manchete'].startswith('100% concluído: 1 de 1'))

    def test_cascata_com_datas(self):
        a = [{'titulo': f't{k}', 'status': 'concluida' if k % 2 else 'aberta',
              'criada_em': f'2026-09-{k + 1:02d}',
              'concluida_em': f'2026-09-{k + 5:02d}' if k % 2 else None}
             for k in range(10)]
        b, *_ = rodar(a)
        self.assertIn('cascata', b)
        self.assertIn('ritmo', b)


class Deck(unittest.TestCase):
    def test_html_completo_e_sem_convite(self):
        b, fora, avisos, base, hoje, faltam, atrasados = rodar(Manchetes().lista(),
                                                                cores={'primaria': '#2f6f4f'})
        html = R.deck_html(base, hoje, list(b.values()), faltam, atrasados)
        tabela = -(-len(faltam) // 4)                                 # 4 linhas por slide
        self.assertEqual(html.count('<deck-stage'), 2 + len(b) + tabela)  # capa e fecho
        self.assertIn('#2f6f4f', html)
        self.assertIn('skill pública da Bunker', html)
        self.assertNotIn('Alumni', html)
        self.assertNotIn('http://', re.sub(r'xmlns="http://www.w3.org/2000/svg"', '', html))

    def test_manchete_do_registro_vence(self):
        b, fora, avisos, base, hoje, faltam, atrasados = rodar(
            Manchetes().lista(), manchetes={'numeros': 'Frase escrita pela pessoa.'})
        html = R.deck_html(base, hoje, list(b.values()), faltam, atrasados)
        self.assertIn('Frase escrita pela pessoa.', html)

    def test_sem_cor_vale_a_paleta_alumni(self):
        R.definir_cores({})
        from pulso import paleta
        self.assertEqual((paleta.PRIMARIA, paleta.SECUNDARIA), ('#3b82f6', '#f43f5e'))

    def test_cor_invalida_cai_no_padrao(self):
        R.definir_cores({'cores': {'primaria': 'azul'}})
        from pulso import paleta
        self.assertEqual(paleta.PRIMARIA, R.PADRAO[0])


class Priorizacao(unittest.TestCase):
    def lista(self):
        a = []
        notas = [(13, 8, 8, 2), (8, 5, 3, 5), (3, 2, 1, 8), (5, 8, 2, 3), (2, 1, 1, 13), (13, 3, 5, 5)]
        for k, (v, u, r, e) in enumerate(notas):
            a.append({'id': f'X{k}', 'titulo': f'item {k}', 'frente': 'A' if k % 2 else 'B',
                      'status': 'aberta', 'prioridade': 'P0' if k == 0 else 'P2',
                      'valor': v, 'urgencia': u, 'risco': r, 'esforco': e})
        a.append({'id': 'X9', 'titulo': 'feito', 'frente': 'A', 'status': 'concluida'})
        a[2]['depende_de'] = ['X0']
        a[4]['depende_de'] = ['X0']
        return a

    def test_wsjf_da_frente_e_soma_sobre_soma(self):
        b, *_ = rodar(self.lista())
        # B: itens 0, 2, 4 -> custo 29+6+4=39, esforço 2+8+13=23 -> 1,7
        # A: itens 1, 3, 5 -> custo 16+15+21=52, esforço 5+3+5=13 -> 4,0
        self.assertIn('A deve vir primeiro', b['wsjf']['manchete'])
        self.assertIn('WSJF de 4,0', b['wsjf']['manchete'])

    def test_quadrantes_e_urgentes_entram(self):
        b, *_ = rodar(self.lista())
        for k in ('agora', 'rapido', 'estrategica', 'urgentes', 'dependencias'):
            self.assertIn(k, b)
        self.assertTrue(b['urgentes']['manchete'].startswith('1 das 6'))
        self.assertTrue(b['dependencias']['manchete'].startswith('item 0 segura 2'))

    def test_sem_plano_tira_a_priorizacao(self):
        base, hoje, itens, _ = R.ler(registro(self.lista()))
        base['_plano'] = False
        blocos, *_ = R.montar(base, hoje, itens)
        chaves = {x['chave'] for x in blocos}
        self.assertFalse(chaves & {'wsjf', 'agora', 'rapido', 'estrategica', 'urgentes'})

    def test_nota_de_contexto_vira_adesivo(self):
        b, fora, avisos, base, hoje, faltam, atrasados = rodar(
            self.lista(), notas={'wsjf': 'Decidido no comitê de 10/09.'})
        html = R.deck_html(base, hoje, list(b.values()), faltam, atrasados)
        self.assertIn('Decidido no comitê de 10/09.', html)
        self.assertIn('O que é WSJF', html)

    def test_tabela_na_ordem_do_wsjf(self):
        _b, _f, _a, base, hoje, faltam, _t = rodar(self.lista())
        ordem = [a['id'] for a in R.ordem_de_ataque(faltam, hoje)]
        self.assertEqual(ordem[0], 'X0')   # WSJF 14,5


if __name__ == '__main__':
    unittest.main()
