# Bunker Open Skills

Skills gratuitas da [Bunker](https://bunkerconsultancy.com) para usar com a IA da sua preferência.

## bunker-pricing

Forma ou confere o preço de um produto ou serviço. Você conversa com a IA, responde umas doze perguntas curtas e recebe um simulador visual, num HTML só, que abre como artefato no Claude ou no seu navegador:

- o preço formado em três blocos: custo, margem sobre a receita líquida gerencial, e depois impostos, comissão e frete (a mesma conta do Pricing Designer);
- margem diferente por grupo de cliente, quando existe: teto, canal, preço de contrato ou rede, desconto do vendedor;
- a margem planejada contra a realizada, e o desvio contra o nível usado, o canal e o teto, em pontos, relativo e reais;
- campos editáveis: mexa no custo, nas margens, nos impostos, na comissão, no frete e no desconto, e tudo recalcula;
- o efeito da reforma tributária (CBS e IBS a partir de 2027), com as fontes oficiais;
- para entregar ao cliente, um painel editável e um PDF A4 com a marca da Bunker com as duas DREs: a da venda, do custo ao preço negociado, e a do mês, orçado contra realizado.

Serve para empresa de qualquer tamanho e para o contador dela. Não precisa de sistema nenhum.

Os números fiscais que a skill usa são hipótese até o seu contador confirmar.

### O que tem na pasta

```
skills/bunker-pricing/
  SKILL.md                          instruções da skill
  assets/simulador.html             o simulador, HTML, CSS, SVG e JS puro
  references/entrevista.md          roteiro de perguntas e hipóteses padrão
  references/niveis.md              teto, canal, específico, desconto e fatores por critério
  references/formulas.md            fórmulas, DRE e exemplos resolvidos
  references/impostos.md            regimes, benefícios por produto e alíquotas, com fontes
  references/reforma-tributaria.md  CBS e IBS, calendário e efeito no preço
  references/simulador.md           formato do cenário, as duas camadas da DRE e os três jeitos de abrir
  references/graficos.md            os blocos do painel, as regras de desenho, o PDF e as conferências
  scripts/preco.py                  a conta de uma linha, sem dependências
  scripts/simulador.py              a régua em níveis; grava e abre o simulador
  scripts/camadas.py                a DRE da venda e a DRE do mês
  scripts/entrega.py                o painel editável e o PDF A4 de entrega
  scripts/grafico/                  formas em SVG, página, marca, PDF e conferências
  assets/                           logos, o B em contorno e a fonte da casa, embutidos
  scripts/test_*.py                 exemplos, casos de borda e a conferência JS contra Python
exemplos/                           três simuladores prontos, com o cenário de cada um
```

## bunker-fix-bug

O rito da Bunker para consertar defeito em Salesforce, na ordem que impede engano:

1. perguntas de arquitetura e de regra de negócio antes de tudo;
2. o defeito escolhido por contagem, e a premissa da correção medida antes de escrever código;
3. um teste que fica vermelho no código de hoje, atacado até não passar por engano;
4. a correção, o verde, e o vermelho de novo quando a correção sai;
5. print do antes e do depois, na mesma cena, no perfil de quem sofria o defeito;
6. deploy com cobertura por classe, e a rodada completa outra vez.

A issue do GitHub é o diário: cada marco vira comentário na hora, e os rótulos dizem a prioridade (WSJF) e a etapa (`e0` a `e6`). Precisa do `gh` autenticado no repositório do projeto e do `sf` autenticado na org; nada vai para produção sem autorização de quem opera.

```
skills/bunker-fix-bug/
  SKILL.md                          o rito completo, com as regras e os casos que criaram cada uma
```

## Torre de controle: ignição, WSJF, confetes ou perguntas e grill me

De Guilherme Reis, com a Bunker. Quatro skills que trabalham juntas, para quem toca muitos assuntos ao mesmo tempo e quer que ninguém fique sem resposta:

- **bunker-ignicao**: a skill mãe. Lê os seus canais, garante que ninguém fique sem resposta, mantém um assunto por issue num repositório privado do GitHub, ordena a fila e despacha os cinco primeiros assuntos para conversas filhas. Ela própria só conversa, decide e delega.
- **bunker-wsjf**: dá as notas de cada issue (valor, urgência, risco e tamanho), grava as notas como etiquetas e mostra a fila em ordem.
- **bunker-confetes-ou-perguntas**: como o Claude termina cada resposta. Confete quando terminou, caixinha de múltipla escolha quando falta uma decisão sua.
- **bunker-grill-me**: antes de um trabalho grande, perguntas em rodadas de até quatro caixinhas, até não sobrar nada assumido em silêncio. É a versão em caixinhas da [grill-me de Matt Pocock](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling).

O que depende da sua rotina (canais, prazos de resposta, quem interrompe tudo, horários) está em `skills/bunker-ignicao/references/adaptar.md`, e a ignição pergunta o que faltar, uma pergunta por vez. A `bunker-ignicao` e a `bunker-wsjf` leem e gravam issues pelo terminal, então funcionam por inteiro no Claude Code, no terminal ou na aba Code do Claude Desktop. A `bunker-confetes-ou-perguntas` e a `bunker-grill-me` funcionam em qualquer lugar.

### Já tem skills suas? Peça para o Claude mesclar

Abra o Claude Code na pasta das suas skills e cole:

> Baixe as skills bunker-ignicao, bunker-wsjf, bunker-confetes-ou-perguntas e bunker-grill-me do repositório público github.com/Bunker-Growth-and-Sales-Intelligence/bunker-open-skills. Compare com as minhas skills, aproveite o que tem de melhor nelas e mescle com as minhas, sem apagar nada que é meu. Antes de gravar, me mostre o que muda em cada skill.

### Primeiros passos

1. Peça: "Crie um repositório privado no GitHub chamado torre-de-controle-seunome e clone dentro da minha pasta de trabalho." Se o Claude pedir login no GitHub, ele abre o navegador e mostra um código para colar.
2. Peça: "Leia tudo o que eu estou tocando nas minhas conversas abertas e transforme cada assunto numa issue nesse repositório, com todos os detalhes."
3. Abra uma conversa nova dentro da pasta da torre de controle e rode a ignição. Ela pergunta o que falta, uma pergunta por vez, e grava as respostas na própria skill.
4. Rode a `bunker-wsjf` para dar as notas. Confira os cinco primeiros. Se a ordem estiver errada, diga o porquê: é assim que a régua aprende o seu critério.
5. A partir daí, trabalhe pela ignição e feche as outras conversas sem medo.

### Como organizar as suas skills

- **Dois repositórios privados.** Um para a torre de controle, só com issues. Outro para as suas skills.
- **Uma pasta (plugin) por função.** Por exemplo: secretário, jurídico, financeiro. Dentro de cada uma ficam as skills das ações daquela função. Ponha um prefixo seu no nome, porque com o tempo você vai instalar plugins de outras pessoas.
- **Toda skill decide antes de fazer.** Primeiro ela vê se a tarefa é dela. Se for, faz e vê qual é o próximo passo. Se não for, passa para a skill certa ou devolve uma pergunta a você. Quando uma skill começa a fazer duas coisas bem diferentes, ela se divide em duas.
- **A conversa mãe fica livre.** A ignição só conversa, decide e despacha. O trabalho acontece nas conversas filhas, no máximo cinco abertas.
- **Feche tudo, várias vezes por dia.** Arquive as conversas: conversa arquivada ainda pode ser consultada, e o histórico de cada assunto está na issue.
- **Cada conversa ensina as skills.** Antes de encerrar, pergunte: "O que fica de ensinamento daqui para as minhas skills? O que você vai atualizar, e onde?"
- **Comando de terminal quem roda é o Claude.** Se ele pedir para você rodar, responda que ele mesmo execute.

### Segurança

- A torre de controle guarda nome de cliente, valores e decisões. Deixe sempre privada.
- A issue guarda onde achar a conversa (canal, data, id da mensagem), nunca o texto inteiro do WhatsApp ou do e-mail.
- Nenhuma destas skills envia mensagem sem o seu ok para aquela mensagem.

### O que tem na pasta

```
skills/bunker-ignicao/
  SKILL.md                          o ciclo da torre de controle, mãe e filhas, as regras
  references/adaptar.md             o que preencher com a sua rotina
  references/estados-e-fup.md       estados, cadência de follow-up e etiquetas
  references/modelo-de-issue.md     o modelo de issue e de comentário
skills/bunker-wsjf/
  SKILL.md                          a conta, as regras de toda nota e o passo do Claude
  references/regua.md               as âncoras de cada nota, os casos que confundem e as fases da venda
  scripts/fila.py                   cria as etiquetas, grava as notas e mostra a fila (só precisa do gh)
  scripts/test_fila.py              testes, sem rede
skills/bunker-confetes-ou-perguntas/
  SKILL.md                          como cada resposta termina
skills/bunker-grill-me/
  SKILL.md                          as rodadas de perguntas antes de começar
```

## Baixar

A versão mais recente de cada skill, pronta para instalar:

- [bunker-pricing.zip](https://github.com/Bunker-Growth-and-Sales-Intelligence/bunker-open-skills/releases/latest/download/bunker-pricing.zip)
- [bunker-pulse.zip](https://github.com/Bunker-Growth-and-Sales-Intelligence/bunker-open-skills/releases/latest/download/bunker-pulse.zip)
- [bunker-fix-bug.zip](https://github.com/Bunker-Growth-and-Sales-Intelligence/bunker-open-skills/releases/latest/download/bunker-fix-bug.zip)
- [bunker-ignicao.zip](https://github.com/Bunker-Growth-and-Sales-Intelligence/bunker-open-skills/releases/latest/download/bunker-ignicao.zip)
- [bunker-wsjf.zip](https://github.com/Bunker-Growth-and-Sales-Intelligence/bunker-open-skills/releases/latest/download/bunker-wsjf.zip)
- [bunker-confetes-ou-perguntas.zip](https://github.com/Bunker-Growth-and-Sales-Intelligence/bunker-open-skills/releases/latest/download/bunker-confetes-ou-perguntas.zip)
- [bunker-grill-me.zip](https://github.com/Bunker-Growth-and-Sales-Intelligence/bunker-open-skills/releases/latest/download/bunker-grill-me.zip)

Descompacte e siga o passo a passo da sua ferramenta abaixo. Os exemplos usam a `bunker-pricing`; para as outras, troque o nome da pasta.

## Instalação

### Claude Code, como plugin

O jeito mais fácil: instala todas as skills de uma vez e recebe as atualizações.

```
/plugin marketplace add Bunker-Growth-and-Sales-Intelligence/bunker-open-skills
/plugin install skills@bunker-open-skills
```

### Claude Code, copiando a pasta

Copie a pasta da skill para a pasta de skills do seu usuário:

```bash
mkdir -p ~/.claude/skills
cp -R skills/bunker-pricing ~/.claude/skills/
```

Para usar só num projeto, copie para `.claude/skills/` dentro do projeto. Depois é só pedir: "quero formar o preço do meu produto" ou "meu preço está certo?".

### Claude.ai (site e aplicativo)

1. Baixe o [bunker-pricing.zip](https://github.com/Bunker-Growth-and-Sales-Intelligence/bunker-open-skills/releases/latest/download/bunker-pricing.zip).
2. No Claude.ai, abra Configurações, procure a área de Skills (em Capacidades) e envie o `bunker-pricing.zip`. Com os artefatos ligados, o simulador abre como artefato na própria conversa.
3. Numa conversa nova, peça: "quanto devo cobrar pelo meu produto?".

Os nomes dos menus podem mudar. Se não achar, procure por "Skills" na ajuda do Claude.

### Codex

Copie a pasta para a pasta de skills do Codex:

```bash
mkdir -p ~/.codex/skills
cp -R skills/bunker-pricing ~/.codex/skills/
```

Se a sua versão do Codex não carregar skills, coloque no `AGENTS.md` do projeto uma linha pedindo para seguir `skills/bunker-pricing/SKILL.md` quando o assunto for preço.

### Qualquer IA de chat (ChatGPT, Gemini e outras)

1. Abra o `skills/bunker-pricing/SKILL.md`, copie o texto inteiro e cole no começo da conversa.
2. Na mesma mensagem, ou logo depois, cole também `references/formulas.md`. Se o assunto envolver imposto, cole `references/impostos.md`; se envolver 2027 em diante, `references/reforma-tributaria.md`.
3. Escreva: "Siga essas instruções. Quero formar o preço do meu produto."

Para não colar toda vez, use os recursos de instrução fixa da ferramenta (GPTs personalizados no ChatGPT, Gems no Gemini): cole o `SKILL.md` nas instruções e envie os arquivos de `references/` como conhecimento. Envie também `assets/simulador.html`: a IA devolve a página com os seus números, para salvar como `.html` e abrir no navegador.

A skill funciona sem o script. Nesse caso a IA faz a conta passo a passo, do jeito que está em `references/formulas.md`.

## O script

Precisa de Python 3.8 ou mais novo, sem instalar nada.

```bash
python3 skills/bunker-pricing/scripts/preco.py --help

# formar o preço
python3 skills/bunker-pricing/scripts/preco.py --custo 8.12 --impostos 13.25 --comissao 3 --frete 2.5 --outras 1 --margem 25

# comparar com a tabela de hoje e um desconto de 10%, e abrir o simulador no navegador
python3 skills/bunker-pricing/scripts/preco.py --custo 8.12 --impostos 13.25 --comissao 3 --frete 2.5 --outras 1 --margem 25 --preco-atual 13.20 --desconto 10 --html preco.html

# várias linhas, com teto, canal, contrato e desconto (formato em references/simulador.md)
python3 skills/bunker-pricing/scripts/simulador.py exemplos/industria.json

# auditar um preço que já existe, sem margem em mente
python3 skills/bunker-pricing/scripts/preco.py --custo 50 --imposto PIS=0.65 --imposto COFINS=3 --imposto ISS=5 --comissao 10 --preco-atual 180 --atividade servico
```

```bash
# o painel editável e o PDF A4 para o cliente (o PDF usa o Chrome da máquina)
python3 skills/bunker-pricing/scripts/entrega.py exemplos/industria.json --painel painel.html --pdf entrega.pdf
```

Sem Chrome, o `entrega.py` grava o HTML das folhas A4 para imprimir no navegador.

```bash
# conferir o painel: geometria, legibilidade, sobreposição, e as fotos em 1440 e 390
cd skills/bunker-pricing/scripts && python3 -m grafico.conferir ../../../painel.html --fotos fotos
```

Percentuais entram em pontos: `18` quer dizer 18%. A margem é em % da receita líquida gerencial.

O HTML abre sozinho no navegador (`open` no macOS, `start` no Windows, `xdg-open` no Linux). Para só gravar, use `--nao-abrir`.

Para conferir a conta com os exemplos de `references/formulas.md` e o JS do simulador contra o Python (este precisa de `node`):

```bash
python3 -m unittest discover -s skills/bunker-pricing/scripts
```

## Operação grande

Se você tem muitos itens, tabela de preço por canal ou por região, ou vendedores que dão desconto, a mesma conta precisa acontecer em cada linha de cada pedido. O Pricing Designer da Bunker faz isso dentro do Salesforce. Conheça em https://bunkerconsultancy.com.
