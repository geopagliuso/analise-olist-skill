### $ python .claude/skills/analise-olist/scripts/olist_analytics.py ticket-medio --dados dados --inicio 2019-01 --fim 2019-03

## ticket-medio
**Métrica:** Soma de vlPreco dos itens dos pedidos entregues selecionados dividida pelo número de idPedido distintos selecionados, sem vlFrete.
**Filtros:** descSituacao = delivered (order_status); data de referência order_purchase_timestamp (dtPedido); período 2019-01-01 a 2019-03-31 (datas inicial e final inclusivas, por dia do calendário); UF: todas
**Arquivos:** olist_orders_dataset.csv, olist_order_items_dataset.csv

| indicador | valor |
| --- | --- |
| pedidos entregues distintos (denominador) | 0 |
| itens | 0 |
| pedidos com itens | 0 |
| cobertura de itens (%) | não aplicável |
| soma de vlPreco (sem frete) | 0.0 |
| **ticket médio** | não aplicável (sem pedidos) |
| ticket médio só dos pedidos com itens | não aplicável |

**Cobertura e conferências:** linhas_pedidos = 99441; linhas_entregues = 96478; sem_id = 0; repetidos_removidos = 0; entregues_distintos = 96478; sem_data_valida = 0; no_periodo = 0; selecionados = 0; itens_com_pedido_inexistente = 0; precos_invalidos = 0; pedidos_com_itens = 0; pedidos_sem_itens = 0

**Avisos:**
- Nenhum pedido entregue no período/filtros informados: ticket médio não aplicável.
[salvo] saidas/ticket-medio__2019-01-01_2019-03-31.json
[salvo] saidas/ticket-medio__2019-01-01_2019-03-31.csv
exit=0
