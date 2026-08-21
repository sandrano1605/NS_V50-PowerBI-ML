import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c=conectar(30); cur=c.cursor()

print("=== VISTA_PEDIDO: cobertura por canal (VTWEG) ===")
cur.execute("""
SELECT RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),VTWEG))),2) AS canal,
       COUNT(DISTINCT VBELN) AS pedidos,
       COUNT(*) AS lineas,
       SUM(CONVERT(DECIMAL(18,2), ISNULL(KWMENG,0))) AS unidades
FROM dbo.VISTA_PEDIDO
GROUP BY RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),VTWEG))),2)
ORDER BY pedidos DESC
""")
for r in cur.fetchall():
    print(f"  canal {r[0]}: {r[1]:,} pedidos / {r[2]:,} lineas / {r[3]:,.0f} unid")

print("\n=== VISTA_PEDIDO: cobertura por AUART (canales 43/45) ===")
cur.execute("""
SELECT AUART, COUNT(DISTINCT VBELN) AS pedidos, COUNT(*) AS lineas
FROM dbo.VISTA_PEDIDO
WHERE RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),VTWEG))),2) IN ('43','45')
GROUP BY AUART
ORDER BY pedidos DESC
""")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]:,} pedidos / {r[2]:,} lineas")

print("\n=== VISTA_PEDIDO: rango fechas ===")
cur.execute("SELECT MIN(ERDAT), MAX(ERDAT), MIN(AEDAT), MAX(AEDAT) FROM dbo.VISTA_PEDIDO")
r = cur.fetchone()
print(f"  ERDAT: {r[0]} a {r[1]} | AEDAT: {r[2]} a {r[3]}")

print("\n=== Universo 43/45 (VBAK 6M) con posiciones en VISTA_PEDIDO ===")
cur.execute("""
SELECT COUNT(DISTINCT K.VBELN) AS total,
       COUNT(DISTINCT CASE WHEN V.VBELN IS NOT NULL THEN K.VBELN END) AS en_vista_pedido
FROM dbo.VBAK_SAP K
LEFT JOIN (SELECT DISTINCT CONVERT(VARCHAR(20),VBELN) AS VBELN FROM dbo.VISTA_PEDIDO) V ON V.VBELN = CONVERT(VARCHAR(20),K.VBELN)
WHERE K.ERDAT >= DATEADD(MONTH,-6,CAST(GETDATE() AS DATE))
  AND RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),K.VTWEG))),2) IN ('43','45')
""")
r = cur.fetchone()
print(f"  Universo 43/45 (VBAK 6M): {r[0]:,}")
print(f"  Con posiciones en VISTA_PEDIDO: {r[1]:,} ({r[1]*100.0/r[0]:.1f}%)")

c.close()
