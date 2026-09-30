---
name: bunker-pulse
description: Transforma uma lista de atividades de projeto em status report em slides, com a cara da Bunker e a cor de quem vai receber. A lista chega do jeito que a pessoa tiver, numa conversa - print de tela, planilha, CSV, export do GitHub, Jira, Trello, Asana, Planner, lista do SharePoint, texto colado - e a IA normaliza, confirma o que ficou em dúvida e entrega um PDF de slides 16:9, um gráfico por página, com a pergunta de negócio no cabeçalho e a resposta como título. Use quando pedirem "status report", "relatório do projeto", "como está o projeto", "o que está atrasado", "pulso do projeto", "relatório para o cliente", "slides do andamento", ou quando a pessoa mandar uma lista de tarefas e quiser mostrar para alguém onde o trabalho está.
---

# Pulso do projeto

Um status report que se lê em cinco segundos por slide. Quem recebe é dono, diretor ou
cliente, e decide olhando: cada slide faz uma pergunta que ele faria ("Onde estão os
atrasos?") e responde no título, com o número ("Desenho de Negócio concentra 4 das 9
atividades atrasadas.").

A skill não depende de sistema nenhum. A pessoa manda a lista do jeito que tiver, você
transforma no registro de `references/formato.md`, e o `scripts/relatorio.py` calcula
tudo e monta os slides. Número nenhum é digitado à mão.

## A conversa, em cinco passos

### 1. Receber a lista

Peça a lista do jeito que for mais fácil para a pessoa. Não peça formato. Serve:

- print de tela (quadro do Trello, board do Jira, lista do Planner, planilha aberta);
- arquivo `.xlsx`, `.csv`, `.json`, export de qualquer ferramenta;
- link ou export do GitHub (issues), ou a saída de `gh issue list`;
- texto colado no chat, ata de reunião, e-mail com a lista de pendências.

Pode vir mais de uma fonte. Junte tudo numa lista só, sem duplicar a mesma atividade.

### 2. Ler e normalizar

Leia cada fonte seguindo `references/entrada.md`, que diz onde procurar cada campo em cada
tipo de fonte e como traduzir o status. O que importa por atividade: título, frente,
status, responsável, prazo, e as datas de criação e de conclusão quando existirem.

Três regras que mudam o relatório:

- **Nada é inventado.** Campo sem sinal fica vazio. Responsável vazio vira "sem
  responsável" no gráfico, e isso é informação: é a primeira coisa que um diretor quer
  saber.
- **Status ambíguo é pergunta, não palpite.** "Atrasado?", "Em risco", "Início hoje",
  "Marcado concluído mas sem evidência": leve para a pessoa decidir no passo 3.
- **Data sem ano** ("16/mar") ganha o ano da data de referência, e isso vai na conferência.

### 3. Conferir com a pessoa, numa mensagem só

Mostre um resumo curto do que você entendeu e pergunte só o que falta. Uma mensagem, não
uma entrevista. Use as caixinhas de pergunta da ferramenta quando houver.

- quantas atividades, em quantas frentes, e a data de referência ("medido em");
- como cada status original foi traduzido (tabela de duas colunas), com as dúvidas;
- nome do cliente e do projeto, para a capa;
- **as cores** (passo 4);
- nomes curtos para as frentes com mais de 17 caracteres, que é o que cabe no gráfico
  ("Construção Sales Cloud" vira "Construção"; o título do slide usa o nome inteiro).

### 4. As cores

A moldura é sempre a da Bunker: preto, branco, cinzas claros, fonte Schibsted Grotesk,
logo. A cor viva dentro do gráfico é a de quem vai receber o relatório, e são duas:

| Cor | Onde aparece |
|---|---|
| primária | o que vai bem e o destaque que a manchete nomeia |
| secundária | o alerta: atraso, bloqueio, trabalho sem dono |

**Sempre pergunte as cores**, antes de gerar: "Quais são a cor principal e a de destaque
da sua empresa (ou do seu cliente)?" Aceite hexadecimal, nome ("o azul do logo"), print do
site ou o logo; tire a cor do material, nunca de memória. Se a pessoa só tiver uma cor,
ela é a primária.

**Sem resposta ou sem preferência, vale a paleta do portal Bunker Alumni**, que é leve e
deixa o dado em destaque:

| Papel | Cor |
|---|---|
| primária, o destaque | azul `#3b82f6` |
| secundária, o alerta | rosa `#f43f5e` |
| contexto | os cinzas claros da Bunker |

Nunca reaproveite a cor de outro cliente, nem a de um relatório anterior, como padrão.

### 5. Gerar, revisar as manchetes e entregar

```bash
python3 scripts/relatorio.py atividades.json --resumo          # perguntas e manchetes
python3 scripts/relatorio.py atividades.json --saida relatorio.html --pdf
```

O `--resumo` imprime a pergunta e a manchete de cada slide e diz quais ficaram de fora e
por quê. **Leia as manchetes antes de entregar.** O script escreve a conclusão com os
números certos; você melhora a frase quando o contexto pede (nome do projeto, um fato
que a pessoa contou), pelo campo `manchetes` do registro, sem mudar número nenhum.

Entregue o HTML (no Claude, ele abre como artefato, com o botão "Salvar em PDF") e o PDF
quando o `--pdf` funcionar. Sem Google Chrome na máquina, o botão do HTML resolve: na
janela de impressão, destino "Salvar como PDF" e margens "Nenhuma".

Depois de entregar, pergunte se alguma manchete ou nome de frente precisa mudar. Mudança
de texto é no registro, e o relatório sai de novo em segundos.

## Os slides

Cada um só entra quando o dado sustenta. Lista sem prazo não tem slide de atraso; lista
sem data de conclusão não tem ritmo de entrega. O detalhe de cada um, e como escrever a
manchete, está em `references/graficos.md`.

| Pergunta do slide | Precisa de |
|---|---|
| Como está o projeto, em quatro números? | status |
| Estamos dando conta do trabalho que chega? | criação e conclusão da maior parte |
| Quais frentes já estão concluídas? | duas frentes ou mais |
| O que falta já está sendo feito? | status |
| Onde estão os atrasos? | prazo e frente |
| Os atrasos são de dias ou de semanas? | cinco atrasadas ou mais |
| O trabalho que falta está bem distribuído? | responsável em parte da lista |
| O ritmo de entrega está aumentando? | três conclusões com data |
| O que continua em aberto (tabela) | sempre que falta algo |

## O que o relatório não faz

- **Não promete data.** Mostra onde o trabalho está; prazo novo é conversa de quem toca
  o projeto.
- **Não julga pessoa.** "Sem responsável" é um fato da lista, não uma acusação.
- **Não mostra dado que você não conferiu.** Abra o HTML e confira dois ou três números
  contra a lista original antes de entregar.

## Tom

Pergunta e manchete em frase direta, com o número, sem gíria. "Há itens urgentes em
aberto?" e não "Sobrou coisa urgente?". A manchete se sustenta sozinha: "Sim: 8 de 21" não
diz sim para quê.

## Precisa de

Python 3.9 ou mais novo, sem biblioteca extra. Para o PDF automático, o Google Chrome;
para decks com mais de 10 slides em PDF automático, também o `pdfunite` (pacote poppler).
Sem eles, o botão "Salvar em PDF" do HTML faz o mesmo.
