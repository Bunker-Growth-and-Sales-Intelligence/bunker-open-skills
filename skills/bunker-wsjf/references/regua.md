# A régua das notas

Tudo o que o Claude precisa para dar as quatro notas de uma issue. Ajuste as âncoras ao seu negócio e acrescente aqui cada correção do usuário.

## Valor (`bv`): quanto o negócio ganha com isso pronto

| Nota | Âncora | Exemplo |
|---|---|---|
| 1 | cosmético | ajuste que ninguém pediu e ninguém nota |
| 2 | interno pequeno | facilita a vida de uma pessoa da casa, de vez em quando |
| 3 | produtividade | poupa horas que se repetem toda semana |
| 5 | o cliente percebe | o cliente vê a melhora, ou a falta dela, no dia a dia |
| 8 | receita ou obrigação legal | contrato, cobrança, venda em curso, nota fiscal, dado pessoal |
| 13 | estratégico | define a renovação ou a perda de um cliente grande, ou abre uma linha de receita |

Quando houver dinheiro envolvido, use a escala em dinheiro da skill e cite o número na frase.

## Urgência (`tc`): quanto custa esperar

| Nota | Âncora |
|---|---|
| 1 | tanto faz daqui a seis meses |
| 2 | perde pouco com o tempo |
| 3 | prazo em meses |
| 5 | prazo em semanas, ou o cliente já cobrou |
| 8 | prazo nesta semana, ou está travando alguém agora |
| 13 | algo parado ou um cliente perdido se não sair hoje |

Prazo de resposta estourado (alguém esperando além do combinado) sobe a urgência. Nunca sobe o valor.

## Risco (`rr`): quanto problema isso evita

| Nota | Âncora |
|---|---|
| 1 | sem efeito |
| 2 | arrumação isolada |
| 3 | risco pequeno, conhecido |
| 5 | reduz um risco que já apareceu |
| 8 | segurança, dado ou dinheiro em jogo |
| 13 | processo, multa ou perda grande se não fizer |

## Tamanho (`sp`): quanto falta para terminar

| Nota | Âncora |
|---|---|
| 1 | menos de 30 minutos |
| 2 | 1 a 2 horas |
| 3 | meio dia |
| 5 | um dia |
| 8 | dois a três dias |
| 13 | grande demais: precisa ser quebrado em issues menores |

## Casos que mais confundem

| Caso | Como pontuar |
|---|---|
| Trabalho feito, falta só conferir ou fechar | valor 2 ou 3, urgência pelo prazo de aceite (senão 1 ou 2), risco 3 ou 5, tamanho 1 |
| Falta uma decisão, e não trabalho | tamanho 1 ou 2 (o tamanho da decisão); valor é o que a decisão destrava |
| Prazo que venceu sem registro de entrega | urgência 3; 5 ou mais só se alguém cobrou depois do prazo |
| Issue repetida ou superada por outra | 1 em tudo, e a frase diz qual issue cobre o assunto; quem fecha é o usuário |
| Trabalho que não cabe em três dias | tamanho 13, sem baixar para caber |

## Fases da venda

Para issue de oportunidade. A fase só avança com sinal do cliente, e a frase cita onde está o sinal.

| Fase | Quando | Chance máxima |
|---|---|---|
| ideia | só o usuário pensou; ninguém foi procurado | 5% |
| oferta | o usuário ofereceu sem o cliente pedir | 10% |
| interesse | o cliente respondeu com interesse ou pediu mais | 30% |
| proposta | o cliente pediu proposta ou preço | 50% |
| negociação | o cliente discute preço, escopo ou prazo | 70% |
| compromisso | o cliente disse sim, falta assinar ou pagar | 90% |
| fechado | assinado ou pago | 100% |

Em ideia e oferta, valor, urgência e risco ficam em 3 no máximo. Silêncio do cliente não sobe fase.

## Correções do usuário

Cada vez que o usuário discordar da ordem, escreva aqui a regra nova, com a data e as palavras dele.
