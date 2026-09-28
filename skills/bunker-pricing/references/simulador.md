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
| `mc_teto` | margem planejada global, % da receita líquida. Pode vir na linha, para sobrepor. |
| `mc_canal` | margem do canal da linha. Sem ele, a linha não tem nível de canal. |
| `preco_especifico` ou `mc_especifica` | preço fechado ou margem própria do cliente. Para o pequeno comércio, o preço de hoje, com `rotulo_especifico: "Preço de hoje"`. |
| `desconto` | desconto do vendedor, % sobre o preço do nível usado. |
| `preco_praticado` | preço cobrado de fato; substitui o desconto. |
| `impostos` | impostos por dentro, % do preço, um por nome. |
| `comissao_sobre` | `bruta` (padrão) ou `liquida` (sobre o preço sem ICMS, PIS e Cofins). |
| `frete_rs_kg` e `peso_kg` | frete por rota e peso; somam em `frete_rs`. |
| `outras_pct` | cartão (taxa × parte no cartão), marketplace. |
| `por_fora` | IPI, ICMS-ST, CBS e IBS; `"base": "sem_icms_iss"` para CBS e IBS. |
| `preco_mercado` | preço do concorrente; o simulador mostra a maior margem que cabe nele. |
| `custo_fixo_mes`, `meta_lucro_pct` | outra conta: lucro depois do custo fixo, e o preço para uma meta de lucro (uma linha só). |
| `hipoteses` | nomes marcados como hipótese: `custo`, `impostos`, `comissao`, `frete`, `outras`, `margem`, `desconto`. |
| `quantidade` | volume da linha no período. Os reais dos gráficos são na quantidade. |

**Dois cenários.** Quando uma hipótese muda a conclusão, use `"cenarios": [{...}, {...}]`, cada um com `nome_cenario` e as próprias `linhas`. Os campos de fora de `cenarios` valem para os dois. A página mostra um botão por cenário.

## O que a página mostra

| Bloco | Pergunta |
|---|---|
| Barra de desempenho e cartões | Quanto da margem planejada a venda manteve? |
| Composição do preço | Para onde vai o preço do nível? (a margem cedida hachurada, a meta marcada) |
| Cascata do preço | Como o preço se forma, por unidade? |
| Cascata dos níveis | Em qual nível a margem ficou na mesa? |
| Três leituras | Quanto a margem se afastou de cada régua? |
| Barras por grupo | Qual grupo entrega a margem planejada? (duas linhas ou mais) |
| Dispersão com a diagonal | Onde o desconto pesa mais na margem? (duas linhas ou mais) |
| Custo fixo | A margem do mês paga o custo fixo? (com `custo_fixo_mes`) |
| Raio-x | Como a conta fecha, centavo a centavo? |

Faixa de cor: mais de 70% da margem planejada mantida é verde; de 50 a 70, âmbar; abaixo de 50, ou margem negativa, vermelho.

## Onde abre

1. **Claude com artefatos (claude.ai ou aplicativo).** Leia `assets/simulador.html`, troque o bloco `cenario` pelos números da conversa e crie um artefato HTML com a página inteira, com o JS como está.
2. **Terminal (Claude Code, Codex, qualquer agente que roda comando).** Grave o cenário em JSON e rode `python3 scripts/simulador.py cenario.json`. O script grava `cenario.html` e abre no navegador: `open` no macOS, `start` no Windows, `xdg-open` no Linux. `--nao-abrir` só grava. `preco.py --html arquivo.html` faz o mesmo a partir dos argumentos de linha de comando.
3. **Chat sem artefato e sem terminal.** Entregue a página com o bloco `cenario` preenchido, num bloco de código, e diga: "salve como preco.html e abra no navegador". Junto, o resumo em poucas linhas.
