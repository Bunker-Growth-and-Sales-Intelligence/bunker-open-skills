# Estados e follow-up

## Estados

| Estado | Quando | Disputa a fila? | Volta |
|---|---|---|---|
| `fila` | a bola está com o usuário e não há horário reservado | sim | já está |
| `agendado` | há bloco na agenda ou reunião marcada para o assunto | não | no dia do bloco; se o bloco passar com o assunto aberto, volta com a urgência um degrau acima |
| `delegado` | outra pessoa executa, a pedido do usuário | não | no dia de cada follow-up |
| `aguardando` | a decisão é de alguém de fora (cliente, banco, fornecedor) | não | no dia de cada follow-up |
| `algum dia` | estacionado de propósito | não | na revisão do mês |

Sugestão de horário não muda o estado. Só horário reservado de verdade.

## Como a ignição percebe sozinha

- **Delegado:** mensagem do usuário pedindo que alguém execute ("fica com você", "consegue fazer?"). Anotar com quem e desde quando.
- **Aguardando:** proposta, pergunta ou pedido de decisão enviado a alguém de fora. Se a pessoa prometeu uma data, anotar a data.
- **Agendado:** evento na agenda sobre o assunto.
- **Volta para a fila:** a pessoa respondeu, entregou ou pediu algo ao usuário.

Toda mudança de estado gera um comentário na issue, com a evidência.

## Cadência de follow-up

- Primeiro follow-up 2 dias úteis depois de delegar ou enviar; o segundo, 3 dias úteis depois do primeiro; o terceiro, 5 dias úteis depois do segundo; daí em diante, um por semana. A partir do terceiro sem resposta, sugerir escalar.
- Se a pessoa prometeu uma data, o follow-up é o dia útil seguinte a ela.
- Com prazo duro, sempre existe um follow-up na véspera útil do prazo.
- Todo follow-up leva algo concreto: o que mudou desde a última conversa e um pedido fácil de responder. "Conseguiu olhar?" não serve.

## Nota da vez

- Na fila: as quatro notas normais.
- Delegado ou aguardando, no dia do follow-up: o mesmo valor, urgência 8 e tamanho 1, para o follow-up sair logo. Cada follow-up sem resposta sobe o risco um degrau.
- Fora disso, o assunto espera.

## Etiquetas

Cada família responde a uma pergunta. No máximo uma etiqueta por família, menos `sinal:`.

| Família | Pergunta | Valores |
|---|---|---|
| `tipo:` | O que é? | `oportunidade`, `entrega`, `dinheiro`, `jurídico`, `rede` |
| `frente:` | Que linha do negócio alimenta? | as frentes do usuário |
| `estado:` | Com quem está a bola? | sem etiqueta é fila; `agendado`, `delegado`, `aguardando`, `algum dia` |
| `sinal:` | O que pede atenção? | `vácuo` (alguém esperando além do prazo), `escalar` (três follow-ups sem resposta) |

As notas do WSJF usam as etiquetas da skill `bunker-wsjf` (`bv-`, `tc-`, `rr-`, `sp-` e `P0` a `P3`).
