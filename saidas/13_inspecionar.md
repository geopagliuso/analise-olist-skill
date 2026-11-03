### $ python .claude/skills/analise-olist/scripts/olist_analytics.py inspecionar --dados dados

## inspecionar
**Métrica:** Arquivos e colunas existentes na pasta dos dados (apenas o cabeçalho é lido).
**Arquivos:** olist_orders_dataset.csv, olist_order_items_dataset.csv, olist_customers_dataset.csv, olist_order_payments_dataset.csv, olist_products_dataset.csv, olist_sellers_dataset.csv, olist_order_reviews_dataset.csv, product_category_name_translation.csv
- **olist_orders_dataset**: order_id, customer_id, order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date
- **olist_order_items_dataset**: order_id, order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value
- **olist_customers_dataset**: customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state
- **olist_order_payments_dataset**: order_id, payment_sequential, payment_type, payment_installments, payment_value
- **olist_products_dataset**: product_id, product_category_name, product_name_lenght, product_description_lenght, product_photos_qty, product_weight_g, product_length_cm, product_height_cm, product_width_cm
- **olist_sellers_dataset**: seller_id, seller_zip_code_prefix, seller_city, seller_state
- **olist_order_reviews_dataset**: review_id, order_id, review_score, review_comment_title, review_comment_message, review_creation_date, review_answer_timestamp
- **product_category_name_translation**: product_category_name, product_category_name_english
- Não encontrados: olist_geolocation_dataset
[salvo] saidas/inspecionar__toda-a-base.json
[salvo] saidas/inspecionar__toda-a-base.csv
exit=0
