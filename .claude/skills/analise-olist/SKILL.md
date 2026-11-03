---
name: analise-olist
description: "Copiloto de analytics sobre a base Olist (marketplace brasileiro). Responde em linguagem natural, executando código Python sobre os arquivos CSV/XLSX do Olist, a: quantos pedidos entregues por mês, quais as cinco UFs dos clientes com mais pedidos entregues e qual o ticket médio do preço dos itens por pedido entregue (sem frete), com período e UF ajustáveis em pedidos de continuação. Use para qualquer pergunta sobre pedidos, vendas, clientes, margem, lucro ou outras métricas da base Olist, mesmo quando não for claro se os dados permitem responder: a skill confere as colunas existentes, calcula o que a base suporta e recusa, sem estimar, o que ela não contém (custo, lucro, devoluções). Não use para dashboards, previsões ou outras bases."
---

# Análise Olist: copiloto de analytics

Autor: George Pagliuso.

## 1. Tarefa e resultado esperado

Responda perguntas sobre pedidos, vendas e clientes do marketplace Olist para a equipe do marketplace, consultando os arquivos de dados por código e entregando uma resposta que a pessoa consiga conferir.

- **Objetivo:** transformar uma pergunta em linguagem natural em uma análise executada, explicada e reproduzível, e continuar a investigação a partir de novos pedidos.
- **Incluído (primeira versão):** três análises sobre pedidos entregues: pedidos por mês, ranking das UFs dos clientes e ticket médio do preço dos itens por pedido, sem frete. Período, UF e tamanho do ranking são parâmetros que o usuário pode mudar na conversa.
- **Fora do escopo:** criar dashboard, chatbot ou servidor MCP; prever o futuro; usar dados que não estejam nos arquivos; alterar os arquivos originais; analisar outras bases.

## 2. Quando usar

Use esta skill quando o usuário fizer uma pergunta sobre pedidos, vendas ou clientes do Olist, ou pedir para mudar o período, a UF ou o tamanho do ranking de uma análise anterior desta skill.

Distinções: uma pergunta sobre dados do Olist que as três análises não cobrem (por exemplo, pagamentos, avaliações, vendedores) é tratada conforme `references/limites-da-base.md`, sem improvisar. Uma pergunta sobre outra base de dados, ou um pedido de código sem relação com o Olist, não precisa desta skill.

## 3. Entradas

| Entrada | Formato ou origem | Obrigatória | Como usar ou validar |
| --- | --- | --- | --- |
| Pergunta | Texto do usuário | Sim | Identificar qual das três análises é pedida (seção 6). |
| Pasta dos dados | Caminho informado pelo usuário, `--dados` ou variável `OLIST_DATA_DIR` | Sim | Se faltar, perguntar onde estão os arquivos. Nunca presumir um caminho da máquina do autor. Conferir com o comando `inspecionar`. |
| Período | Datas inicial e/ou final em `AAAA-MM-DD` ou `AAAA-MM` | Não | Padrão acordado: sem período, usa toda a base. Datas **inclusivas**, por dia do calendário. |
| UF do cliente | Sigla com 2 letras (ex.: SP) | Não | Padrão: todas as UFs. |
| Tamanho do ranking | Inteiro | Não | Padrão acordado: 5. |
| Pasta de saída | Caminho fora da pasta dos dados | Não | Só quando o usuário pedir arquivos; usar `--saida`. |

Quando faltar uma entrada que altere o resultado (a pasta dos dados, ou um período dito de forma relativa como "mês passado" ou "último trimestre"), pergunte antes de executar. Para uma entrada inválida (data inexistente, data inicial depois da final, arquivo ou coluna ausente), mostre a mensagem de erro do script, explique o impedimento em português simples e peça a correção; não calcule com valores adivinhados.

## 4. Saída

- **Entrega:** resposta em português com, nesta ordem: pergunta entendida, **métrica**, **filtros**, **arquivos usados**, **resultado** (tabela quando houver mais de um valor), **código ou comando executado com a saída relevante**, **cobertura e avisos**, **limitações**.
- **Formato:** texto em Markdown, tabela para séries e rankings. Gráfico só se ajudar e o usuário pedir ou concordar.
- **Destino:** a resposta fica na conversa. Arquivos só quando o usuário pedir, com `--saida <pasta>`, fora da pasta dos dados e sem sobrescrever sem autorização (`--sobrescrever`).
- **Evidências:** o comando executado, o trecho da saída que contém os números e as contagens de cobertura (quantos pedidos entraram em cada etapa).

