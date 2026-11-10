---
name: bunker-grill-me
description: Afina um pedido, um plano ou um briefing antes de começar o trabalho, com perguntas em rodadas. Monta a árvore de decisões do pedido, pergunta numa rodada só tudo o que já dá para perguntar (até quatro caixinhas de múltipla escolha, cada uma com a resposta recomendada primeiro), espera as respostas e abre a rodada seguinte. O que dá para descobrir sozinho a skill descobre; decisão fica com o usuário. O trabalho só começa quando não sobra nada assumido em silêncio. Versão com caixinhas da grill-me de Matt Pocock. Use quando o usuário disser "grill me", "me faz perguntas", "me entrevista", "afina o briefing", "antes de começar, pergunta", ou quando o pedido tiver mais de uma leitura possível.
---

# Grill me: perguntas em rodadas antes de começar

Um pedido mal entendido custa mais tempo do que as perguntas que teriam evitado o engano. Esta skill entrevista o usuário até os dois terem o mesmo entendimento do que vai ser feito, e só então o trabalho começa.

É a versão em caixinhas da [grill-me de Matt Pocock](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling) (licença MIT). A árvore de decisões e as rodadas vêm de lá; a forma de perguntar segue a skill `bunker-confetes-ou-perguntas`.

## A árvore de decisões

Cada decisão do pedido puxa outras que dependem dela. O público de uma apresentação define o tom, e o tom define que exemplos entram. Antes de perguntar, desenhe essa árvore para você.

A **fronteira** são as decisões que já dá para perguntar agora, porque tudo de que elas dependem está resolvido. Pergunta cuja resposta depende de outra ainda aberta fica para a rodada seguinte.

## Uma rodada

1. **Contexto antes.** No texto, antes das caixinhas, escreva em poucas linhas o que você já entendeu do pedido e o que descobriu sozinho. Quem lê pelo celular muitas vezes não vê a prévia da caixa.
2. **Até quatro perguntas por rodada**, todas da fronteira, numa chamada só de `AskUserQuestion`. Cada pergunta é uma decisão, com até quatro opções, a recomendada primeiro com "(recomendado)" no rótulo e uma linha dizendo o que cada opção faz.
3. **Fronteira com mais de quatro decisões:** pergunte primeiro as que destravam mais coisas e deixe o resto para a rodada seguinte.
4. **Espere as respostas.** Elas mudam a árvore: cada decisão resolvida libera as que dependiam dela. Recalcule a fronteira e abra a próxima rodada.

## O que perguntar e o que descobrir

- Fato que dá para descobrir lendo um arquivo ou o sistema, você descobre antes de perguntar. Se a busca for demorada, mande um subagente e pergunte enquanto isso o que não depende dela.
- Ao usuário vão só as decisões, que são dele.
- Pergunta com resposta óbvia fica de fora: decida e diga em uma linha, no contexto da rodada, o que decidiu.

## Quando acaba

A entrevista acaba quando a fronteira fica vazia: todo galho da árvore visitado e nada assumido em silêncio. Feche com um resumo curto do combinado, em tópicos, e uma última caixinha perguntando se o entendimento está certo e se pode começar. O trabalho só começa com o sim.

Se o usuário disser no meio que já basta, pare, resuma o combinado e diga em uma linha o que vai assumir em cada ponto ainda aberto.

## Onde ela entra

- Antes de qualquer trabalho com mais de uma leitura possível: documento, proposta, apresentação, automação, aula.
- Na conversa filha que a skill `bunker-ignicao` abriu, quando a issue não diz o bastante para começar.
