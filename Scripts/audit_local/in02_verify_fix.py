import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c = conectar(10); cur = c.cursor()

print("=== Parser corregido (fix efbfda7): TRY_CONVERT(TIME(0), NULLIF(LTRIM(RTRIM(ERZET)),'')) ===")
cur.execute("""
SELECT
    V.VBELN,
    V.ERZET,
    NULLIF(LTRIM(RTRIM(V.ERZET)), '') AS erzet_trim,
    TRY_CONVERT(TIME(0), NULLIF(LTRIM(RTRIM(V.ERZET)), '')) AS HORA_VBAK,
    CASE WHEN TRY_CONVERT(TIME(0), NULLIF(LTRIM(RTRIM(V.ERZET)), '')) IS NULL THEN 'NULL' ELSE 'OK' END AS estado
FROM dbo.VBAK_SAP AS V
WHERE CONVERT(VARCHAR(20), TRY_CONVERT(BIGINT, V.VBELN)) IN ('1166551','1166552','1166574','1166596','1166599','4190139307','4190139329','1166496','1166503','4190139326')
""")
cols = [d[0] for d in cur.description]
print('\t'.join(cols))
for r in cur.fetchall():
    print('\t'.join(repr(x) if x is not None else 'NULL' for x in r))

print("\n=== Conteo de VBAK recuperables con parser corregido (canales 43/45, 3 meses) ===")
cur.execute("""
SELECT
    COUNT(*) AS filas,
    SUM(CASE WHEN TRY_CONVERT(TIME(0), NULLIF(LTRIM(RTRIM(ERZET)), '')) IS NOT NULL
          AND TRY_CONVERT(TIME(0), NULLIF(LTRIM(RTRIM(ERZET)), '')) <> CAST('00:00:00' AS TIME)
         THEN 1 ELSE 0 END) AS horas_validas_no_cero
FROM dbo.VBAK_SAP
WHERE RIGHT('00' + LTRIM(RTRIM(CONVERT(VARCHAR(10), VTWEG))), 2) IN ('43','45')
  AND COALESCE(
        TRY_CONVERT(DATE, CONVERT(VARCHAR(30), ERDAT), 112),
        TRY_CONVERT(DATE, CONVERT(VARCHAR(30), ERDAT), 103),
        TRY_CONVERT(DATE, CONVERT(VARCHAR(30), ERDAT))
      ) >= DATEADD(MONTH, -3, CAST(GETDATE() AS DATE))
""")
for r in cur.fetchall(): print(f"filas={r[0]}, horas_validas={r[1]}")

c.close()
