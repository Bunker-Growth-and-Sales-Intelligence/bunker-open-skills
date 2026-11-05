---
name: bunker-fix-bug
description: "O rito da Bunker para consertar defeito em Salesforce, do alvo ao deploy, na ordem que impede engano. Abre com perguntas de arquitetura e de regra de negócio, elege o defeito por contagem, mede a premissa antes de escrever uma linha, reproduz o defeito num teste que fica vermelho hoje, ataca o próprio teste, corrige e prova o par vermelho e verde, tira print do antes e do depois na mesma cena, faz deploy com cobertura por classe e roda tudo de novo. A issue do GitHub é o diário, e cada marco vira comentário na hora, o WSJF decide a fila e a esteira e0 a e6 diz onde cada issue está. Use ao consertar bug, escrever teste de regressão, decidir qual bug atacar primeiro, ou quando alguém disser \"escreve o teste\", \"prova o erro\", \"qual bug atacar\", \"isso melhorou mesmo?\", \"reproduz o erro\"."
---

# Consertar defeito: o rito

A ordem não é decorativa. Trocar dois passos de lugar já custou correção que
piorou o produto e teste que passava sem provar nada.

## Três vertentes, e a primeira manda

**1. O rito de consertar, que é o foco.** Eleger por contagem, medir a premissa,
reproduzir em teste vermelho, atacar o próprio teste, corrigir, provar o par,
capturar o antes e o depois, deployar com cobertura e rodar tudo de novo. É isto
que a skill é. O resto existe porque sem ele este rito não se enxerga de fora.

**2. Reconstruir a estrutura de épicos e de issues, mesmo sem pedido.** Se a fila
não está organizada do jeito que o relatório da casa precisa, organizar faz parte
do trabalho, e não é tarefa separada para outro dia. **Grava de verdade, no
GitHub.** O critério é um só: no fim, a fila precisa contar a verdade do projeto
para quem olha de fora. O procedimento está na seção "Normalizar a fila", abaixo.

**3. Gerar a visão do repositório para o cliente, quando o operador quiser.** A
skill NÃO gera material sozinha e NÃO faz as três coisas de uma vez. Ela pergunta
se é para gerar, e só então chama a skill `bunker-pulse`, deste mesmo repositório.

### Varredura total, quando o operador liga

O operador diz qual org, qual SharePoint, quais caixas de e-mail e quais projetos
entram no contexto. Com isso a skill liga a varredura total e reconstrói a fila a
partir do que existe fora do repositório, porque metade da entrega de uma operação
Salesforce nunca passou por commit.

| Sistema | Como se chega | O que se busca lá |
|---|---|---|
| GitHub | `gh` autenticado | issues, PRs, commits e a fila |
| org Salesforce | `sf` com o alias que o operador indicar | o metadado e o dado real do defeito, só leitura |
| e-mail e Teams | `m365`, na caixa de quem roda | quem reportou, quando, e o que já foi combinado |
| SharePoint | `m365`, busca por termo do projeto | especificação, ata e requisito por trás do defeito |

Quando faltar acesso, pedir ao operador que conecte, dizer qual comando resolve, e
seguir com o que existe. **Fonte que faltou é declarada, nunca omitida.**

## A ordem

0. **Abrir pelas perguntas: abordagem de arquitetura e regras de negócio, com o operador**
1. Eleger o defeito, por contagem e não por rótulo
2. Medir a premissa da correção, antes de escrever uma linha
3. **Reproduzir o defeito num teste, e vê-lo vermelho no código de hoje**
4. Atacar o próprio teste
5. Corrigir, e ver verde
6. Desfazer, e ver vermelho de novo
7. **Capturar o antes e o depois, e subir o par para a issue**
8. Deployar, com cobertura por classe
9. Rodar tudo de novo, e reeleger

O passo 0 responde "qual caminho, e com que regra de negócio?". Os passos 1 e 2 respondem "vale a pena?". Os passos 3 a 6 respondem "está certo?".
O passo 7 responde "onde isso fica registrado para quem vier depois?". Os passos 8 e 9 respondem
"chegou, e o que vem agora?".

---

## A issue é o diário, e se escreve durante, não depois

**Todo defeito vira issue antes de virar correção**, e é nela que o rito aparece
enquanto acontece. O operador acompanha o andamento abrindo a issue, não
perguntando. Relatório único no fim não serve: quando ele chega, a decisão que
dependia dele já passou.

**Um comentário por marco, curto, no momento em que o marco acontece.** Cinco
momentos obrigatórios:

| Passo | O que o comentário traz |
|---|---|
| 2, premissa medida | o número medido, e a frase "se eu fizer X, então Y" que ele testa |
| 3, vermelho | a classe de teste, o id da execução e a mensagem da asserção PROVA |
| 5, verde | os dois números do par, vermelho e verde |
| 7, evidência | as duas imagens subidas para a própria issue, mesma cena |
| qualquer um, travou | onde travou e o que falta decidir, sem enfeite |

**Comentário de travamento não é derrota, é o mais útil dos cinco.** Issue parada
sem explicação custa mais que issue com defeito confessado, porque o operador
descobre tarde que o rito morreu no passo 2 esperando uma decisão de produto.

### A classificação, que é como a fila se forma

A issue nasce classificada, e a classificação é o que decide a ordem de ataque.
O padrão da casa é WSJF, três dimensões de valor divididas pelo tamanho:

| Eixo | Rótulos | O que mede |
|---|---|---|
| Valor de negócio | `bv-1` a `bv-13` | de cosmético a estratégico |
| Redução de risco | `rr-1` a `rr-13` | de sem efeito a fundação crítica |
| Urgência | `tc-1` a `tc-13` | de sem decaimento a produção quebrada |
| Tamanho | `SP-1` a `SP-13` | de trivial a épico que precisa quebrar |

Junto vão a prioridade (`P0` a `P3`), o tipo (`type-bug`, `type-feat`,
`type-refactor`, `type-docs`, `type-infra`) e o estado (`in-progress`, `on-hold`,
`discovered`). `cliente-facing` marca o que o cliente enxerga.

**O `in-progress` entra quando o rito começa e sai quando ele termina**, e é por
ele que o operador sabe, de fora, o que está vivo agora. Issue com `in-progress`
parada há um dia é sinal de rito morto, não de trabalho profundo.

### A esteira, e um rótulo de etapa por vez

A classificação diz a ordem. **A esteira diz onde a issue está no rito**, e ela é a
única coisa que responde, de fora e sem perguntar, "isso aqui está onde?".

