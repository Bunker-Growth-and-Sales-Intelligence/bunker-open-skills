# O simulador

Um HTML só, `assets/simulador.html`, sem biblioteca. Os números entram num bloco JSON no fim da página:

```html
<script id="cenario" type="application/json"> ...o cenário... </script>
```

Troque só esse bloco. O resto da página (desenhos, campos editáveis e a conta) fica como está. A conta em JS é a mesma de `scripts/preco.py`, com o mesmo arredondamento, e os testes conferem as duas.

## O cenário

```json
{
 "titulo": "Queijo prato 500 g",
 "subtitulo": "Laticínio · Lucro Real",
 "unidade": "peça",
 "atividade": "industria",
 "rotulos": {"teto": "Teto", "canal": "Canal", "especifico": "Contrato"},
 "mc_teto": 50,
 "hipoteses": ["frete"],
 "custo_fixo_mes": 40000,
 "meta_lucro_pct": 10,
 "linhas": [
  {"nome": "Rede Y BA", "quantidade": 18000, "custo": 11.60,
   "impostos": {"ICMS": 7, "PIS": 1.65, "COFINS": 7.6},
   "comissao": 1.5, "comissao_sobre": "bruta",
   "frete_rs_kg": 4.0491, "peso_kg": 0.5, "frete_pct": 0, "frete_rs": 0,
   "outras_pct": 0, "outras_rs": 0,
   "mc_canal": 42, "preco_especifico": 25.90, "rotulo_especifico": "Contrato Rede Y",
   "desconto": 3, "preco_praticado": null, "preco_mercado": null, "custo_real": null,
   "por_fora": [{"nome": "IPI", "aliq": 9.75}],
   "hipoteses": ["comissao"]}
 ]
}
```

