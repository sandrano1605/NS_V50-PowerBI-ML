import sys, time; sys.path.insert(0,'scripts')
from conexion_sql import conectar

def q(cur, sql, label):
    t0 = time.perf_counter()
    cur.execute(sql)
    r = cur.fetchone()
    t1 = time.perf_counter()
    vals = tuple(str(x) if x is not None else 'NULL' for x in r)
    print(f"  {label}: {vals}  [{t1-t0:.2f}s]")

c = conectar(120); cur = c.cursor()

print("="*70)
print("P0 — ¿Filtrar VBFA a 3 meses pierde FES/entregas/manifiestos?")
print("="*70)

# Universo ZART 3M (pedidos del reporte)
cur.execute("""
IF OBJECT_ID('tempdb..#zart3m') IS NOT NULL DROP TABLE #zart3m;
SELECT DISTINCT TRY_CONVERT(BIGINT, ZVBELN_PED) AS pedido
INTO #zart3m
FROM dbo.ZART_TRACK_DATA_SAP
WHERE ZERDAT_PED >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE));
""")
q(cur, "SELECT COUNT(*) FROM #zart3m", "ZART 3M pedidos")

# ¿Cuántos pedidos del universo tienen VBFA C->C con ERDAT fuera de 3 meses?
print()
print("=== VBFA C->C (pedidos posteriores) por rango de ERDAT ===")
q(cur, """
SELECT
    COUNT(DISTINCT TRY_CONVERT(BIGINT, VBELV)) AS pedidos_orig
FROM dbo.VBFA_SAP
WHERE VBTYP_V='C' AND VBTYP_N='C'
  AND TRY_CONVERT(BIGINT, VBELV) IN (SELECT pedido FROM #zart3m)
  AND COALESCE(TRY_CONVERT(DATE, CONVERT(VARCHAR(30), ERDAT), 112), TRY_CONVERT(DATE, CONVERT(VARCHAR(30), ERDAT), 103)) < DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))
""", "Pedidos universo con C->C ERDAT<3m (se perderian con filtro)")

q(cur, """
SELECT
    COUNT(DISTINCT TRY_CONVERT(BIGINT, VBELV)) AS pedidos_orig
FROM dbo.VBFA_SAP
WHERE VBTYP_V='C' AND VBTYP_N='C'
  AND TRY_CONVERT(BIGINT, VBELV) IN (SELECT pedido FROM #zart3m)
  AND COALESCE(TRY_CONVERT(DATE, CONVERT(VARCHAR(30), ERDAT), 112), TRY_CONVERT(DATE, CONVERT(VARCHAR(30), ERDAT), 103)) >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))
""", "Pedidos universo con C->C ERDAT>=3m (se conservan)")

print()
print("=== VBFA C->J (entregas posteriores) por rango de ERDAT, para pedidos universo ===")
q(cur, """
SELECT
    COUNT(DISTINCT TRY_CONVERT(BIGINT, VBELV)) AS pedidos_orig
FROM dbo.VBFA_SAP
WHERE VBTYP_V='C' AND VBTYP_N='J'
  AND TRY_CONVERT(BIGINT, VBELV) IN (SELECT pedido FROM #zart3m)
  AND COALESCE(TRY_CONVERT(DATE, CONVERT(VARCHAR(30), ERDAT), 112), TRY_CONVERT(DATE, CONVERT(VARCHAR(30), ERDAT), 103)) < DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))
""", "Pedidos universo con C->J ERDAT<3m (se perderian)")

q(cur, """
SELECT
    COUNT(DISTINCT TRY_CONVERT(BIGINT, VBELV)) AS pedidos_orig
FROM dbo.VBFA_SAP
WHERE VBTYP_V='C' AND VBTYP_N='J'
  AND TRY_CONVERT(BIGINT, VBELV) IN (SELECT pedido FROM #zart3m)
  AND COALESCE(TRY_CONVERT(DATE, CONVERT(VARCHAR(30), ERDAT), 112), TRY_CONVERT(DATE, CONVERT(VARCHAR(30), ERDAT), 103)) >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))
""", "Pedidos universo con C->J ERDAT>=3m (se conservan)")

c.close()