Quando o usuário fizer um pedido de continuação, diga o que mudou (período, UF, ranking), execute o código de novo e explique o novo resultado. Nunca reaproveite números da resposta anterior.

## 5. Regras específicas da tarefa

As regras completas, a correspondência de nomes e o tratamento de dados problemáticos estão em `references/regras-e-metricas.md`. Leia esse arquivo antes da primeira análise da conversa. Em resumo:

1. Pedido entregue é `order_status` (descSituacao) igual a `delivered`; a data de referência é `order_purchase_timestamp` (dtPedido).
2. Conte `order_id` (idPedido) **distintos**.
3. O ranking de UFs relaciona pedido e cliente por `customer_id` (idCliente) e usa `customer_state` (descUF).
4. Ticket médio = soma de `price` (vlPreco) dos itens dos pedidos selecionados ÷ número de pedidos distintos selecionados. **Sem frete.** Não confunda preço do item, frete e `payment_value` (vlPagamento).
5. Um pedido tem vários itens e vários pagamentos: some por pedido antes de relacionar tabelas, para não multiplicar valores. O script já faz isso.
6. Contagem sem pedidos é **zero**; média sem pedidos é **não aplicável**. Se houver pedidos sem itens, explique a cobertura.
7. Informe sempre o período e a convenção das datas (inclusivas, por dia).

## 6. Procedimento

### Compreender o pedido

1. Identifique a análise: `pedidos-por-mes`, `top-ufs` ou `ticket-medio`; e os parâmetros (período, UF, tamanho do ranking). Converta "janeiro a março de 2018" em `--inicio 2018-01 --fim 2018-03`.
2. Se a pasta dos dados for nova na conversa, rode `inspecionar` para conferir quais arquivos e colunas existem e leia `references/regras-e-metricas.md`.
3. Se a pergunta não puder ser respondida com as colunas existentes, ou estiver fora das três análises, consulte `references/limites-da-base.md` e siga a classificação de lá.
4. Resolva ambiguidades que mudem o resultado (por exemplo, "vendas" como valor ou como número de pedidos, ou outro status que não `delivered`). Quando usar um padrão acordado, informe qual.

### Executar a tarefa

5. Execute o script com os parâmetros (seção 8). Prefira a saída em Markdown para mostrar ao usuário; use `--json` quando precisar ler campos com precisão.
6. Em um pedido de continuação, altere só o parâmetro pedido e execute de novo.

### Conferir o resultado

7. Leia a seção de cobertura e os avisos da saída: o total da tabela deve bater com `selecionados`; se houver pedidos sem itens, preços inválidos, datas inválidas, repetições ou clientes sem correspondência, relate cada um.
8. Para períodos vazios ou UF inexistente, confirme que a contagem é zero e o ticket é "não aplicável".
9. Se algo divergir, identifique a causa (parâmetro mal interpretado, arquivo diferente, dado inválido), corrija e execute de novo. Se não for possível resolver, relate o impedimento e o que ficou sem verificar.

### Entregar

10. Apresente a resposta no formato da seção 4.
11. Informe as decisões padrão usadas, as limitações de qualidade dos dados e as pendências.

## 7. Recursos de apoio

- **Referências:** `references/regras-e-metricas.md` — ler antes da primeira análise e quando houver dúvida sobre regra, chave, tratamento de dados ou convenção de datas.
- **Referências:** `references/limites-da-base.md` — ler quando a pergunta fugir das três análises ou parecer pedir um dado que a base talvez não tenha.
- **Scripts:** `scripts/olist_analytics.py` — executar para toda análise numérica; contém as regras já aplicadas e nunca grava na pasta dos dados.

Resolva os caminhos dos recursos a partir da pasta da skill (`.claude/skills/analise-olist/` no projeto local do Claude Code). A pasta dos dados fica fora do repositório: informe-a com `--dados` ou com a variável `OLIST_DATA_DIR`.

## 8. Ambiente e ferramentas

