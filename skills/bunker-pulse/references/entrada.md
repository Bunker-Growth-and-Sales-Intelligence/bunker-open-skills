# Como ler cada tipo de lista

A pessoa manda o que tiver. Aqui está onde cada campo costuma morar, e como traduzir.

## Print de tela

Leia a imagem inteira antes de escrever qualquer coisa. Em quadro de colunas (Trello,
Jira, Planner, GitHub Projects), **a coluna é o status**: "A fazer" é `aberta`, "Fazendo"
é `andamento`, "Feito" é `concluida`. Etiqueta colorida costuma ser a frente. Avatar é o
responsável: pergunte o nome se só aparecer a inicial.

Print cortado é lista incompleta. Pergunte se há mais colunas ou mais linhas fora da
imagem antes de fechar a conta.

## Planilha (xlsx, csv, Google Sheets)

Procure a aba que tem uma linha por atividade. Colunas comuns:

| Campo | Nomes que aparecem |
|---|---|
| título | Tarefa, Atividade, Item, Entrega, Nome, Title, Summary |
| frente | Bloco, Fase, Etapa, Frente, Épico, Módulo, Área, Workstream |
| status | Status, Situação, Andamento, Estado |
| responsável | Responsável, Dono, Owner, Assignee, Atribuído a |
| prazo | Conclusão, Prazo, Término, Fim, Data limite, Due date |
| criada | Criado em, Data de abertura, Created |
| concluída | Concluído em, Data de entrega, Closed, Resolved |

Linha de título de bloco (sem data, sem status) é o nome da frente das linhas de baixo,
e não uma atividade. Linha de total não é atividade.

## GitHub

Com o `gh` instalado:

```bash
gh issue list --repo dono/repositorio --state all --limit 1000 \
  --json number,title,state,stateReason,labels,milestone,assignees,createdAt,closedAt,url
```

`state` CLOSED é `concluida` (ou `cancelada` quando o `stateReason` é "not planned");
OPEN é `aberta`, a não ser que uma etiqueta diga andamento ou bloqueio. A frente sai do
`milestone` ou da etiqueta de área. `createdAt` e `closedAt` ligam os slides de entrada
e saída e de ritmo. Issue não tem prazo: use a data do milestone quando houver.

## Jira, Asana, Monday, ClickUp, Notion, Planner, Lista do SharePoint

Todos exportam para CSV ou Excel. Leia como planilha. No Jira, a frente costuma ser
`Epic Link` ou `Component`; no Asana, `Section/Column`; no Planner, `Bucket`; numa Lista
do SharePoint, a coluna de agrupamento que a pessoa usa na visão. "Resolution: Won't Do"
é `cancelada`.

## Texto colado, ata, e-mail

Uma linha por atividade. O que tiver data vira prazo. Verbo no passado ("enviamos a
proposta") é `concluida`; "vamos", "falta", "pendente" é `aberta`. Na dúvida, pergunte.

## Tradução de status

| Na fonte | Canônico |
|---|---|
| Concluído, Feito, Done, Closed, Entregue, Resolvido, Pronto | `concluida` |
| Em andamento, Fazendo, Doing, In progress, Em revisão, Em teste, Homologação | `andamento` |
| A fazer, To do, Backlog, Pendente, Aberto, Novo, Planejado, Não iniciado | `aberta` |
| Bloqueado, Impedido, Aguardando, Esperando cliente, On hold, Pausado | `bloqueada` |
| Cancelado, Descartado, Fora de escopo, Won't do | `cancelada` |

Status que carrega juízo em vez de situação (**"Atrasado?", "Vencido", "Em risco",
"Início hoje"**) não diz se a atividade começou. Proponha a tradução e deixe a pessoa
decidir no passo de conferência. O atraso o script calcula pelo prazo, então "Vencido"
quase sempre vira `aberta` com prazo passado.

Status que contradiz a evidência ("marcado concluído", mas a entrega não existe): mantenha
o que a fonte diz e avise a pessoa. O relatório reflete a lista; corrigir a lista é
decisão dela.

## Frente

Sem nenhuma coluna de agrupamento, proponha até oito frentes lendo os títulos, mostre a
proposta e espere o sim. Nunca passe de oito: acima disso o gráfico vira lista telefônica.
Frentes parecidas se juntam.

## Duas fontes ao mesmo tempo

A mesma atividade aparece no quadro e na planilha? Fica uma só, com o campo mais completo
de cada lado. Duplicar infla o total e o percentual mente.
