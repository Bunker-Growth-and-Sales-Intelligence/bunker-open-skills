# Fórmulas, DRE da linha e casos de borda

Impostos, comissão e frete em % entram em % do preço de venda (a receita bruta da linha). Frete e outras despesas em reais entram em R$ por unidade. A margem planejada entra em % da **receita líquida gerencial**. Esta página explica por quê e mostra a conta inteira. É a fórmula em três blocos do Pricing Designer: custo, margem, e depois impostos, comissão e frete.

## 1. Os termos

| Termo | O que é, em uma frase |
|---|---|
| Receita bruta | O valor da venda, já com o desconto dado na nota, sem os tributos cobrados por fora (IPI, ICMS-ST, CBS e IBS). |
| Deduções da receita bruta | Os impostos sobre a venda, que vêm dentro do preço: ICMS, ISS, PIS, Cofins, ou o DAS do Simples. |
| Receita líquida contábil | Receita bruta menos as deduções. É a receita líquida da DRE societária, a que o contador fecha. |
| Despesas variáveis de venda | Comissão, frete de entrega, taxa de cartão, taxa de marketplace. Só existem porque a venda aconteceu. |
| Receita líquida gerencial | Receita bruta menos as deduções e as despesas variáveis de venda. É o que sobra do preço para pagar o custo e deixar margem. É a base em que a margem é planejada, a mesma do nível 0 do Pricing Designer. |
| Custo do que foi vendido | Custo da mercadoria vendida (CMV) no comércio, do produto vendido (CPV) na indústria, do serviço prestado (CSP) em serviço. Sempre líquido dos créditos de imposto que a empresa recupera. |
| Margem de contribuição | Receita líquida gerencial menos o custo do que foi vendido. É o que a venda deixa para pagar as despesas fixas, o IRPJ e a CSLL, e o lucro. Não é lucro. |
| Margem planejada, ou meta | A margem que a pessoa quer, em % da receita líquida gerencial: a do canal, quando existe, senão a do teto. É com ela que o preço é formado. Preço de hoje e preço fechado não são meta: a margem que eles deixam é medida contra a meta. No preço formado, a margem medida fica a centésimos da meta por causa do arredondamento do preço. |
| Margem realizada | A margem de contribuição no preço que foi cobrado de fato, com os custos reais. |
| Desvio | Realizada menos planejada: em pontos percentuais (p.p.), relativo e em reais. |
| Deixado na mesa | Margem em R$ da mesma venda no preço do primeiro nível (o teto, ou o formado) menos a margem em R$ realizada. Não confundir com o desvio em R$, que é pontos × receita líquida gerencial realizada e dá outro número. |

### Margem bruta, margem líquida, margem de contribuição e markup

As quatro palavras aparecem juntas na conversa e querem dizer coisas diferentes. A skill trabalha com a margem de contribuição; as outras são da DRE contábil, e o contador usa.

| Termo | Conta | Base | A skill usa? |
|---|---|---|---|
| Margem bruta | Lucro bruto ÷ receita líquida contábil. Lucro bruto = receita líquida contábil − CMV, CPV ou CSP. | receita líquida contábil | Não. É da DRE contábil. |
| Margem líquida | Lucro líquido ÷ receita líquida contábil. Lucro líquido é o que sobra depois das despesas fixas, juros, depreciação, IRPJ e CSLL. | receita líquida contábil | Não. Ela só existe depois do custo fixo e dos tributos sobre o lucro. |
| Margem de contribuição | Receita líquida gerencial − custo do que foi vendido. Em % da receita líquida gerencial (a base da meta) e em % da receita bruta, as duas rotuladas. | receita líquida gerencial | Sim. É o centro da conta. Não é lucro. |
| Markup divisor | (1 − margem %) × (1 − despesas variáveis %). Preço = custo ÷ markup divisor, quando não há frete ou despesa em R$. | preço | Sim, é a mesma conta dos três blocos escrita de outro jeito. |
| Markup multiplicador | 1 ÷ markup divisor. Preço = custo × markup multiplicador, quando não há frete ou despesa em R$. | custo | Sim, com a mesma ressalva. |

Custo × (1 + margem) não é nenhum dos dois markups: põe a margem em cima do custo e deixa imposto, comissão e frete comerem a margem por dentro (exemplo 1, seção 8). No queijo do exemplo 1, markup divisor = 0,75 × 0,8025 = 0,601875; multiplicador = 1,6615; 8,12 × 1,6615 = R$ 13,49, o mesmo preço formado.

