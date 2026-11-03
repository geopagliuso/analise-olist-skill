# T3_selecao_automatica_top_ufs

**Pedido ao agente:** `Quais são as cinco UFs dos clientes com mais pedidos entregues? Os arquivos do Olist estão na pasta ./dados`

**Ferramentas usadas pelo agente (na ordem):**

1. `Skill: analise-olist`
2. `Read: /home/claude/analise-olist-skill/.claude/skills/analise-olist/references/regras-e-metricas.md`
3. `Bash: python3 .claude/skills/analise-olist/scripts/olist_analytics.py inspecionar --dados ./dados`
4. `Bash: python3 .claude/skills/analise-olist/scripts/olist_analytics.py top-ufs --dados ./dados --top 5`

**Resposta do agente:**

## UFs com mais pedidos entregues

**Pergunta:** quais são as cinco UFs dos clientes com mais pedidos entregues?

**Métrica:** quantidade de pedidos (`order_id` distintos) com `order_status = delivered`, agrupados pela UF do cliente (`customer_state`). Pedido e cliente são ligados por `customer_id`.

**Filtros:** só pedidos entregues. Sem período, então usei toda a base, com `order_purchase_timestamp` como data de referência. Sem filtro de UF, e o ranking tem as 5 primeiras (o padrão).

**Arquivos usados:** `olist_orders_dataset.csv` e `olist_customers_dataset.csv`, da pasta `./dados`.

**Resultado:**

| Posição | UF | Pedidos entregues | % dos pedidos com UF |
| --- | --- | --- | --- |
| 1 | SP | 40.501 | 41,98% |
| 2 | RJ | 12.350 | 12,80% |
| 3 | MG | 11.354 | 11,77% |
| 4 | RS | 5.345 | 5,54% |
| 5 | PR | 4.923 | 5,10% |

**Comando executado:**
```
python .claude/skills/analise-olist/scripts/olist_analytics.py top-ufs --dados ./dados --top 5
```

**Cobertura e avisos:** a base tem 99.441 pedidos, dos quais 96.478 estão entregues. Todos os 96.478 entraram no ranking (27 UFs). Não houve pedido sem cliente correspondente, cliente sem UF, data inválida nem `order_id` repetido, e o total selecionado bate com o total entregue. O script não emitiu avisos.

**Limitações:**
- O ranking conta pedidos, não pessoas. Quem comprou mais de uma vez tem mais de um `customer_id`.
- Usei a correspondência de nomes em inglês dos arquivos públicos do Olist, confirmada pelo George. O `dicionario.xlsx` do professor não estava disponível.

Posso repetir a análise para outro período ou outro tamanho de ranking.

<!-- session_id: 51cd1bda-82ab-4a8a-b6ec-c63538264a15 -->