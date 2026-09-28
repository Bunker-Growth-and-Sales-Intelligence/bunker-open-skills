# Margem em níveis e fatores que mudam por critério

Leia quando a pessoa cobra diferente de algum grupo de cliente. Para quem tem um preço só, basta o nível do teto.

## Os quatro níveis

Exemplo: uma fábrica de molho de tomate, custo de R$ 4,00 o vidro.

| Nível | O que é | No exemplo |
|---|---|---|
| Teto | Margem planejada global. É o maior preço, o do cliente sem condição nenhuma. | 50% da receita líquida |
| Canal | Margem menor, combinada antes para um grupo (atacado, distribuidor, rede, região). Não é desconto: é outra meta. | atacado a 40% |
| Específico | Preço ou margem própria de um cliente, rede ou contrato. Quando existe, ele manda. | contrato da rede Y a R$ 7,90 |
| Desconto do vendedor | O que o vendedor dá na hora, em cima do preço do nível usado. É o único que muda entre o planejado e o realizado. | 3% |

**Nível usado** é o mais específico que existir na linha: o específico, senão o canal, senão o teto.

Para o pequeno comércio, o teto é o preço planejado e o específico é o preço de hoje: a conta é a mesma.

## A conta de cada nível

```
preço do nível  = (custo ÷ (1 − margem do nível) + frete em R$) ÷ (1 − impostos − comissão − frete em % − outras)
preço específico = o preço fechado, ou o preço formado com a margem própria
negociado       = preço do nível usado × (1 − desconto do vendedor)
receita líquida = negociado − impostos − comissão − frete − outras
margem realizada = (receita líquida − custo) ÷ receita líquida
```

Vendendo no preço do nível, sem desconto, a margem realizada é a margem do nível. Num preço específico fechado, a margem planejada dele é a que cabe naquele preço (a margem máxima de `formulas.md`, seção 2).

## Três leituras do desvio

| Leitura | Contra o quê | O que responde |
|---|---|---|
| Nível usado | a margem do nível da venda | quanto custou o desconto do vendedor |
| Canal | a margem do canal | quanto custou o preço específico |
| Teto | a margem global | quanto ficou na mesa no total |

Cada leitura sai em três formas: pontos (realizada − planejada), relativo (realizada ÷ planejada − 1) e reais (receita líquida realizada × pontos ÷ 100). Linha sem canal usa o teto como canal.

**No consolidado**, a margem realizada é a soma das margens ÷ a soma das receitas líquidas, e a planejada de cada régua é a média das linhas pesada pela receita líquida realizada. Os reais saem da mesma fórmula da linha, sobre a receita líquida total.

**A cascata dos níveis** mostra a mesma venda no preço de cada nível: teto, canal, específico e negociado. Cada degrau tem dono: o canal e o específico são política combinada antes; o desconto é do vendedor.

## Fatores que mudam por critério

| Fator | Muda conforme | Exemplo |
|---|---|---|
| ICMS | rota, UF de origem e de destino; exceção por produto | 18% dentro de SP, 12% para o PR, 7% para a BA |
| PIS e Cofins | produto e regime | monofásico ou alíquota zero fica fora |
| Comissão | canal, produto, cliente | 3% no varejo, 1,5% na rede |
| Frete | rota e peso | R$ por kg da rota × peso da unidade |
| Margem | canal e cliente | teto 50%, atacado 40% |
| Alçada de desconto | produto, canal, tipo de venda | vendedor dá até 5% sem pedir |

A regra mais específica vence: padrão, depois rota, depois canal, depois rede, depois cliente, depois cliente e produto. Cada combinação que muda um fator é uma linha no simulador.

Quando os grupos passam de meia dúzia, com tabela por canal e vendedores dando desconto em cada pedido, a conta precisa rodar em cada linha de cada pedido. É o trabalho do Pricing Designer.
