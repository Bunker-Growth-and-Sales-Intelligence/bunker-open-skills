---
name: bunker-prioridade-copilot
description: Organiza qualquer lista de demandas pela conta WSJF e monta os quadrantes para decidir o que fazer primeiro. Você junta o que tem a fazer (e-mail, planilha, lista colada, print), a IA propõe as notas de valor, urgência, risco e tamanho em 1, 2, 3, 5, 8 ou 13, calcula o WSJF, ordena a fila, dá a prioridade P0 a P3 e coloca cada demanda nos quadrantes de três matrizes (valor por urgência, esforço por WSJF, valor por risco), com a lista do que cai em cada quadrante e um quadrante em destaque por matriz. Entrega a fila e as matrizes em texto, e um HTML com a marca da Bunker. Use quando pedirem "o que eu faço primeiro", "organiza minhas demandas", "prioriza minha lista", "WSJF", "matriz de prioridade", "matriz de Eisenhower", "o que está urgente e o que vale a pena", "fila de tarefas", ou quando alguém colar uma lista de tarefas e quiser a ordem.
---

# Prioridade: o que fazer primeiro

Uma lista de tarefas sem ordem faz quem a executa atender o que grita mais alto. Esta skill
dá a ordem por uma conta, e mostra a lista em quadrantes para decidir.

**A frase que guia tudo: sempre a primeira da lista.** Ordenou? Faça a primeira até
terminar. Só então a segunda. E **pressão não fura fila**: o pedido sob pressão entra na fila,
é pontuado pela mesma régua de todos, e, se a nota for baixa, a conta é a resposta.

Funciona em qualquer IA de chat. Se a IA rodar Python, o script `scripts/prioridade.py` faz a
conta e gera o HTML. Se não rodar, ela faz a conta passo a passo, como está abaixo.

## A conta

**WSJF = (valor + urgência + risco) ÷ tamanho.** O trabalho mais curto e mais caro de esperar
vai primeiro.

| Nota | Pergunta |
|---|---|
| Valor | Quanto o cliente ou a empresa ganha com isso pronto? Em reais, em horas ou, se não houver número, o valor intangível. |
| Urgência | Existe prazo? Perde cliente se demorar? O valor cai com o tempo? |
| Risco | Quanto isso evita um problema ou abre uma oportunidade? O risco cresce quanto mais o assunto espera. |
| Tamanho | Quanto dá de trabalho para terminar? Esforço, tempo ou complexidade. |

**As notas são só 1, 2, 3, 5, 8 ou 13.** Os saltos são de propósito: ninguém sabe se um
trabalho é 6 ou 7, mas todo mundo sabe se é 5 ou 8. Não existe 9,5, e alta, média e baixa não
substituem a nota. No empate de WSJF, a tarefa mais curta vai primeiro.

**Régua:** P0 é WSJF de 8 ou mais, P1 de 5 a 7,9, P2 de 3 a 4,9 e P3 abaixo de 3. Quem manda é
o WSJF, e a prioridade é consequência.

Exemplo resolvido: *renovar o contrato do maior cliente, que vence dia 20.* Valor 13, urgência
13, risco 8, tamanho 3. (13 + 13 + 8) ÷ 3 = 11,3. *Testar o backup do banco, parado há seis
meses.* Valor 8, urgência 5, risco 13, tamanho 2. (8 + 5 + 13) ÷ 2 = 13,0. O backup vai antes do
contrato, porque é pequeno e o risco é enorme.

## O que fazer, na ordem

1. **Juntar.** Peça tudo o que a pessoa precisa fazer, de todos os canais: e-mail, planilha,
   lista de tarefas, CRM, WhatsApp, conversa de corredor. Se a IA estiver conectada ao e-mail
   ou às ferramentas dela, ela lê e lista. Senão, a pessoa cola ou arrasta o arquivo. Junte as
   demandas do mesmo assunto numa só.
2. **Separar sintoma de causa.** Sintoma é o que aparece (preço errado, cliente reclamando).
   Causa é o que provoca (cadastro sem regra, processo sem dono). Três sintomas da mesma causa
   viram uma tarefa só, com o valor somado.
3. **Propor as notas.** Para cada demanda, a IA sugere valor, urgência, risco e tamanho e diz
   em uma frase de onde veio cada nota. **A IA sugere, quem executa decide.** Mostre as notas e
   deixe a pessoa corrigir. Se faltar informação para uma nota, pergunte, e nunca invente.
4. **Calcular.** WSJF de cada demanda, ordem da fila e prioridade P0 a P3. Demanda com alguma
   das quatro notas faltando fica sem WSJF e vai para o fim, avisada: meia conta ordenaria a fila
   com um número que ninguém mediu.
