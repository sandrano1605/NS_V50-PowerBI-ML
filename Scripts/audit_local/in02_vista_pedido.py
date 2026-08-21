import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c = conectar(30); cur = c.cursor()

print("=== VISTA_PEDIDO: filas y pedidos ===")
cur.execute("SELECT COUNT(*) AS filas, COUNT(DISTINCT VBELN) AS pedidos FROM dbo.VISTA_PEDIDO")
r = cur.fetchone()
print(f"  VISTA_PEDIDO: {r[0]:,} filas / {r[1]:,} pedidos")

print("\n=== VISTA_PEDIDO: AUART de sus pedidos (join VBAK) ===")
cur.execute("""
SELECT K.AUART, COUNT(DISTINCT V.VBELN) AS pedidos
FROM dbo.VISTA_PEDIDO V
LEFT JOIN dbo.VBAK_SAP K ON CONVERT(VARCHAR(20),K.VBELN) = CONVERT(VARCHAR(20),V.VBELN)
GROUP BY K.AUART
ORDER BY pedidos DESC
""")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]:,}")

print("\n=== LIPS_SAP: solo conteo rapido ===")
cur.execute("SELECT COUNT(*) FROM dbo.LIPS_SAP")
print(f"  LIPS_SAP total filas: {cur.fetchone()[0]:,}")

c.close()
