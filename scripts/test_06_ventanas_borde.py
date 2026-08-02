# -*- coding: utf-8 -*-
"""Prueba queries de ventanas de borde (solo SELECT).

Lee credenciales desde variables de entorno (NS_SQL_UID / NS_SQL_PWD).
Nota: ERDAT es varchar formato dd-MM-yyyy; se usa TRY_CONVERT estilo 105.
"""
import pyodbc, sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import conexion_sql

conn = conexion_sql.conectar()
cur = conn.cursor()

print("=== Borde 30-06 a 03-07 (TRY_CONVERT estilo 105) ===")
try:
    cur.execute("""SELECT COUNT(*) AS total,
        COUNT(DISTINCT VBELV) AS ped_orig, COUNT(DISTINCT VBELN) AS doc_post
        FROM dbo.VBFA_SAP
        WHERE VBTYP_V IN ('M','J') AND VBTYP_N = 'C'
          AND TRY_CONVERT(date, ERDAT, 105) >= TRY_CONVERT(date, '30-06-2026', 105)
          AND TRY_CONVERT(date, ERDAT, 105) <= TRY_CONVERT(date, '03-07-2026', 105);""")
    r = cur.fetchone()
    print(f"  total={r[0]} ped_orig={r[1]} doc_post={r[2]}")
except Exception as e:
    print(f"ERROR: {str(e)[:300]}")

print("\n=== Ventana solicitada 01-07 a 02-07 ===")
try:
    cur.execute("""SELECT COUNT(*) AS total,
        COUNT(DISTINCT VBELV) AS ped_orig, COUNT(DISTINCT VBELN) AS doc_post
        FROM dbo.VBFA_SAP
        WHERE VBTYP_V IN ('M','J') AND VBTYP_N = 'C'
          AND TRY_CONVERT(date, ERDAT, 105) >= TRY_CONVERT(date, '01-07-2026', 105)
          AND TRY_CONVERT(date, ERDAT, 105) <= TRY_CONVERT(date, '02-07-2026', 105);""")
    r = cur.fetchone()
    print(f"  total={r[0]} ped_orig={r[1]} doc_post={r[2]}")
except Exception as e:
    print(f"ERROR: {str(e)[:300]}")

conn.close()
