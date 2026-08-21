import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c = conectar(10)
cur = c.cursor()

# SAP_PRD VBAP check using three-part names (cross-db query from DMF_VTA_PRD)
tests = [
    ("VBAP tables in SAP_PRD",
     "SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE FROM SAP_PRD.INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE '%VBAP%'"),
    ("Tables with VBELN in SAP_PRD (top 30)",
     "SELECT TOP 30 TABLE_SCHEMA, TABLE_NAME FROM SAP_PRD.INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME='VBELN' ORDER BY TABLE_NAME"),
    ("YV01 in SAP_PRD.dbo.VBAP (sample 5)",
     "SELECT TOP 5 V.VBELN FROM SAP_PRD.dbo.VBAP V INNER JOIN DMF_VTA_PRD.dbo.VBAK_SAP K ON CAST(K.VBELN AS VARCHAR(20))=CAST(V.VBELN AS VARCHAR(20)) WHERE K.AUART='YV01' AND K.ERDAT>='2026-06-01'"),
    ("VISTA_PEDIDO definition (just WHERE clause)",
     "SELECT TOP 1 OBJECT_DEFINITION(OBJECT_ID('dbo.VISTA_PEDIDO')) AS def FROM sys.objects WHERE name='VISTA_PEDIDO'"),
]

for title, sql in tests:
    print(f"\n=== {title} ===")
    try:
        cur.execute(sql)
        if cur.description:
            for r in cur.fetchall():
                vals = [str(v)[:200] if v else 'NULL' for v in r]
                print('\t'.join(vals))
        print(f"({cur.rowcount} rows)")
    except Exception as e:
        print(f"ERROR: {str(e)[:300]}")

c.close()
