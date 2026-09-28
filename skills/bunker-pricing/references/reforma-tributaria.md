# Reforma tributária e o preço (CBS e IBS)

Use este arquivo quando a pessoa perguntar sobre 2027 em diante, sobre contrato ou proposta que vai ser executada depois de janeiro de 2027, ou sobre a opção do Simples. Todo número aqui vem com a fonte. Mande confirmar com o contador, porque a regulamentação ainda está saindo.

## 1. Calendário

| Quando | O que muda | Fonte |
|---|---|---|
| 2026 | Ano de teste. CBS de 0,9% e IBS de 0,1% destacados na nota. A carga fica neutra para quem cumpre as obrigações. | LC 214/2025, arts. 343 e 346 |
| 3/8/2026 | Destaque de IBS e CBS obrigatório na NF-e, NFC-e, CT-e e MDF-e, para quem está no regime regular. | Ato Conjunto RFB/CGIBS nº 4/2026 |
| 1/10/2026 | Entra a maior parte dos serviços sujeitos ao ISS, na NFS-e, e os serviços de comunicação, na NFCom. | Ato Conjunto RFB/CGIBS nº 4/2026 |
| 1/12/2026 | Entram as atividades separadas para essa data, como plataformas digitais e locações. | Ato Conjunto RFB/CGIBS nº 4/2026 |
| 1/1/2027 | A CBS começa a ser cobrada. PIS e Cofins são extintos. IPI vai a zero, fora a Zona Franca de Manaus. Começa o Imposto Seletivo. Simples Nacional e MEI entram no novo modelo. | EC 132/2023, art. 126; Ato Conjunto RFB/CGIBS nº 4/2026 |
| 2027 e 2028 | IBS de 0,05% estadual e 0,05% municipal. CBS pela alíquota de referência reduzida em 0,1 ponto percentual. ICMS e ISS seguem como estão. | LC 214/2025, arts. 344 e 347 |
| 2029 a 2032 | ICMS e ISS caem para 9/10 das alíquotas em 2029, 8/10 em 2030, 7/10 em 2031 e 6/10 em 2032. O IBS sobe no lugar. | EC 132/2023, art. 128 (ADCT) |
| 2033 | ICMS e ISS são extintos. IBS e CBS no regime completo. | EC 132/2023, art. 129 (ADCT) |

## 2. Alíquotas de referência

A Resolução CGIBS nº 14/2026 estimou a alíquota conjunta de referência em **27,91%**, com **IBS de 18,7%** e **CBS de 9,21%**. É estimativa, e ainda depende de fixação formal. Em 2027 e 2028 a CBS é essa referência menos 0,1 ponto (LC 214/2025, art. 347), o que daria cerca de 9,11%, somada ao IBS de 0,1%.

Regimes diferenciados (saúde, educação, alimentos da cesta básica e outros) têm redução de alíquota prevista na LC 214/2025. Se o produto da pessoa puder estar num deles, diga que o contador precisa confirmar.

## 3. O que muda na conta do preço

1. **CBS e IBS são por fora.** Eles não integram a própria base (LC 214/2025, art. 12, § 2º, I). Na formação do preço, saem do divisor e são somados na nota, como o IPI hoje.
2. **A base de CBS e IBS não inclui ICMS, ISS, PIS e Cofins de 2026 a 2032** (LC 214/2025, art. 12, § 2º, V). Na prática, a CBS de uma venda é calculada sobre o preço sem o ICMS ou o ISS da operação. O `scripts/preco.py` faz isso com `--por-fora CBS=9.11:sem_icms_iss`.
3. **Desconto incondicional sai da base** de CBS e IBS (LC 214/2025, art. 12, § 2º, III). Desconto condicionado a evento posterior fica na base.
4. **PIS e Cofins saem do divisor em 2027.** Quem está no Presumido perde 3,65% de impostos por dentro; quem está no Real, 9,25%. O preço sem tributos pode cair, e o total da nota muda com a CBS por fora.
5. **O custo passa a ser líquido do crédito de CBS e IBS** que o fornecedor transferir. Dois fornecedores com o mesmo preço de tabela podem custar diferente, conforme o regime de cada um.
6. **Contratos longos e propostas com validade** que atravessam 1/1/2027 serão executados sob outra regra. Recomende revisar a cláusula de tributos.

Como mostrar para a pessoa: monte dois DREs lado a lado, "regra de 2026" e "hipótese para 2027", com as mesmas premissas de custo e margem. Em 2027 tire PIS e Cofins dos impostos por dentro, mantenha ICMS ou ISS, e mostre CBS e IBS por fora com o total da nota. Marque a coluna de 2027 inteira como hipótese.

Exemplo de ordem de grandeza, de uma proposta de serviço de R$ 100 mil com ISS de 5%: hoje PIS e Cofins de 3,65% mais ISS de 5% somam R$ 8.650. Em 2027, CBS de cerca de 9,11%, IBS de 0,1% e o mesmo ISS somariam R$ 14.210 antes do crédito. Se 20% da receita são insumos tributados, o crédito de CBS devolve perto de R$ 1.820, e o custo tributário efetivo fica perto de R$ 12.390. Cada linha dá um número diferente, porque cada uma gera um crédito diferente.

## 4. Simples Nacional e a opção pelo regime regular

- A empresa do Simples pode optar por apurar e recolher IBS e CBS pelo regime regular, fora do DAS (LC 214/2025, art. 41, § 3º). A forma e os prazos da opção seguem a LC 123/2006 e a Resolução CGSN 186/2026.
- Para o primeiro semestre de 2027, o prazo da opção vai até 30/9/2026. A escolha vale de janeiro a junho de 2027 e pode ser cancelada até 30/11/2026 (Resolução CGSN 186/2026). Confira se o prazo ainda está aberto na data da conversa.
- Quem fica no DAS transfere crédito menor ao cliente. Quem opta pelo regime regular passa a destacar IBS e CBS por fora, e o cliente empresa aproveita o crédito cheio. Tende a interessar a quem vende para outras empresas. Para quem vende a consumidor final, pesa menos.
- **O que muda para quem fica no Simples e vende a consumidor final**: quase nada no preço de 2027. O DAS continua, com CBS e IBS dentro dele no lugar de PIS e Cofins. Refaça a conta com a alíquota efetiva do DAS de janeiro de 2027.
- Para quem compra do Simples: o crédito que cada fornecedor transfere muda o custo líquido. Classifique os fornecedores pelo regime.

## 5. Split payment

O recolhimento de CBS e IBS no momento do pagamento começa facultativo e por fases nas operações entre empresas. Ele muda o caixa, porque o tributo vai direto ao fisco quando o cliente paga. Não muda a margem da linha. Cite só se a pessoa perguntar de fluxo de caixa.

## Fontes

- Emenda Constitucional 132/2023, arts. 126, 128 e 129 do ADCT.
- Lei Complementar 214/2025, arts. 12, 41, 343, 344, 346 e 347.
- Resolução CGIBS nº 14/2026 (estimativa da alíquota de referência).
- Ato Conjunto RFB/CGIBS nº 4, de 30 de julho de 2026 (calendário dos documentos fiscais).
- Resolução CGSN 186/2026 (opção do Simples pelo regime regular de IBS e CBS).