**Nota para o contador.** A margem é medida em duas bases, e a DRE mostra as duas, rotuladas:

- **% da receita líquida gerencial**: é a base da meta, depois das deduções e das despesas variáveis de venda. A receita líquida contábil, só depois das deduções, aparece numa linha própria, acima.
- **% da receita bruta**: a mesma margem em reais, dividida pelo preço. Serve para comparar com relatórios que medem tudo sobre o faturamento.

As duas se relacionam assim: margem % da receita bruta = margem % da receita líquida gerencial × receita líquida gerencial ÷ receita bruta.

Na DRE societária o desconto incondicional é dedução da receita bruta (Decreto-Lei 1.598/1977, art. 12, § 1º). Aqui a receita bruta da coluna Realizado já vem com o desconto, para a margem ser medida sobre o que foi faturado. A reclassificação não muda a margem em reais. Os tributos por fora ficam fora da receita bruta, como manda o § 4º do mesmo artigo. Margem de contribuição é conceito gerencial e não é linha da DRE da Lei 6.404/1976, art. 187.

## 2. Formação do preço

```
Bloco 1  Custo
Bloco 2  Preço base = Custo ÷ (1 − margem planejada %)
         (+) frete e outras despesas em R$ por unidade, somados depois da margem
Bloco 3  Preço = (Preço base + despesas em R$) ÷ (1 − (impostos por dentro % + comissão % + frete % + outras %))
```

O preço base é a receita líquida gerencial que a venda precisa deixar. Frete em R$ entra somado a ele. Frete em % entra no divisor, junto com impostos e comissão.

Arredonde o preço em 2 casas (arredondamento comercial: 5 ou mais sobe).

"Despesas variáveis em R$" é o frete ou outra despesa que a pessoa informou em reais por unidade, e não em %. Ela sai do preço junto com as despesas em %, então entra no numerador do segundo passo, e não no custo.

Comissão sobre o preço sem ICMS, PIS e Cofins, em vez da receita bruta: use comissão % × (1 − impostos por dentro %) na soma das despesas variáveis. Atenção à palavra "sem impostos": numa indústria ela quase sempre quer dizer sem IPI, e o preço sem IPI já é a receita bruta. Nesse caso a comissão é sobre a receita bruta.

**Por que a conta confere.** No preço formado, a receita líquida gerencial é preço × (1 − despesas variáveis %) − despesas em R$ = Custo ÷ (1 − margem). A margem sobre ela é 1 − Custo ÷ receita líquida gerencial = margem planejada, exata, antes do arredondamento do preço. É a identidade que os testes conferem: vendendo no preço formado sem desconto, a margem realizada é igual à planejada.

**A mesma identidade audita qualquer preço.** Num preço P qualquer:

```
Margem sobre a receita líquida gerencial = 1 − Custo ÷ (P × (1 − despesas variáveis %) − despesas variáveis em R$)
```

É a conta que dá a margem planejada no preço formado, a margem de um preço de tabela, a de um preço de mercado e a realizada.

### As três possibilidades da planilha

A planilha de conceitos de precificação da Bunker testa três jeitos de chegar ao preço. Com custo R$ 8,12, impostos de 13,25% e margem de 46,25%:

| Jeito | Fórmula | Preço | Margem sobre a receita líquida gerencial | Margem sobre a receita bruta |
|---|---|---:|---:|---:|
| 1. Somar tudo ao custo | Custo × (1 + margem % + despesas %) | R$ 12,95 | 27,72% | 24,05% |
| 2. Divisor único | Custo ÷ (1 − (margem % + despesas %)) | R$ 20,05 | 53,32% | 46,25% |
| 3. Divisor em duas etapas | (Custo ÷ (1 − margem %)) ÷ (1 − despesas %) | R$ 17,41 | 46,24% | 40,11% |

A skill usa a **possibilidade 3**, pelos motivos abaixo.

