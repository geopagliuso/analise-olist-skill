### $ python .claude/skills/analise-olist/scripts/olist_analytics.py ticket-medio --dados dados

## ticket-medio
**Métrica:** Soma de vlPreco dos itens dos pedidos entregues selecionados dividida pelo número de idPedido distintos selecionados, sem vlFrete.
**Filtros:** descSituacao = delivered (order_status); data de referência order_purchase_timestamp (dtPedido); período início da base a fim da base (datas inicial e final inclusivas, por dia do calendário); UF: todas
**Arquivos:** olist_orders_dataset.csv, olist_order_items_dataset.csv

| indicador | valor |
| --- | --- |
| pedidos entregues distintos (denominador) | 96478 |
| itens | 110197 |
| pedidos com itens | 96478 |
| cobertura de itens (%) | 100.0 |
| soma de vlPreco (sem frete) | 13211395.96 |
| **ticket médio** | 136.94 |
| ticket médio só dos pedidos com itens | 136.94 |

**Cobertura e conferências:** linhas_pedidos = 99441; linhas_entregues = 96478; sem_id = 0; repetidos_removidos = 0; entregues_distintos = 96478; sem_data_valida = 0; no_periodo = 96478; selecionados = 96478; itens_com_pedido_inexistente = 0; precos_invalidos = 168; pedidos_com_itens = 96478; pedidos_sem_itens = 0

**Avisos:**
- 168 item(ns) dos pedidos selecionados têm preço (vlPreco) ausente ou não numérico (ex.: célula convertida em data) e foram ignorados na soma; o ticket pode estar subestimado.
[salvo] saidas/ticket-medio__toda-a-base.json
[salvo] saidas/ticket-medio__toda-a-base.csv
exit=0
