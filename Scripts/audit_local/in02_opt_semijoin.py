import sys, time; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c=conectar(120); cur=c.cursor()

print("=== Optimizacion: semi-join VBAP con universo VBAK reciente (sin AEDAT) ===")
print("  Filtra VBAP por los pedidos que estan en VBAK en ventana 6M canales 42-47")
t0 = time.perf_counter()
cur.execute("""
SELECT V.VBELN AS Pedido, COUNT(*) AS Lineas, SUM(ISNULL(V.KWMENG,0)) AS Suma_Unidades
FROM VBAP_SAP AS V
WHERE V.VBELN IN (
    SELECT DISTINCT K.VBELN
    FROM dbo.VBAK_SAP K
    WHERE K.ERDAT >= DATEADD(MONTH,-6,CAST(GETDATE() AS DATE))
      AND RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),K.VTWEG))),2) IN ('42','43','44','45','46','47')
)
GROUP BY V.VBELN
""")
rows = cur.fetchall()
t1 = time.perf_counter()
print(f"  Filas agregadas: {len(rows):,}")
print(f"  Tiempo SQL: {t1-t0:.2f}s")

print("\n=== Cobertura ZART 3M con esta version optimizada ===")
cur.execute("""
IF OBJECT_ID('tempdb..#zart') IS NOT NULL DROP TABLE #zart;
SELECT DISTINCT CONVERT(VARCHAR(20), ZVBELN_PED) AS pedido
INTO #zart
FROM dbo.ZART_TRACK_DATA_SAP
WHERE ZERDAT_PED >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE));
""")
cur.execute("""
IF OBJECT_ID('tempdb..#vbap_opt') IS NOT NULL DROP TABLE #vbap_opt;
SELECT DISTINCT CONVERT(VARCHAR(20), VBELN) AS pedido
INTO #vbap_opt
FROM dbo.VBAP_SAP AS V
WHERE V.VBELN IN (
    SELECT DISTINCT K.VBELN FROM dbo.VBAK_SAP K
    WHERE K.ERDAT >= DATEADD(MONTH,-6,CAST(GETDATE() AS DATE))
      AND RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),K.VTWEG))),2) IN ('42','43','44','45','46','47')
);
""")
cur.execute("""
SELECT COUNT(*) AS zart, SUM(CASE WHEN V.pedido IS NOT NULL THEN 1 ELSE 0 END) AS en_vbap
FROM #zart Z LEFT JOIN #vbap_opt V ON V.pedido = Z.pedido
""")
r = cur.fetchone()
print(f"  ZART 3M: {r[0]:,} | En VBAP (opt): {r[1]:,} ({r[1]*100.0/r[0]:.1f}%) | Sin: {r[0]-r[1]:,}")

c.close()
