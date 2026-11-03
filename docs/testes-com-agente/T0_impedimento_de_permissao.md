# T1_ativacao_explicita

**Pedido ao agente:** `/analise-olist Os dados estão em ./dados. Quantos pedidos entregues foram feitos em cada mês entre janeiro e março de 2018?`

**Ferramentas usadas pelo agente (na ordem):**

1. `Read: /home/claude/analise-olist-skill/.claude/skills/analise-olist/references/regras-e-metricas.md`
2. `Bash: ls dados; python3 .claude/skills/analise-olist/scripts/olist_analytics.py inspecionar --dados ./dados`

**Resposta do agente:**

Não consegui calcular a resposta. A execução de comandos (Bash) foi negada neste ambiente, porque o Claude Code está em modo "don't ask".

Os números só podem vir do script `olist_analytics.py`. Calcular sem rodá-lo, ou inventar valores, violaria a regra da skill.

**O que eu ia executar:**

```
python3 .claude/skills/analise-olist/scripts/olist_analytics.py inspecionar --dados ./dados
python3 .claude/skills/analise-olist/scripts/olist_analytics.py pedidos-por-mes --dados ./dados --inicio 2018-01 --fim 2018-03
```

Os parâmetros da análise já estão definidos:
- **Métrica:** `order_id` distintos com `order_status = delivered`.
- **Mês de referência:** `order_purchase_timestamp`.
- **Período:** 2018-01-01 a 2018-03-31, datas inclusivas, por dia do calendário.
- **Arquivos esperados:** `olist_orders_dataset` (`.csv` ou `.xlsx`) e `olist_customers_dataset`.

**Como seguir (escolha uma):**
1. Liberar a execução de comandos Bash, por exemplo trocando o modo de permissão. Eu rodo os dois comandos e devolvo a resposta completa: tabela mês a mês, total, cobertura, avisos e limitações.
2. Rodar os comandos acima por conta própria e colar a saída aqui. Eu interpreto e confiro a cobertura.

<!-- session_id: 8067c9d1-99e6-4f2e-aafd-04815991adf2 -->