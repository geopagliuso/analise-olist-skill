### $ python .claude/skills/analise-olist/scripts/olist_analytics.py pedidos-por-mes --dados dados

## pedidos-por-mes
**Métrica:** Quantidade de idPedido distintos com descSituacao = delivered, agrupados pelo mês de dtPedido.
**Filtros:** descSituacao = delivered (order_status); data de referência order_purchase_timestamp (dtPedido); período início da base a fim da base (datas inicial e final inclusivas, por dia do calendário); UF: todas
**Arquivos:** olist_orders_dataset.csv

| mês | pedidos entregues | mês parcial |
| --- | --- | --- |
| 2016-09 | 1 |  |
| 2016-10 | 265 |  |
| 2016-11 | 0 |  |
| 2016-12 | 1 |  |
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
| 2018-01 | 7069 |  |
| 2018-02 | 6555 |  |
| 2018-03 | 7003 |  |
| 2018-04 | 6798 |  |
| 2018-05 | 6749 |  |
| 2018-06 | 6099 |  |
| 2018-07 | 6159 |  |
| 2018-08 | 6351 |  |

**Total no período:** 96478

**Cobertura e conferências:** linhas_pedidos = 99441; linhas_entregues = 96478; sem_id = 0; repetidos_removidos = 0; entregues_distintos = 96478; sem_data_valida = 0; no_periodo = 96478; selecionados = 96478
[salvo] saidas/pedidos-por-mes__toda-a-base.json
[salvo] saidas/pedidos-por-mes__toda-a-base.csv
exit=0
