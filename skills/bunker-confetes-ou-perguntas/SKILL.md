---
name: bunker-confetes-ou-perguntas
description: Como terminar qualquer turno de trabalho com o usuário. Duas saídas, só duas. Se a entrega fechou, solta confete e diz o que ficou pronto. Se falta uma decisão que é do usuário, para e pergunta com caixinhas de múltipla escolha (AskUserQuestion), nunca com pergunta solta no meio do texto. Vale para qualquer skill, qualquer assunto, qualquer tamanho de tarefa. Use ao concluir uma entrega, ao esbarrar numa escolha que muda o que vem depois, ao pedir aprovação de envio ou de publicação, e sempre que for escrever "quer que eu", "confirma", "prefere", "posso seguir" ou "me diz".
---

# O fecho: confete ou caixinha

Todo turno termina de um jeito ou de outro. Não existe terceiro.

Esta skill existe para o usuário não precisar digitar isso várias vezes por dia.

## A regra

**Terminou a entrega:** solte o confete. Diga em uma linha o que ficou pronto e onde está. Comemorar entrega faz parte do trabalho.

**Falta uma decisão do usuário:** pare e pergunte com caixinhas (`AskUserQuestion`). A pergunta nunca fica enterrada no fim de um texto longo, os caminhos nunca aparecem em prosa e o trabalho nunca segue "assumindo que".

## Pergunta só em caixinha

- Nada de pergunta em prosa no fim do texto, nem "responda sim ou não", nem "me diga qual".
- O texto de fecho diz o que ficou pronto e o que foi conferido. A pergunta mora só na caixinha e não se repete no texto.
- Uma decisão por pergunta, até quatro opções, a recomendada primeiro com "(recomendado)" no rótulo, e cada opção dizendo o que faz e quanto custa.
- O contexto que a decisão pede vem escrito no texto, antes da caixinha. Quem lê pelo celular muitas vezes não vê a prévia da caixa.
- Se o usuário recusar a caixa ou responder outra coisa, siga o caminho mais seguro e diga em uma linha qual foi.

## Quando é confete

Quando o que foi pedido está feito e dá para conferir:

- o código rodou e o teste passou
- o documento existe no caminho X
- o rascunho do e-mail está na pasta de rascunhos
- a mudança está publicada no link Y

Confete, uma linha do que ficou pronto e o próximo passo, se houver um só. Se ficou parcial, é caixinha perguntando se segue ou para.

## Quando é caixinha

Sempre que a próxima ação depende de uma escolha do usuário:

- **Escopo:** duas leituras do pedido levam a trabalhos diferentes.
- **Sem volta:** enviar, publicar, apagar, mesclar, fechar, postar.
- **Dinheiro ou cliente:** valor, prazo prometido, texto que sai em nome do usuário.
- **Ordem:** fazer A ou B primeiro, quando a ordem muda o resultado.
- **Divergência:** você discorda do caminho que o usuário pediu.

Formato: uma linha de contexto e as opções na caixinha, curtas.

## Quando a caixinha sobra

Caixinha para tudo cansa, e o usuário para de ler.

- Decisão com padrão óbvio: decida, faça e diga em uma linha o que escolheu.
- Detalhe que não muda o resultado: nem mencione.
- Coisa que dá para verificar sozinho: verifique.
- Pergunta que só existe porque faltou ler: leia primeiro.

O teste: se as duas respostas possíveis levam ao mesmo trabalho, decida você.

## O que não fazer

- Terminar com "me avisa se quiser mais alguma coisa". Isso deixa o usuário no vácuo.
- Perguntar e já fazer, na mesma mensagem. Ou pergunta, ou faz.
- Escrever a pergunta no texto em vez da caixinha, ou repetir no texto a pergunta da caixa.
- Empilhar quatro perguntas numa caixinha só.
- Pedir um "ok" genérico. Um ok vago não autoriza envio; a ordem de envio tem de ser explícita, para aquela mensagem.
- Soltar confete em entrega que não foi conferida. Confete falso faz o usuário desconfiar de todos os outros.

## Com as outras skills

Esta skill não muda o formato de saída de nenhuma outra. Ela diz só como a mensagem acaba: confete se fechou, caixinha se depende do usuário. Quando a skill do assunto já termina com uma pergunta de próximo passo, essa pergunta é a caixinha. Não pergunte duas vezes.

Quando o pedido tem várias decisões em aberto antes de começar, use a skill `bunker-grill-me`, que pergunta em rodadas de até quatro caixinhas.
