# T2_continuacao_so_SP

**Pedido ao agente:** `Agora só para clientes de SP.`

**Ferramentas usadas pelo agente (na ordem):**

1. `Bash: S=.claude/skills/analise-olist/scripts/olist_analytics.py; python3 $S pedidos-por-mes --dados ./dados --inicio 2018-01 --fim 2018-03 --uf SP; echo "exit=$?"; python3 $S pedidos-por-mes --dados ./dados --inicio 2018-01 --fim 2018-03 --json > /tmp/claude-0/-home-claude-analise-olist-skill/799ae900-bedd-476d-a895-0391a968add0/scratchpad/todas.json; python3 $S pedidos-por-mes --dados ./dados --inicio 2018-01 --fim 2018-03 --uf SP --json > /tmp/claude-0/-home-claude-analise-olist-skill/799ae900-bedd-476d-a895-0391a968add0/scratchpad/sp.json; head -c 1500 /tmp/claude-0/-home-claude-analise-olist-skill/799ae900-bedd-476d-a895-0391a968add0/scratchpad/sp.json`
2. `Bash: cd /tmp/claude-0/-home-claude-analise-olist-skill/799ae900-bedd-476d-a895-0391a968add0/scratchpad && python3 -I -c "
import json
a=json.load(open('todas.json'))['resultado'];s=json.load(open('sp.json'))['resultado']
for x,y in zip(a['linhas'],s['linhas']): print(x['mes'],x['pedidos'],y['pedidos'],round(100*y['pedidos']/x['pedidos'],1))
print(a['total'],s['total'],round(100*s['total']/a['total'],1))"`

**Resposta do agente:**

## Pedidos entregues por mês, só clientes de SP (jan–mar de 2018)

**O que mudou:** só o filtro de UF, que passou de todas as UFs para `customer_state = SP`. O período e o status continuam os mesmos. Executei o script de novo, sem reaproveitar os números anteriores.

**Métrica:** quantidade de `order_id` distintos com `order_status = delivered`, agrupados pelo mês de `order_purchase_timestamp`. Pedido e cliente são relacionados por `customer_id`.

**Filtros:** período de 2018-01-01 a 2018-03-31, com as duas datas inclusivas e comparadas por dia do calendário. UF do cliente: SP.

**Arquivos usados:** `olist_orders_dataset.csv` e `olist_customers_dataset.csv`

**Resultado, com a comparação com todas as UFs:**

| Mês | SP | Todas as UFs | SP / total |
| --- | --- | --- | --- |
| 2018-01 | 2.975 | 7.069 | 42,1% |
| 2018-02 | 2.632 | 6.555 | 40,2% |
| 2018-03 | 2.971 | 7.003 | 42,4% |
| **Total** | **8.578** | **20.627** | **41,6%** |

A coluna "Todas as UFs" vem da execução anterior, repetida por código. Os percentuais foram calculados por código a partir da saída `--json` das duas execuções.

**Comando executado:**
```
python .claude/skills/analise-olist/scripts/olist_analytics.py pedidos-por-mes --dados ./dados --inicio 2018-01 --fim 2018-03 --uf SP
```

**Cobertura e avisos:**
- 20.627 pedidos entregues caem no período, o mesmo número da análise sem filtro de UF. Desses, 8.578 são de clientes de SP, igual ao total da tabela, então a conferência fecha.
- Nenhum pedido ficou sem cliente correspondente (`sem_cliente_correspondente = 0`) e nenhum cliente está sem UF (`cliente_sem_uf = 0`). Portanto, nenhum pedido deixou de ser classificado por UF.
- O script não emitiu avisos. Nenhum mês é parcial e nenhum ficou sem pedidos.

**Limitações:**
- Os pedidos contam pela data da compra, não pela data da entrega, e só entram os com status `delivered`.
- A UF é a do cadastro do cliente em cada pedido (`customer_id`), que não é necessariamente a UF de entrega.
- Os nomes da atividade foram associados às colunas em inglês por uma correspondência confirmada pelo usuário, não por um dicionário oficial.

<!-- session_id: 799ae900-bedd-476d-a895-0391a968add0 -->