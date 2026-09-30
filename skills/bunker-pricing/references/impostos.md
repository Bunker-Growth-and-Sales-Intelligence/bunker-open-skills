# Impostos sobre a venda, regime por regime

Regra de ouro: todo número de imposto que você usar é hipótese até o contador confirmar. Escreva isso na resposta. Cite a fonte ao lado do número.

## 1. Por dentro e por fora

- **Por dentro**: o imposto está dentro do preço. Ele entra no divisor do markup e aparece na DRE como dedução da receita bruta. São eles: ICMS (a lei manda que ele integre a própria base, LC 87/1996, art. 13, § 1º, I), ISS, PIS, Cofins, o DAS do Simples Nacional e o DIFAL que o vendedor recolhe na venda a consumidor final de outra UF.
- **Por fora**: o tributo é somado ao preço na nota e repassado ao governo. Ele não entra na receita bruta (Decreto-Lei 1.598/1977, art. 12, § 4º) e não entra no divisor. São eles: IPI, ICMS cobrado por substituição tributária (ICMS-ST) e, a partir de 2027, CBS e IBS (LC 214/2025, art. 12, § 2º, I).

Tributo por fora não mexe na margem da linha. Ele muda o total que o cliente paga, e isso pesa na hora de competir. Mostre o total da nota quando for relevante.

## 2. Como descobrir o regime

1. Pergunte ao contador. É o caminho mais rápido.
2. Consulte o CNPJ no Portal do Simples Nacional, em "Consulta Optantes". A página diz se a empresa é do Simples ou MEI.
3. Olhe uma nota fiscal eletrônica emitida pela empresa. O campo CRT (código de regime tributário) diz: 1 ou 2 para Simples Nacional, 3 para regime normal (Lucro Presumido ou Real), 4 para MEI.
4. Se não for Simples nem MEI e a pessoa não souber se é Presumido ou Real: empresas com faturamento acima de R$ 78 milhões por ano são obrigadas ao Lucro Real (Lei 9.718/1998, art. 14). Abaixo disso, pergunte ao contador. Use Presumido como hipótese marcada.

## 3. Regime por regime (regras vigentes em 2026)

### MEI

Paga um valor fixo por mês no DAS, qualquer que seja o faturamento dentro do limite (LC 123/2006, art. 18-A). Na conta da linha, imposto sobre a venda = 0%. O DAS mensal é despesa fixa e sai da margem de contribuição do mês.

### Simples Nacional

Um único documento, o DAS, junta os tributos. A alíquota efetiva depende do faturamento dos últimos 12 meses (LC 123/2006, art. 18, § 1º-A):

```
Alíquota efetiva = (receita bruta dos últimos 12 meses × alíquota nominal − parcela a deduzir) ÷ receita bruta dos últimos 12 meses
```

Como descobrir sem fazer a conta: pegue o extrato do PGDAS-D de um mês recente e divida o valor do DAS pela receita daquele mês. Esse percentual é o imposto sobre a venda.

Sem o extrato, pergunte o faturamento dos últimos 12 meses: ele dá a faixa, e a fórmula acima dá a alíquota efetiva. Quem não sabe o de 12 meses quase sempre sabe o de um mês normal: use o do mês × 12, marcado como hipótese.

**Nominal não é efetiva.** A tabela dá a alíquota nominal da faixa; o DAS cobra a efetiva, que é menor por causa da parcela a deduzir. "O contador disse 7,3%" num comércio é a nominal da 2ª faixa do Anexo I; a efetiva nessa faixa vai de 4,00% (R$ 180 mil) a 5,65% (R$ 360 mil). Quando o número bate com uma nominal, avise e calcule a efetiva.

Faixas dos três anexos mais comuns (LC 123/2006, Anexos I, II e III, redação da LC 155/2016):

| Receita bruta em 12 meses | Anexo I, comércio | Anexo II, indústria | Anexo III, serviços |
|---|---|---|---|
| até R$ 180.000,00 | 4,00%, dedução 0 | 4,50%, dedução 0 | 6,00%, dedução 0 |
| até R$ 360.000,00 | 7,30%, R$ 5.940 | 7,80%, R$ 5.940 | 11,20%, R$ 9.360 |
| até R$ 720.000,00 | 9,50%, R$ 13.860 | 10,00%, R$ 13.860 | 13,50%, R$ 17.640 |
| até R$ 1.800.000,00 | 10,70%, R$ 22.500 | 11,20%, R$ 22.500 | 16,00%, R$ 35.640 |
| até R$ 3.600.000,00 | 14,30%, R$ 87.300 | 14,70%, R$ 85.500 | 21,00%, R$ 125.640 |
| até R$ 4.800.000,00 | 19,00%, R$ 378.000 | 30,00%, R$ 720.000 | 33,00%, R$ 648.000 |

