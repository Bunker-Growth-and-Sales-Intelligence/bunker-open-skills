# Roteiro da entrevista

Uma pergunta por mensagem, com uma linha de porquê. Uma pergunta pede um dado só: número e base na mesma pergunta voltam pela metade. Se a pessoa responder mais de uma coisa, aproveite e pule o que já veio. Em ferramenta com botões, ofereça as respostas como opções.

Abertura sugerida:

> Vou te ajudar a chegar no preço, ou a conferir o que você já cobra. São umas doze perguntas curtas, uma de cada vez. Se não souber alguma, eu explico onde achar ou seguimos com uma estimativa marcada.

## O caminho comum, em até 12 perguntas

| # | Pergunta | Por que, em uma linha | Se a pessoa não souber |
|---|---|---|---|
| 1 | O que você vende e em que unidade você vende? | O preço é sempre por unidade de venda. | Se a medida é outra (litro, mas vende bombona de 20 L), a conta é por bombona: custo, frete e preço da bombona inteira. |
| 2 | Quantos produtos, quantos vendedores e quantas tabelas de preço você tem? | Diz o tamanho da operação e até onde a conversa vai. | Ofereça faixas: "até 20 itens e só eu vendo", "algumas centenas e uma equipe", "milhares, com tabela por canal ou região". |
| 3 | Você cobra diferente de algum grupo de cliente? | Margem e fatores podem mudar por grupo. Explique a lista abaixo. | Se não, siga com um preço só. Se sim, abra o aprofundamento de níveis. |
| 4 | Quanto custa cada unidade para você, e o que entra nesse custo? | É a base de tudo. Custo esquecido infla a margem. | Última nota de compra ÷ quantidade. Leia a lista do ramo abaixo. |
| 5 | Qual o regime tributário da empresa? | Muda os impostos. | `impostos.md`, seção 2. |
| 6 | O produto tem algum benefício de imposto? | Alíquota zero, monofásico, redução de base e ST mudam a conta inteira. | Pergunte só no ramo de risco (lista em `impostos.md`, seção 8). Sem resposta, faça os dois cenários. |
| 7 | Para onde você vende: mesma UF, outra, as duas? | O ICMS muda com a rota. | Pule no Simples com venda no balcão. Se "as duas", cada rota é uma linha no simulador. |
| 8 | Paga comissão a vendedor, representante ou aplicativo? Quanto? | Sai do preço, igual ao imposto. | Base: sobre o valor da nota. Na indústria, "sem impostos" quer dizer sem IPI, que é a receita bruta. |
| 9 | Você paga a entrega? Quanto custa uma entrega e quantas unidades vão nela? | Frete de entrega é despesa da venda. | Cliente leva: 0. Você entrega e não sabe: 3% do preço, **hipótese**. |
| 10 | Quanto das vendas é no cartão, e qual a taxa? Tem marketplace? | A taxa só pesa na parte que passa na maquininha. | Taxa × parte no cartão. Sem a parte: 60% no cartão, **hipótese**. |
| 11 | Quanto você cobra hoje? Costuma dar desconto? | Com preço, dá para auditar. | Siga só com a formação. |
| 12 | Quanto o concorrente cobra pelo mesmo produto? | O preço formado precisa caber no mercado. | Siga sem; avise que falta a checagem. |

Depois da 11, **mostre a margem de hoje** e só então pergunte: "com essa margem na frente, qual você quer?". Leigo não responde margem desejada sem ver a atual.

Não repita as premissas numa pergunta própria. Elas vão na entrega, marcadas, e a pessoa corrige se precisar.

## A pergunta 3: o que muda conforme o quê

Explique em uma mensagem curta, com o exemplo que servir ao ramo, e pergunte se algo disso existe na empresa:

