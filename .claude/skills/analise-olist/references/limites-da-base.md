# O que a base Olist permite (e não permite) responder

Autor: George Pagliuso. Consulte antes de aceitar uma pergunta nova ou fora das três análises.
Para confirmar as colunas reais da pasta de dados do usuário, rode o comando `inspecionar` do script.

## Tabelas e colunas conhecidas (cabeçalhos conferidos nos arquivos recebidos)

| Arquivo | Colunas |
| --- | --- |
| olist_orders_dataset | order_id, customer_id, order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date |
| olist_order_items_dataset | order_id, order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value |
| olist_customers_dataset | customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state |
| olist_order_payments_dataset | order_id, payment_sequential, payment_type, payment_installments, payment_value |
| olist_order_reviews_dataset | review_id, order_id, review_score, review_comment_title, review_comment_message, review_creation_date, review_answer_timestamp |
| olist_products_dataset | product_id, product_category_name, product_name_lenght, product_description_lenght, product_photos_qty, product_weight_g, product_length_cm, product_height_cm, product_width_cm |
| olist_sellers_dataset | seller_id, seller_zip_code_prefix, seller_city, seller_state |
| olist_geolocation_dataset | geolocation_zip_code_prefix, geolocation_lat, geolocation_lng, geolocation_city, geolocation_state |
| product_category_name_translation | product_category_name, product_category_name_english |

## Classificação do pedido

1. **Coberto pela skill:** as três análises (pedidos entregues por mês, ranking de UFs, ticket médio),
   com período, UF e tamanho do ranking como parâmetros.
2. **Possível com a base, mas fora desta versão da skill:** outras métricas com as tabelas existentes
   (por exemplo, pagamentos por tipo, nota de avaliação, vendedores, categorias, prazos de entrega).
   Explique que o script não cobre isso, e só prossiga com código novo se o usuário concordar, mantendo as
   regras de `regras-e-metricas.md` (somar itens e pagamentos por pedido antes de relacionar tabelas).
3. **Impossível com a base:** o dado não existe. Exemplos: custo do produto, margem ou lucro,
   devoluções e estornos, receita líquida de impostos ou comissão, dados demográficos do cliente (idade,
   gênero, renda), estoque, campanhas de marketing, previsão do futuro, qualquer informação posterior ao
   período coberto pela base.

## Como responder a uma pergunta impossível

1. Diga claramente que a base não permite responder e **qual dado falta** (cite as colunas conferidas
   com `inspecionar`).
2. **Não** estime, não use dados de outra fonte e não apresente número algum.
3. Se houver, ofereça a pergunta respondível mais próxima (por exemplo, "ticket médio do preço dos itens"
   no lugar de "margem").
