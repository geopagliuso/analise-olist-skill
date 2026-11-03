# T1_ativacao_explicita

**Pedido ao agente:** `/analise-olist Os dados estão em ./dados. Quantos pedidos entregues foram feitos em cada mês entre janeiro e março de 2018?`

**Ferramentas usadas pelo agente (na ordem):**

1. `Read: /home/claude/analise-olist-skill/.claude/skills/analise-olist/references/regras-e-metricas.md`
2. `Bash: python3 .claude/skills/analise-olist/scripts/olist_analytics.py inspecionar --dados ./dados; echo "exit=$?"`
3. `Bash: python3 .claude/skills/analise-olist/scripts/olist_analytics.py pedidos-por-mes --dados ./dados --inicio 2018-01 --fim 2018-03; echo "exit=$?"`

**Resposta do agente:**

## Pedidos entregues por mês, jan–mar de 2018

**Pergunta entendida:** quantos pedidos entregues foram feitos em cada mês de janeiro a março de 2018.

**Métrica:** quantidade de `order_id` distintos com `order_status = delivered`, agrupados pelo mês de `order_purchase_timestamp`.

**Filtros:** período de 2018-01-01 a 2018-03-31, com as duas datas inclusivas e comparadas por dia do calendário. Todas as UFs.

**Arquivo usado:** `olist_orders_dataset.csv`

**Resultado:**

| Mês | Pedidos entregues |
| --- | --- |
| 2018-01 | 7.069 |
| 2018-02 | 6.555 |
| 2018-03 | 7.003 |
| **Total** | **20.627** |

**Comando executado:**
```
python .claude/skills/analise-olist/scripts/olist_analytics.py pedidos-por-mes --dados ./dados --inicio 2018-01 --fim 2018-03
```

**Cobertura e avisos:**
- A base tem 99.441 linhas de pedidos, e 96.478 delas são entregues.
- Todas as 96.478 têm `order_id` distinto, sem repetições, sem `order_id` ausente e sem data inválida.
- 20.627 pedidos caem no período. Esse número é igual ao total da tabela, então a conferência fecha.
- Nenhum mês é parcial e nenhum mês ficou sem pedidos.

**Limitações:**
- A data de referência é a da compra, não a da entrega. Um pedido feito em março e entregue em abril conta em março.
- Só entram pedidos com status `delivered`. Pedidos enviados, cancelados e os demais ficam fora.
- Os nomes da atividade (`idPedido`, `dtPedido` etc.) foram associados às colunas em inglês por uma correspondência confirmada pelo usuário. Ela não veio de um dicionário oficial.

<!-- session_id: 799ae900-bedd-476d-a895-0391a968add0 -->