### $ python .claude/skills/analise-olist/scripts/olist_analytics.py top-ufs --dados dados

## top-ufs
**Métrica:** UFs (descUF) dos clientes com mais idPedido distintos entregues; pedido e cliente ligados por idCliente.
**Filtros:** descSituacao = delivered (order_status); data de referência order_purchase_timestamp (dtPedido); período início da base a fim da base (datas inicial e final inclusivas, por dia do calendário); UF: todas
**Arquivos:** olist_orders_dataset.csv, olist_customers_dataset.csv

| posição | UF | pedidos entregues | % dos pedidos com UF |
| --- | --- | --- | --- |
| 1 | SP | 40501 | 41.98 |
| 2 | RJ | 12350 | 12.8 |
| 3 | MG | 11354 | 11.77 |
| 4 | RS | 5345 | 5.54 |
| 5 | PR | 4923 | 5.1 |

**Pedidos com UF no período:** 96478 em 27 UF(s)

**Cobertura e conferências:** linhas_pedidos = 99441; linhas_entregues = 96478; sem_id = 0; repetidos_removidos = 0; entregues_distintos = 96478; sem_data_valida = 0; no_periodo = 96478; sem_cliente_correspondente = 0; cliente_sem_uf = 0; selecionados = 96478
[salvo] saidas/top-ufs__toda-a-base.json
[salvo] saidas/top-ufs__toda-a-base.csv
exit=0
