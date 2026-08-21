import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c = conectar(30); cur = c.cursor()

print("=== LIPS coverage para faltantes 43/45 ===")
cur.execute("""
SELECT COUNT(DISTINCT K.VBELN) AS sin_pos,
       SUM(CASE WHEN L.VBELN IS NOT NULL THEN 1 ELSE 0 END) AS en_lips
FROM dbo.VBAK_SAP K
LEFT JOIN (SELECT DISTINCT CONVERT(VARCHAR(20),VBELN) AS VBELN FROM dbo.LIPS_SAP) L ON L.VBELN = K.VBELN
WHERE K.ERDAT >= DATEADD(MONTH,-6,CAST(GETDATE() AS DATE))
  AND RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),K.VTWEG))),2) IN ('43','45')
  AND NOT EXISTS (SELECT 1 FROM dbo.VBAP_SAP V2 WHERE V2.VBELN = K.VBELN AND V2.AEDAT >= DATEADD(MONTH,-24,CAST(GETDATE() AS DATE)))
""")
r = cur.fetchone()
print(f"  Sin posicion VBAP: {r[0]:,} | En LIPS: {r[1]:,}")

print("\n=== Muestra faltantes 3M 43/45 ===")
cur.execute("""
SELECT TOP 25 K.VBELN, K.AUART, K.ERDAT, K.VTWEG
FROM dbo.VBAK_SAP K
WHERE K.ERDAT >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))
  AND RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),K.VTWEG))),2) IN ('43','45')
  AND NOT EXISTS (SELECT 1 FROM dbo.VBAP_SAP V2 WHERE V2.VBELN = K.VBELN AND V2.AEDAT >= DATEADD(MONTH,-24,CAST(GETDATE() AS DATE)))
ORDER BY K.ERDAT DESC
""")
for r in cur.fetchall():
    print(f"  {r[0]} AUART={r[1]} ERDAT={r[2]} VTWEG={r[3]}")

print("\n=== VISTA_PEDIDO: filas totales y rangos ===")
cur.execute("SELECT COUNT(*) AS filas, COUNT(DISTINCT VBELN) AS pedidos FROM dbo.VISTA_PEDIDO")
r = cur.fetchone()
print(f"  VISTA_PEDIDO: {r[0]:,} filas / {r[1]:,} pedidos")

print("\n=== VISTA_PEDIDO: AUART de sus pedidos ===")
cur.execute("""
SELECT K.AUART, COUNT(DISTINCT V.VBELN) AS pedidos
FROM dbo.VISTA_PEDIDO V
LEFT JOIN dbo.VBAK_SAP K ON CONVERT(VARCHAR(20),K.VBELN) = CONVERT(VARCHAR(20),V.VBELN)
GROUP BY K.AUART
ORDER BY pedidos DESC
""")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]:,}")

c.close()