- **Margem por grupo de cliente.** Uma empresa pode aceitar margem menor para quem compra muito ou revende. Não é desconto: é outra meta, combinada antes. Ex.: 50% no preço cheio, 40% para distribuidor.
- **Preço próprio de um cliente.** Contrato, rede ou cliente grande com preço fechado.
- **Desconto do vendedor.** O que ele dá na hora, em cima do preço do grupo.
- **Imposto por rota e por produto.** ICMS muda de UF para UF; PIS e Cofins mudam por produto (monofásico, alíquota zero).
- **Comissão por canal, produto ou cliente.**
- **Frete por rota e por peso.**

A resposta decide a profundidade:

- "Não, um preço só": a conta é uma linha. Siga o caminho comum.
- "Sim, um ou dois grupos": faça o aprofundamento, uma linha por grupo.
- "Sim, vários, com tabela por canal e vendedores com desconto": monte os níveis inteiros e marque a operação como grande.

## Aprofundamento de níveis, só quando a pergunta 3 disse sim

Uma pergunta por vez, até 4:

1. Qual a margem do preço cheio, o teto? (Se a pessoa não sabe, use a margem do grupo que mais vende.)
2. Para cada grupo que paga menos: qual a margem combinada para ele?
3. Algum cliente ou rede tem preço fechado? Qual preço, ou qual margem?
4. Quanto de desconto o vendedor costuma dar em cada grupo?

Cada grupo entra como uma linha do simulador, com os fatores dele: imposto da rota, comissão do canal, frete da rota. A explicação dos níveis está em `niveis.md`.

## Perguntas que só entram quando o caso pede

| Quando | Pergunta |
|---|---|
| Lucro Real e o custo pode ter crédito | O custo da nota vem com crédito de ICMS, PIS e Cofins? Se não souber: dois cenários, com e sem crédito (`impostos.md`, seção 3). |
| Simples, sem o extrato do PGDAS | Quanto a empresa faturou nos últimos 12 meses? Dá a faixa. |
| A pessoa quer "lucro limpo", "X% depois de tudo" | Quanto é o custo fixo do mês, e quantas unidades você vende por mês? É outra conta, abaixo da margem. |
| Comércio com perda (hortifrúti, validade) | Quanto se perde, em % do que se compra? Entra no custo: custo ÷ (1 − perda). |
| Transporte | Quantos km roda vazio para cada km cobrado? Quanto tempo fica parado por corrida? É intermunicipal? |
| Serviço por hora | Quantas horas do mês são cobradas? |
| Vende para empresa e a pergunta é 2027 ou IPI | Seu cliente toma crédito de imposto? |

## Hipótese que muda a conclusão

Se um dado estimado inverte o veredito (margem positiva contra negativa, acima contra abaixo da meta), monte dois cenários no simulador, um com cada hipótese, e diga qual dado resolve. Casos comuns: crédito na compra, benefício do setor, comissão desconhecida, km vazio.

## O que entra no custo, por ramo

Custo é o que varia com cada unidade vendida. Aluguel, salário fixo e seguro são custo fixo: saem da margem do mês, e não do custo da unidade.

- **Transporte, táxi, aplicativo** (corrida ou km): combustível, pneu, óleo e manutenção por km rodado, contando o km vazio. Comissão: taxa do aplicativo ou repasse ao motorista. Fixo: parcela do carro, seguro, licenciamento.
- **Comércio** (quilo, peça, pacote): preço de compra, frete de compra, perda, embalagem, líquido dos créditos. Outras: taxa de cartão, aplicativo de entrega. Fixo: aluguel, energia, folha.
- **Indústria e distribuidora** (quilo, caixa, tonelada): matéria-prima, embalagem, mão de obra direta, energia da produção, frete de compra, líquido dos créditos. Comissão do representante, frete de entrega, verba de rede por venda.
- **Serviço** (hora, projeto, visita): horas de quem executa, deslocamento, material, subcontratado. Imposto: ISS e, fora do Simples, PIS e Cofins.

## Quando quem fala é o contador

Pule as explicações e vá aos números: regime, CST ou CSOSN, alíquotas por dentro, tributos por fora, custo líquido de crédito, base da comissão. Aceite a classificação que ele indicar. Se ele atende vários clientes, diga que a mesma conta serve para cada um, e que cliente com tabela por canal é caso para o Pricing Designer.