| Etapa | O que significa | Passos do rito |
|---|---|---|
| `e0-nao-lida` | chegou e ninguém olhou | antes de tudo |
| `e0-triagem` | olhada e classificada, ainda não eleita | antes do 1 |
| `e1-medindo` | alvo eleito, premissa em medição | 1 e 2 |
| `e2-provado` | vermelho, correção e verde, fora do ambiente | 3 a 6 |
| `e3-aguardando-deploy` | correção pronta e ainda não implantada | entre 6 e 8 |
| `e4-no-ar` | implantado, ainda sem prova de tela | 8 |
| `e5-reteste` | em reteste ou conferência de fecho | 9 |
| `e6-validado` | provado em tela, pronta para fechar | fim |

Duas paradas, que não são etapas e andam junto com elas: `bloq-decisao`, quando o
rito para esperando decisão de negócio, e `bloq-ambiente`, quando para por
permissão, credencial ou terceiro.

**Uma issue tem exatamente um rótulo de etapa.** Duas etapas ao mesmo tempo é
backlog mentindo, e é o que faz a mesma issue voltar para a mesa do operador
parecendo nova.

**A etapa se move no mesmo minuto em que o marco acontece.** O rótulo é irmão do
comentário do passo: quem escreve o comentário do vermelho move para `e2-provado`
na mesma tacada. Rótulo que fica para depois nunca é corrigido.

**Rótulo de estado que precede a esteira sai de circulação.** `feito-nao-deployado`,
`deployado-nao-testado`, `estado-no-ar` e `reprovado-no-reteste` nasceram antes do
rito e dizem, pior, o que a esteira já diz: `feito-nao-deployado` virou a etapa
`e3-aguardando-deploy`, `deployado-nao-testado` e `estado-no-ar` são `e4-no-ar`, e
`reprovado-no-reteste` é voltar para `e1-medindo` com `tentativa-N`.
Manter os dois vocabulários vivos obriga quem lê a traduzir de cabeça, e é assim que
uma issue aparece em duas colunas de painel ao mesmo tempo.

Caso que criou a regra, 24/09/2026: o operador pediu o refactor com a frase "hoje
temos reprovado-no-teste, e isso precede nosso processo padrão conforme skill de
correção de bug, quero repadronizar todos os rótulos", e no mesmo dia perguntou
"as fases que a minha skill de fix bug coloca são as fases da issue hoje? não está
fácil ver quais são". As etapas existiam na prática e não estavam escritas aqui.

**A porta da triagem é do operador, e só dele.** Nenhuma issue sai de `e0-triagem`
por iniciativa de quem executa: ela sai quando ele libera, com palavra dele. Isso
não é burocracia, é o que impede o efeito que ele descreveu em 24/09/2026: "preciso
dar ok explícito, porque estou sentindo que estou andando em círculos". O círculo
nasce quando ele decide uma issue e o rótulo não acompanha a decisão, então ela
reaparece dias depois com cara de não triada, e ele lê a mesma coisa duas vezes.

### O painel do backlog, de tempos em tempos e sem ele pedir

A lista de issues não para de crescer, e ninguém governa uma fila que só se enxerga
abrindo o GitHub issue por issue. **De tempos em tempos, entregue um resumo visual
do backlog**, sem esperar o pedido: quantas abertas, quantas por etapa da esteira, o
que está bloqueado e por quê, e as mais graves pela classificação. Destaque separado
para **as que já foram atacadas alguma vez**, porque são elas que correm o risco de
morrer no meio do caminho e ninguém notar.

O painel não substitui o diário da issue: ele responde outra pergunta. A issue
responde "o que aconteceu com esta aqui"; o painel responde "onde está a fila e o
que eu escolho agora".

Caso que criou a regra, 23/09/2026: "a lista de issues não para de crescer, preciso
pegar as mais graves e as que já atuou... isso depois deve fazer parte da skill de
fix bug, de tempos em tempos mostra automaticamente".

**Antes de classificar, achar o requisito.** Defeito reportado por cliente tem
quase sempre uma linha de especificação por trás, e ela muda tudo: se o
comportamento cobrado nunca foi pedido, a issue não é defeito e sim pedido novo,
e isso se diz antes de escrever código. Se foi pedido e não entregamos, o
`bv` sobe. Caso que criou a regra, 22/09/2026: um cenário de QA cobrava trava de
edição, e a especificação funcional do próprio cliente trazia a trava em três
lugares, inclusive nos critérios gerais de aceite. Sem essa leitura, a issue teria
sido respondida como divergência de entendimento.

### Normalizar a fila, passo a passo

**1. Descobrir as frentes, quando elas não existem.** A IA lê os títulos da fila
inteira (`gh issue list --state all --limit 1000 --json number,title,labels,milestone`) e
propõe até oito épicos, cada um com uma linha dizendo o que entra e o que não entra.
"Etapa 3" e "Infra" não são épicos, são etiquetas sem significado para quem lê.

A proposta é revisada por quem toca o projeto antes de virar marco. O marco recebe **o
nome que o cliente usa**, e não o nome do módulo.

**2. Criar e arrumar no GitHub.** Marco novo se cria e se avisa. Marco com nome sem
significado se renomeia. Issue no marco errado se move.

```bash
gh api repos/<owner/repo>/milestones -f title='<a frente como o cliente a chama>'
gh api -X PATCH repos/<owner/repo>/milestones/<n> -f title='<nome corrigido>'
gh issue edit <n> -R <owner/repo> --milestone '<marco>'
```

**Renomear rótulo propaga para todas as issues de uma vez**, e por isso é a operação mais
barata da arrumação. Vale para corrigir vocabulário sem tocar issue por issue:

```bash
gh label edit <velho> -R <owner/repo> --name <novo> --description '<o que significa>'
```

**Apagar rótulo é irreversível e espera decisão do operador.** Rótulo morto, com zero uso,
fica listado e não some sozinho.

**3. Classificar o que ficou sem frente.** O que o rótulo e o marco não cobriram, a leitura
de IA cobre, escolhendo DENTRO da lista fechada e guardando a evidência da escolha: a
frase do título ou do corpo que sustenta a frente escolhida.

**4. Retroalimentar o que foi entregue e nunca virou issue.** Frente inteira concluída
aparece em 0% quando ninguém registrou, e o cliente lê isso como projeto parado.