Exemplo: serviço com R$ 22 mil por mês, R$ 264 mil em 12 meses, 2ª faixa do Anexo III: (264.000 × 11,2% − 9.360) ÷ 264.000 = **7,65%**. Com R$ 38 mil por mês, R$ 456 mil, 3ª faixa: (456.000 × 13,5% − 17.640) ÷ 456.000 = **9,63%**.

Hipótese para quem está sem o extrato nem o faturamento, válida só na primeira faixa (até R$ 180 mil nos últimos 12 meses), conforme os anexos da LC 123/2006: comércio, Anexo I, 4%; indústria, Anexo II, 4,5%; a maior parte dos serviços, Anexo III, 6%. Acima da primeira faixa a alíquota sobe. Marque como hipótese.

Produto com ICMS-ST ou com PIS e Cofins monofásico: essa receita é segregada no PGDAS-D e a parte do tributo que já foi paga na cadeia sai do DAS (LC 123/2006, art. 18, § 4º-A). A alíquota efetiva desse produto fica menor que a do extrato.

**Benefício por produto dentro do DAS (cesta básica e afins).** A empresa do Simples não aproveita incentivo fiscal fora do que a LC 123 prevê (art. 24, § 1º), e a alíquota zero de PIS e Cofins da Lei 10.925/2004 só reduz o DAS se o contador segregar essa receita no PGDAS-D. Monte o cenário "com benefício" assim, marcado como hipótese:

```
alíquota com benefício = alíquota efetiva × (1 − parte de PIS e Cofins na faixa)
```

No Anexo I, da 1ª à 5ª faixa, PIS e Cofins são 15,50% do DAS (Cofins 12,74%, PIS 2,76%, tabela de partilha do Anexo I). Com 7,3%: 7,3 × 0,845 = 6,17%. Redução de ICMS da cesta básica na UF tira ainda a parte do ICMS (34% do DAS no Anexo I, faixas 1 a 5) na proporção da redução. Se o contador não confirmar a segregação, a alíquota é a cheia: diga isso e deixe os dois cenários.

### Lucro Presumido

- PIS 0,65% e Cofins 3%, cumulativos, sem crédito nas compras (Lei 9.718/1998). Juntos, 3,65%.
- ICMS na venda de mercadoria ou ISS no serviço, por dentro.
- IRPJ e CSLL incidem sobre um lucro presumido pela lei, que é uma parte da receita. Não entram na DRE da linha. Avise que a margem de contribuição precisa cobrir esses dois. Na DRE do mês, use `"regime": "presumido"` e `irpj_csll_pct` em % da receita bruta (num serviço com o adicional, perto de 8,54%): eles pesam mesmo com prejuízo.

### Lucro Real

- PIS 1,65% e Cofins 7,6%, não cumulativos (Leis 10.637/2002 e 10.833/2003). Juntos, 9,25%, com crédito sobre boa parte das compras.
- Com crédito, o custo da mercadoria entra na conta **líquido** do crédito. Exemplo: compra de R$ 100 com R$ 9,25 de crédito de PIS e Cofins e R$ 12 de crédito de ICMS custa R$ 78,75 para a formação do preço.
- **Quem não sabe o próprio crédito**: faça dois cenários. Um com o custo cheio da nota. Outro com o custo × (1 − 0,0925 − ICMS da compra), a hipótese de crédito cheio. Se as duas dão conclusões opostas (margem positiva contra negativa), diga que o crédito decide e peça ao contador. Nunca aplique débito cheio na venda e custo sem crédito sem mostrar o outro cenário: o imposto pesaria duas vezes.
- IRPJ e CSLL sobre o lucro, fora da DRE da linha.

## 4. ICMS

- **Venda dentro da UF**: alíquota interna da UF, que muda por produto. Pergunte junto com a rota; a pessoa muitas vezes sabe ("acho que é 17%"). Sem o dado, use a alíquota modal da UF como hipótese marcada e diga que a do produto pode ser outra (cesta básica, insumo agropecuário e medicamento costumam ter redução). Modais de referência, a conferir no RICMS da UF e com o contador, porque mudam por lei estadual: SP 18%, MG 18%, RJ 20% + 2% do fundo de pobreza, PR 19,5%, SC 17%, RS 17%, GO 19%, MT 17%, MS 17%, DF 20%, BA 20,5%, PE 20,5%. UF fora da lista: 18%, hipótese.
- **Venda para outra UF, para contribuinte**: 12% na regra geral; 7% quando a venda sai do Sul ou do Sudeste (menos o Espírito Santo) para Norte, Nordeste, Centro-Oeste ou Espírito Santo (Resolução do Senado 22/1989); 4% para produto importado ou com conteúdo de importação acima de 40% (Resolução do Senado 13/2012).
- **Venda para consumidor final não contribuinte de outra UF**: o vendedor recolhe também o DIFAL, a diferença entre a alíquota interna do destino e a interestadual (EC 87/2015 e LC 190/2022). Some ao ICMS da linha.
- Benefício, redução de base, diferimento e substituição tributária mudam tudo. Se a pessoa mencionar qualquer um, diga que o contador precisa confirmar a alíquota efetiva.

