### $ python .claude/skills/analise-olist/scripts/olist_analytics.py pedidos-por-mes --dados dados --inicio 2019-01 --fim 2019-03

## pedidos-por-mes
**Métrica:** Quantidade de idPedido distintos com descSituacao = delivered, agrupados pelo mês de dtPedido.
**Filtros:** descSituacao = delivered (order_status); data de referência order_purchase_timestamp (dtPedido); período 2019-01-01 a 2019-03-31 (datas inicial e final inclusivas, por dia do calendário); UF: todas
**Arquivos:** olist_orders_dataset.csv

| mês | pedidos entregues | mês parcial |
| --- | --- | --- |
| 2019-01 | 0 |  |
| 2019-02 | 0 |  |
| 2019-03 | 0 |  |

**Total no período:** 0

**Cobertura e conferências:** linhas_pedidos = 99441; linhas_entregues = 96478; sem_id = 0; repetidos_removidos = 0; entregues_distintos = 96478; sem_data_valida = 0; no_periodo = 0; selecionados = 0

**Avisos:**
- Nenhum pedido entregue no período/filtros informados: contagem = 0.
[salvo] saidas/pedidos-por-mes__2019-01-01_2019-03-31.json
[salvo] saidas/pedidos-por-mes__2019-01-01_2019-03-31.csv
exit=0
