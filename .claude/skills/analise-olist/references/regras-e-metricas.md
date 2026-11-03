# Regras de negócio, métricas e relacionamentos (Olist)

Autor: George Pagliuso. Consulte este arquivo antes de calcular qualquer métrica e sempre que o
pedido do usuário puder ser lido de mais de um jeito.

## 1. Correspondência entre os nomes da lista e as colunas dos arquivos

O enunciado do trabalho usa nomes como `idPedido` e `vlPreco`. Os arquivos que o usuário forneceu
são a versão pública do Olist, com colunas em inglês. O `dicionario.xlsx` do professor **não** estava
disponível; a correspondência abaixo foi proposta e **confirmada pelo usuário (George)**, não
extraída de um dicionário. Se o professor fornecer um dicionário diferente, revise esta tabela
antes de qualquer cálculo.

| Nome na atividade | Arquivo (sem extensão) | Coluna usada |
| --- | --- | --- |
| idPedido | olist_orders_dataset | order_id |
| descSituacao | olist_orders_dataset | order_status |
| dtPedido | olist_orders_dataset | order_purchase_timestamp |
| idCliente | olist_orders_dataset e olist_customers_dataset | customer_id |
| descUF | olist_customers_dataset | customer_state |
| vlPreco | olist_order_items_dataset | price |
| vlFrete | olist_order_items_dataset | freight_value (nunca entra no ticket) |
| vlPagamento | olist_order_payments_dataset | payment_value (não usado nas três análises) |

Os arquivos podem estar em `.csv` ou `.xlsx` (o script procura primeiro o `.csv`).

## 2. Chaves e relacionamentos

| Relação | Chave | Cardinalidade | Cuidado |
| --- | --- | --- | --- |
| pedidos → clientes | customer_id (idCliente) | muitos pedidos para 1 linha de cliente | Confirmar que `customer_id` não se repete em clientes; se repetir, manter a primeira ocorrência e avisar. |
| pedidos → itens | order_id (idPedido) | 1 pedido para vários itens | **Somar os itens por pedido antes de relacionar**; nunca contar pedidos depois de juntar com itens. |
| pedidos → pagamentos | order_id (idPedido) | 1 pedido para vários pagamentos | Não usado nas três análises. Somar `payment_value` junto com itens multiplicaria valores. |

`customer_id` identifica o cliente **em um pedido**; quem compra mais de uma vez tem mais de um
`customer_id` (a coluna `customer_unique_id` identifica a pessoa). Por isso o ranking de UFs conta
**pedidos**, e não pessoas.

## 3. Regras comuns às três análises

1. **Pedido entregue:** `order_status` igual a `delivered` (comparação sem diferenciar maiúsculas e
   sem espaços nas pontas). Os demais status (shipped, canceled, unavailable, invoiced, processing,
   created, approved) ficam fora.
2. **Data de referência:** `order_purchase_timestamp` (dtPedido). Não usar as datas de aprovação,
   envio ou entrega.
3. **Contagem de pedidos:** `order_id` distintos. Linhas repetidas do mesmo pedido contam uma vez.
4. **Convenção das datas inicial e final (acordada com o usuário):** as duas são **inclusivas** e
   comparadas **por dia do calendário**, ignorando a hora. Uma data final `2018-03-31` inclui os pedidos
   feitos até 23:59:59 desse dia. Sem período, usa-se toda a base. Em `AAAA-MM`, a data inicial vira o
   dia 1 e a data final vira o último dia do mês.
5. **Mês parcial:** se o período não cobre o mês inteiro, a linha do mês aparece marcada como parcial.
6. **Meses sem pedido:** dentro do intervalo pedido aparecem com **zero**. Contagem sem pedidos é
   zero; média sem pedidos é **não aplicável** (nunca zero).
7. **UF:** `customer_state` em maiúsculas e sem espaços. UF vazia não entra no ranking.

## 4. Métricas

- **pedidos-por-mes:** quantidade de `order_id` distintos entregues, agrupados pelo mês de dtPedido.
- **top-ufs:** quantidade de `order_id` distintos entregues por `customer_state`, ordenada do maior para o
  menor; desempate pela ordem alfabética da UF. Padrão: cinco UFs. Se houver empate na posição de corte,
  o resultado avisa.
- **ticket-medio:** `soma(price dos itens dos pedidos selecionados) / nº de order_id distintos selecionados`.
  Sem frete. O denominador é o número de **pedidos**, não de itens. Pedidos entregues sem itens permanecem
  no denominador; a cobertura informa quantos selecionados têm itens, e o resultado traz também o ticket
  calculado só com os pedidos que têm itens, para comparação.

## 5. Preço, frete e pagamento são coisas diferentes

- `price` é o preço do item, sem frete.
- `freight_value` é o frete do item. Não entra no ticket médio pedido pelo trabalho.
- `payment_value` é o valor pago e pode somar `price + frete` (e até diferir por parcelas, vouchers etc.).
  Não substitua `price` por `payment_value`.

## 6. Tratamento de dados problemáticos (o script aplica e avisa)

| Situação | Tratamento |
| --- | --- |
| Data do pedido ausente ou inválida | O pedido sai de todas as análises (a data é a referência). Quantidade informada no aviso. |
| `order_id` repetido entre pedidos entregues | Mantida uma linha por pedido. Quantidade informada. |
| `order_id` entregue que também aparece com outra situação | Mantido como entregue e avisado como conflito. |
| `customer_id` repetido em clientes | Mantida a primeira ocorrência, para não multiplicar pedidos. Avisado. |
| Pedido sem cliente correspondente ou cliente sem UF | Fica fora do ranking de UFs e do filtro por UF; continua nas análises que não usam UF. Quantidade informada. |
| Pedido entregue sem itens | Permanece no denominador do ticket; cobertura menor que 100% é informada. |
| `price` vazio ou não numérico | O item é ignorado na soma. Quantidade informada; o ticket pode estar subestimado. |
| Item que aponta para pedido inexistente | Não afeta as análises; informado como aviso. |
| UF pedida que não existe na base | Resultado zero (ou não aplicável) com aviso listando as UFs existentes. |

## 7. Qualidade conhecida dos arquivos recebidos

Os arquivos `.xlsx` recebidos vieram de planilhas do Google (o usuário também enviou os atalhos `.gsheet`). Nesse caminho, algumas células
numéricas de `price`, `freight_value` e `payment_value` viraram **datas** (por exemplo, `2024-10-29 00:00:00`),
provavelmente porque valores como "29.10" foram lidos como dia.mês. Não é possível recuperar o valor
original: "12.5" e "12.05", por exemplo, resultam na mesma data (12 de maio). Por isso o script **não
tenta corrigir**: trata como ausente e avisa. Se os CSVs originais do Olist estiverem disponíveis, use-os
para obter resultados exatos e informe ao usuário qual fonte foi usada.
