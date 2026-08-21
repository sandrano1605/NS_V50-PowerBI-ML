import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c=conectar(60); cur=c.cursor()

print("="*72)
print("COMPARACION COHERENTE: ZART_TRACK vs VBAP_SAP (SIN filtro AEDAT)")
print("="*72)

print("\n1) Universo ZART_TRACK (canales 43/45, 3M): pedidos totales")
cur.execute("""
SELECT COUNT(DISTINCT CONVERT(VARCHAR(20), ZVBELN_PED)) AS pedidos_zart
FROM dbo.ZART_TRACK_DATA_SAP
""")
r = cur.fetchone()
print(f"   ZART_TRACK pedidos (todo el historial): {r[0]:,}")

print("\n2) VBAP_SAP: pedidos distintos (SIN filtro AEDAT)")
cur.execute("SELECT COUNT(DISTINCT CONVERT(VARCHAR(20), VBELN)) FROM dbo.VBAP_SAP")
r = cur.fetchone()
print(f"   VBAP_SAP pedidos distintos (todo): {r[0]:,}")

print("\n3) VBAP_SAP: pedidos distintos CON filtro AEDAT 730d")
cur.execute("SELECT COUNT(DISTINCT CONVERT(VARCHAR(20), VBELN)) FROM dbo.VBAP_SAP WHERE AEDAT >= GETDATE()-730")
r = cur.fetchone()
print(f"   VBAP_SAP pedidos (AEDAT>=730d): {r[0]:,}")

print("\n4) CRUCE: pedidos de ZART_TRACK (canales 43/45, 3M) que estan en VBAP_SAP SIN filtro AEDAT")
cur.execute("""
SELECT
    COUNT(DISTINCT CONVERT(VARCHAR(20), Z.ZVBELN_PED)) AS zart_4345_3m,
    COUNT(DISTINCT CASE WHEN V.VBELN IS NOT NULL THEN CONVERT(VARCHAR(20), Z.ZVBELN_PED) END) AS en_vbap_sin_filtro
FROM dbo.ZART_TRACK_DATA_SAP Z
LEFT JOIN (SELECT DISTINCT CONVERT(VARCHAR(20),VBELN) AS VBELN FROM dbo.VBAP_SAP) V
    ON V.VBELN = CONVERT(VARCHAR(20), Z.ZVBELN_PED)
WHERE 1=1
""")
r = cur.fetchone()
print(f"   ZART_TRACK total: {r[0]:,}")
print(f"   En VBAP_SAP (sin filtro AEDAT): {r[1]:,} ({r[1]*100.0/r[0] if r[0] else 0:.1f}%)")

c.close()
