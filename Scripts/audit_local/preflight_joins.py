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
print("P2 — Joins con TRY_CONVERT/CONVERT(BIGINT): cardinalidad y NULLs")
print("="*70)

print("\n=== VBFA_SAP.VBELV: NULLs y no-numéricos ===")
q(cur, "SELECT COUNT(*) FROM dbo.VBFA_SAP WHERE VBELV IS NULL OR LTRIM(RTRIM(VBELV))=''", "VBFA VBELV null/blank")
q(cur, "SELECT COUNT(*) FROM dbo.VBFA_SAP WHERE TRY_CONVERT(BIGINT, VBELV) IS NULL", "VBFA VBELV no convertible a BIGINT")
q(cur, "SELECT COUNT(DISTINCT VBELV) FROM dbo.VBFA_SAP", "VBFA VBELV distintos")

print("\n=== VBFA_SAP.VBELV (referencia, VBTYP_V=V) vs VBELN (documento posterior) ===")
q(cur, "SELECT COUNT(DISTINCT TRY_CONVERT(BIGINT, VBELV)) FROM dbo.VBFA_SAP WHERE VBTYP_V='C' AND VBTYP_N='C'", "C->C VBELV distintos")
q(cur, "SELECT COUNT(DISTINCT CONVERT(VARCHAR(20), VBELN)) FROM dbo.VBFA_SAP WHERE VBTYP_V='C' AND VBTYP_N='C'", "C->C VBELN distintos")

print("\n=== VTTP_SAP: cardinalidad y NULLs ===")
q(cur, "SELECT COUNT(*) FROM dbo.VTTP_SAP", "VTTP total")
q(cur, "SELECT COUNT(*) FROM dbo.VTTP_SAP WHERE TRY_CONVERT(BIGINT, VBELN) IS NULL", "VTTP VBELN no convertible")
q(cur, "SELECT COUNT(DISTINCT VBELN) FROM dbo.VTTP_SAP", "VTTP VBELN distintos")

print("\n=== VBAK_SAP.KUNNR / KNA1_SAP.KUNNR (join cliente) ===")
q(cur, "SELECT COUNT(*) FROM dbo.VBAK_SAP WHERE TRY_CONVERT(BIGINT, KUNNR) IS NULL", "VBAK KUNNR no convertible")
q(cur, "SELECT COUNT(*) FROM dbo.KNA1_SAP WHERE TRY_CONVERT(BIGINT, KUNNR) IS NULL", "KNA1 KUNNR no convertible")

print("\n=== Duplicados en VBFA C->C a nivel VBELV+VBELN (para detectar multi-filas) ===")
q(cur, """
SELECT COUNT(*) FROM (
  SELECT VBELV, VBELN
  FROM dbo.VBFA_SAP
  WHERE VBTYP_V='C' AND VBTYP_N='C'
  GROUP BY VBELV, VBELN
  HAVING COUNT(*) > 1
) d
""", "Grupos VBELV+VBELN duplicados (C->C)")

c.close()
