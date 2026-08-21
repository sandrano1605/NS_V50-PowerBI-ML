import sys, time; sys.path.insert(0,'scripts')
from conexion_sql import conectar

c = conectar(timeout=300)
cur = c.cursor()

print("="*72)
print("1) UNIVERSO 43/45 (VBAK 6M) Y COBERTURA VBAP ACTUAL")
print("="*72)
cur.execute("""
SELECT
    COUNT(DISTINCT K.VBELN) AS total_4345,
    COUNT(DISTINCT CASE WHEN V.VBELN IS NOT NULL AND V.AEDAT >= DATEADD(MONTH,-24,CAST(GETDATE() AS DATE)) THEN K.VBELN END) AS con_pos_730d,
    COUNT(DISTINCT CASE WHEN V.VBELN IS NOT NULL AND V.AEDAT >= DATEADD(MONTH,-4,CAST(GETDATE() AS DATE)) THEN K.VBELN END) AS con_pos_120d,
    COUNT(DISTINCT CASE WHEN V.VBELN IS NULL OR V.AEDAT < DATEADD(MONTH,-24,CAST(GETDATE() AS DATE)) THEN K.VBELN END) AS sin_pos_730d
FROM dbo.VBAK_SAP K
LEFT JOIN dbo.VBAP_SAP V ON V.VBELN = K.VBELN
WHERE K.ERDAT >= DATEADD(MONTH,-6,CAST(GETDATE() AS DATE))
  AND RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),K.VTWEG))),2) IN ('43','45')
""")
r = cur.fetchone()
total, p730, p120, sin730 = r[0], r[1], r[2], r[3]
print(f"  Universo 43/45 (VBAK 6M): {total:,}")
print(f"  Con posiciones AEDAT<=730d: {p730:,} ({p730*100.0/total:.1f}%)")
print(f"  Con posiciones AEDAT<=120d: {p120:,} ({p120*100.0/total:.1f}%)")
print(f"  SIN posiciones 730d: {sin730:,} ({sin730*100.0/total:.1f}%)")

print()
print("="*72)
print("2) LOS SIN POSICIONES: existen en otras fuentes de lineas?")
print("="*72)
cur.execute("""
SELECT
    COUNT(DISTINCT K.VBELN) AS sin_pos,
    SUM(CASE WHEN VP.VBELN IS NOT NULL THEN 1 ELSE 0 END) AS en_vista_pedido,
    SUM(CASE WHEN BRP.VBELN IS NOT NULL THEN 1 ELSE 0 END) AS en_vbrp,
    SUM(CASE WHEN LPS.VBELN IS NOT NULL THEN 1 ELSE 0 END) AS en_lips
FROM dbo.VBAK_SAP K
LEFT JOIN (SELECT DISTINCT CONVERT(VARCHAR(20),VBELN) AS VBELN FROM dbo.VISTA_PEDIDO) VP ON VP.VBELN = K.VBELN
LEFT JOIN (SELECT DISTINCT CONVERT(VARCHAR(20),VBELN) AS VBELN FROM dbo.VBRP_SAP) BRP ON BRP.VBELN = K.VBELN
LEFT JOIN (SELECT DISTINCT CONVERT(VARCHAR(20),VBELN) AS VBELN FROM dbo.LIPS_SAP) LPS ON LPS.VBELN = K.VBELN
WHERE K.ERDAT >= DATEADD(MONTH,-6,CAST(GETDATE() AS DATE))
  AND RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),K.VTWEG))),2) IN ('43','45')
  AND NOT EXISTS (SELECT 1 FROM dbo.VBAP_SAP V2 WHERE V2.VBELN = K.VBELN AND V2.AEDAT >= DATEADD(MONTH,-24,CAST(GETDATE() AS DATE)))
""")
r = cur.fetchone()
print(f"  Sin posiciones VBAP 730d: {r[0]:,}")
print(f"  En Lineas_y_unidades_por_pedidos (modelo actual): {r[1]:,}")
print(f"  En VISTA_PEDIDO: {r[2]:,}")
print(f"  En VBRP_SAP: {r[3]:,}")
print(f"  En LIPS_SAP: {r[4]:,}")

c.close()