- É a única que entrega a margem planejada sobre a receita líquida gerencial, que é o dinheiro que fica com a empresa depois de pagar imposto, comissão e frete. A 1 entrega menos. A 2 entrega a margem sobre a receita bruta e, sobre a líquida, mais do que foi pedido, o que encarece o preço.
- A meta não muda quando o imposto ou a comissão mudam. Custo e margem decidem quanto a venda precisa deixar; imposto, comissão e frete só dizem quanto o preço precisa subir para deixar isso.
- Só existe preço impossível quando a margem chega a 100% ou quando as despesas variáveis sozinhas chegam a 100%. Na possibilidade 2, uma margem de 80% com 25% de despesas já dava preço impossível.
- É a conta do nível 0 do Pricing Designer. Quem usa a skill e depois o produto vê o mesmo número.

Os 46,24% da possibilidade 3 ficam a um centésimo dos 46,25% porque o preço foi arredondado para R$ 17,41.

**Por que o multiplicador falha.** Custo × (1 + margem) põe a margem em cima do custo. Imposto, comissão e frete são cobrados sobre o preço e saem dessa margem. Mostre sempre com o número do caso da pessoa (exemplo 1).

## 3. DRE da linha

Para uma quantidade Q no preço P:

```
Receita bruta (RB)                       = P × Q                                  → 4 casas
(−) Deduções da receita bruta            = soma de (RB × alíquota), cada uma em 4 casas
(=) Receita líquida contábil             = RB − deduções                          (subtração exata)
(−) Comissão                             = RB × comissão %                        → 4 casas
(−) Frete de entrega                     = RB × frete % + frete em R$ × Q         → 4 casas
(−) Outras despesas variáveis de venda   = RB × outras % + outras em R$ × Q       → 4 casas
(=) Receita líquida gerencial (RL)       = receita líquida contábil − despesas    (subtração exata)
(−) Custo do que foi vendido             = custo unitário × Q                     → 4 casas
(=) Margem de contribuição (MC)          = RL − custo                             (subtração exata)
    MC em % da receita líquida gerencial = MC ÷ RL × 100                          ← base da meta
    MC em % da receita bruta             = MC ÷ RB × 100
Tributos por fora (IPI, ICMS-ST)         = base × alíquota                        → 4 casas
Total da nota                            = RB + tributos por fora
```

Use o nome da linha de custo que vale para a atividade: CMV, CPV ou CSP. Linha de despesa que é zero em todas as colunas pode sair da tabela (frete num serviço, por exemplo).

**Duas escalas.** O preço arredonda em 2 casas, porque ninguém cobra R$ 13,4912. A leitura da DRE vai com 4 casas. Com 2 casas, cada parcela perde um pedaço diferente no arredondamento, e a receita bruta menos as deduções deixa de bater com a receita líquida contábil por um centavo. Quem confere vê essa diferença antes de qualquer outra coisa.

**Conferência obrigatória antes de mostrar:**

1. RB − deduções = receita líquida contábil, exato.
2. Receita líquida contábil − despesas variáveis de venda = RL, exato.
3. RL − custo = MC, exato.
4. A soma dos impostos separados é igual ao total das deduções, e a soma das despesas separadas é igual ao total das despesas.
5. No preço formado, a MC em % da receita líquida gerencial fica a centésimos da margem planejada.

**Hipótese na tabela.** Toda linha que usa número estimado leva a palavra "hipótese" ao lado do rótulo, na tabela e no texto.

## 4. Planejado, tabela, realizado e desconto

São até três colunas:

| Coluna | Preço | Para que serve |
|---|---|---|
| Planejado | O preço formado com a margem planejada | A referência da meta. |
| Tabela | O preço que a pessoa cobra hoje, antes do desconto | Mostra se a tabela já está abaixo ou acima do formado. |
| Realizado | Tabela × (1 − desconto %), ou o preço cobrado de fato, com os custos reais | O que aconteceu na venda. |

Sem margem planejada, a conta fica só na auditoria do preço de hoje. A margem da tabela é então a margem implícita nela.

```
Preço com desconto = preço de tabela × (1 − desconto % ÷ 100)   → 2 casas
Desvio em pontos   = margem % realizada − margem % de referência, sobre a receita líquida gerencial
Desvio relativo    = margem % realizada ÷ margem % de referência − 1
Desvio em R$       = receita líquida gerencial realizada × desvio em pontos ÷ 100
```

As referências são duas: a margem planejada e, quando há tabela, a margem implícita no preço de tabela. O desvio contra a tabela é o custo do desconto do vendedor. É a mesma leitura do Pricing Designer: desvio contra o nível usado e contra o teto.