- **Ferramentas necessárias:** execução de comandos (shell) e leitura de arquivos.
- **Dependências:** Python 3 e `pandas`; `openpyxl` só se os dados estiverem em `.xlsx`. Instalação: `pip install -r requirements.txt` na raiz do repositório. Testado com Python 3.13 e pandas 3.0.5.
- **Execução** (a partir da raiz do projeto; use `python3` se `python` não existir):

```
python .claude/skills/analise-olist/scripts/olist_analytics.py <analise> --dados <pasta> [--inicio AAAA-MM[-DD]] [--fim AAAA-MM[-DD]] [--uf SP] [--top 5] [--json] [--saida <pasta>] [--sobrescrever]
```

  `<analise>` é `pedidos-por-mes`, `top-ufs`, `ticket-medio` ou `inspecionar`. Código de saída 0 = sucesso; 2 = entrada ausente ou inválida (mensagem em `stderr`).
- **Verificação do código:** `python -m pytest -q` na raiz do repositório.
- **Se o recurso não estiver disponível:** sem permissão para executar comandos, ou sem acesso aos arquivos, explique o impedimento e o que o usuário pode fazer (informar a pasta, liberar a execução). Não calcule de cabeça e não invente números.

Não descreva uma operação como executada quando ela tiver sido apenas proposta. Todo número apresentado como calculado deve vir da saída de uma execução feita nesta conversa, que o usuário deve poder ver. Isso vale também para percentuais e diferenças entre execuções: calcule-os por código (por exemplo, a partir da saída `--json`) ou não os apresente.

## 9. Limites de atuação

- **Preservar:** os arquivos originais de dados (somente leitura) e as decisões acordadas: pedidos entregues, dtPedido como referência, datas inclusivas, ticket sem frete, denominador por pedidos distintos.
- **Alterações previstas:** apenas arquivos de saída, quando o usuário pedir, em pasta separada. Não altere o script nem as referências para fazer um resultado "bater"; se achar que há erro nas regras, aponte e peça decisão.
- **Decisões a esclarecer:** período relativo, significado de "vendas" ou de outro status, e qualquer extensão fora das três análises.

## 10. Critérios de conclusão

Considere a tarefa concluída quando:

- a resposta traz métrica, filtros, arquivos, resultado, código ou comando executado com a saída relevante, cobertura e limitações;
- os números vieram de uma execução feita na conversa e a cobertura foi conferida (total da tabela igual aos pedidos selecionados);
- períodos vazios aparecem como zero (contagens) ou "não aplicável" (médias), e perguntas sem resposta possível foram recusadas com o motivo;
- o pedido de continuação foi executado de novo, e a diferença para a resposta anterior foi explicada.

Se um critério não puder ser verificado, informe essa limitação sem apresentá-lo como atendido.

## 11. Exemplos de uso

### Pedido pertinente

> Os dados estão em ./dados. Quantos pedidos entregues foram feitos em cada mês entre janeiro e março de 2018?

**Resultado esperado:** o agente roda `pedidos-por-mes --inicio 2018-01 --fim 2018-03`, mostra a tabela mês a mês (meses sem pedido com zero), o total, os filtros (entregues, dtPedido, datas inclusivas), os arquivos lidos, o comando e os avisos de cobertura.

Continuação: "Agora só para clientes de SP" → o agente repete a execução com `--uf SP`, informa que mudou apenas a UF e compara com o resultado anterior.

### Entrada ausente ou inválida

> Qual o ticket médio de ontem?  (sem informar a pasta dos dados)

**Comportamento esperado:** o agente pergunta onde estão os arquivos do Olist e a que data "ontem" se refere (a base é histórica), em vez de executar com um palpite. Com uma data impossível (por exemplo 2018-02-31), mostra o erro do script e pede a correção.

### Pergunta que a base não permite responder

> Qual foi a margem de lucro por categoria de produto?

**Comportamento esperado:** o agente consulta `inspecionar` e `references/limites-da-base.md`, explica que a base não tem custo nem lucro, não apresenta número algum e oferece a pergunta mais próxima que a base responde (por exemplo, ticket médio do preço dos itens).

### Pedido fora do escopo

> Crie um dashboard e uma previsão de vendas para o próximo trimestre.

**Comportamento esperado:** o agente informa que a skill não cria dashboards nem previsões e propõe o que pode fazer dentro das três análises.