| Campo | O que é |
|---|---|
| `mc_teto` | margem planejada global, % da receita líquida gerencial. Pode vir na linha, para sobrepor. Sem teto e sem canal, a linha não tem meta: não preencha com a margem do preço de hoje. |
| `mc_canal` | margem do canal da linha. Sem ele, a linha não tem nível de canal. É a meta da linha quando existe. |
| `preco_especifico` ou `mc_especifica` | preço fechado ou margem própria do cliente. Para o pequeno comércio, o preço de hoje, com `rotulo_especifico: "Preço de hoje"`. |
| `desconto` | desconto do vendedor, % sobre o preço do nível usado. |
| `preco_praticado` | preço cobrado de fato; substitui o desconto. |
| `impostos` | impostos por dentro, % do preço, um por nome. |
| `comissao_sobre` | `bruta` (padrão) ou `liquida` (sobre o preço sem ICMS, PIS e Cofins). |
| `frete_rs_kg` e `peso_kg` | frete por rota e peso; somam em `frete_rs`. |
| `outras_pct` | cartão (taxa × parte no cartão), marketplace. |
| `por_fora` | IPI, ICMS-ST, CBS e IBS; `"base": "sem_icms_iss"` para CBS e IBS. |
| `preco_mercado` | preço do concorrente; o simulador mostra a maior margem que cabe nele. |
| `custo_fixo_mes`, `meta_lucro_pct` | outra conta: lucro depois do custo fixo, ponto de equilíbrio no mix de hoje e o preço de cada linha para a meta de lucro, com uma ou várias linhas. O fixo vai para cada linha pela parte dela na margem de contribuição do mês, e não por unidade; a linha que já cobre a sua parte fica no preço negociado, nunca abaixo. |
| `unidade` (na linha) | a unidade da linha quando ela difere da do cenário: `"mês de contrato"` numa, `"hora"` na outra. Linhas em unidades diferentes não se somam em unidade: o painel fala de cada uma e soma só em reais. |
| `hipoteses` | nomes marcados como hipótese: `custo`, `impostos`, `comissao`, `frete`, `outras`, `margem`, `desconto`, `volume`, `perda`. |
| `quantidade` | volume da linha no mês. O consolidado e os reais dos gráficos pesam por ele. |
| `quantidade_sem_desconto` | quanto a linha venderia sem o desconto ou a promoção. O simulador compara a margem do mês nos dois volumes. |
| `perda_pct` | perda (quebra, validade), % do que se compra. Entra no custo: custo ÷ (1 − perda), em 4 casas. |
| `rotulos.desconto` | nome do degrau do desconto: "Desconto do vendedor" por padrão; "Promoção", "Desconto do representante". |
| `regra_margem` | `"teto"` (padrão) ou `"piso"`. Piso é a margem MÍNIMA aceita (serviço com margem alta): tabela acima dela é o esperado, o aviso de "passa do teto" some, e o aviso passa a ser o de nível abaixo do piso. Pode vir na linha. |
| `moeda` (na linha) e `cambio` | preço em outra moeda: `"moeda": "USD"` na linha e `"cambio": {"USD": 5.2132}` no cenário. Vale para `preco_especifico`, `preco_praticado` e `preco_mercado`, convertidos em 2 casas; custo, frete e despesas em R$ ficam em reais. `cambio_fonte` diz de onde veio a taxa, e as premissas mostram o valor original e o convertido. |
| `despesas_fixas` | as despesas fixas do mês abertas por natureza, `[{"nome": "Despesas com pessoal e encargos", "valor": 38000}]`. Sem `custo_fixo_mes`, a soma delas é o custo fixo. |
| `receitas_financeiras`, `despesas_financeiras`, `irpj_csll_pct`, `regime` | o resto da DRE do mês: resultado financeiro em R$ no mês, separado em receitas e despesas, e IRPJ e CSLL. No Lucro Real (padrão), `irpj_csll_pct` é % do lucro antes deles e zera com prejuízo; com `"regime": "presumido"`, é % da receita bruta (8,54% num serviço com o adicional) e pesa mesmo com prejuízo. Sem `irpj_csll_pct`, a DRE para no lucro antes do IRPJ e da CSLL. |
| `cliente`, `fonte`, `porte`, `marca` | da entrega: o nome na capa, de onde vieram os números (rodapé), o degrau da escada (`pequeno`, `muitos_itens`, `grande`; sem ele, a skill estima) e a cor do cliente, `{"primaria": "#...", "secundaria": "#..."}`. |

**A meta.** A leitura principal é sempre contra a margem que o dono quer: `mc_especifica`, senão `mc_canal`, senão `mc_teto`. O preço de hoje e o preço fechado (`preco_especifico`) são nível usado, nunca meta. Sem meta, a página diz "sem meta" e não pinta de verde.

**Dois cenários ou mais.** Quando uma hipótese muda a conclusão, ou para 2026 e 2027, use `"cenarios": [{...}, {...}]`, cada um com `nome_cenario`. Cada cenário herda todos os campos de fora de `cenarios` (margens, hipóteses, rótulos, custo fixo e até `linhas`), e os campos dele mandam. A mesma regra roda no Python (`simulador.mesclar`) e no JS (`Motor.cenarios`), e o teste de paridade confere as duas. A página mostra um botão por cenário (uma lista no celular), os cenários lado a lado, e a DRE contábil do cenário escolhido.

## O que a página mostra

| Bloco | Pergunta |
|---|---|
| Barra de desempenho e cartões | Quanto da margem desejada a venda entrega? (contra a meta; sem meta, diz isso) |
| Composição do preço | Para onde vai o preço do nível? (a margem cedida hachurada; a margem que a meta pede, na legenda) |
| Cascata do preço | Como o preço se forma, por unidade? |
| Cascata dos níveis | Em qual nível a margem ficou na mesa? |
| Três leituras | Quanto a margem se afastou de cada régua? |
| Barras por grupo | Qual grupo entrega a meta? (duas linhas ou mais) |
| Dispersão com a diagonal | Onde o desconto pesa mais na margem? (duas linhas ou mais, e só quando há desconto) |
| Desconto que vende mais | O desconto compensa? (com `quantidade_sem_desconto`) |
| Lucro depois do custo fixo, outra conta | A margem do mês paga o custo fixo? Qual o preço para a meta de lucro? (com `custo_fixo_mes`) |
| Cenários lado a lado | 2026 contra 2027, com e sem benefício: margem, impostos e total da nota (dois cenários ou mais) |
| Raio-x | Como a conta fecha, centavo a centavo? |

