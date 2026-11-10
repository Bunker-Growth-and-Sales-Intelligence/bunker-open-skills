---
name: bunker-wsjf
description: Dá a ordem da fila de issues pela régua WSJF. Para cada issue aberta, lê corpo e comentários, dá as quatro notas em Fibonacci (valor, urgência, risco e tamanho), cada uma com a frase da fonte que a sustenta, grava as notas como etiquetas e calcula WSJF = (valor + urgência + risco) ÷ tamanho, com prioridade de P0 a P3. Mostra a fila em ordem e os cinco primeiros. Chamada pela skill bunker-ignicao a cada fato novo. Use quando o usuário disser "classifica as issues", "roda o WSJF", "o que eu faço primeiro", "prioriza a fila", "dá as notas".
---

# WSJF: o que fazer primeiro

A skill responde uma pergunta: **o que eu faço primeiro?** Ela dá as notas e mostra a ordem. Abrir issue, conversar com alguém e executar o trabalho ficam com a skill `bunker-ignicao` e com as conversas filhas.

## A conta

```
WSJF = (valor + urgência + risco) ÷ tamanho
```

| WSJF | Prioridade |
|---|---|
| 8 ou mais | `P0` |
| 5 a 7,99 | `P1` |
| 3 a 4,99 | `P2` |
| abaixo de 3 | `P3` |

**O Claude dá as notas e o script faz a conta.** A prioridade sai do WSJF e nunca é escolhida à mão. As âncoras de cada nota estão em [references/regua.md](references/regua.md).

## As regras de toda nota

1. **Só vale 1, 2, 3, 5, 8 ou 13.** Ninguém sabe dizer se um trabalho é 6 ou 7, mas todo mundo sabe se é 5 ou 8.
2. **Toda nota tem uma frase que a sustenta**, tirada da issue ou de um comentário. Nota sem frase fica de fora.
3. **A nota é do que falta.** Issue com o trabalho quase pronto e só a conferência pendente tem tamanho 1 e o valor do que a conferência confirma.
4. **Recalcula tudo.** A nota antiga entra como contexto. Se a leitura nova der outro número, vale o novo.
5. **Prazo só com data dita** pelo outro lado ou pelo usuário. Data imaginada não sobe urgência.
6. **Só o que está na fila disputa a nota.** Issue com etiqueta `estado: agendado`, `delegado`, `aguardando` ou `algum dia` sai da lista até o dia do bloco ou do follow-up (ver a skill `bunker-ignicao`).
7. **A fila manda.** Quem muda a ordem é um fato novo, que gera nota nova. Se alguém pedir para passar um assunto na frente sem fato novo, pergunte ao usuário em caixinha.

## Valor medido em dinheiro

O valor é o dinheiro esperado do usuário com aquilo resolvido: o valor do negócio × a chance de acontecer × a parte que é dele. Conta a pagar entra como risco. Monte a escala com os números do seu negócio e grave em [references/regua.md](references/regua.md). Um jeito de começar:

| Nota | Dinheiro esperado |
|---|---|
| 13 | o maior negócio que você fecha com alguma frequência, ou mais |
| 8 | metade disso |
| 5 | um quarto |
| 3 | um oitavo |
| 2 | pouco dinheiro, ou ganho indireto |
| 1 | nenhum dinheiro |

**Venda que só você pensou vale pouco.** Oportunidade criada sem pedido do cliente fica com valor, urgência e risco em até 3, até o cliente responder com interesse. A tabela de fases da venda, com a chance máxima de cada uma, está na régua.

## Como rodar

O script fica em `scripts/fila.py` e só precisa do `gh` autenticado. `DONO/REPO` é a torre de controle.

```bash
# uma vez por repositório: cria as etiquetas da régua
python3 scripts/fila.py rotulos DONO/REPO

# para cada issue: o Claude lê, dá as quatro notas e grava
python3 scripts/fila.py nota DONO/REPO NUMERO VALOR URGENCIA RISCO TAMANHO

# a fila em ordem, só o que está na fila
python3 scripts/fila.py fila DONO/REPO

# a fila com os assuntos agendados, delegados e aguardando junto
python3 scripts/fila.py fila DONO/REPO --todas
```

Qualquer comando de gravação aceita `--simular`, que mostra o que faria sem mudar nada.

### O passo do Claude

1. Listar as issues abertas: `gh issue list --repo DONO/REPO --state open --limit 500`.
2. Para cada uma, ler corpo e comentários (`gh issue view NUMERO --repo DONO/REPO --comments`).
3. Dar as quatro notas pela régua, cada uma com a frase da fonte.
4. Gravar com `fila.py nota` e comentar na issue as quatro frases, curtas, numa linha cada.
5. Rodar `fila.py fila` e mostrar ao usuário os cinco primeiros, com a nota e a frase do valor.

Com muitas issues (mais de 40), dividir em lotes e passar cada lote a um subagente, todos com o mesmo texto de instrução e a mesma régua. Depois comparar as medianas de cada lote: lote que destoa muito volta para revisão.

## Calibrar com o usuário

Se os cinco primeiros não batem com o que o usuário faria, a régua ainda não tem o critério dele. Pergunte por quê, em caixinha, e grave a resposta como regra nova em [references/regua.md](references/regua.md). A régua melhora a cada correção.
