# O porquê da conta

## Toda tarefa dá prejuízo enquanto espera

A pergunta que orienta a ordem não é "qual é a mais importante?", e sim **quanto custa esperar**.
Receita que não entra, cliente que esfria e risco que cresce são o custo do atraso. O WSJF põe
esse custo em cima da fração (valor + urgência + risco) e divide pelo tamanho do trabalho: o que
é pequeno e caro de esperar vai primeiro, porque devolve o resultado mais cedo.

## O exemplo das três tarefas

Três tarefas e uma pessoa fazendo uma de cada vez. Enquanto uma não fica pronta, perde dinheiro
toda semana.

| Tarefa | Perde por semana | Leva | Perda ÷ semanas |
|---|---|---|---|
| A. Renovar o contrato | R$ 10 mil | 1 semana | 10 |
| C. Relatório de crédito | R$ 8 mil | 2 semanas | 4 |
| B. O pedido de quem pressionou | R$ 3 mil | 3 semanas | 1 |

- **Ordem A, C, B** (maior resultado primeiro): A fica pronta na semana 1 e perdeu 10. C fica
  pronta na 3 e perdeu 8 três vezes, 24. B fica pronta na 6 e perdeu 3 seis vezes, 18.
  Total: **R$ 52 mil**.
- **Ordem B, A, C** (atendendo quem pressionou): B pronta na 3, perdeu 9. A pronta na 4, perdeu
  40. C pronta na 6, perdeu 48. Total: **R$ 97 mil**.
- **As três ao mesmo tempo:** todas prontas só na semana 6, 60 + 18 + 48 = **R$ 126 mil**, sem
  contar o tempo perdido na troca de tarefa.

Mesmo time, mesmas seis semanas, só a ordem mudou: R$ 45 mil a mais. A ordem por "perda por
semana ÷ semanas de trabalho" é a do WSJF, e a regra de Smith (1956) mostra que ela dá a menor
perda total possível.

## O princípio da fila única

Um lugar, uma ordem, um histórico. A lista espalhada por e-mail, planilha, CRM e conversa de
corredor precisa virar uma fila só, para que alguém a ordene. O GitHub serve a isso mesmo para
quem não programa: cada demanda é uma issue, as etiquetas guardam a nota e a prioridade, e o
histórico fica. É uma escolha, e não a única possível.

## Sobre o corte dos quadrantes

A conta WSJF e a régua P0 a P3 são o método. O ponto em que uma nota passa a ser "alta" nos
quadrantes é uma decisão de desenho, e esta skill usa 8 ou mais. Com notas em Fibonacci, um corte
fixo pode jogar quase tudo num canto: se isso acontecer, mude o corte, ou use a mediana da sua
própria lista.
