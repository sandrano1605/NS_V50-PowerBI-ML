import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c=conectar(120); cur=c.cursor()

print("="*72)
print("COBERTURA REAL: ZART_TRACK 43/45 (3M) vs VBAP_SAP SIN filtro AEDAT")
print("="*72)

print("\n1) ZART_TRACK 43/45 (ERDAT del pedido >= 3M) -> pedidos")
cur.execute("""
SELECT COUNT(DISTINCT CONVERT(VARCHAR(20), ZVBELN_PED)) AS pedidos
FROM dbo.ZART_TRACK_DATA_SAP
WHERE ZERDAT_PED >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))
""")
r = cur.fetchone()
print(f"   ZART_TRACK 3M (por ZERDAT_PED): {r[0]:,}")

print("\n2) ZART_TRACK 43/45 (3M) que tienen posiciones en VBAP_SAP (SIN filtro AEDAT)")
cur.execute("""
SELECT
    COUNT(DISTINCT CONVERT(VARCHAR(20), Z.ZVBELN_PED)) AS zart_3m,
    COUNT(DISTINCT CASE WHEN V.VBELN IS NOT NULL THEN CONVERT(VARCHAR(20), Z.ZVBELN_PED) END) AS en_vbap
FROM dbo.ZART_TRACK_DATA_SAP Z
LEFT JOIN (SELECT DISTINCT CONVERT(VARCHAR(20),VBELN) AS VBELN FROM dbo.VBAP_SAP) V
    ON V.VBELN = CONVERT(VARCHAR(20), Z.ZVBELN_PED)
WHERE Z.ZERDAT_PED >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))
""")
r = cur.fetchone()
print(f"   ZART 3M: {r[0]:,}")
print(f"   Con posiciones VBAP (sin filtro AEDAT): {r[1]:,} ({r[1]*100.0/r[0] if r[0] else 0:.1f}%)")
print(f"   SIN posiciones: {r[0]-r[1]:,}")

print("\n3) Mismo cruce pero CON filtro AEDAT>=730d (la query actual del modelo)")
cur.execute("""
SELECT
    COUNT(DISTINCT CONVERT(VARCHAR(20), Z.ZVBELN_PED)) AS zart_3m,
    COUNT(DISTINCT CASE WHEN V.VBELN IS NOT NULL THEN CONVERT(VARCHAR(20), Z.ZVBELN_PED) END) AS en_vbap
FROM dbo.ZART_TRACK_DATA_SAP Z
LEFT JOIN (SELECT DISTINCT CONVERT(VARCHAR(20),VBELN) AS VBELN FROM dbo.VBAP_SAP WHERE AEDAT >= GETDATE()-730) V
    ON V.VBELN = CONVERT(VARCHAR(20), Z.ZVBELN_PED)
WHERE Z.ZERDAT_PED >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))
""")
r = cur.fetchone()
print(f"   ZART 3M: {r[0]:,}")
print(f"   Con posiciones VBAP (AEDAT>=730d): {r[1]:,} ({r[1]*100.0/r[0] if r[0] else 0:.1f}%)")

print("\n4) Muestras de pedidos ZART 3M SIN posicion en VBAP (que SI deberian estar)")
cur.execute("""
SELECT TOP 15 CONVERT(VARCHAR(20), Z.ZVBELN_PED) AS pedido, Z.ZERDAT_PED
FROM dbo.ZART_TRACK_DATA_SAP Z
WHERE Z.ZERDAT_PED >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))
  AND NOT EXISTS (SELECT 1 FROM dbo.VBAP_SAP V WHERE CONVERT(VARCHAR(20),V.VBELN) = CONVERT(VARCHAR(20), Z.ZVBELN_PED))
ORDER BY Z.ZERDAT_PED DESC
""")
for r in cur.fetchall():
    print(f"   {r[0]}  ZERDAT={r[1]}")

c.close()
