import sys, time; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c=conectar(60); cur=c.cursor()

print("=== Impacto rendimiento: query SIN filtro AEDAT (Lineas_y_unidades_por_pedidos) ===")
t0 = time.perf_counter()
cur.execute("""
SELECT VBAP.VBELN AS Pedido, COUNT(*) AS Lineas, SUM(ISNULL(VBAP.KWMENG,0)) AS Suma_Unidades
FROM VBAP_SAP AS VBAP
GROUP BY VBAP.VBELN
""")
rows = cur.fetchall()
t1 = time.perf_counter()
print(f"  Filas agregadas (pedidos distintos): {len(rows):,}")
print(f"  Tiempo SQL: {t1-t0:.2f}s")

# Cobertura para el universo ZART 3M
print("\n=== Cobertura ZART 3M vs esta agregacion (sin AEDAT) ===")
cur.execute("""
IF OBJECT_ID('tempdb..#zart') IS NOT NULL DROP TABLE #zart;
SELECT DISTINCT CONVERT(VARCHAR(20), ZVBELN_PED) AS pedido
INTO #zart
FROM dbo.ZART_TRACK_DATA_SAP
WHERE ZERDAT_PED >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE));
""")
cur.execute("""
IF OBJECT_ID('tempdb..#vbap_agg') IS NOT NULL DROP TABLE #vbap_agg;
SELECT DISTINCT CONVERT(VARCHAR(20), VBELN) AS pedido
INTO #vbap_agg
FROM dbo.VBAP_SAP;
""")
cur.execute("""
SELECT COUNT(*) AS zart, SUM(CASE WHEN V.pedido IS NOT NULL THEN 1 ELSE 0 END) AS en_vbap
FROM #zart Z LEFT JOIN #vbap_agg V ON V.pedido = Z.pedido
""")
r = cur.fetchone()
print(f"  ZART 3M: {r[0]:,} | En VBAP: {r[1]:,} ({r[1]*100.0/r[0]:.1f}%) | Sin: {r[0]-r[1]:,}")

c.close()
