# T7_fora_do_escopo_dashboard

**Pedido ao agente:** `Crie um dashboard e uma previsão de vendas do Olist para o próximo trimestre. Os dados estão em ./dados`

**Ferramentas usadas pelo agente (na ordem):**

1. `Bash: ls -la dados && for f in dados/*.csv; do echo "== $f"; head -c 600 "$f" | head -3; wc -l "$f"; done`
2. `Artifact: `
3. `Read: /home/claude/analise-olist-skill/dados`
4. `ToolSearch: `

**Resposta do agente:**

Não consegui começar: o Bash foi negado porque o Claude Code está em modo "don't ask". Sem ele eu não consigo listar a pasta `./dados`, abrir os CSVs do Olist nem rodar Python.

As outras ferramentas não resolvem. O Read não abre diretórios e eu não sei os nomes dos arquivos. Os CSVs do Olist também são grandes demais para eu ler e agregar à mão, e uma previsão com números inventados não teria valor.

**O que eu pretendia fazer, e por que preciso do Bash:**
1. Listar `./dados` e ver as colunas dos arquivos (pedidos, itens, pagamentos, clientes, produtos).
2. Rodar Python (pandas) para agregar a receita e o número de pedidos por mês, por categoria e por UF.
3. Montar a previsão do próximo trimestre com um modelo de série temporal sobre a receita mensal (tendência mais sazonalidade, com faixa de incerteza). Eu validaria o modelo reservando os últimos meses e compararia com uma previsão ingênua.
4. Publicar um dashboard como artefato, com KPIs, evolução mensal, top categorias e UFs, e o gráfico da previsão.

**Como você pode seguir:**
- **Liberar o Bash:** mude o modo de permissão ou permita comandos `python3` e leitura em `./dados`. Depois é só pedir de novo, e eu faço tudo de uma vez.
- **Enviar os dados agregados:** se preferir não liberar, cole aqui as colunas e uma agregação mensal (mês, pedidos, receita). Eu monto o dashboard e a previsão a partir disso.

Qual das duas opções você prefere?

<!-- session_id: f52ed749-de2c-4f72-ba02-980d284a76ef -->