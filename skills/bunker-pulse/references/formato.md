# O registro das atividades

Tudo o que o `relatorio.py` lê é este arquivo JSON. De onde a lista veio não importa: a IA
lê a fonte e escreve aqui.

```json
{
  "titulo": "Onde o projeto está hoje",
  "subtitulo": "O que já foi entregue, o que segue em aberto e onde estão os atrasos.",
  "cliente": "Loja Exemplo",
  "projeto": "Implantação do CRM",
  "medido_em": "2026-09-30",
  "fonte": "planilha de tarefas do time",
  "cores": {"primaria": "#2f6f4f", "secundaria": "#d9822b"},
  "exibicao": {"Construção Sales Cloud": "Construção"},
  "manchetes": {"atrasos": "O CRM concentra os atrasos: 3 das 6 atividades atrasadas."},
  "atividades": [
    {
      "id": "T-01",
      "titulo": "Funil de vendas no CRM",
      "frente": "CRM",
      "status": "andamento",
      "status_original": "Doing",
      "responsavel": "Diego",
      "tipo": "configuração",
      "prioridade": "alta",
      "criada_em": "2026-09-02",
      "inicio": "2026-09-05",
      "prazo": "2026-09-13",
      "concluida_em": null,
      "link": "https://..."
    }
  ]
}
```

## Os campos do topo

| Campo | Obrigatório | O que é |
|---|---|---|
| `atividades` | sim | a lista |
| `medido_em` | recomendado | a data de referência, em `AAAA-MM-DD`. É contra ela que se mede atraso. Sem ela, vale o dia de hoje. Lista exportada semana passada mede a semana passada |
| `fonte` | recomendado | de onde a lista veio, em palavras de quem lê: "quadro do Trello do time", "planilha do plano no SharePoint". Vai no rodapé de todo slide |
| `cliente`, `projeto` | recomendado | vão na capa |
| `titulo`, `subtitulo` | não | a capa; o padrão serve para quase tudo |
| `cores` | não | `primaria` e `secundaria` em hexadecimal; `clara` opcional (a segunda série; sem ela, sai uma versão clara da primária). Sem `cores`, a paleta do portal Bunker Alumni: azul `#3b82f6` e rosa `#f43f5e` |
| `exibicao` | não | nome curto de frente ou pessoa para caber no gráfico (até 17 caracteres). A manchete continua com o nome inteiro |
| `manchetes` | não | troca a manchete de um slide pela chave dele (`numeros`, `cascata`, `frentes`, `situacao`, `atrasos`, `dias`, `responsaveis`, `ritmo`). Só a frase muda; confira que o número bate com o desenho |

## Os campos de cada atividade

| Campo | O que é |
|---|---|
| `titulo` | o nome da atividade, como a pessoa escreveu |
| `status` | um de cinco: `concluida`, `andamento`, `aberta`, `bloqueada`, `cancelada` |
| `status_original` | o texto que veio na fonte, para conferência |
| `frente` | o agrupamento: bloco, fase, épico, milestone, coluna de área, etiqueta de área |
| `responsavel` | uma pessoa; vazio quando a fonte não diz |
| `prazo` | a data em que deveria terminar |
| `criada_em` | quando a atividade entrou na lista |
| `concluida_em` | quando terminou, para as concluídas |
| `inicio`, `tipo`, `prioridade`, `id`, `link` | opcionais; o `link` vira clicável na tabela |

Datas em `AAAA-MM-DD`. O script também aceita `DD/MM/AAAA` e o ISO com hora do GitHub.

## Os cinco status

| Canônico | Quando usar |
|---|---|
| `concluida` | terminou e foi entregue |
| `andamento` | alguém está fazendo agora |
| `aberta` | ainda não começou (a fazer, backlog, pendente, planejada) |
| `bloqueada` | parada esperando alguém ou alguma coisa |
| `cancelada` | saiu do escopo; fica fora de todas as contas |

"Atrasada" não é status: é `aberta` ou `andamento` com prazo antes de `medido_em`, e o
script calcula sozinho.
