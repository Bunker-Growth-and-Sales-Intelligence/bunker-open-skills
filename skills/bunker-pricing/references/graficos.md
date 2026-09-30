# Gráficos da entrega

O método de gráfico da Bunker, na parte que esta skill usa. Painel da Bunker mostra gráfico, tabela e manchete curta: quem recebe é empresário e decide olhando. Página com mais texto que desenho está errada.

## A ordem de trabalho

1. **Pergunta de negócio** antes da forma. Ela nomeia a medida, a unidade e o recorte, e não fala do desenho (nada de curva, eixo ou barra).
2. **Forma pela pergunta**, na tabela abaixo.
3. **Manchete com a conclusão e o número**, defensável pelo que está desenhado. Ela abre com a resposta.
4. **Cor só no que a manchete nomeia.** O resto fica em cinza.
5. **Fonte uma vez**, no rodapé da página: de onde veio o dado, que cenário, quando.
6. **Conferências e fotos** antes de mostrar a alguém.

## Os blocos da entrega

| Bloco | Pergunta | Forma (`scripts/grafico/formas.py`) |
|---|---|---|
| DRE da venda | por unidade, planejado no preço teto contra realizado no negociado | tabela, com os campos no painel e as três colunas de nome |
| DRE do mês | orçado no preço teto contra realizado | tabela, até o lucro líquido |

Por ora a entrega é só as duas DREs: sem gráfico, manchete, conclusão nem próximo passo no PDF. As formas de `scripts/grafico/formas.py` ficam para quando os blocos de gráfico voltarem. As hipóteses ficam no chat e no cenário.

## As regras de desenho

- **Eixo do zero, sempre.** A altura é proporcional ao dado; a ponte aceita negativo com a linha do zero.
- **A cor julga.** A primária do cliente é o que vai bem, a secundária é o alerta (o cedido, o que ficou abaixo). Sem cliente definido, preto e vermelho da Bunker. A cor do cliente entra por `"marca": {"primaria": "#...", "secundaria": "#..."}` no cenário, tirada do tema dele, e não estimada.
- **Hachura é o cedido**, dentro do bloco a que pertence, com piso de 6 px para a parte pequena não sumir.
- **Nome na ponta**, sem legenda de canto: a barra diz "planejada R$ 80,11" na própria ponta.
- **Régua para julgar contra**: a linha tracejada da margem planejada; o piso, no cartão.
- **O desenho nasce na largura em que aparece**: 468 na meia coluna, 980 na página cheia, 658 na folha A4. Bloco de largura cheia leva o de 980 e o de 468, e o CSS mostra o da tela; encolher o de 980 no celular deixaria a letra com 4 px.
- **Número em português**: tudo em 2 casas na tela e no PDF, percentual em 1 (alíquota em 2); a conta roda em 4. Sinal de menos tipográfico.
- **Desvio que julga**: seta ▲ ou ▼ e cor pelo sentido da linha, verde no que vai bem e o alerta no que vai mal; menos custo ou dedução é bom, menos receita ou margem é ruim. Sem negrito.

## A marca

Preto e branco com os cinzas da Bunker, Schibsted Grotesk embutida, logo real (preto no claro, branco no escuro e na capa) e o B em contorno como marca d'água da capa. Tudo mora em `assets/`, já no tamanho e na cor em que aparece, e vai embutido em base64: nada baixa da internet na hora de abrir ou de imprimir.

## O PDF

`scripts/grafico/saida.py` acha o Chrome da máquina (BUNKER_CHROME, os caminhos do macOS e do Windows, e os comandos do Linux; Chromium, Edge e Brave servem) e imprime a página pelo `@page` dela: A4 em pé, sem margem de impressão, com a margem desenhada na folha. As folhas são compostas pela altura medida de cada bloco, na ordem da leitura: cada um entra na última folha aberta quando cabe, e senão abre outra; a composição sai mais baixa para dividir a folha com a DRE da venda, com os pequenos múltiplos numa fileira só, e o fecho entra como uma caixa escura no fim da última folha quando cabe; senão, ganha a folha preta dele. Logo com largura fixa e altura automática, na proporção do arquivo. Antes de imprimir, `entrega.py` mede cada folha no Chrome e recusa a que não cabe, porque a folha corta o excesso sem avisar. Depois confere a contagem de páginas. Sem Chrome, fica o HTML das folhas para imprimir no navegador.

**Por que A4 em pé, e não 16:9.** A DRE do mês tem perto de trinta linhas e a da venda, perto de trinta, com as colunas de nome. Num slide de 16:9 elas quebrariam em vários slides de cinco linhas, e quem confere a conta perde o fio. O A4 cabe cada DRE numa folha, imprime em qualquer escritório e anexa em e-mail. O painel continua em HTML para a tela.

## As conferências

```bash
cd scripts
python3 -m grafico.conferir painel.html --fotos fotos/
```

| Conferência | O que reprova |
|---|---|
| geometria | elemento fora da moldura do SVG |
| bloco vazio | bloco sem desenho nem tabela |
| legibilidade | texto que, depois da escala, fica abaixo de 9 px |
| manchete | manchete que descreve a forma sem concluir |
| denominador | total repetido dentro do desenho |
| pergunta | pergunta sobre o desenho, ou contagem mecânica |
| sobreposição | dois textos no mesmo lugar |
| texto cortado | texto que passa da borda do desenho |
| rolagem lateral | a página rola para o lado em 1440 ou em 390 |
| texto contra gráfico | num bloco, o texto ocupa mais área que o desenho |

As fotos existem para ser abertas: leia a de 390 com atenção, porque o defeito de celular é o que mais passa. A janela do Chrome headless não desce de 500 px, então a página é medida dentro de um iframe da largura exata. As páginas do PDF também se conferem como imagem antes de ir para o cliente.
