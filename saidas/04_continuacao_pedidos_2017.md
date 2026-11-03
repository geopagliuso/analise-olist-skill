### $ python .claude/skills/analise-olist/scripts/olist_analytics.py pedidos-por-mes --dados dados --inicio 2017-01 --fim 2017-12

## pedidos-por-mes
**Métrica:** Quantidade de idPedido distintos com descSituacao = delivered, agrupados pelo mês de dtPedido.
**Filtros:** descSituacao = delivered (order_status); data de referência order_purchase_timestamp (dtPedido); período 2017-01-01 a 2017-12-31 (datas inicial e final inclusivas, por dia do calendário); UF: todas
**Arquivos:** olist_orders_dataset.csv

| mês | pedidos entregues | mês parcial |
| --- | --- | --- |
| 2017-01 | 750 |  |
| 2017-02 | 1653 |  |
| 2017-03 | 2546 |  |
| 2017-04 | 2303 |  |
| 2017-05 | 3546 |  |
| 2017-06 | 3135 |  |
| 2017-07 | 3872 |  |
| 2017-08 | 4193 |  |
| 2017-09 | 4150 |  |
| 2017-10 | 4478 |  |
| 2017-11 | 7289 |  |
| 2017-12 | 5513 |  |

**Total no período:** 43428

**Cobertura e conferências:** linhas_pedidos = 99441; linhas_entregues = 96478; sem_id = 0; repetidos_removidos = 0; entregues_distintos = 96478; sem_data_valida = 0; no_periodo = 43428; selecionados = 43428
[salvo] saidas/pedidos-por-mes__2017-01-01_2017-12-31.json
[salvo] saidas/pedidos-por-mes__2017-01-01_2017-12-31.csv
exit=0
