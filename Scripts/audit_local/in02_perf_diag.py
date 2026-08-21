import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c = conectar(10); cur = c.cursor()

print("=== Tamano tablas fuente ===")
cur.execute("""
SELECT t.name, SUM(p.rows) AS filas
FROM sys.tables t
JOIN sys.partitions p ON t.object_id=p.object_id AND p.index_id IN (0,1)
WHERE t.name IN ('ZART_TRACK_DATA_SAP','VBAK_SAP','VBAP_SAP','Fact_Pedidos_Auditoria','Pedidos_Normal_VBAK')
GROUP BY t.name ORDER BY filas DESC
""")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]:,} filas")

print("\n=== VBAK_SAP: total vs ventana 90d (canales 43/45) ===")
cur.execute("""
SELECT
    COUNT(*) AS total_filas,
    COUNT(DISTINCT VBELN) AS total_pedidos,
    SUM(CASE WHEN ERDAT >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE)) THEN 1 ELSE 0 END) AS filas_90d
FROM dbo.VBAK_SAP
""")
r = cur.fetchone()
print(f"  VBAK_SAP total: {r[0]:,} filas / {r[1]:,} pedidos / {r[2]:,} en 90d")

print("\n=== Indices VBAK_SAP ===")
cur.execute("""
SELECT i.name, i.type_desc, STRING_AGG(COL_NAME(ic.object_id, ic.column_id), ',') WITHIN GROUP (ORDER BY ic.key_ordinal) AS cols
FROM sys.indexes i
JOIN sys.index_columns ic ON i.object_id=ic.object_id AND i.index_id=ic.index_id
WHERE i.object_id = OBJECT_ID('dbo.VBAK_SAP') AND i.index_id > 0
GROUP BY i.name, i.type_desc
""")
for r in cur.fetchall():
    print(f"  {r[0]} ({r[1]}): {r[2]}")

print("\n=== ZART_TRACK_DATA_SAP: total vs ventana 90d ===")
cur.execute("""
SELECT
    COUNT(*) AS total_filas,
    COUNT(DISTINCT ZVBELN_PED) AS total_pedidos
FROM dbo.ZART_TRACK_DATA_SAP
""")
r = cur.fetchone()
print(f"  ZART total: {r[0]:,} filas / {r[1]:,} pedidos")

print("\n=== Indices ZART_TRACK_DATA_SAP ===")
cur.execute("""
SELECT i.name, i.type_desc
FROM sys.indexes i
WHERE i.object_id = OBJECT_ID('dbo.ZART_TRACK_DATA_SAP') AND i.index_id > 0
""")
for r in cur.fetchall():
    print(f"  {r[0]} ({r[1]})")

c.close()
