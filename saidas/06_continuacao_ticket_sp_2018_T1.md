### $ python .claude/skills/analise-olist/scripts/olist_analytics.py ticket-medio --dados dados --inicio 2018-01 --fim 2018-03 --uf SP

## ticket-medio
**Métrica:** Soma de vlPreco dos itens dos pedidos entregues selecionados dividida pelo número de idPedido distintos selecionados, sem vlFrete.
**Filtros:** descSituacao = delivered (order_status); data de referência order_purchase_timestamp (dtPedido); período 2018-01-01 a 2018-03-31 (datas inicial e final inclusivas, por dia do calendário); UF: SP
**Arquivos:** olist_orders_dataset.csv, olist_customers_dataset.csv, olist_order_items_dataset.csv

| indicador | valor |
| --- | --- |
| pedidos entregues distintos (denominador) | 8578 |
| itens | 9816 |
| pedidos com itens | 8578 |
| cobertura de itens (%) | 100.0 |
| soma de vlPreco (sem frete) | 1053156.63 |
| **ticket médio** | 122.77 |
| ticket médio só dos pedidos com itens | 122.77 |

**Cobertura e conferências:** linhas_pedidos = 99441; linhas_entregues = 96478; sem_id = 0; repetidos_removidos = 0; entregues_distintos = 96478; sem_data_valida = 0; no_periodo = 20627; sem_cliente_correspondente = 0; cliente_sem_uf = 0; selecionados = 8578; itens_com_pedido_inexistente = 0; precos_invalidos = 15; pedidos_com_itens = 8578; pedidos_sem_itens = 0

**Avisos:**
- 15 item(ns) dos pedidos selecionados têm preço (vlPreco) ausente ou não numérico (ex.: célula convertida em data) e foram ignorados na soma; o ticket pode estar subestimado.
[salvo] saidas/ticket-medio__2018-01-01_2018-03-31__UF-SP.json
[salvo] saidas/ticket-medio__2018-01-01_2018-03-31__UF-SP.csv
exit=0
