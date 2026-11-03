# Roteiro para o print do copiloto em uso

Autor: George Pagliuso. A lista pede **um print legível do copiloto em uso, mostrando uma pergunta, a execução de código e a resposta**. O print mais fiel é o da sua própria sessão do Claude Code, com a skill instalada em `.claude/skills/analise-olist/`.

## Preparação (uma vez)

1. Clone o repositório e entre na pasta dele:
   ```
   git clone <link-do-seu-repositorio> analise-olist-skill
   cd analise-olist-skill
   ```
2. Instale as dependências: `pip install -r requirements.txt` (para ler `.xlsx` o `openpyxl` já está na lista).
3. Deixe os arquivos do Olist numa pasta **fora** do repositório, com os nomes `olist_orders_dataset`, `olist_order_items_dataset` e `olist_customers_dataset` (`.csv` ou `.xlsx`). Anote o caminho. Com `.csv` a resposta sai em segundos; com `.xlsx`, cerca de 40 segundos por execução.
4. (Opcional) Defina a pasta uma vez: PowerShell `$env:OLIST_DATA_DIR = "C:\caminho\da\pasta"`.
5. Abra o Claude Code **na raiz do repositório** (`claude`). Digite `/` e confira que `analise-olist` aparece na lista. Se ficou vazio, você não está na raiz do repositório.

## Sequência sugerida

Faça estas perguntas na mesma conversa. Diga o caminho da pasta na primeira.

1. `/analise-olist Os dados estão em <caminho da pasta>. Quantos pedidos entregues foram feitos em cada mês?`
2. Continuação: `Agora só de janeiro a março de 2018.`
3. Continuação: `Agora só para clientes de SP.`
4. `Quais são as cinco UFs dos clientes com mais pedidos entregues?`
5. `Qual foi o ticket médio do preço dos itens por pedido entregue, sem frete?`
6. Pergunta que a base não permite: `Qual foi a margem de lucro por categoria?`

## O que mostrar nos prints

Tire de 2 a 3 capturas para que tudo fique legível:

- **Captura 1:** a pergunta (1), a linha de execução do comando (`Bash(python .claude/skills/analise-olist/scripts/olist_analytics.py ...)`) e o início da resposta.
- **Captura 2:** a resposta com a tabela, os filtros, o arquivo usado, o comando executado e a cobertura.
- **Captura 3:** a continuação (2 ou 3), mostrando que o agente executou de novo e explicou a mudança.

Dicas:
- Aumente o zoom do terminal para o texto ficar legível e role até o trecho certo antes de capturar.
- A atividade proíbe vermelho. Use um tema de terminal sem vermelho nos destaques (`/theme` no Claude Code), evite capturar mensagens de erro e diferenças de arquivos, e recorte a imagem se aparecer algo vermelho.
- Se a primeira resposta pedir permissão para executar o script, aceite: isso também mostra a execução de código.
- Confira que os números do print batem com `saidas/` (com os mesmos arquivos). Com CSVs diferentes dos que usei, os valores do ticket médio podem variar.
