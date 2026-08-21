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
print("P0 — VBFA_SAP: filas por escenario")
print("="*70)

q(cur, "SELECT COUNT(*) FROM dbo.VBFA_SAP", "VBFA total")
q(cur, "SELECT COUNT(*) FROM dbo.VBFA_SAP WHERE VBTYP_V='C' AND VBTYP_N='C'", "VBFA C->C")
q(cur, "SELECT COUNT(*) FROM dbo.VBFA_SAP WHERE VBTYP_V='C' AND VBTYP_N='J'", "VBFA C->J")
q(cur, "SELECT COUNT(DISTINCT TRY_CONVERT(BIGINT, VBELV)) FROM dbo.VBFA_SAP WHERE VBTYP_V='C' AND VBTYP_N='C' AND TRY_CONVERT(BIGINT, VBELV) IS NOT NULL", "VBFA C->C pedidos originales distintos")

print()
print("=== Con filtro de fecha ERDAT >= 3 meses ===")
q(cur, "SELECT COUNT(*) FROM dbo.VBFA_SAP WHERE VBTYP_V='C' AND VBTYP_N='C' AND COALESCE(TRY_CONVERT(DATE, CONVERT(VARCHAR(30), ERDAT), 112), TRY_CONVERT(DATE, CONVERT(VARCHAR(30), ERDAT), 103), TRY_CONVERT(DATE, CONVERT(VARCHAR(30), ERDAT))) >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))", "VBFA C->C ERDAT>=3m")
q(cur, "SELECT COUNT(*) FROM dbo.VBFA_SAP WHERE VBTYP_V='C' AND VBTYP_N='J' AND COALESCE(TRY_CONVERT(DATE, CONVERT(VARCHAR(30), ERDAT), 112), TRY_CONVERT(DATE, CONVERT(VARCHAR(30), ERDAT), 103), TRY_CONVERT(DATE, CONVERT(VARCHAR(30), ERDAT))) >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))", "VBFA C->J ERDAT>=3m")

print()
print("="*70)
print("Distribución de ERDAT en VBFA C->C (para saber si 3 meses basta)")
print("="*70)
q(cur, "SELECT MIN(COALESCE(TRY_CONVERT(DATE, CONVERT(VARCHAR(30), ERDAT), 112), TRY_CONVERT(DATE, CONVERT(VARCHAR(30), ERDAT), 103))) FROM dbo.VBFA_SAP WHERE VBTYP_V='C' AND VBTYP_N='C'", "ERDAT MIN C->C")
q(cur, "SELECT MAX(COALESCE(TRY_CONVERT(DATE, CONVERT(VARCHAR(30), ERDAT), 112), TRY_CONVERT(DATE, CONVERT(VARCHAR(30), ERDAT), 103))) FROM dbo.VBFA_SAP WHERE VBTYP_V='C' AND VBTYP_N='C'", "ERDAT MAX C->C")

c.close()
