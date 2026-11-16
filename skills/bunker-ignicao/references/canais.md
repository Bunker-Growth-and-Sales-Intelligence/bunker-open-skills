# Mapa dos canais

A ignição só enxerga o que consegue ler. Antes da primeira passada, e sempre que aparecer um ponto cego, o Claude faz três coisas com o usuário: descobre por onde chegam os assuntos, liga cada canal pelo caminho mais simples que existir e testa a leitura. Só depois monta a lista de assuntos.

Serve para qualquer pessoa e qualquer sistema. Ninguém precisa ter Salesforce, Gmail ou Teams: o que importa é que cada canal tenha algum caminho até o Claude, nem que seja um arquivo exportado.

## 1. Descobrir os canais

Pergunte em caixinhas, um grupo por vez, e anote tudo o que a pessoa marcar. Peça também o "outro": é ali que aparece o sistema que ninguém lembra.

| Grupo | Exemplos |
|---|---|
| Mensagens | WhatsApp (pessoal e do trabalho), Telegram, Slack, Teams, Discord, direct do Instagram ou do LinkedIn |
| E-mail | Gmail, Outlook, e-mail da empresa, mais de uma conta |
| Agenda e reuniões | Google Agenda, Outlook, Calendly, gravações e transcrições de reunião |
| Trabalho | CRM (HubSpot, Pipedrive, RD Station, Salesforce), gestão de projetos (Trello, Asana, Notion, Jira, ClickUp, Monday), sistema de chamados, ERP |
| Documentos | Google Drive, OneDrive, SharePoint, Dropbox, pastas no computador |
| Dinheiro | contas a pagar e a receber, nota fiscal, extrato do banco |
| Pessoas | quem mais manda pedido, e por onde manda |

Feche com uma pergunta aberta: "Tem algum lugar onde chega pedido para você e que eu ainda não perguntei?". Um papel na mesa e o caderno também contam: entram por foto ou ditado.

## 2. Ligar cada canal

Para cada canal, tente nesta ordem e pare no primeiro degrau que funcionar. Confira sempre na hora o que existe, porque conectores novos aparecem toda semana.

| Degrau | Caminho | Como achar |
|---|---|---|
| 1 | **Conector nativo do Claude** | No Claude.ai ou no Claude Desktop, Configurações e Conectores. No Claude Code, o mesmo conector aparece se a conta for a mesma. |
| 2 | **Servidor MCP** do próprio fornecedor ou da comunidade | Procure "NOME DO SISTEMA MCP server" no registro oficial (registry.modelcontextprotocol.io) e no GitHub. Prefira o do fornecedor. No Claude Code, instale com `claude mcp add`. |
| 3 | **Linha de comando ou API** | Muitos sistemas têm CLI oficial (`gh` para GitHub, `sf` para Salesforce, `m365` para Microsoft 365) ou API com chave. O Claude roda os comandos; a chave fica num arquivo de configuração da máquina, nunca na conversa. |
| 4 | **Exportação do próprio sistema** | Quase todo sistema exporta CSV, Excel, PDF ou um pacote dos seus dados. Exemplos: "Exportar conversa" no WhatsApp, "Baixar suas informações" no Instagram, relatório em Excel no ERP. Combine com a pessoa a frequência (todo dia, toda semana) e a pasta onde o arquivo vai cair. |
| 5 | **Navegador** | Com o Claude no Chrome, o Claude lê a página já aberta e logada pela pessoa (WhatsApp Web, o portal do fornecedor). Só leitura, e o login é sempre da pessoa. |
| 6 | **Colar ou mandar print** | O último recurso, e vale: melhor um canal colado uma vez por dia do que um ponto cego. |

Casos que sempre aparecem:

- **WhatsApp pessoal** não tem API oficial de leitura. Os caminhos seguros são o "Exportar conversa" e o WhatsApp Web pelo navegador. Uma biblioteca de terceiros conectada ao número pode levar o WhatsApp a bloquear a conta: avise antes, e só siga se a pessoa decidir assim. O WhatsApp Business tem API oficial (Cloud API), útil para quem atende cliente em volume.
- **Sistema interno ou antigo**, sem conector nem API: degrau 4. Um relatório exportado toda manhã resolve.
- **Dois e-mails ou dois números**: cada um é um canal no mapa.

## 3. Testar a leitura

Um canal só entra no mapa como ligado depois de uma leitura de verdade: "mostre as cinco últimas mensagens", "quais os três próximos eventos", "liste os negócios abertos". Se a leitura falhar, o canal fica como ponto cego, com o motivo e o próximo degrau a tentar.

## 4. Gravar o mapa

O mapa fica numa issue fixa da torre de controle, com o título `Mapa dos canais`. Uma linha por canal:

| Canal | Conta ou número | Degrau | Como ler | Desde quando ler | Situação |
|---|---|---|---|---|---|
| E-mail do trabalho | nome@empresa.com | 1, conector | conector de e-mail, caixa de entrada e enviados | 30 dias | ligado em 16/11 |
| WhatsApp | (41) 9xxxx-xxxx | 4, exportação | arquivo da pasta Downloads, toda manhã | 30 dias | ligado em 16/11 |
| ERP | | | | | ponto cego: sem exportação ainda |

A cada passada a ignição lê esta issue primeiro. Canal novo, troca de degrau e ponto cego resolvido entram como comentário com a data.

## 5. A primeira lista de assuntos

Com os canais ligados, a primeira passada olha para trás:

1. Ler cada canal nos últimos 30 dias. E-mail enviado também: é ali que estão as promessas da própria pessoa.
2. Juntar por assunto, nunca por mensagem. O e-mail, o WhatsApp e a reunião sobre o mesmo cliente são um assunto só.
3. Para cada assunto, uma issue pelo [modelo](modelo-de-issue.md): o que é, de onde veio, quem está esperando e o que foi prometido, com data.
4. Mostrar à pessoa a lista antes de gravar, agrupada por frente. Ela tira o que já acabou e junta o que está repetido.
5. Gravar as issues e chamar a skill `bunker-wsjf` para dar as notas.
6. Responder com quem está esperando, os cinco primeiros da fila e os pontos cegos que sobraram.

## Regras do mapa

- **Senha nunca vai para a conversa.** Login é pelo próprio conector, pela tela do fornecedor ou pela pessoa, no navegador dela. Chave de API fica em arquivo de configuração, fora da torre.
- **Só leitura no começo.** Ao ligar um conector, escolha a permissão de leitura quando houver a opção. Enviar, apagar e mover pedem o ok da pessoa em cada ação, como em todo o resto da ignição.
- **O mapa não guarda segredo.** Na issue vai o caminho ("conector de e-mail"), nunca token, senha ou chave.
- **Um canal por vez.** Liga, testa, grava, passa para o próximo. Dez conectores pela metade não servem para nada.
- **O mapa envelhece.** Uma vez por mês, ou quando a pessoa disser que algo não está aparecendo, refaça a pergunta do passo 1.