A fonte é o histórico do git (`git log --since=<AAAA-MM-DD>`) e o que a org mostra que
mudou. Cada entrega vira uma issue já fechada (`gh issue create` seguido de
`gh issue close`), com `Aberta originalmente em DD/MM/AAAA` no corpo. Quem monta o
relatório lê essa linha e joga a entrega no dia em que ela aconteceu, e não no dia em que
a issue foi criada. Sem esse passo, trinta e oito entregas de setembro caem todas em
hoje e o gráfico de ritmo mente.

**5. Conferir o teto.** Oito frentes por repositório. Acima disso o gráfico vira lista
telefônica, e a resposta é juntar frente, não alargar o desenho.

**Ao vivo, enquanto a operação roda:** toda vez que o rito toca uma issue, os rótulos dela
são revistos, e não só no nascimento. É a mesma regra da anatomia: todos no nascimento, e
todos revistos a cada atualização.

### A anatomia da issue

Fechado em 24/09/2026, em dez lotes de decisão. Isto é o que faz a fila contar a
verdade e o relatório existir.

**Uma issue é um sintoma reportado.** Não uma tarefa, não um commit. Se o sintoma
é grande demais para um ciclo, ele vira uma issue guarda-chuva que lista as
filhas e fecha quando todas fecham.

**O título é o sintoma que o usuário vê.** "Portal AR: editar proposta zera o
valor financiado". A causa técnica entra no corpo quando já for conhecida.

**Tudo é escrito em português de cliente, sempre.** O cliente não abre as issues,
mas elas são escritas como se ele fosse ler. Ninguém é pego de calça curta no dia
em que uma issue precisa ser compartilhada.

| Campo | Regra |
|---|---|
| Quem abre | a skill abre sozinha, depois de buscar colisão, e avisa |
| Rótulos no nascimento | TODOS, e todos revistos a cada atualização da issue |
| O que falta no nascimento | a leitura de IA completa depois, com rastro da evidência |
| WSJF | a skill propõe, e vale até alguém discordar. Nota humana existente nunca é repontuada |
| Marco | a skill cria e avisa. Nome é a frente como o CLIENTE a chama |
| Issue de duas frentes | vai para a frente que tem maior esforço |
| Quem reportou | nome e canal, sempre: "Maria, por e-mail, em 18/09" |
| Defeito que nós causamos | diz o que causou e quem fez |
| Nunca entra | credencial, token ou chave |
| Repositório | o do projeto. Diretório ambíguo obriga a perguntar, nunca a chutar |
| Mesmo tema em dois repos | uma issue em cada, ligadas por link |

**A evidência mora na própria issue.** As duas imagens, mesma cena, anexadas no
comentário. Print é obrigatório sempre que houver tela; correção sem tela prova
por saída de execução.

**Um agente por vez, nunca dois.** Trabalho paralelo exige issues separadas.

