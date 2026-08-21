import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c=conectar(15); cur=c.cursor()

print("=== sys.sql_modules VISTA_PEDIDO ===")
cur.execute("SELECT definition FROM sys.sql_modules WHERE object_id = OBJECT_ID('dbo.VISTA_PEDIDO')")
r = cur.fetchone()
if r and r[0]:
    print(r[0][:4000])
else:
    print("No accesible")

print("\n=== VISTA_PEDIDO: tiene YV01? ===")
cur.execute("""
SELECT AUART, COUNT(DISTINCT VBELN) AS pedidos
FROM dbo.VISTA_PEDIDO
GROUP BY AUART
ORDER BY pedidos DESC
""")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]:,}")

print("\n=== VISTA_PEDIDO: total filas por fecha (muestra) ===")
cur.execute("""
SELECT ERDAT, COUNT(*) AS filas
FROM dbo.VISTA_PEDIDO
GROUP BY ERDAT
ORDER BY ERDAT DESC
""")
rows = cur.fetchall()
print(f"  {len(rows)} fechas distintas; ultimas 10:")
for r in rows[:10]:
    print(f"  {r[0]}: {r[1]:,}")

c.close()
