import sys
sys.path.insert(0, 'scripts')
from conexion_sql import conectar

conn = conectar(timeout=10)
cur = conn.cursor()

queries = [
    ("OBJETOS VBAP/VBAP_SAP",
     "SELECT s.name+'.'+o.name AS obj, o.type, o.type_desc, o.create_date FROM sys.objects o JOIN sys.schemas s ON o.schema_id=s.schema_id WHERE o.name LIKE '%VBAP%' ORDER BY s.name, o.name"),
    ("SINONIMOS VBAP",
     "SELECT s.name+'.'+sy.name AS syn, base_object_name FROM sys.synonyms sy JOIN sys.schemas s ON sy.schema_id=s.schema_id WHERE sy.name LIKE '%VBAP%'"),
    ("DEFINICION VBAP_SAP",
     "SELECT sm.definition FROM sys.sql_modules sm JOIN sys.objects o ON sm.object_id=o.object_id WHERE o.name='VBAP_SAP'"),
    ("DEPENDENCIAS VBAP_SAP",
     "SELECT OBJECT_NAME(referencing_id) AS ref_obj, referenced_server_name+'.'+ISNULL(referenced_database_name,'')+'.'+ISNULL(referenced_schema_name,'')+'.'+referenced_entity_name AS depends_on FROM sys.sql_expression_dependencies WHERE OBJECT_NAME(referencing_id)='VBAP_SAP'"),
    ("COBERTURA VBAK->VBAP (30d)",
     "SELECT COUNT(DISTINCT K.VBELN) AS headers_vbak, COUNT(DISTINCT V.VBELN) AS headers_in_vbap, COUNT(DISTINCT V.VBELN)*100.0/COUNT(DISTINCT K.VBELN) AS pct FROM (SELECT DISTINCT VBELN FROM VBAK_SAP WHERE ERDAT >= GETDATE()-90) K LEFT JOIN VBAP_SAP V ON V.VBELN=K.VBELN AND V.AEDAT >= GETDATE()-730"),
    ("GAP POR AUART",
     "SELECT K.AUART, COUNT(DISTINCT K.VBELN) AS headers, COUNT(DISTINCT V.VBELN) AS in_vbap FROM (SELECT DISTINCT VBELN, AUART FROM VBAK_SAP WHERE ERDAT >= GETDATE()-90) K LEFT JOIN VBAP_SAP V ON V.VBELN=K.VBELN AND V.AEDAT >= GETDATE()-730 GROUP BY K.AUART ORDER BY headers DESC"),
    ("COMPARACION dbo.VBAP",
     "SELECT 'VBAP_SAP' as src, COUNT(DISTINCT VBELN) AS total, MIN(AEDAT) as min_aedat, MAX(AEDAT) as max_aedat FROM VBAP_SAP UNION ALL SELECT 'dbo.VBAP' as src, COUNT(DISTINCT VBELN), MIN(AEDAT), MAX(AEDAT) FROM dbo.VBAP"),
]

for title, sql in queries:
    print(f"\n=== {title} ===")
    try:
        cur.execute(sql)
        if cur.description:
            cols = [d[0] for d in cur.description]
            print('\t'.join(cols))
            for r in cur.fetchall():
                vals = [str(v)[:120] if v is not None else 'NULL' for v in r]
                print('\t'.join(vals))
        print(f"({cur.rowcount} rows)")
    except Exception as e:
        print(f"ERROR: {str(e)[:300]}")

conn.close()
