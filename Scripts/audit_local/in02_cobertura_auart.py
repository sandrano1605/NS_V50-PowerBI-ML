import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c=conectar(30); cur=c.cursor()

print("=== Cobertura VBAP_SAP por AUART en canales 43/45 (3M) ===")
cur.execute("""
SELECT
    K.AUART,
    COUNT(DISTINCT K.VBELN) AS pedidos_vbak,
    COUNT(DISTINCT CASE WHEN V.VBELN IS NOT NULL THEN K.VBELN END) AS con_pos_vbap,
    COUNT(DISTINCT CASE WHEN V.VBELN IS NULL THEN K.VBELN END) AS sin_pos
FROM dbo.VBAK_SAP K
LEFT JOIN dbo.VBAP_SAP V ON V.VBELN = K.VBELN AND V.AEDAT >= DATEADD(MONTH,-24,CAST(GETDATE() AS DATE))
WHERE K.ERDAT >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))
  AND RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),K.VTWEG))),2) IN ('43','45')
GROUP BY K.AUART
ORDER BY pedidos_vbak DESC
""")
print(f"{'AUART':<8} {'pedidos':>9} {'con_pos':>9} {'sin_pos':>9} {'cov%':>7}")
for r in cur.fetchall():
    cov = r[2]*100.0/r[1] if r[1] else 0
    print(f"{r[0]:<8} {r[1]:>9,} {r[2]:>9,} {r[3]:>9,} {cov:>6.1f}%")

print("\n=== Total 43/45 (3M): cobertura global VBAP_SAP ===")
cur.execute("""
SELECT
    COUNT(DISTINCT K.VBELN) AS total,
    COUNT(DISTINCT CASE WHEN V.VBELN IS NOT NULL THEN K.VBELN END) AS con_pos
FROM dbo.VBAK_SAP K
LEFT JOIN dbo.VBAP_SAP V ON V.VBELN = K.VBELN AND V.AEDAT >= DATEADD(MONTH,-24,CAST(GETDATE() AS DATE))
WHERE K.ERDAT >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))
  AND RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),K.VTWEG))),2) IN ('43','45')
""")
r = cur.fetchone()
print(f"  Total: {r[0]:,} | Con posiciones: {r[1]:,} ({r[1]*100.0/r[0]:.1f}%) | Sin: {r[0]-r[1]:,}")

c.close()