Separe os efeitos, cada um contra a sua referência:

1. **Efeito da tabela**: margem na tabela − margem planejada. Mostra quanto a tabela já deixa na mesa antes de qualquer desconto.
2. **Efeito do desconto**: medido contra a tabela, com o custo planejado.
   ```
   Saída da margem por causa do desconto = desconto em R$ × (1 − despesas variáveis % ÷ 100)
   Parte do desconto que deixou de ir para imposto, comissão e frete = desconto em R$ − saída da margem
   ```
   Sem preço de tabela, o desconto é medido contra o preço formado.
3. **Efeito do custo**: DRE no preço realizado com o custo real − DRE no mesmo preço com o custo planejado.

A soma dos três dá o que ficou na mesa: margem em R$ no preço formado menos margem em R$ realizada.

**Preço cobrado acima da referência.** A mesma conta vale ao contrário: a receita subiu, e a parte do acréscimo que "entrou na margem" é acréscimo em R$ × (1 − despesas variáveis %). O resto foi para imposto, comissão e frete, que sobem junto com o preço. Nunca escreva "caiu" nem "desconto" nesse caso.

**Abaixo do custo real.** Se a margem de contribuição de uma coluna fica negativa, cada venda nesse preço tira dinheiro do caixa. Mostre o preço mínimo, que é o preço formado com margem zero: (custo + despesas em R$) ÷ (1 − despesas variáveis %).

**Deixado na mesa.** Margem em R$ no preço do primeiro nível − margem realizada em R$, por unidade ou na quantidade informada. O simulador mostra esse número na cascata dos níveis; o desvio em R$ das três leituras é outra conta, rotulada "na receita realizada".

## 5. Casos de borda

**Despesas variáveis de 100% ou mais.** Impostos, comissão, frete e outras levam o preço inteiro, e nenhum preço sobra para pagar o custo. Nem com margem zero existe preço. Faça assim:

1. Mostre a soma e liste os percentuais do maior para o menor.
2. Diga quantos pontos a soma precisa cair (mais que soma − 100) e explique que perto de 100% o preço cresce sem limite.
3. Diga que o corte tem que vir de imposto, comissão ou frete. Muitas vezes é alíquota lançada errada.

**Margem planejada de 100% ou mais.** Margem de 100% sobre a receita líquida gerencial quer dizer custo zero. Peça uma margem menor e mostre o preço com algumas margens abaixo de 100%.

**Preço de mercado.** Com um preço de mercado P, a maior margem que cabe nele é a identidade da seção 2: 1 − Custo ÷ (P × (1 − despesas variáveis %) − despesas em R$).

**Receita bruta ou receita líquida gerencial zero ou negativa.** Mostre os valores em reais e não calcule a margem em %. Não há base para dividir, e um percentual nesse caso engana. Quase sempre é preço zerado, devolução ou alíquota errada.

**Margem de contribuição negativa com receita positiva.** Calcule normalmente e diga com clareza: cada unidade vendida nesse preço tira dinheiro do caixa. Com margem negativa não existe ponto de equilíbrio: vender mais aumenta o buraco. Mostre o preço mínimo e pare aí.

**Perda.** Perda (quebra, validade) entra no custo, sobre o custo: custo com perda = custo ÷ (1 − perda %). Com 2% de perda, cada unidade vendida carrega o custo de 1 ÷ 0,98 unidades compradas.

**Cartão só numa parte das vendas.** Outras despesas % = taxa da maquininha × parte das vendas no cartão. Taxa de 3,5% com 60% no cartão = 2,1%.

**Mesma UF e outra UF.** São duas linhas, uma por rota, cada uma com o seu ICMS. O simulador mostra as duas e o consolidado.

## 6. Níveis, leituras e consolidado

Detalhe em `niveis.md`. Em resumo, para cada linha:

```
preço do teto   = formar(margem do teto)
preço do canal  = formar(margem do canal)
preço específico = preço fechado, ou formar(margem própria)
nível usado     = o mais específico que existir
negociado       = preço do nível usado × (1 − desconto)   → 2 casas
margem planejada do específico fechado = margem máxima no preço dele (seção 2)
desvio contra a régua k = margem realizada − margem de k, em pontos (4 casas), relativo e em reais
```

Linha sem canal usa o teto como canal. No consolidado de várias linhas:

