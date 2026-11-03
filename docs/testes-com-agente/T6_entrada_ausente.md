# T6_entrada_ausente

**Pedido ao agente:** `Qual o ticket médio de ontem no Olist?`

**Ferramentas usadas pelo agente (na ordem):**

1. `Skill: analise-olist`
2. `Bash: echo "OLIST_DATA_DIR=${OLIST_DATA_DIR:-<não definida>}"; ls /home/claude/analise-olist-skill`

**Resposta do agente:**

Ainda não consegui calcular o ticket médio de ontem (02/11/2026). Faltam duas informações, e a execução de comandos foi negada neste modo, então também não pude procurar a pasta dos dados.

**O que preciso de você**

1. **Onde estão os arquivos do Olist?** Preciso do caminho da pasta, ou da variável `OLIST_DATA_DIR` definida. Não vou presumir um caminho.
2. **Qual período você quer?** A base do Olist é histórica e, pelo que sei dela, termina em 2018. Para 02/11/2026 o resultado quase certamente seria zero pedidos e ticket médio "não aplicável". Algumas alternativas:
   - rodar mesmo assim para 2026-11-02 e confirmar que está vazio;
   - usar o último dia disponível na base (posso descobrir com `inspecionar`);
   - indicar uma data ou período específico, por exemplo `2018-08` ou `2018-08-15`.

**Como vou calcular**
- Só entram pedidos com `order_status = delivered`, pela data de `order_purchase_timestamp`.
- O ticket médio é a soma de `price` dos itens dividida pelo número de pedidos distintos. O frete fica de fora.
- As datas são inclusivas, por dia do calendário.

**O que falta para eu rodar**
- Responda as duas perguntas acima.
- Libere a execução de comandos (Bash), porque o cálculo roda por script Python.

<!-- session_id: fd20e1cd-037f-4cd7-8aa0-93c6dbb7af61 -->