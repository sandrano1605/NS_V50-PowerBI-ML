import sys, time; sys.path.insert(0,'scripts')
from conexion_sql import conectar

def medir(cur, sql, label, n=3):
    tiempos = []
    for _ in range(n):
        t0 = time.perf_counter()
        cur.execute(sql)
        rows = cur.fetchall()
        t1 = time.perf_counter()
        tiempos.append(t1-t0)
    mejor = min(tiempos)
    filas = len(rows)
    print(f"  {label}: {mejor:.2f}s (mejor de {n}) | {filas} filas")
    return mejor, filas

c = conectar(timeout=300)
cur = c.cursor()

print("="*70)
print("CONSULTA ACTUAL: Lineas_y_unidades_por_pedidos (VBAP_SAP AEDAT 730d + GROUP BY)")
print("="*70)
medir(cur, """
SELECT VBAP.VBELN AS Pedido, COUNT(*) AS Lineas, SUM(ISNULL(VBAP.KWMENG,0)) AS Suma_Unidades
FROM VBAP_SAP AS VBAP
WHERE VBAP.AEDAT >= GETDATE() - 730
GROUP BY VBAP.VBELN
""", "ACTUAL 730d")

print()
print("="*70)
print("VARIANTE A: misma consulta pero AEDAT 90d (coincide con universo)")
print("="*70)
medir(cur, """
SELECT VBAP.VBELN AS Pedido, COUNT(*) AS Lineas, SUM(ISNULL(VBAP.KWMENG,0)) AS Suma_Unidades
FROM VBAP_SAP AS VBAP
WHERE VBAP.AEDAT >= GETDATE() - 90
GROUP BY VBAP.VBELN
""", "VARIANTE_A 90d")

print()
print("="*70)
print("VARIANTE B: VBAP limitado a pedidos recientes de VBAK (semi-join)")
print("="*70)
medir(cur, """
SELECT V.VBELN AS Pedido, COUNT(*) AS Lineas, SUM(ISNULL(V.KWMENG,0)) AS Suma_Unidades
FROM VBAP_SAP AS V
WHERE V.AEDAT >= GETDATE() - 730
  AND V.VBELN IN (SELECT DISTINCT K.VBELN FROM VBAK_SAP K WHERE K.ERDAT >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE)))
GROUP BY V.VBELN
""", "VARIANTE_B semi-join VBAK 90d")

print()
print("="*70)
print("VARIANTE C: VBAP sin GROUP BY global, solo para canales 43/45 via VBAK")
print("="*70)
medir(cur, """
SELECT V.VBELN AS Pedido, COUNT(*) AS Lineas, SUM(ISNULL(V.KWMENG,0)) AS Suma_Unidades
FROM VBAP_SAP AS V
INNER JOIN (SELECT DISTINCT K.VBELN FROM VBAK_SAP K
            WHERE K.ERDAT >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))
              AND RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),K.VTWEG))),2) IN ('43','45')) K
  ON K.VBELN = V.VBELN
WHERE V.AEDAT >= GETDATE() - 730
GROUP BY V.VBELN
""", "VARIANTE_C solo 43/45")

print()
print("="*70)
print("VBAKHoraOrigen (fix IN02): VBAK 90d canales 43/45")
print("="*70)
medir(cur, """
SELECT
    CONVERT(VARCHAR(20), TRY_CONVERT(BIGINT, V.VBELN)) AS PED_KEY,
    TRY_CONVERT(TIME(0), NULLIF(LTRIM(RTRIM(V.ERZET)), '')) AS HORA_VBAK
FROM dbo.VBAK_SAP AS V
WHERE RIGHT('00' + LTRIM(RTRIM(CONVERT(VARCHAR(10), V.VTWEG))), 2) IN ('43','45')
  AND COALESCE(TRY_CONVERT(DATE, CONVERT(VARCHAR(30), V.ERDAT), 112),
               TRY_CONVERT(DATE, CONVERT(VARCHAR(30), V.ERDAT), 103),
               TRY_CONVERT(DATE, CONVERT(VARCHAR(30), V.ERDAT))) >= DATEADD(MONTH, -3, CAST(GETDATE() AS DATE))
""", "VBAKHoraOrigen fix")

c.close()
