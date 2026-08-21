import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c = conectar(10); cur = c.cursor()

print("=== Indices VBAK_SAP ===")
cur.execute("""
SELECT i.name, i.type_desc
FROM sys.indexes i
WHERE i.object_id = OBJECT_ID('dbo.VBAK_SAP') AND i.index_id > 0
""")
for r in cur.fetchall(): print(f"  {r[0]} ({r[1]})")

print("\n=== Indices ZART_TRACK_DATA_SAP ===")
cur.execute("""
SELECT i.name, i.type_desc
FROM sys.indexes i
WHERE i.object_id = OBJECT_ID('dbo.ZART_TRACK_DATA_SAP') AND i.index_id > 0
""")
for r in cur.fetchall(): print(f"  {r[0]} ({r[1]})")

print("\n=== VBAK_SAP filas por canal (VTWEG) 90d ===")
cur.execute("""
SELECT RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),VTWEG))),2) AS canal, COUNT(*) AS filas
FROM dbo.VBAK_SAP
WHERE ERDAT >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))
GROUP BY RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),VTWEG))),2)
ORDER BY filas DESC
""")
for r in cur.fetchall(): print(f"  canal {r[0]}: {r[1]:,}")

print("\n=== Datos brutos VBAK_SAP 90d canales 43/45 ===")
cur.execute("""
SELECT COUNT(*) AS filas
FROM dbo.VBAK_SAP
WHERE ERDAT >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))
  AND RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),VTWEG))),2) IN ('43','45')
""")
print(f"  {cur.fetchone()[0]:,} filas")

c.close()
