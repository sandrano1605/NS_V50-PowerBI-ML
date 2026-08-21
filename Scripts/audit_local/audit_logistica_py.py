import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c=conectar(60); cur=c.cursor()

print("=== Recalculo independiente de hitos desde ZART (columnas crudas reales) ===")
print("  ENT = ZP_ERDAT_ENT + ZP_ERZET_ENT")
print("  FAC = ZP_ERDAT_FAC + ZP_UZEIT_FAC")
print("  TRP = ZP_ERDAT_TRP + ZP_UZEIT_TRP")
print("  CRD = ZP_UDATE_CRD + ZP_UTIME_CRD")

# Muestra cruda de fechas compuestas
cur.execute("""
SELECT TOP 5
    ZVBELN_PED,
    ZERDAT_PED, ZERZET_PED,
    ZP_UDATE_CRD, ZP_UTIME_CRD,
    ZP_ERDAT_ENT, ZP_ERZET_ENT,
    ZP_ERDAT_FAC, ZP_UZEIT_FAC,
    ZP_ERDAT_TRP, ZP_UZEIT_TRP
FROM dbo.ZART_TRACK_DATA_SAP
WHERE ZERDAT_PED >= '2026-06-01'
""")
cols = [d[0] for d in cur.description]
print("\n" + "\t".join(cols))
for r in cur.fetchall():
    print("\t".join(str(x)[:17] if x else 'NULL' for x in r))

print("\n=== Nulos en fechas de hitos (universo 3M, todos canales) ===")
cur.execute("""
SELECT COUNT(*) AS total,
    SUM(CASE WHEN ZP_ERDAT_ENT IS NULL THEN 1 ELSE 0 END) AS ENT_null,
    SUM(CASE WHEN ZP_ERDAT_FAC IS NULL THEN 1 ELSE 0 END) AS FAC_null,
    SUM(CASE WHEN ZP_ERDAT_TRP IS NULL THEN 1 ELSE 0 END) AS TRP_null,
    SUM(CASE WHEN ZP_UDATE_CRD IS NULL THEN 1 ELSE 0 END) AS CRD_null
FROM dbo.ZART_TRACK_DATA_SAP
WHERE ZERDAT_PED >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))
""")
r = cur.fetchone()
print(f"  total={r[0]:,} ENT_null={r[1]:,} FAC_null={r[2]:,} TRP_null={r[3]:,} CRD_null={r[4]:,}")

c.close()
