# Impostos sobre a venda, regime por regime

Regra de ouro: todo número de imposto que você usar é hipótese até o contador confirmar. Escreva isso na resposta. Cite a fonte ao lado do número.

## 1. Por dentro e por fora

- **Por dentro**: o imposto está dentro do preço. Ele entra no divisor do markup e aparece no DRE como dedução da receita bruta. São eles: ICMS (a lei manda que ele integre a própria base, LC 87/1996, art. 13, § 1º, I), ISS, PIS, Cofins, o DAS do Simples Nacional e o DIFAL que o vendedor recolhe na venda a consumidor final de outra UF.
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

Sem o extrato, pergunte o faturamento dos últimos 12 meses: ele dá a faixa, e a fórmula acima dá a alíquota efetiva.

Hipótese para quem está sem o extrato nem o faturamento, válida só na primeira faixa (até R$ 180 mil nos últimos 12 meses), conforme os anexos da LC 123/2006: comércio, Anexo I, 4%; indústria, Anexo II, 4,5%; a maior parte dos serviços, Anexo III, 6%. Acima da primeira faixa a alíquota sobe. Marque como hipótese.

Produto com ICMS-ST ou com PIS e Cofins monofásico: essa receita é segregada no PGDAS-D e a parte do tributo que já foi paga na cadeia sai do DAS (LC 123/2006, art. 18, § 4º-A). A alíquota efetiva desse produto fica menor que a do extrato. Cesta básica pode ter ainda redução de ICMS na UF. Mande o contador conferir.

### Lucro Presumido

- PIS 0,65% e Cofins 3%, cumulativos, sem crédito nas compras (Lei 9.718/1998). Juntos, 3,65%.
- ICMS na venda de mercadoria ou ISS no serviço, por dentro.
- IRPJ e CSLL incidem sobre um lucro presumido pela lei. São tributos sobre o lucro e não entram no DRE da linha. Avise que a margem de contribuição precisa cobrir esses dois.

### Lucro Real

- PIS 1,65% e Cofins 7,6%, não cumulativos (Leis 10.637/2002 e 10.833/2003). Juntos, 9,25%, com crédito sobre boa parte das compras.
- Com crédito, o custo da mercadoria entra na conta **líquido** do crédito. Exemplo: compra de R$ 100 com R$ 9,25 de crédito de PIS e Cofins e R$ 12 de crédito de ICMS custa R$ 78,75 para a formação do preço.
- **Quem não sabe o próprio crédito**: faça dois cenários. Um com o custo cheio da nota. Outro com o custo × (1 − 0,0925 − ICMS da compra), a hipótese de crédito cheio. Se as duas dão conclusões opostas (margem positiva contra negativa), diga que o crédito decide e peça ao contador. Nunca aplique débito cheio na venda e custo sem crédito sem mostrar o outro cenário: o imposto pesaria duas vezes.
- IRPJ e CSLL sobre o lucro, fora do DRE da linha.

## 4. ICMS

- **Venda dentro da UF**: alíquota interna da UF, que muda por produto. A alíquota geral hoje fica em torno de 17% a 23%, conforme a UF. Confirme no regulamento do ICMS da secretaria da fazenda da UF de origem. Sem esse dado, use 18% como hipótese marcada e diga que a alíquota do produto pode ser outra (cesta básica, por exemplo, costuma ter redução).
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
| Cesta básica (arroz, feijão, leite, carne) | PIS e Cofins com alíquota zero; ICMS reduzido em muitas UFs | Lei 10.925/2004, art. 1º; RICMS da UF |
| Medicamento, perfumaria, higiene | PIS e Cofins monofásico: o varejo não paga de novo | Lei 10.147/2000 |
| Combustível, bebida fria, autopeça, pneu | monofásico e, muitas vezes, ICMS-ST | Leis 9.718/1998, 13.097/2015 e 10.485/2002; convênios do Confaz |

Sem resposta do contador, monte os dois cenários (regra geral e com o benefício) e marque os dois como hipótese.

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
