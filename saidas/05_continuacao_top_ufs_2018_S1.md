### $ python .claude/skills/analise-olist/scripts/olist_analytics.py top-ufs --dados dados --inicio 2018-01 --fim 2018-06

## top-ufs
**Métrica:** UFs (descUF) dos clientes com mais idPedido distintos entregues; pedido e cliente ligados por idCliente.
**Filtros:** descSituacao = delivered (order_status); data de referência order_purchase_timestamp (dtPedido); período 2018-01-01 a 2018-06-30 (datas inicial e final inclusivas, por dia do calendário); UF: todas
**Arquivos:** olist_orders_dataset.csv, olist_customers_dataset.csv

| posição | UF | pedidos entregues | % dos pedidos com UF |
| --- | --- | --- | --- |
| 1 | SP | 17456 | 43.34 |
| 2 | RJ | 4923 | 12.22 |
| 3 | MG | 4735 | 11.76 |
| 4 | RS | 2136 | 5.3 |
| 5 | PR | 2070 | 5.14 |

**Pedidos com UF no período:** 40273 em 27 UF(s)

**Cobertura e conferências:** linhas_pedidos = 99441; linhas_entregues = 96478; sem_id = 0; repetidos_removidos = 0; entregues_distintos = 96478; sem_data_valida = 0; no_periodo = 40273; sem_cliente_correspondente = 0; cliente_sem_uf = 0; selecionados = 40273
[salvo] saidas/top-ufs__2018-01-01_2018-06-30.json
[salvo] saidas/top-ufs__2018-01-01_2018-06-30.csv
exit=0
