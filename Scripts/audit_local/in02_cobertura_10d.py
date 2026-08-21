import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c=conectar(120); cur=c.cursor()

cur.execute("""
IF OBJECT_ID('tempdb..#zart') IS NOT NULL DROP TABLE #zart;
SELECT DISTINCT CONVERT(VARCHAR(20), ZVBELN_PED) AS pedido
INTO #zart
FROM dbo.ZART_TRACK_DATA_SAP
WHERE ZERDAT_PED >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE));
""")

print("=== ZART 3M de 10 digitos: prefijo ===")
cur.execute("SELECT LEFT(pedido,4) AS pref, COUNT(*) FROM #zart WHERE LEN(pedido)=10 GROUP BY LEFT(pedido,4) ORDER BY 2 DESC")
for r in cur.fetchall():
    print(f"   prefijo {r[0]}: {r[1]:,}")

print("\n=== Cobertura ZART 10 digitos vs VBAP 10 digitos (clave exacta) ===")
cur.execute("""
IF OBJECT_ID('tempdb..#vbap10') IS NOT NULL DROP TABLE #vbap10;
SELECT DISTINCT CONVERT(VARCHAR(20), VBELN) AS pedido
INTO #vbap10
FROM dbo.VBAP_SAP
WHERE LEN(VBELN) = 10;
""")
cur.execute("""
SELECT
    SUM(CASE WHEN LEN(Z.pedido)=10 THEN 1 ELSE 0 END) AS zart_10d,
    SUM(CASE WHEN LEN(Z.pedido)=10 AND V.pedido IS NOT NULL THEN 1 ELSE 0 END) AS en_vbap_10d
FROM #zart Z
LEFT JOIN #vbap10 V ON V.pedido = Z.pedido
""")
r = cur.fetchone()
print(f"   ZART 10 digitos: {r[0]:,}")
print(f"   En VBAP 10 digitos (exacto): {r[1]:,} ({r[1]*100.0/r[0] if r[0] else 0:.1f}%)")
print(f"   SIN posicion: {r[0]-r[1]:,}")

print("\n=== Cobertura TOTAL ZART 3M vs VBAP (clave exacta, sin filtro AEDAT) ===")
cur.execute("""
IF OBJECT_ID('tempdb..#vbap_all') IS NOT NULL DROP TABLE #vbap_all;
SELECT DISTINCT CONVERT(VARCHAR(20), VBELN) AS pedido
INTO #vbap_all
FROM dbo.VBAP_SAP;
""")
cur.execute("""
SELECT
    COUNT(*) AS zart_total,
    SUM(CASE WHEN V.pedido IS NOT NULL THEN 1 ELSE 0 END) AS en_vbap
FROM #zart Z
LEFT JOIN #vbap_all V ON V.pedido = Z.pedido
""")
r = cur.fetchone()
print(f"   ZART 3M total: {r[0]:,}")
print(f"   En VBAP (clave exacta, sin filtro): {r[1]:,} ({r[1]*100.0/r[0] if r[0] else 0:.1f}%)")
print(f"   SIN posicion: {r[0]-r[1]:,}")

c.close()
