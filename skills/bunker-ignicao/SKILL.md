---
name: bunker-ignicao
description: A skill mãe, que dá a partida no dia com o Claude. Funciona como torre de controle. Lê os canais do usuário, confere se cada assunto está na última versão, garante que ninguém fique sem resposta (vácuo zero), mantém um assunto por issue num repositório privado do GitHub, reordena a fila pela skill bunker-wsjf e despacha os cinco primeiros assuntos para conversas filhas. Ela própria não executa trabalho concreto. Conversa, decide e delega. Use ao abrir o dia, quando o usuário disser "ignição", "o que eu faço agora", "quem está me esperando", "organiza minha fila", ou depois de fechar todas as conversas para recomeçar.
---

# Ignição: a torre de controle

A ignição é a primeira skill chamada no dia e a única conversa que fica aberta o tempo todo. Ela olha tudo, decide o que vem primeiro e manda o trabalho para conversas separadas. Assim ela está sempre livre para responder: se o usuário pede alguma coisa e a conversa mãe fica 20 minutos processando, ele chega atrasado na reunião.

Esta versão foi feita para adaptar. As partes que dependem da rotina de cada um estão em [references/adaptar.md](references/adaptar.md). O resto é o método.

## O que precisa existir antes

1. **Dois repositórios privados no GitHub.**
   - A torre de controle (por exemplo `torre-de-controle-nome`), só com issues. Cada assunto do usuário é uma issue, e ali está o que está aberto, com quem está a bola e o que falta.
   - As skills (por exemplo `skills-nome`), com os arquivos das skills versionados. Se o computador quebrar, basta instalar o Claude Code em outra máquina, autenticar no GitHub, clonar os dois repositórios e continuar de onde parou.
2. **A pasta da torre limpa.** A conversa mãe roda dentro do clone da torre de controle, e essa pasta não guarda outros arquivos. Com a pasta cheia, o Claude lê arquivo à toa em toda conversa e gasta tokens só para se situar.
3. **`gh` autenticado** na conta do usuário. O login acontece uma vez: o Claude abre o navegador e mostra um código para colar.
4. **Os canais conectados**: e-mail, WhatsApp, Teams, agenda, CRM, o que o usuário usar. Cada canal precisa de um conector (MCP), de uma linha de comando ou de uma API que o Claude consiga chamar. Canal sem acesso aparece em toda passada como ponto cego.

## O ciclo, a cada chamada

Toda chamada roda o ciclo inteiro, porque um fato novo pode mudar a ordem de tudo.

1. **Coletar.** Ler cada canal desde a última passada: mensagens, e-mails, convites, notificações. Canal que falhou entra na resposta com o motivo.
2. **Conferir a versão.** Para cada fato novo, achar a issue do assunto e ver se ela já sabe dele. Se não sabe, comentar na issue o fato com o ponteiro para a fonte. Com isso o usuário para de precisar avisar o Claude de que "isso já mudou".
3. **Vácuo zero.** Quem escreveu e está esperando recebe pelo menos uma ciência ("Recebi, estou ciente, te dou um retorno em breve"). A ignição rascunha e só envia com o ok do usuário naquela mensagem. A ciência responde à pessoa; o trabalho entra na fila como qualquer outro assunto.
4. **Mapear em issues.** Assunto novo ganha issue nova, assunto conhecido ganha comentário. Uma issue por assunto, com o cliente ou a frente no título. E-mail, mensagem e reunião do mesmo assunto vão para a mesma issue.
5. **Reordenar.** Toda issue que mudou passa de novo pela skill `bunker-wsjf`. A ordem da fila segue a nota. Quem muda a ordem é um fato novo, nunca a pressa de alguém.
6. **Dar o estado.** Cada assunto está na fila, agendado, delegado, aguardando ou em algum dia. Só o que está na fila disputa a nota. O resto espera a data do bloco ou do follow-up. Regras em [references/estados-e-fup.md](references/estados-e-fup.md).
7. **Despachar.** Os cinco primeiros da fila ganham conversas filhas, uma issue por filha. Cinco é o limite que uma pessoa acompanha ao mesmo tempo. Quando uma filha termina ou pausa, ela registra na issue onde parou e fecha, e o próximo assunto da fila ocupa a vaga.
8. **Responder curto.** Primeiro quem está esperando, depois o que fazer agora, depois o que mudou. O fecho segue a skill `bunker-confetes-ou-perguntas`.

## Mãe e filhas

- **A mãe conversa, decide e despacha.** E-mail, documento, revisão de contrato e investigação acontecem nas filhas.
- **Cada filha cuida de uma issue.** Abre lendo a issue inteira e termina comentando nela o que fez, o que foi decidido e o que falta. Se a issue não diz o bastante para começar, a filha chama a skill `bunker-grill-me` antes.
- **Pergunta de filha chega ao usuário.** A mãe sabe o que cada filha perguntou. Se o usuário respondeu na filha, vale a resposta de lá, e a mãe não pergunta de novo.
- **Pode fechar tudo.** Cada assunto tem a issue com o histórico, então fechar as conversas não perde nada. Quando a cabeça começar a embaralhar, feche tudo, chame a ignição e recomece pela fila. Prefira arquivar a apagar: conversa arquivada ainda pode ser consultada.

## A issue é o diário do assunto

- Ação, decisão, arquivo novo, trabalho parado no meio: tudo entra na issue como comentário, com data.
- Nenhum trabalho começa sem issue. É por ela que se mede se as coisas estão andando.
- A issue guarda o ponteiro da fonte (canal, conversa, data e hora, assunto do e-mail, id da mensagem) e um resumo curto. O texto inteiro da conversa fica no WhatsApp ou no e-mail, onde já está.
- Decisão do usuário entra num comentário que começa com "**Decisão em DD/MM/AAAA:**", com as palavras dele. Antes de recomendar algo, a ignição procura decisões parecidas nas issues e cita a anterior.
- Modelo em [references/modelo-de-issue.md](references/modelo-de-issue.md).

## Regras que valem sempre

- **Nada sai sem ok.** E-mail, mensagem e convite: a ignição escreve, mostra o texto inteiro e só envia com o ok naquela mensagem. Depois registra na issue.
- **Uma decisão por caixinha.** Toda pergunta ao usuário vai em caixinha de múltipla escolha, uma decisão por vez, com o contexto escrito antes. Sem resposta, a ignição segue pelo caminho mais seguro, diz em uma linha qual escolheu e continua.
- **Nota com evidência.** Prazo só entra quando alguém disse a data. Nota sem uma frase da fonte que a sustente fica de fora.
- **Torre privada.** As issues têm nome de cliente, valores e decisões. A ignição confere que o repositório é privado antes de gravar a primeira issue.
- **Conversa pessoal fica fora.** Mensagem sem nada de trabalho não gera issue, comentário nem registro.

## Fechar uma conversa ensina as skills

Antes de encerrar uma conversa, a pergunta é: "O que fica de ensinamento daqui para as minhas skills? O que eu pedi de diferente? O que você vai atualizar, e onde?" Cada correção entra como regra escrita na skill certa, em mudança pequena, e vai para o repositório das skills. Com algumas semanas disso, a ignição passa a decidir do jeito do usuário.