```
margem realizada = Σ margem R$ ÷ Σ receita líquida gerencial
margem planejada da régua k = Σ (receita líquida gerencial da linha × margem de k da linha) ÷ Σ receita líquida gerencial
desvio em reais = Σ receita líquida gerencial × pontos ÷ 100
```

A cascata dos níveis soma a mesma venda no preço de cada nível (linha sem o nível entra com o preço do nível de cima). O degrau é a diferença de margem, ou de receita, entre um nível e o seguinte.

## 7. Outra conta: custo fixo e lucro depois dele

Fora da margem de contribuição, rotulada como outra conta:

```
lucro do mês            = margem do mês − custo fixo do mês
receita de equilíbrio   = custo fixo ÷ (margem ÷ receita bruta)            → 2 casas
ponto de equilíbrio     = custo fixo ÷ (margem do mês ÷ volume do mês)     (só com margem positiva)
preço para lucro de L%  = (custo + despesas em R$ + custo fixo ÷ volume do mês) ÷ (1 − despesas variáveis % − L%)
```

"20% limpo depois de tudo" é o L da última linha, em % do preço, no volume do mês. IRPJ e CSLL ainda saem desse lucro.

**Com várias linhas**, o volume do mês é a soma das linhas, na mesma unidade, e o ponto de equilíbrio é no mix de hoje. O preço para a meta de lucro sai por linha, com o custo fixo repartido por unidade vendida: cada linha no seu preço deixa L% da própria receita, e a soma deixa L% da receita do mês. Rotule sempre como "lucro depois do custo fixo, outra conta".

**Desconto que vende mais.** Quando a pessoa diz que o desconto ou a promoção vende mais, compare a margem do mês: no preço com desconto e no volume que ele traz, contra o preço sem desconto e o volume de antes. Na promoção do arroz, 90 pacotes a R$ 26,90 deixam R$ 196 de margem; 30 pacotes a R$ 29,12 deixariam R$ 126. A promoção compensa.

## 8. Exemplos resolvidos

Todos foram conferidos com `scripts/preco.py` e estão nos testes.

Queijo de 500 g, comércio. Custo R$ 8,12. Impostos por dentro 13,25%. Comissão 3%. Frete 2,5%. Taxa de cartão 1%. Margem planejada 25% da receita líquida gerencial. Despesas variáveis = 13,25 + 3 + 2,5 + 1 = 19,75%.

### Exemplo 1: formação normal

1. Receita líquida necessária = 8,12 ÷ (1 − 0,25) = 8,12 ÷ 0,75 = R$ 10,8267.
2. Preço = 10,8267 ÷ (1 − 0,1975) = 10,8267 ÷ 0,8025 = 13,4912 → **R$ 13,49**.

| Linha | R$ | % da RB |
|---|---:|---:|
| Receita bruta | 13,4900 | 100,00% |
| (−) Deduções da receita bruta | 1,7874 | 13,25% |
| (=) Receita líquida contábil | 11,7026 | 86,75% |
| (−) Comissão | 0,4047 | 3,00% |
| (−) Frete de entrega | 0,3373 | 2,50% |
| (−) Outras despesas variáveis de venda | 0,1349 | 1,00% |
| (=) Receita líquida gerencial | 10,8257 | 80,25% |
| (−) Custo da mercadoria vendida (CMV) | 8,1200 | 60,19% |
| (=) Margem de contribuição | 2,7057 | 20,06% |
| Margem em % da receita líquida gerencial | | **24,99%** |
| Margem em % da receita bruta | | 20,06% |

A margem sobre a receita líquida gerencial fica em 24,99% porque o preço foi arredondado para baixo. Sobre a receita bruta, os mesmos R$ 2,7057 são 20,06%.

Pelo multiplicador: 8,12 × 1,25 = R$ 10,15. Nesse preço a margem de contribuição é R$ 0,0253, ou **0,31% da receita líquida gerencial**. A pessoa acharia que ganha 25% e ganharia quase nada.

### Exemplo 2: tabela abaixo do formado, e desconto em cima da tabela

A pessoa cobra R$ 13,20 de tabela e dá 10% de desconto: 13,20 × 0,90 = **R$ 11,88**.

