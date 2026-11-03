### $ python .claude/skills/analise-olist/scripts/olist_analytics.py top-ufs --dados dados --inicio 2019-01 --fim 2019-03

## top-ufs
**Métrica:** UFs (descUF) dos clientes com mais idPedido distintos entregues; pedido e cliente ligados por idCliente.
**Filtros:** descSituacao = delivered (order_status); data de referência order_purchase_timestamp (dtPedido); período 2019-01-01 a 2019-03-31 (datas inicial e final inclusivas, por dia do calendário); UF: todas
**Arquivos:** olist_orders_dataset.csv, olist_customers_dataset.csv

| posição | UF | pedidos entregues | % dos pedidos com UF |
| --- | --- | --- | --- |

**Pedidos com UF no período:** 0 em 0 UF(s)

**Cobertura e conferências:** linhas_pedidos = 99441; linhas_entregues = 96478; sem_id = 0; repetidos_removidos = 0; entregues_distintos = 96478; sem_data_valida = 0; no_periodo = 0; sem_cliente_correspondente = 0; cliente_sem_uf = 0; selecionados = 0

**Avisos:**
- Nenhum pedido entregue no período/filtros informados: ranking vazio.
[salvo] saidas/top-ufs__2019-01-01_2019-03-31.json
[salvo] saidas/top-ufs__2019-01-01_2019-03-31.csv
exit=0