**Colisão se procura também no que outras sessões abriram nas últimas horas.** Antes de
começar o rito, leia as issues e as PRs criadas ou mergeadas nas últimas 24 horas no mesmo
repositório, e não só a busca por termo. Caso que criou a regra, 29/09/2026: duas sessões
consertaram o mesmo hreflang do site na mesma madrugada, cada uma com a sua issue (#295 e
#450), e uma delas só descobriu depois de pronta.

**Issue parada com `in-progress`: a skill avisa o operador e não mexe.** Trabalho
profundo também parece parado, e mexer na issue alheia custa mais que avisar.

### A régua que liga WSJF a prioridade

Quem manda na fila é o WSJF, e a prioridade é consequência dele. Decisão do operador em
24/09/2026, registrada na governança do backlog.

| Faixa de WSJF | Prioridade |
|---|---|
| 8 ou mais | `P0` |
| 5 a 7,99 | `P1` |
| 3 a 4,99 | `P2` |
| abaixo de 3 | `P3` |

Issue que diz duas coisas ao mesmo tempo, com WSJF alto e prioridade baixa, está mentindo
em uma das duas. A régua desempata, e quem ajusta é a prioridade.

### Fechar, descartar e provar

**Issue descartada não fica com rótulo de etapa.** Duplicada, não será atendida e não é
defeito não pararam em ponto nenhum do rito: elas saíram dele. O rótulo de etapa sai, e o
de descarte fala sozinho. Quarenta issues de um repositório de cliente apareciam vivas no painel
por causa disso.

**`e6-validado` só entra com prova, nunca por inferência.** A tentação é marcar em massa
toda fechada como concluída. Nas palavras do operador: não colocar como finalizado com
confiança se não foi tirado o print da tela funcionando.

**Saída de servidor vale no lugar do print só quando não existe tela para fotografar.**
Cobertura de classe, credencial, permission set, dado de referência e job entram por
`describe`, consulta ou log, lado a lado. Onde existe superfície de tela, o print continua
obrigatório, mesmo com a medição de servidor completa e conclusiva.

**Quem executa fecha, e deve fechar**, quando tem os três: a cena que reproduzia o defeito
verde no servidor com o id da execução, o gesto que a issue acusa feito na tela no perfil
que a issue acusa e com print, e a org confirmando o efeito depois da tentativa. Faltando
qualquer um, a issue não fecha por conta própria.

**Antes de contrariar um fecho, ler as issues irmãs do mesmo assunto.** Uma validação foi
publicada com veredito de reprovação e a issue reaberta por engano: a varredura procurou
`select` e `combobox` onde havia `lightning-checkbox-group`, e quem apontou o erro foi a
issue irmã. Comentário errado não se apaga, se tarja apontando para a retificação.

**Cobrar reteste do cliente não é escopo do backlog.** O backlog governa o que nós medimos,
corrigimos e provamos. Nenhuma issue nasce, fica aberta ou é reaberta com a tarefa de
cobrar reteste de quem contratou.

### A esteira, oito etapas

| Etapa | O que significa |
|---|---|
| `e0-nao-lida` | chegou e ninguém olhou |
| `e0-triagem` | olhada e classificada |
| `e1-medindo` | premissa sendo medida, defeito sendo reproduzido |
| `e2-provado` | par vermelho e verde feito |
| `e3-aguardando-deploy` | correção pronta e ainda não implantada |
| `e4-no-ar` | implantada no ambiente onde o cliente vê |
| `e5-reteste` | cenário rodando no ar |
| `e6-validado` | passou no reteste |

**Quem faz o passo move o rótulo, no mesmo momento em que comenta.** A esteira
vale para absolutamente tudo, inclusive feature, documentação e infraestrutura.

**A esteira anda para trás em três casos**: reprovar no reteste, descobrir que a
premissa estava errada, e deploy revertido. Reprovação reabre a MESMA issue, com
`tentativa-N`.

**Fecha quando está provado no ar e retestado.** Defeito que não vamos consertar
fecha com `debito-aceito` ou `nao-sera-atendido`, e o motivo escrito: o relatório
conta isso como decisão, e não como entrega.

**Antes de cada relatório, a fila inteira é reclassificada pela leitura de IA.**
Material não sai com balde de "sem classificação" liderando o gráfico.

### A fila vira painel, e o painel vira o relatório do cliente

O diário na issue não serve só a quem conserta. Ele é a matéria-prima do status
report que o cliente recebe, e quem desenha esse material é a skill irmã
[`bunker-pulse`](../bunker-pulse/SKILL.md), deste mesmo repositório: um gráfico
por página, 16:9, PDF que abre como slide.

**Perguntar antes de gerar.** O material custa tempo e nem toda sessão de conserto
termina em apresentação. A pergunta é uma só, e no fim do trabalho: gerar a visão
do repositório para o cliente? Sem o sim, o rito acaba na issue.

Com o sim, exporte a fila (`gh issue list --state all --limit 1000 --json
number,title,state,labels,milestone,createdAt,closedAt > fila.json`) e entregue o arquivo à
`bunker-pulse`.

**O que este rito precisa alimentar para o painel dizer a verdade**, e é por isso
que a classificação não é burocracia:

| O que a issue carrega | O que o painel responde com isso |
|---|---|
| `bv`, `tc`, `rr`, `SP` | por onde a fila deveria começar, pelo WSJF |
| `P0` a `P3` | se sobrou coisa urgente em aberto |
| `type-bug`, `type-feat`, … | se o time apaga incêndio ou constrói coisa nova |
| `e0` a `e5` | se o que está aberto já está perto de virar entrega |
| marco | de que frente do projeto o item é |
| data de abertura e de fechamento | o ritmo de entrega e o tempo até fechar |

**O marco é a classificação central, e são no máximo oito.** Acima de oito
frentes o gráfico vira lista telefônica e ninguém lê. Quando o repositório estoura
o teto, a resposta é juntar frentes, e não alargar o desenho: a ingestão avisa
alto quando isso acontece.

**Trabalho entregue sem issue não existe no painel.** Frente inteira concluída
aparece em 0% se ninguém registrou, e o cliente lê isso como projeto parado. A
correção é retroalimentar: cada entrega antiga vira uma issue já fechada, com a
data real no corpo, na forma `Aberta originalmente em DD/MM/AAAA`. A camada de
leitura lê essa linha e joga a entrega no dia em que ela aconteceu, e não no dia
em que a issue foi criada. Caso que criou a regra, 24/09/2026: uma frente de 38
componentes estava 100% pronta e o relatório mostrava 0%, porque o trabalho tinha
acontecido antes de o repositório ter controle de issues.

**Classificação que o rótulo não deu, a leitura de IA dá, com rastro.** A IA lê
título e corpo e escolhe uma frente DENTRO da lista fechada, guardando de onde veio
(rótulo, marco ou leitura) e a frase que sustenta a escolha. Frente inventada pelo modelo é descartada, e o item continua sem
classificação: o vocabulário é decisão de quem toca o projeto. Num repositório com
272 itens sem frente, isso derrubou o balde vazio para 11 sem inventar nada.

**A régua do relatório é a mesma do rito.** Nada de prazo prometido: o material
mostra a curva e para onde ela aponta. Promessa de data que o time não cumpre gera
ansiedade e queima a confiança que o painel existe para construir.

---

## 0. Abrir pelas perguntas, antes de qualquer outra coisa

**Este passo é obrigatório e vem primeiro.** Nenhum defeito entra em eleição,
medição, teste ou correção sem o operador ter escolhido a abordagem e esclarecido
as regras de negócio que mudam o rumo. Corrigir rápido o defeito errado, do jeito
errado, custa mais que perguntar: já saiu correção que resolvia o sintoma e
quebrava uma regra que só o dono do negócio conhecia.

**Primeiro lê, depois pergunta.** Antes de abrir a caixinha, ler a issue inteira com
os comentários, o estado real no código e no ambiente (só leitura) e o que já foi
tentado. Pergunta com opção genérica, que valeria para qualquer defeito, é
pergunta mal feita: cada opção cita o objeto, o número ou o registro concreto do
caso. Ler não é pedir licença para investigar, e investigar não é consertar.

**Duas famílias de pergunta, e as duas entram:**

| Família | O que decide | Exemplos |
|---|---|---|
| Arquitetura | onde e como corrigir | na causa ou no sintoma; no flow, no Apex ou no dado; correção pontual ou estrutural; trocar o mecanismo ou tolerar a falha; quanto do que já roda é tocado |
| Regra de negócio | o que é o comportamento certo | o que o cliente ou o aluno já viu e espera; quem é afetado e quem não pode ser; o que acontece com o que já saiu; o que muda de frequência, de preço ou de contato |

Regra de negócio que o código não responde nunca é decidida por quem corrige.
Sempre que a correção puder ir para dois comportamentos diferentes, a pergunta é do
operador.

**Como perguntar.** Com `AskUserQuestion`, **em linguagem de negócio**: a pergunta
e as opções falam de aluno, e-mail, cliente, preço e prazo, e nunca de flow, objeto,
campo ou classe. O termo técnico vai para o comentário gravado na issue, não para a
caixinha. **Um assunto por pergunta**, e por padrão uma pergunta por chamada, na
ordem em que a resposta de uma muda a próxima. Quando o operador pedir pressa,
junta até quatro perguntas de assuntos diferentes numa chamada, e volta ao ritmo
normal depois. **Quatro opções por pergunta**, cada uma com o que faz e o que
custa. A recomendada vai primeiro, marcada "(Recomendada)", e a opção que a segue
diz o que ela deixa de resolver. Quando o operador responde "me traga mais
informações", o rito traz o que falta, medido, em prosa curta, e pergunta de novo.
Não decide por ele.

**A resposta fica na issue, na hora.** Comentário "Decisão de abordagem" com a
escolha, as opções descartadas em uma linha cada e a regra de negócio esclarecida.
É o primeiro dos marcos do diário. Sem a resposta, o rito para aqui e o comentário
de travamento diz qual pergunta está aberta.

**Quando não há bifurcação.** Se, depois de ler, só existe um caminho e nenhuma
regra de negócio em jogo, isso se mostra ao operador, com a evidência de por que
não há alternativa, e o rito segue. O que não existe é pular o passo em silêncio.

**O que o passo 0 entrega ao passo 2.** A abordagem escolhida é de onde nasce a
premissa "se eu fizer X, então Y". Premissa escrita antes da escolha mede a
correção que o operador não pediu.

## 1. Eleger o defeito, por contagem e não por rótulo

**Qual defeito atinge mais?** Não o mais irritante, não o mais fácil, não o que
apareceu na última conversa. O que atinge mais, medido.

**Contagem determinística ganha de prosa.** Quando existir um sinal que não depende
de julgamento (o teste esperava N chamadas e houve M; o campo ficou vazio; o
registro não nasceu), é ele que vale. Filtro de texto sobre a explicação de um
avaliador, humano ou modelo, aponta o alvo errado com frequência.

**Rótulo de texto mente.** Ler um punhado de casos reais antes de cravar o alvo. Um
filtro pode estar juntando duas coisas diferentes, ou capturando a frase genérica
que o avaliador usa quando não sabe nomear o problema.

**Liderar a lista não é ser o alvo certo.** O primeiro colocado pode já estar
resolvido, se a base for anterior à última correção. Sempre recortar a medição
pela janela de tempo posterior à última entrega, senão você ataca fantasma.

**Alcance não é entrega.** "Esta correção alcança metade dos casos" é projeção, e
projeção não medida vale zero.

Ao fim deste passo você tem: o defeito, quantos casos ele atinge, em quantos
fluxos, e se ele é o primeiro erro (o que mata o caso ali) ou um erro posterior.

## 2. Medir a premissa, antes de escrever uma linha

Toda correção tem uma premissa embutida. Escreva-a numa frase, no formato "se eu
fizer X, então Y acontece". Depois **meça essa frase**, barato, antes de tocar no
código de produção.

Formas de medir, da mais barata para a mais cara:

- reprocessar dados já coletados com a lógica nova, offline;
- montar a saída nova a partir do que já está gravado e comparar com a antiga, nos
  mesmos casos, lado a lado;
- rodar um punhado de casos reais pelo caminho novo, sem deployar nada.

Se a medição não mostrar conversão, **a correção não é escrita.**

**Amostra pequena não decide nada.** Quando o avaliador é um modelo, ele muda de
opinião sobre o mesmo texto. Meça essa instabilidade uma vez: rejulgue o mesmo
conteúdo duas vezes e veja quantos vereditos viram. Ganho abaixo desse ruído não é
ganho. Uma amostra de trinta casos costuma ser cega para diferenças reais; se o
resultado ficar em cima do ruído, aumente a amostra antes de descartar a ideia.

**Meça também o que NÃO pode mudar.** Junto do grupo alvo, leve um grupo de
controle que deve continuar reprovando. Se ele se mexer, a correção não consertou
o defeito, ela afrouxou o critério.

**Meça o que a AUTOMAÇÃO escreve, antes de escolher onde a trava pega.** Quando a
correção é uma regra que recusa gravação, ela não distingue quem grava: pega a
pessoa e pega o robô. Levante, antes de escrever a regra, quais rotinas escrevem
naqueles mesmos campos, com qual usuário e em que momento. Se alguma delas roda
como o usuário que você quer barrar, a regra vai transformar uma operação legítima
em erro de plataforma na cara dele.

A saída quase nunca é enfraquecer a regra: é **separar o que a pessoa digita do que
o sistema deriva**, e deixar de fora da regra os campos derivados. E isso não vale
como promessa: vira cenário de teste, provando que a automação atravessa.

Caso que criou a regra, 24/09/2026: uma trava de edição por fase, numa proposta,
listaria também a soma dos equipamentos e o percentual. Esses dois campos são
gravados por uma rotina disparada pelo gatilho de equipamento, rodando como o
próprio usuário barrado. Tivessem entrado na lista, adicionar um equipamento viraria
erro de plataforma. Medir antes custou uma consulta; descobrir depois custaria uma
correção implantada em cima do cliente.

Registre o número. Ele é a promessa contra a qual o resultado final será cobrado.

## 3. Reproduzir, e ver vermelho no código de hoje

**O vermelho legítimo é o teste falhando no código atual, sem você ter mexido em
nada.** O defeito está vivo agora; não há o que desfazer. Escreva o teste, rode,
veja falhar.

Se o teste não ficar vermelho, **você não entendeu o defeito.** Pare. Volte para os
dados. Não escreva a correção.

Regras do teste:

- **Entrar pelo caminho que o produto usa.** Nunca chamar a função nova direto: ela
  existe nas duas versões do código, então o teste passaria de qualquer jeito. Ele
  precisa entrar pela porta do produto e olhar o que o produto ENTREGA, o texto ou
  o dado que a pessoa do outro lado recebe.
- **Reproduzir o caso real, com os dados do caso real.** O teste vale mais quando
  alguém consegue rastrear dele até o registro que expôs o defeito. Cite o caso no
  comentário de cima.
- **Simular a fronteira, não o miolo.** Serviço externo, integração e modelo entram
  simulados, para o teste ser determinístico, gratuito e imune a ambiente caído. A
  lógica do produto roda de verdade.
- **Marcar a asserção que carrega a prova.** Uma asserção, com a palavra `PROVA` na
  mensagem. É ela que fica vermelha quando a correção sai, e é por ela que o
  arquivo existe.

**Vermelho pelo motivo errado não é vermelho.** Antes de comemorar a falha, leia a
mensagem dela. Teste que cai por campo obrigatório faltando na montagem, por dado de
apoio que não existe, ou por erro de compilação, está falhando por defeito SEU, e
não pelo defeito do produto. O vermelho que vale é o que aponta para a asserção
`PROVA`; qualquer outro é montagem para consertar antes de seguir.

Caso que criou a regra, 24/09/2026: a primeira execução de um teste novo deu cinco
vermelhos, e os cinco eram um campo obrigatório ausente na criação do registro. Lido
de longe, parecia o defeito reproduzido cinco vezes.

## 4. Atacar o próprio teste

Antes de aceitar o teste como bom, pergunte: **de quantos jeitos ele passaria com o
código errado?** Liste, e feche cada porta.

Armadilhas conhecidas:

- asserção sobre ausência de marca, e não sobre o conteúdo que a pessoa lê;
- asserção que passa quando o resolvedor devolve a própria chave em vez do texto;
- cenário de falha escolhido justamente onde a falha nunca acontece;
- verificação da chamada feita, e não do efeito no banco;
- asserção que um despejo de dados brutos satisfaria;
- **recusa que vem de acesso, e não da regra que você quer provar.**

**A armadilha do acesso é a mais traiçoeira, porque ela deixa o teste VERDE.** Se o
registro do cenário nasce pela mão de um administrador, o usuário que sofre o
defeito pode simplesmente não enxergar aquele registro. A operação dele é recusada,
o teste vê a recusa que esperava, e fica verde: verde pelo motivo errado, com o
defeito vivo. Depois da correção ele continua verde, e ninguém descobre nada.

Como fechar: **o dado do cenário nasce pela mão de quem sofre o defeito**, pelas
mesmas chamadas que a tela faz. E vale uma asserção de porta fechada dizendo que o
usuário ALCANÇA o registro, para um verde nunca poder significar "ele não tinha
acesso a nada".

Caso que criou a regra, 24/09/2026: o cenário provava que um usuário de portal não
pode alterar valor financeiro fora de certa fase. A proposta era criada pelo
administrador, e a recusa que o teste leu era de compartilhamento, não da fase. O
teste passou com o defeito vivo, e quem pegou foi quem desconfiou de um verde que
chegou cedo demais.

**Teste que passa sem provar nada é pior que não ter teste**, porque compra
confiança falsa. E o sinal mais comum dele é passar na primeira tentativa, antes de
a correção existir.

## 5. Corrigir, e ver verde

Agora, e só agora, escrever a correção. O menor conserto que faz o teste do passo 3
ficar verde.

**Procurar a peça pronta antes de escrever peça nova.** Muitas vezes o produto já
calcula a coisa certa e a descarta em algum ponto do caminho. Achar isso é mais
barato e mais seguro que escrever um caminho paralelo.

**Pedir não é garantir.** Correção que depende de um modelo obedecer a uma
instrução entrega uma fração do prometido. Quando o resultado precisa ser certo,
faça o código impor, não o texto pedir.

## 6. Desfazer, e ver vermelho de novo

Retirar a correção e rodar. O teste tem de voltar a falhar, **pelo motivo certo**.
Guardar os dois números.

Feito na ordem certa, este passo é confirmação, não descoberta: o vermelho já
existia no passo 3. Ele fica no rito porque prova que o vermelho vem DESTA correção
e não de outra coisa que mudou junto.

**Registrar o par no cabeçalho da classe de teste**, em uma linha: "rodado nos dois
sentidos em DD/MM: sem a correção X vermelhos; com ela Y verdes."

## 7. Capturar o antes e o depois, e subir o par para a issue

Número verde não mostra nada a quem não lê teste. **Toda correção sai com um par de
imagens**, o antes e o depois, e uma ficha curta. Quem decide o que fazer com isso
(mandar para o cliente, entrar num dossiê, anexar ao chamado, arquivar) é o operador,
depois de ver. O rito produz a evidência e para.

**O antes se captura antes, e essa é a única janela.** Depois que a correção entra,
o defeito não existe mais para ser fotografado. Por isso este passo mora colado ao 6:
com a correção desfeita, o defeito está vivo na tela, e é ali que se aperta o botão.
Quem pular isso vai ter de desfazer de novo só para tirar a foto.

**Não existe correção sem superfície.** Se a mudança aparece numa tela, a evidência é
print de tela. Se aparece num e-mail, é o e-mail renderizado. Se é relatório ou
documento, é a página. Se é API, integração ou job, é a saída literal, o JSON, o log,
a linha do registro no banco, lado a lado. "Não dava para mostrar" não é resposta:
tudo que o produto faz tem uma saída que alguém lê.

**Print sempre, e não só quando corrige.** Todo relatório ao operador leva evidência
de tela, inclusive quando o rito para antes da correção: no passo 2, porque a
premissa não converteu; no passo 3, porque o defeito não reproduziu; e também em
triagem, reteste, conferência e frente só de evidência. "Não reproduz" também se
prova com print: a tela fazendo o certo, no registro e no perfil que a issue acusa.
Sem superfície de tela, vale a saída literal lado a lado, como diz o parágrafo
acima, mas o relatório nunca volta só com prosa.

Caso que criou a regra (24/09/2026): numa issue, o rito parou no passo 2 porque o
defeito do título não reproduzia, e o relatório voltou sem nenhum print. O operador
não conseguiu entender o que estava acontecendo e teve de pedir a referência visual.
O mesmo já tinha acontecido em triagem e em frentes de evidência.

**As duas imagens mostram a mesma cena.** Mesmo registro, mesmo usuário, mesma tela,
mesmo recorte, mesmo zoom. Duas fotos de lugares diferentes não provam nada, e um
recorte generoso no depois esconde o que não foi consertado. Quando o defeito é um
detalhe dentro de uma tela cheia, vale o par completo mais um par ampliado do ponto.

**Capturar como o usuário vê, não como o desenvolvedor vê.** A tela é a do perfil que
sofreu o defeito, no idioma dele, no ambiente onde ele trabalha. Print do Setup, do
console do navegador ou da ferramenta de linha de comando serve de apoio técnico,
nunca como a evidência principal.

**Evidência de texto vai em escala cheia, e o texto se confere pelo DOM.** Captura
reduzida economiza espaço e come letra: numa tela em escala 0,5 a diferença entre
"configurado" e "configurada" some, e quem transcreve jura ter lido o que não estava
lá. Quando o defeito é uma frase, um rótulo ou uma mensagem de erro, capture em escala
cheia e amplie o ponto. E antes de citar a frase em qualquer lugar, leia o texto pela
árvore de acessibilidade ou pelo DOM, não pela imagem: a imagem mostra que a tarja
existe, o DOM diz o que ela escreve.

Caso que criou a regra (20/09/2026): uma tarja de erro foi transcrita com uma letra
trocada a partir de um print reduzido. O engano quase invalidou a evidência de um
defeito verdadeiro, porque a frase citada não batia com nenhum rótulo do produto e
parecia vir de outro ponto do sistema. Quem pegou foi quem duvidou da transcrição.

Onde os arquivos ficam e como se chamam:

```
evidencias/<identificador do defeito>/antes.png
evidencias/<identificador do defeito>/depois.png
evidencias/<identificador do defeito>/ficha.md
```

A ficha tem seis linhas, e só:

```
Defeito:     o que a pessoa via de errado, em uma frase sem jargão
Quem sofria: o perfil, e em que tela ou fluxo
Causa:       a raiz medida, não a suspeita
Correção:    o que mudou, em uma frase
Prova:       o par vermelho e verde, com os números
Evidência:   antes.png e depois.png, mesma cena
```

### O par sobe para a issue, e é ali que ele mora

**Corrigiu, tem print na issue.** Não é opcional, não é "quando der", não depende de
alguém pedir. O comentário de fechamento da correção leva as duas imagens anexadas,
o antes e o depois, e a ficha de seis linhas junto. A issue é o arquivo permanente do
defeito: quem for montar material meses depois vai buscar ali, e o que não estiver na
issue não existe.

Anexar imagem a comentário pela linha de comando não é direto. O caminho que funciona:

```bash
# 1. a evidencia mora na propria issue: anexa as duas imagens no comentario
#    (a branch de evidencias abaixo continua valendo para imagem grande demais
#     para o anexo, ou quando o repositorio exigir rastro por SHA)
git add evidencias/<id>/antes.png evidencias/<id>/depois.png
git commit -m "evidencia(<id>): antes e depois de <defeito em tres palavras>"
git push origin <branch de evidencias>
git rev-parse HEAD   # o <sha> que o comentário vai citar

# 2. confere que o arquivo existe naquele SHA, pela API de conteúdo
gh api "repos/<owner>/<repo>/contents/evidencias/<id>/antes.png?ref=<sha>" --jq .path
gh api "repos/<owner>/<repo>/contents/evidencias/<id>/depois.png?ref=<sha>" --jq .path

# 3. comenta na issue com a forma que abre em repositório privado
gh issue comment <n> -R <owner>/<repo> --body "$(cat <<'MD'
## Corrigido

**Print 1 de 2, antes.** <o que a tela mostra, em linguagem de negócio>

[![antes](https://github.com/<owner>/<repo>/blob/<sha>/evidencias/<id>/antes.png?raw=true)](https://github.com/<owner>/<repo>/blob/<sha>/evidencias/<id>/antes.png)

---

**Print 2 de 2, depois.** <o que a tela mostra agora>

[![depois](https://github.com/<owner>/<repo>/blob/<sha>/evidencias/<id>/depois.png?raw=true)](https://github.com/<owner>/<repo>/blob/<sha>/evidencias/<id>/depois.png)

---

<a ficha de seis linhas>
MD
)"
```

**Imagem em repositório privado não se embute por `raw.githubusercontent.com`.** Esse
endereço só responde com token. Na sessão do navegador, que é onde o operador abre a
issue, ele dá 404, e o comentário mostra imagem quebrada no lugar da prova. A forma
que abre para quem tem acesso ao repositório é o endereço do arquivo em `github.com`,
fixado pelo SHA, com `?raw=true`, e a imagem vira link para o próprio arquivo:

```
[![legenda](https://github.com/<owner>/<repo>/blob/<sha>/<caminho>?raw=true)](https://github.com/<owner>/<repo>/blob/<sha>/<caminho>)
```

**A legenda vem ANTES do print, numerada, e um separador fecha cada print.** Com
vários prints seguidos, uma frase solta entre duas imagens serve igual para a de cima
e para a de baixo, e quem lê não sabe a qual das duas ela se refere. Cada print vira
um bloco de três partes, nesta ordem:

```
**Print 3 de 12, formulário de edição da conta, etapa Actividad.** <o que a tela mostra>

[![conta-i292-...-antes](<endereço fixado pelo SHA>?raw=true)](<endereço fixado pelo SHA>)

---
```

- a legenda abre o bloco, em negrito, com "Print N de T" e a tela;
- a imagem vem logo abaixo, separada da legenda por uma linha em branco;
- o `---` fecha o bloco, e nenhum texto fica entre a imagem e o separador.

Nunca legenda embaixo da imagem, nunca duas imagens coladas sem legenda própria, e
quando o texto do comentário se refere a um print, ele cita o número ("no print 3").

Caso que criou a regra (28/09/2026): numa issue de cliente, treze prints saíram cada um com
a legenda embaixo e sem separador, e o operador não conseguia saber se a frase
comentava a imagem de cima ou a de baixo.

**A existência se confere pela API de conteúdo, no SHA, e não por curl.**
`gh api repos/<owner>/<repo>/contents/<caminho>?ref=<sha>` diz se o arquivo está
naquele commit. Curl autenticado na URL crua devolve 200 porque leva o token que o
navegador não leva, e por isso não diz nada sobre o que o operador vai ver.

**A imagem mora no CORPO da issue quando ela é a evidência que sustenta o card.**
Comentário some no meio de vinte outros, e o operador abre a issue pelo topo. Se o
corpo cita um arquivo de evidência pelo nome, ele carrega o link embutido; citar
`imagem17.png` sem endereço nenhum é o mesmo que não ter evidência.

Caso que criou a regra (24/09/2026): três issues saíram com as imagens embutidas por
`raw.githubusercontent.com`, e as três deram 404 para o operador no navegador. O teste
com curl autenticado dava 200, e foi isso que escondeu o erro até ele abrir a issue.
No mesmo dia, outras três issues citavam as evidências do cliente só pelo nome do
arquivo, sem link: as imagens estavam no repositório desde o início e ele nunca
conseguiu vê-las.

Quando o repositório não puder receber a imagem, vale qualquer hospedagem que o
operador já use, e o comentário carrega o link. O que **não** vale é comentário de
correção sem imagem: uma frase dizendo que está corrigido não prova nada a quem lê
depois, e é exatamente o que produziu issues fechadas com o defeito vivo.

### O padrão de nome, para o material se montar sozinho depois

O material de entrega é montado DEPOIS, quando as correções estiverem fechadas, e ele
se monta a partir das evidências das issues. Para isso funcionar sem trabalho manual,
o nome do arquivo carrega o que o montador precisa saber:

```
<frente>-<id do defeito>-<etapa>-<estado>.png

exemplos:
  conta-i150-localidade-antes.png
  conta-i150-localidade-depois.png
  proposta-i148-guardar-resumen-antes.png
  proposta-i148-guardar-resumen-depois.png
```

- **frente**: a área do produto (conta, proposta, modais, chat)
- **id do defeito**: o número da issue, com `i` na frente
- **etapa**: a tela ou o passo, em uma ou duas palavras
- **estado**: `antes` ou `depois`, e só isso

Junto de cada par vai uma linha no `ficha.md` dizendo, em linguagem de negócio, o que
aquela tela mostra. É essa frase que vira legenda no material, então ela se escreve
pensando em quem vai ler e não em quem corrigiu.

### O que este passo NÃO faz

**Não atualiza material de entrega.** Dossiê, deck, galeria e página de vitrine se
montam uma vez, no fim, quando o conjunto de correções fechar. Regenerar material a
cada correção gasta tempo, produz versões que divergem entre si, e coloca no
documento telas de defeito que já foram resolvidas.

Entregar ao operador é mostrar as duas imagens e a ficha na conversa, e dizer que
elas já estão na issue. **Nada sai daqui sozinho**: e-mail ao cliente, material
publicado e qualquer coisa que saia no nome da Bunker são decisão dele, uma a uma.

## 8. Deployar, com cobertura por classe

**Testes verdes não destravam deploy.** O corte é de cobertura, e é POR ARQUIVO, não
pela média. A tabela agregada mente.

Medir os dois lados por simulação de deploy, que compila e roda sem gravar. Rodar a
suíte relacionada de verdade, pelo impacto real da mudança, não uma lista escolhida
para passar rápido.

**Antes de subir, comparar o que está no ambiente com o que está na sua cópia.** Se
a sua cópia tem trabalho de outra pessoa junto, você vai deployar o dela também.

**Nunca deployar durante uma medição em andamento.** O deploy no meio invalida a
rodada inteira e a comparação entre antes e depois vira lixo.

Este passo toca o ambiente do cliente. **Espera autorização explícita**, mesmo com
tudo verde.

## 9. Rodar tudo de novo, e reeleger

**Bug resolvido, roda TUDO.** Não um bloco, não uma amostra.

**Rodar o caso inteiro, e não só o pedaço atingido.** Se um cenário tem vinte
passos e a correção toca o quinto, rode os vinte: a correção pode ter estragado o
décimo segundo.

**Cuidado com o alcance da lista.** Ao escolher o que remedir, o filtro tem de
varrer a base inteira, e não só a fatia medida por último. Fatia velha esconde
casos que a correção resolveria, e o número global fica pessimista.

**Não ler bloco pela metade.** É fácil ler o número parcial que confirma a própria
correção e parar ali. O total costuma desmentir.

Comparar contra o número prometido no passo 2. Se a entrega ficou muito abaixo da
premissa, a premissa estava errada, e isso é informação: registre.

**Procurar o estrago que a própria correção fez.** Toda correção mexe na saída. Leia
alguns casos que passaram, não só os que falharam, e pergunte se o texto novo ficou
bom. Defeito introduzido por conserto costuma nascer grande, porque atinge todo
caso onde o conserto atua.

Depois, voltar ao passo 1 e reeleger com a base nova.

---

## Regras que valem o rito inteiro

**Pergunta antes de rumo, sempre.** Abordagem de arquitetura e regra de negócio ambígua se decidem com o operador no passo 0, nunca no meio da correção. Descobriu uma bifurcação nova depois de começar, para e pergunta de novo.

**Achado vira proposta, não correção.** Diagnóstico não é autorização. "O que você
arrumaria?" é pergunta. Mostrar o defeito, a evidência e o diff proposto, e
esperar. Vale inclusive dentro de um laço autônomo que foi pedido.

**Escrever teste que só prova o defeito não é alterar produto.** Pode escrever e
rodar à vontade. Deployar já mexe no ambiente, então espera.

**Falha de ambiente nunca vira defeito.** Credencial vencida, cota estourada, limite
de taxa, tempo esgotado e serviço fora do ar saem da conta e são declarados
separados. Sem essa separação, um teto de uso atingido no meio da tarde marca
dezenas de casos como reprovados e a comparação entre duas medições morre.

**Medição que morreu no meio não vale.** Antes de comparar, conferir que a rodada
terminou inteira. Rodada que caiu por falha de ambiente vai fora, não entra na foto
como se fosse defeito do produto.

**A régua só cresce.** Nunca diminuir a exigência de um cenário, nunca remover
cenário, nunca relaxar critério para fechar entrega. Se um cenário passou a
incomodar, o defeito é do código.

**Consertar o avaliador é legítimo; afrouxá-lo não.** Se o avaliador reprova algo
verdadeiro, isso é falso positivo e vale corrigir, com duas travas: um grupo de
controle que precisa continuar reprovando, e armadilhas de critério impossível que
precisam continuar falhando. Se qualquer uma passar, a mudança é inválida.

**Relatório sem print não sai, e print que não abre não conta.** Vale para qualquer
parada do rito, não só para a correção, e imagem em repositório privado vai pela
forma que abre no navegador. As duas regras estão no passo 7.

**Correção que derruba um critério de aceitação já existente não se resolve
emendando o critério, e muito menos por quem escreveu a correção.** A tentação é
ajustar o teste antigo até ele caber na mudança nova, e isso é afrouxar a régua com
outro nome. Quando a emenda for mesmo legítima, ela precisa de três coisas: a
exigência tem de ficar MAIOR e não menor, a exceção tem de ser nomeada e justificada
dentro do próprio teste, e **quem revisa não pode ser quem escreveu a correção**.
Sem o terceiro item, os outros dois se auto-concedem.

**Fundir issue é extrair primeiro, fechar depois.** Ao juntar duas issues no mesmo
assunto, o que morre não é a issue, é o que só ela media: um número, um id de
registro, um arquivo e linha, uma branch com correção escrita, um pedido de mescla
aberto. A ordem que não perde trabalho é: ler a absorvida inteira, escrever no card
dono o que só ela carrega, e **só então** fechar apontando para lá. Fechar primeiro e
prometer consolidar depois é como se perde correção pronta.

Caso que criou a regra, 24/09/2026: numa consolidação de vinte e quatro issues, três
delas carregavam correção já escrita e provada em branch não mesclada. Fechadas na
ordem errada, esse trabalho teria virado arqueologia.

**Trabalhar em worktree isolado**, com branch própria, sem perguntar.

**Não commitar trabalho de terceiros.** Se a árvore tem mudanças de outras sessões
misturadas nos mesmos arquivos, o commit espera decisão de quem manda.

**Uma tarefa de fundo que vigia processos não pode se reconhecer na própria busca.**
Vigia que procura o nome do processo alvo e encontra a si mesmo nunca termina, ou
dispara de novo o que já rodou.

## O que este rito NÃO faz

Não escreve caderno de aceitação para o cliente rodar. Não monta dossiê de
evidência de entrega. Não desenha o relatório do cliente, que é da
`bunker-pulse`: aqui a obrigação é deixar a issue classificada e o
diário escrito, que é o que aquele material lê. Não decide o que entra no escopo. Este rito começa quando já
existe um defeito medido e termina quando ele está morto e provado morto.
