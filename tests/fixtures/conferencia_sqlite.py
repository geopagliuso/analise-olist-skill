"""Conferência INDEPENDENTE do recorte: calcula os resultados esperados com SQL (sqlite3),
sem usar scripts/olist_analytics.py nem pandas. Uso: python conferencia_sqlite.py <pasta_dos_csv>"""
import csv, sqlite3, sys
from pathlib import Path

pasta = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "olist_recorte")
db = sqlite3.connect(":memory:")
for tabela, arq in (("pedidos", "olist_orders_dataset"), ("itens", "olist_order_items_dataset"),
                    ("clientes", "olist_customers_dataset")):
    with open(pasta / f"{arq}.csv", newline="", encoding="utf-8") as f:
        linhas = list(csv.reader(f))
    cab = linhas[0]
    db.execute(f"CREATE TABLE {tabela} ({', '.join(c + ' TEXT' for c in cab)})")
    db.executemany(f"INSERT INTO {tabela} VALUES ({', '.join('?' * len(cab))})", linhas[1:])

def mostrar(titulo, sql):
    print(f"\n-- {titulo}")
    for r in db.execute(sql): print(r)

mostrar("pedidos entregues por mês (dtPedido)", """
  SELECT substr(order_purchase_timestamp,1,7) AS mes, COUNT(DISTINCT order_id)
  FROM pedidos WHERE order_status='delivered' GROUP BY mes ORDER BY mes""")
mostrar("pedidos entregues por UF", """
  SELECT c.customer_state, COUNT(DISTINCT p.order_id) AS n
  FROM pedidos p JOIN clientes c ON c.customer_id=p.customer_id
  WHERE p.order_status='delivered' GROUP BY c.customer_state ORDER BY n DESC, c.customer_state""")
mostrar("ticket médio sem frete: soma(price) / pedidos entregues distintos (todo o recorte)", """
  SELECT ROUND((SELECT SUM(CAST(price AS REAL)) FROM itens WHERE order_id IN
                (SELECT order_id FROM pedidos WHERE order_status='delivered')) * 1.0 /
               (SELECT COUNT(DISTINCT order_id) FROM pedidos WHERE order_status='delivered'), 6)""")
mostrar("ticket médio, 2018-01-01 a 2018-01-31", """
  WITH sel AS (SELECT DISTINCT order_id FROM pedidos WHERE order_status='delivered'
               AND substr(order_purchase_timestamp,1,10) BETWEEN '2018-01-01' AND '2018-01-31')
  SELECT (SELECT COUNT(*) FROM sel),
         ROUND((SELECT SUM(CAST(price AS REAL)) FROM itens WHERE order_id IN sel) * 1.0 / (SELECT COUNT(*) FROM sel), 6)""")
mostrar("ticket médio, 2018-01-01 a 2018-01-31, UF = SP", """
  WITH sel AS (SELECT DISTINCT p.order_id FROM pedidos p JOIN clientes c ON c.customer_id=p.customer_id
               WHERE p.order_status='delivered' AND c.customer_state='SP'
               AND substr(p.order_purchase_timestamp,1,10) BETWEEN '2018-01-01' AND '2018-01-31')
  SELECT (SELECT COUNT(*) FROM sel),
         ROUND((SELECT SUM(CAST(price AS REAL)) FROM itens WHERE order_id IN sel) * 1.0 / (SELECT COUNT(*) FROM sel), 6)""")
mostrar("guarda: itens com price NÃO numérico (deve ser 0, senão o CAST do SQLite mascara o erro)", """
  SELECT COUNT(*) FROM itens WHERE price GLOB '*[^0-9.]*' OR price = ''""")
