# Os slides, e como escrever cada manchete

Todo slide tem dois textos, e só dois:

- **a pergunta**, no cabeçalho: a de quem decide, sobre o negócio, nunca sobre o desenho;
- **a manchete**, como título: a resposta, com o número, que se sustenta sozinha.

Embaixo do desenho vai uma linha só, a fonte: de onde veio o dado, que recorte e quando
foi medido. Parágrafo explicativo não entra.

## As regras do desenho

O motor já segue todas; elas estão aqui para você não pedir o contrário.

- **Eixo começa no zero.** A altura é proporcional ao dado.
- **Uma cor para o que a manchete nomeia.** O resto fica em cinza claro.
- **A cor julga.** A primária é o que vai bem; a secundária é o alerta.
- **Nome na ponta da barra**, sem legenda de canto.
- **No máximo oito categorias.** Acima disso, as sete maiores e "Outras (N)".
- **Empate divide o destaque.** Duas frentes com 4 atrasos cada ganham a mesma cor.
- **Nenhum dado some calado.** O que fica fora do desenho vai escrito na nota.

## Slide por slide

| Chave | Pergunta | A manchete diz | Forma |
|---|---|---|---|
| `numeros` | Como está o projeto, em quatro números? | o percentual concluído, com o denominador, e quantas estão atrasadas | quatro cartões |
| `cascata` | Estamos dando conta do trabalho que chega? | quanto entrou, quanto saiu e para onde foi o que falta, em 8 semanas | cascata de entrada e saída |
| `frentes` | Quais frentes já estão concluídas? | as frentes concluídas pelo nome, e a próxima a fechar | barra de progresso por frente |
| `situacao` | O que falta já está sendo feito? | quanto do que falta não começou, anda ou está bloqueado | barras ordenadas |
| `atrasos` | Onde estão os atrasos? | a frente que concentra os atrasos, ou as que dividem | barras ordenadas, na cor de alerta |
| `dias` | Os atrasos são de dias ou de semanas? | o atraso típico (mediana) e o pior, pelo nome | um ponto por atividade, com mediana e P90 |
| `responsaveis` | O trabalho que falta está bem distribuído? | quem carrega mais, ou quanto está sem dono | barras ordenadas |
| `ritmo` | O ritmo de entrega está aumentando? | as últimas 4 semanas contra as 4 anteriores | colunas por semana |
| `tempo` | Alguma frente está demorando demais para concluir? | a frente de maior mediana até concluir, contra o resto | quartis por frente |
| `esforco` ou `onde_falta` | Qual frente vai exigir mais esforço? | a frente com mais pontos (ou atividades) em aberto | barras ordenadas |
| `acumulo` | Em que frente e em que situação o que falta se acumula? | a célula maior do cruzamento | mapa de calor |
| `idade` | Tem atividade envelhecendo em alguma frente? | a frente com atividades abertas há mais tempo | quartis por frente |
| `dependencias` | Alguma atividade está segurando as outras? | a atividade que mais segura as outras | barras ordenadas, na cor de alerta |
| `urgentes` | Há atividades urgentes em aberto? | quantas são P0 e P1 (ou alta) | barras, urgentes na cor de alerta |
| `wsjf` | Por qual frente devemos começar? | a frente de maior WSJF, com nota "O que é WSJF" | barras ordenadas |
| `agora` | Tem alguma coisa que não pode esperar? | quantas têm muito valor e muita urgência | matriz de quadrantes |
| `rapido` | Tem ganho rápido disponível agora? | quantas têm WSJF alto e esforço baixo | matriz de quadrantes |
| `estrategica` | Tem algo que entrega valor e tira risco junto? | quantas têm valor alto e risco alto | matriz de quadrantes |
| tabela | O que continua em aberto | na ordem de ataque: WSJF, prioridade, atraso, prazo; com o porquê e o que cada uma espera | tabela |

## O WSJF

WSJF é o custo do atraso dividido pelo esforço. O custo do atraso é a soma de três notas:
valor para o negócio, urgência e redução de risco. O WSJF de uma frente é a soma dos custos
sobre a soma dos esforços, e não a média dos WSJF de cada atividade: a média daria o mesmo
peso a uma atividade de 1 ponto e a uma de 13. Nos quadrantes, o corte é a mediana de cada
eixo.

## As notas adesivas

São três, e cada uma aparece onde ajuda:

- **Como ler este gráfico**: na primeira vez que uma forma aparece (quartis, quadrantes).
- **O que é WSJF**: no slide do WSJF.
- **Contexto**: o porquê que a pessoa contou, pelo campo `notas` do registro. É onde vai
  "isso espera aquilo, decidido na reunião de tal dia".

## Versão curta

`--sem-plano` tira os slides de prioridade e ordena a tabela por prazo. Serve para quem
quer só o panorama.

## Quando reescrever a manchete

A manchete automática tem sempre o número certo e a estrutura certa. Reescreva, pelo
campo `manchetes` do registro, quando:

- o contexto que a pessoa contou explica o número ("Integração ainda não começou por
  decisão: ela depende do desenho técnico, previsto para maio");
- o nome da frente pede artigo ou ajuste ("O CRM concentra..." em vez de "CRM concentra...");
- a pessoa quer destacar outra leitura do mesmo gráfico.

Três testes antes de trocar:

1. O número da frase é o mesmo do desenho?
2. A frase se entende sem ler a pergunta?
3. A frase afirma só o que o desenho mostra? Causa que o dado não mostra vai para a
   conversa com a pessoa, não para o slide.

## Concordância

"Atividade" é feminino: "3 das 9 atividades atrasadas", "todas as 25". Com uma só, o
verbo vai para o singular: "1 atividade está bloqueada".