Onde achar: a nota fiscal de uma venda igual mostra a alíquota e a base do ICMS. O NCM do produto está na nota de compra ou no cadastro do sistema.

## 5. ISS

Alíquota do município do prestador, na maioria dos serviços, entre 2% e 5% (LC 116/2003, art. 8º, II, e art. 8º-A). A alíquota está na lei do município e aparece na nota de serviço já emitida. O código do serviço é o da lista anexa à LC 116/2003.

## 6. IPI

Por fora, somado na nota. A alíquota sai da TIPI pelo NCM do produto. A partir de 2027 vai a zero, menos para produtos com industrialização incentivada na Zona Franca de Manaus (EC 132/2023, art. 126, III).

## 7. Transporte

- Transporte de passageiros ou carga **dentro do município**: ISS. No Simples, Anexo III.
- **Intermunicipal ou interestadual**: ICMS no lugar do ISS (LC 87/1996, art. 2º, II). No Simples, Anexo III sem a parte do ISS e com a parte do ICMS do Anexo I (LC 123/2006, art. 18, § 5º-E).
- Corrida que sai do município (aeroporto na cidade vizinha, por exemplo) muda de imposto. Pergunte.
- Custo por km cobrado = custo por km rodado × (km rodados ÷ km cobrados). Volta vazia dobra o custo.

## 8. Benefício por produto: pergunte nestes ramos

Benefício por produto pode levar o imposto de 26% para 7%, e o leigo quase nunca fala dele. Pergunte quando o produto estiver num destes grupos:

| Grupo | O que costuma ter | Fonte |
|---|---|---|
| Insumo agropecuário (adubo, fertilizante, semente, defensivo, ração) | PIS e Cofins com alíquota zero; ICMS com redução de base | Lei 10.925/2004, art. 1º; Convênio ICMS 100/1997 e alterações |
| Cesta básica (arroz, feijão, leite, carne) | PIS e Cofins com alíquota zero; ICMS reduzido em muitas UFs. No Simples, só com a receita segregada: conta na seção 3 | Lei 10.925/2004, art. 1º; LC 123/2006, arts. 18, § 4º-A, e 24, § 1º; RICMS da UF |
| Medicamento, perfumaria, higiene | PIS e Cofins monofásico: o varejo não paga de novo | Lei 10.147/2000 |
| Combustível, bebida fria, autopeça, pneu | monofásico e, muitas vezes, ICMS-ST | Leis 9.718/1998, 13.097/2015 e 10.485/2002; convênios do Confaz |

Sem resposta do contador, monte os dois cenários (regra geral e com o benefício) e marque os dois como hipótese. O cenário com benefício sai com número: PIS e Cofins em zero no Lucro Real e no Presumido; no Simples, a conta da seção 3. A redução de base do ICMS (Convênio ICMS 100/1997 para insumo agropecuário) varia por produto e UF: sem o percentual do contador, deixe o ICMS cheio e escreva que a redução não entrou.

## 9. Hipótese padrão, para quem está sem dado nenhum

Serve para a conversa seguir. Marque cada número como hipótese.

| Situação | Impostos sobre a venda (hipótese) | Fonte da regra |
|---|---|---|
| MEI | 0% (DAS fixo) | LC 123/2006, art. 18-A |
| Simples, comércio, 1ª faixa | 4% | LC 123/2006, Anexo I |
| Simples, serviço, 1ª faixa | 6% | LC 123/2006, Anexo III |
| Presumido, comércio na mesma UF | 3,65% + ICMS interno (18% como hipótese) | Lei 9.718/1998; RICMS da UF |
| Presumido, serviço | 3,65% + ISS (5% como hipótese) | Lei 9.718/1998; LC 116/2003 |
| Real, comércio na mesma UF | 9,25% + ICMS interno (18% como hipótese), custo líquido de crédito | Leis 10.637/2002 e 10.833/2003; RICMS da UF |
