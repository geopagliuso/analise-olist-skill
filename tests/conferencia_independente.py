"""Conferência INDEPENDENTE das três análises com SQL (sqlite3), sem usar o script da skill nem pandas.
Uso: python tests/conferencia_independente.py <pasta_dos_csv> [--inicio AAAA-MM-DD] [--fim AAAA-MM-DD] [--uf SP]
Só lê CSV. Imprime os mesmos números que a skill deve produzir, para comparação manual ou automática."""
import argparse, csv, sqlite3
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("pasta"); ap.add_argument("--inicio"); ap.add_argument("--fim"); ap.add_argument("--uf")
a = ap.parse_args()
db = sqlite3.connect(":memory:")
for tabela, arq in (("pedidos", "olist_orders_dataset"), ("itens", "olist_order_items_dataset"),
                    ("clientes", "olist_customers_dataset")):
    with open(Path(a.pasta) / f"{arq}.csv", newline="", encoding="utf-8") as f:
        linhas = list(csv.reader(f))
    db.execute(f"CREATE TABLE {tabela} ({', '.join(c + ' TEXT' for c in linhas[0])})")
    db.executemany(f"INSERT INTO {tabela} VALUES ({', '.join('?' * len(linhas[0]))})", linhas[1:])

ini, fim, uf = a.inicio or "0000-00-00", a.fim or "9999-12-31", (a.uf or "").upper()
db.execute("""CREATE TEMP TABLE sel AS
  SELECT DISTINCT p.order_id, p.customer_id, c.customer_state AS uf, substr(p.order_purchase_timestamp,1,7) AS mes
  FROM pedidos p LEFT JOIN clientes c ON c.customer_id = p.customer_id
  WHERE p.order_status = 'delivered'
    AND substr(p.order_purchase_timestamp,1,10) BETWEEN ? AND ?
    AND (? = '' OR upper(c.customer_state) = ?)""", (ini, fim, uf, uf))
print("pedidos entregues selecionados:", db.execute("SELECT COUNT(*) FROM sel").fetchone()[0])
print("\npedidos por mês:")
for r in db.execute("SELECT mes, COUNT(*) FROM sel GROUP BY mes ORDER BY mes"): print(" ", r)
print("\nrank de UFs (top 8):")
for r in db.execute("SELECT upper(uf), COUNT(*) n FROM sel WHERE uf IS NOT NULL AND uf <> '' GROUP BY upper(uf) ORDER BY n DESC, upper(uf) LIMIT 8"): print(" ", r)
num = "price <> '' AND price NOT GLOB '*[^0-9.]*'"
soma, n_inval = db.execute(f"""SELECT SUM(CASE WHEN {num} THEN CAST(price AS REAL) END),
    SUM(CASE WHEN NOT ({num}) THEN 1 ELSE 0 END) FROM itens WHERE order_id IN (SELECT order_id FROM sel)""").fetchone()
n = db.execute("SELECT COUNT(*) FROM sel").fetchone()[0]
sem_itens = db.execute("SELECT COUNT(*) FROM sel WHERE order_id NOT IN (SELECT order_id FROM itens)").fetchone()[0]
print(f"\nsoma de price válido: {soma}; itens com price inválido: {n_inval}; pedidos sem itens: {sem_itens}")
print("ticket médio:", round(soma / n, 2) if n and soma is not None else "não aplicável")