5. **Montar os quadrantes**, abaixo.
6. **Entregar** a fila ordenada, as três matrizes e, no topo, **a primeira da fila**.
7. **Reponderar.** O risco e a urgência mudam com o tempo. A nota de hoje não é a da semana
   que vem: refaça a conta com regularidade.

## Os três quadrantes

Cada demanda cai em exatamente um quadrante de cada matriz. Dentro do quadrante, a ordem é a do
WSJF. Cada matriz tem um quadrante em **destaque**, de onde sai a primeira tarefa.

**Matriz 1: valor × urgência. Para gestor e dono: o que sai agora?**

| Quadrante | Leitura | O que fazer |
|---|---|---|
| **Fazer agora** (destaque) | valor alto e urgente | Quem trabalha sozinho escolhe a primeira. Quem tem equipe delega estas. |
| Agendar | valor alto, pode esperar | Dê uma data. Fica com você. |
| Armadilha | urgente e de pouco valor | É onde caem os pedidos de pressão. Tire da frente: responda dizendo em que posição da fila ele está e por quê. |
| Estacionar | nem valor nem urgência | Fica fora da semana. |

**Matriz 2: esforço × WSJF. Para quem toca projeto: o que sai rápido e rende?**
**Rápido e rende** (destaque: WSJF alto e pouco esforço) é a ordem do que entra na semana.
Projeto grande (WSJF alto, muito trabalho). Se sobrar tempo (pouco esforço, WSJF baixo). Vale a
pena? (muito trabalho, WSJF baixo): questione antes de começar. O eixo é o da facilidade: o bom
fica à direita.

**Matriz 3: valor × risco. Para TI, fiscal, contábil e dono: o que protege o negócio?**
**Estratégico** (destaque: valor alto e risco grande evitado). Manutenção (tira um risco
grande, com pouco valor direto: backup, LGPD, segurança, que ninguém pressiona). Novidade (traz
valor, não reduz risco). Pouco valor (não merece lugar na fila).

**Os cortes são uma convenção desta skill, não uma regra do WSJF, e se ajustam:** nota 8 ou
mais é alta (valor, urgência e risco); tamanho 3 ou menos é pouco esforço; WSJF 5 ou mais é
alto. Diga isso ao usuário e ofereça mudar o corte se a fila ficar toda num canto só.

## A entrega

**Com Python**, grave as demandas em JSON e rode:

```bash
python3 scripts/prioridade.py demandas.json --saida pasta
```

O formato está em `exemplos/demandas.json`: um nome e as quatro notas por demanda. A saída é
`prioridade.md` e `prioridade.html`, com a marca da Bunker, que abre no navegador e imprime em
PDF. Ajuste os cortes com `--corte-alto`, `--corte-facil` e `--corte-wsjf`. Os testes rodam com
`python3 -m unittest discover -s scripts`.

**Sem Python**, entregue em texto: (1) a primeira da fila em uma frase; (2) uma tabela da fila
com as quatro notas, o WSJF e a prioridade, em ordem; (3) para cada uma das três matrizes, os
quatro quadrantes com o nome, a leitura e a lista de demandas, marcando o destaque; (4) as
demandas sem nota, se houver; (5) uma linha dizendo que as notas são sugestão e quais foram os
cortes.

## Regras de conduta

- **Não invente número.** Valor em reais, horas ou prazo só entram se a pessoa deu ou se está
  no material lido. Sem número, diga que a nota é um palpite e por quê.
- **A pessoa decide as notas.** Mostre-as antes de fechar a ordem e aceite correção.
- **Pressão não fura fila.** Se alguém pede para furar a fila, registre, pontue, e mostre a
  conta.
- Dado pessoal ou de cliente fica com a pessoa: não o copie para fora da conversa.

## O que a skill não faz

Não mede esforço de verdade nem conhece o seu negócio: as notas vêm da conversa. Não decide
por você: o WSJF ordena, e o julgamento é seu. Não substitui um planejamento de projeto. E o
corte dos quadrantes é uma convenção: confira se faz sentido para a sua lista.

## Arquivos

```
SKILL.md                       esta skill; colada sozinha numa conversa, já funciona
references/metodo.md           o porquê da conta: custo do atraso e o exemplo das três tarefas
scripts/prioridade.py          a conta, os quadrantes e a saída em texto e HTML (só biblioteca padrão)
scripts/test_prioridade.py     testes
exemplos/demandas.json         quatro demandas com as notas, para ver a saída
assets/bunker-logo-preto.png   logo usado no HTML
```

Gratuita, da [Bunker](https://bunkerconsultancy.com). Quer aprender a ler e a montar isto com a sua
equipe? Abra o portal Bunker Alumni.
