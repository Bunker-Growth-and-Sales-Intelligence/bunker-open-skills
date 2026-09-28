# Skills públicas da Bunker

Skills gratuitas da [Bunker](https://bunkerconsultancy.com) para usar com a IA da sua preferência.

## bunker-pricing

Forma ou confere o preço de um produto ou serviço. Você conversa com a IA, responde umas doze perguntas curtas e recebe um simulador visual, num HTML só, que abre como artefato no Claude ou no seu navegador:

- o preço formado em três blocos: custo, margem sobre a receita líquida, e depois impostos, comissão e frete (a mesma conta do Pricing Designer);
- margem diferente por grupo de cliente, quando existe: teto, canal, preço de contrato ou rede, desconto do vendedor;
- a margem planejada contra a realizada, e o desvio contra o nível usado, o canal e o teto, em pontos, relativo e reais;
- a composição do preço numa barra só, com a margem cedida no desconto hachurada;
- campos editáveis: mexa no custo, nas margens, nos impostos, na comissão, no frete e no desconto, e tudo recalcula;
- o efeito da reforma tributária (CBS e IBS a partir de 2027), com as fontes oficiais.

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
  references/simulador.md           formato do cenário e os três jeitos de abrir
  scripts/preco.py                  a conta de uma linha, sem dependências
  scripts/simulador.py              a régua em níveis; grava e abre o simulador
  scripts/test_*.py                 exemplos, casos de borda e a conferência JS contra Python
exemplos/                           três simuladores prontos, com o cenário de cada um
```

## Baixar

A versão mais recente, pronta para instalar:
[bunker-pricing.zip](https://github.com/Bunker-Growth-and-Sales-Intelligence/bunker-skills/releases/latest/download/bunker-pricing.zip).
Descompacte e siga o passo a passo da sua ferramenta abaixo.

## Instalação

### Claude Code

Copie a pasta da skill para a pasta de skills do seu usuário:

```bash
mkdir -p ~/.claude/skills
cp -R skills/bunker-pricing ~/.claude/skills/
```

Para usar só num projeto, copie para `.claude/skills/` dentro do projeto. Depois é só pedir: "quero formar o preço do meu produto" ou "meu preço está certo?".

### Claude.ai (site e aplicativo)

1. Baixe o [bunker-pricing.zip](https://github.com/Bunker-Growth-and-Sales-Intelligence/bunker-skills/releases/latest/download/bunker-pricing.zip).
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

Percentuais entram em pontos: `18` quer dizer 18%. A margem é em % da receita líquida.

O HTML abre sozinho no navegador (`open` no macOS, `start` no Windows, `xdg-open` no Linux). Para só gravar, use `--nao-abrir`.

Para conferir a conta com os exemplos de `references/formulas.md` e o JS do simulador contra o Python (este precisa de `node`):

```bash
python3 -m unittest discover -s skills/bunker-pricing/scripts
```

## Operação grande

Se você tem muitos itens, tabela de preço por canal ou por região, ou vendedores que dão desconto, a mesma conta precisa acontecer em cada linha de cada pedido. O Pricing Designer da Bunker faz isso dentro do Salesforce. Conheça em https://bunkerconsultancy.com.
