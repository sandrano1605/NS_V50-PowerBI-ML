import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c=conectar(30); cur=c.cursor()

print("=== YV01: que es y cuanto pesa en el universo 43/45 ===")
cur.execute("""
SELECT
    K.AUART,
    COUNT(DISTINCT K.VBELN) AS pedidos_6m,
    MIN(K.ERDAT) AS min_erdat,
    MAX(K.ERDAT) AS max_erdat
FROM dbo.VBAK_SAP K
WHERE K.ERDAT >= DATEADD(MONTH,-6,CAST(GETDATE() AS DATE))
  AND RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),K.VTWEG))),2) IN ('43','45')
GROUP BY K.AUART
ORDER BY pedidos_6m DESC
""")
print(f"{'AUART':<8} {'pedidos_6m':>12} {'min_erdat':>12} {'max_erdat':>12}")
for r in cur.fetchall():
    print(f"{r[0]:<8} {r[1]:>12,} {r[2]} {r[3]}")

print("\n=== Muestra de pedidos YV01 (canales 43/45, 6M) ===")
cur.execute("""
SELECT TOP 15 K.VBELN, K.ERDAT, K.AUART, K.VTWEG, K.NETWR, K.VKORG
FROM dbo.VBAK_SAP K
WHERE K.ERDAT >= DATEADD(MONTH,-6,CAST(GETDATE() AS DATE))
  AND RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),K.VTWEG))),2) IN ('43','45')
  AND K.AUART = 'YV01'
ORDER BY K.ERDAT DESC
""")
cols = [d[0] for d in cur.description]
print('\t'.join(cols))
for r in cur.fetchall():
    print('\t'.join(str(x) for x in r))

print("\n=== YV01 en el universo del modelo Power BI (Fact_Tracking) ===")
cur.execute("""
SELECT
    CASE WHEN K.AUART = 'YV01' THEN 'YV01' ELSE 'OTRO' END AS grupo,
    COUNT(DISTINCT K.VBELN) AS pedidos
FROM dbo.VBAK_SAP K
WHERE K.ERDAT >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))
  AND RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),K.VTWEG))),2) IN ('43','45')
GROUP BY CASE WHEN K.AUART = 'YV01' THEN 'YV01' ELSE 'OTRO' END
""")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]:,}")

c.close()