| Linha | Planejado | Tabela | Realizado |
|---|---:|---:|---:|
| Preço | 13,49 | 13,20 | 11,88 |
| Receita bruta | 13,4900 | 13,2000 | 11,8800 |
| (−) Deduções da receita bruta | 1,7874 | 1,7490 | 1,5741 |
| (=) Receita líquida contábil | 11,7026 | 11,4510 | 10,3059 |
| (−) Comissão | 0,4047 | 0,3960 | 0,3564 |
| (−) Frete de entrega | 0,3373 | 0,3300 | 0,2970 |
| (−) Outras despesas variáveis de venda | 0,1349 | 0,1320 | 0,1188 |
| (=) Receita líquida gerencial | 10,8257 | 10,5930 | 9,5337 |
| (−) CMV | 8,1200 | 8,1200 | 8,1200 |
| (=) Margem de contribuição | 2,7057 | 2,4730 | 1,4137 |
| % da receita líquida gerencial | 24,99% | 23,35% | 14,83% |
| % da receita bruta | 20,06% | 18,73% | 11,90% |

- **Efeito da tabela**: a tabela está R$ 0,29 abaixo do formado e já tira R$ 0,2327 da margem (−1,65 p.p. sobre a receita líquida gerencial).
- **Efeito do desconto**, contra a tabela: R$ 1,32 de desconto. Desses, 1,32 × (1 − 0,1975) = **R$ 1,0593** saíram da margem, e só R$ 0,2607 deixaram de ir para imposto, comissão e frete (−8,52 p.p.). Um desconto de 10% no preço levou 43% da margem da tabela.
- **Desvio**: contra a planejada de 25%, −10,17 p.p., −40,69% relativo, −R$ 0,9697 (9,5337 × −10,17 ÷ 100). Contra a margem implícita da tabela, 23,3456%: −8,52 p.p.
- **Deixado na mesa**: R$ 1,2920 por peça, que é 0,2327 + 1,0593.

### Exemplo 3: preço cobrado acima do formado

A pessoa cobra R$ 15,90, sem desconto.

| Linha | Planejado | Realizado |
|---|---:|---:|
| Receita bruta | 13,4900 | 15,9000 |
| (−) Deduções da receita bruta | 1,7874 | 2,1068 |
| (=) Receita líquida contábil | 11,7026 | 13,7932 |
| (−) Despesas variáveis de venda | 0,8769 | 1,0335 |
| (=) Receita líquida gerencial | 10,8257 | 12,7597 |
| (−) CMV | 8,1200 | 8,1200 |
| (=) Margem de contribuição | 2,7057 | 4,6397 |
| % da receita líquida gerencial | 24,99% | 36,36% |
| % da receita bruta | 20,06% | 29,18% |

O preço ficou R$ 2,41 acima do formado. Desse acréscimo, 2,41 × 0,8025 = R$ 1,9340 entraram na margem, e R$ 0,4760 foram para imposto, comissão e frete. Desvio contra a planejada: +11,36 p.p., +45,45% relativo, +R$ 1,4498. Aqui a pergunta certa passa a ser se o mercado aceita esse preço.

### Exemplo 4: frete em reais, preço de contrato e desconto (prova A do Pricing Designer)

Custo R$ 11,60. Margem planejada 50%. ICMS 12%. Sem comissão. Frete de R$ 1,7776 por kg × 0,12 kg = R$ 0,2133 por caixa. A pessoa vende a R$ 23,00 de contrato, com 2% de desconto.

1. Preço base = 11,60 ÷ 0,50 = R$ 23,20.
2. Preço = (23,20 + 0,2133) ÷ (1 − 0,12) = 23,4133 ÷ 0,88 = **R$ 26,61**. Com margem de 45%, o mesmo cálculo dá R$ 24,21.
3. Negociado = 23,00 × 0,98 = **R$ 22,54**.
4. Receita líquida gerencial = 22,54 − 2,7048 de ICMS − 0,2133 de frete = R$ 19,6219. Sobra = 19,6219 − 11,60 = R$ 8,0219. Margem realizada = 8,0219 ÷ 19,6219 = **40,8824%**.
5. Margem implícita no contrato: no preço de 23,00, 1 − 11,60 ÷ (23,00 × 0,88 − 0,2133) = 42,0773%. Desvio contra ela: −1,1949 p.p., −R$ 0,2345. Contra a margem de 45%: −4,12 p.p. Contra a planejada de 50%: −9,12 p.p.

São os números que o Pricing Designer grava na linha do pedido para o mesmo caso.