Faixa de cor: mais de 70% da meta é verde; de 50 a 70, âmbar; abaixo de 50, ou margem negativa, vermelho; sem meta, neutro. A fonte dos números aparece uma vez, no rodapé. Conflito entre níveis (margem acima do teto, canal mais caro que a tabela de outro grupo) sai como aviso âmbar no topo; erro de conta, como aviso vermelho.

## A entrega: painel e PDF

Do mesmo cenário, `python3 scripts/entrega.py cenario.json --painel painel.html --pdf entrega.pdf` grava o painel (HTML autocontido, claro e escuro) e o PDF A4 do cliente. A conta é a de `simulador.calcular`; `--cenario 2` escolhe outro cenário do arquivo. O foco é o preço pelo qual cada produto deve ser vendido. A entrega, por ora, é a capa e as duas DREs, só as tabelas:

1. **DRE da venda**, por unidade: formação do preço e resultado da venda até a margem de contribuição, com os tributos abertos, os da reforma (CBS e IBS) inclusive, e a margem cedida. No painel, uma aba por produto; no PDF, o principal.
2. **DRE do mês**, orçado no preço teto contra realizado, até o lucro líquido quando há despesas fixas.

As duas DREs trazem três colunas de nome: como o Alumni chama a linha, como a skill chama e como o Pricing Designer grava. Onde o termo ainda não existe, o nome da skill sai em vermelho (a criar). No painel, cada nome é clicável e a escolha fica no navegador (`localStorage`), trocando o nome da primeira coluna.

No painel, todo número que é premissa se edita dentro da própria célula, sem mudar a altura da linha: custo, margem desejada, alíquotas, comissão, frete, descontos de campanha e tático em R$, volume, despesas fixas, receitas e despesas financeiras e IRPJ e CSLL. Editar recalcula as duas DREs e as conclusões no navegador (`assets/painel.js`, sobre o motor do simulador); o teste de paridade confere cada número contra o Python. Os gráficos seguem o cenário original e ficam esmaecidos enquanto há edição. O desvio sai com seta e cor que julga pelo sentido da linha: menos custo ou menos dedução é bom, menos receita ou menos margem é ruim. Tudo em 2 casas na tela; a conta roda em 4.

Preço teto é o primeiro nível da linha (com `regra_margem: "piso"`, a tabela acima do piso). Campanha é do preço teto ao nível usado; desconto tático, do nível usado ao negociado. O orçado é a mesma venda no preço teto, nas mesmas unidades. As hipóteses ficam no chat e no cenário, e não na entrega.

## Onde abre

1. **Claude com artefatos (claude.ai ou aplicativo).** Leia `assets/simulador.html`, troque o bloco `cenario` pelos números da conversa e crie um artefato HTML com a página inteira, com o JS como está.
2. **Terminal (Claude Code, Codex, qualquer agente que roda comando).** Grave o cenário em JSON e rode `python3 scripts/simulador.py cenario.json`. O script grava `cenario.html` e abre no navegador: `open` no macOS, `start` no Windows, `xdg-open` no Linux. `--nao-abrir` só grava. `preco.py --html arquivo.html` faz o mesmo a partir dos argumentos de linha de comando.
3. **Chat sem artefato e sem terminal.** Entregue a página com o bloco `cenario` preenchido, num bloco de código, e diga: "salve como preco.html e abra no navegador". Junto, o resumo em poucas linhas.
