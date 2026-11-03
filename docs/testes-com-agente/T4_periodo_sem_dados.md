# T4_periodo_sem_dados

**Pedido ao agente:** `Os dados do Olist estão em ./dados. Qual foi o ticket médio dos itens por pedido entregue em 2019?`

**Ferramentas usadas pelo agente (na ordem):**

1. `Skill: analise-olist`
2. `Read: /home/claude/analise-olist-skill/.claude/skills/analise-olist/references/regras-e-metricas.md`
3. `Bash: python3 .claude/skills/analise-olist/scripts/olist_analytics.py inspecionar --dados ./dados`
4. `Bash: python3 .claude/skills/analise-olist/scripts/olist_analytics.py ticket-medio --dados ./dados --inicio 2019-01-01 --fim 2019-12-31`
5. `Bash: python3 .claude/skills/analise-olist/scripts/olist_analytics.py pedidos-por-mes --dados ./dados`

**Resposta do agente:**

Não dá para calcular o ticket médio de 2019, porque a base não tem pedidos entregues nesse ano. O resultado é **não aplicável**, e não zero.

**Métrica:** soma de `price` dos itens dos pedidos entregues, dividida pelos `order_id` distintos entregues. O frete não entra.

**Filtros:** `order_status = delivered`, data de referência `order_purchase_timestamp`, período de 2019-01-01 a 2019-12-31 (datas inclusivas, por dia), todas as UFs.

**Arquivos usados:** `olist_orders_dataset.csv` e `olist_order_items_dataset.csv`, em `./dados`.

**Comando executado:**
```
python3 .claude/skills/analise-olist/scripts/olist_analytics.py ticket-medio --dados ./dados --inicio 2019-01-01 --fim 2019-12-31
```

**Resultado:** o denominador (pedidos entregues em 2019) é 0, então o ticket médio é não aplicável.

**Cobertura:**
- A base tem 99.441 pedidos, dos quais 96.478 são entregues.
- Nenhum pedido tem data inválida e nenhum `order_id` está repetido.
- Dos entregues, 0 caíram em 2019.

**Por que não há pedidos em 2019:** rodei também a contagem de pedidos entregues por mês, sobre a base inteira. Os pedidos vão de **setembro de 2016 a agosto de 2018**. O último mês com pedidos é 2018-08, com 6.351 entregues.

**Limitação:** não estimei nenhum valor para 2019.

Posso recalcular para outro período. Alguns exemplos:
- 2018, o último ano com dados quase completos (até agosto).
- 2017, o único ano completo.
- Um período em que você tenha acertado o ano por engano, por exemplo 2018 em vez de 2019.

<!-- session_id: b908cdaa-a04b-4b23-8c41-1848c3ffd409 -->