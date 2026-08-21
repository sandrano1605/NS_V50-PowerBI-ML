import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c=conectar(120); cur=c.cursor()

print("=== ZART 3M: pedidos por AUART no aplica (ZART no tiene AUART). Solo pedidos ===")
cur.execute("""
SELECT COUNT(DISTINCT CONVERT(VARCHAR(20), ZVBELN_PED)) AS pedidos
FROM dbo.ZART_TRACK_DATA_SAP
WHERE ZERDAT_PED >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))
""")
zart_3m = cur.fetchone()[0]
print(f"  ZART 3M: {zart_3m:,}")

# Tabla temporal de pedidos ZART 3M
print("\n=== Crear temp de pedidos ZART 3M y cruzar con VBAP ===")
cur.execute("""
IF OBJECT_ID('tempdb..#zart') IS NOT NULL DROP TABLE #zart;
SELECT DISTINCT CONVERT(VARCHAR(20), ZVBELN_PED) AS pedido
INTO #zart
FROM dbo.ZART_TRACK_DATA_SAP
WHERE ZERDAT_PED >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE));
""")

cur.execute("""
SELECT COUNT(*) FROM #zart
""")
print(f"  Pedidos en #zart: {cur.fetchone()[0]:,}")

# Cruce con VBAP sin filtro AEDAT (usando temp VBAP con clave indexada)
print("\n=== VBAP distinct pedidos en temp (sin filtro AEDAT) ===")
cur.execute("""
IF OBJECT_ID('tempdb..#vbap') IS NOT NULL DROP TABLE #vbap;
SELECT DISTINCT CONVERT(VARCHAR(20), VBELN) AS pedido
INTO #vbap
FROM dbo.VBAP_SAP;
""")
cur.execute("SELECT COUNT(*) FROM #vbap")
print(f"  Pedidos en #vbap (todo VBAP, sin filtro): {cur.fetchone()[0]:,}")

print("\n=== Cobertura: #zart en #vbap ===")
cur.execute("""
SELECT COUNT(*) AS zart, SUM(CASE WHEN V.pedido IS NOT NULL THEN 1 ELSE 0 END) AS en_vbap
FROM #zart Z
LEFT JOIN #vbap V ON V.pedido = Z.pedido
""")
r = cur.fetchone()
print(f"  ZART 3M: {r[0]:,}")
print(f"  En VBAP (sin filtro): {r[1]:,} ({r[1]*100.0/r[0] if r[0] else 0:.1f}%)")
print(f"  SIN posiciones: {r[0]-r[1]:,}")

c.close()
