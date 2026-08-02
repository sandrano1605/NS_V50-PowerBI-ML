# -*- coding: utf-8 -*-
"""Diagnostica ERDAT_DATE y formatos de fecha en VBFA_SAP (solo SELECT).

Lee credenciales desde variables de entorno (NS_SQL_UID / NS_SQL_PWD).
"""
import pyodbc, sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import conexion_sql

conn = conexion_sql.conectar()
cur = conn.cursor()

print("=== Tipo ERDAT_DATE ===")
cur.execute("""SELECT c.name, t.name AS tipo FROM sys.columns c
    JOIN sys.types t ON c.user_type_id = t.user_type_id
    WHERE c.object_id = OBJECT_ID('dbo.VBFA_SAP') AND c.name = 'ERDAT_DATE';""")
for r in cur.fetchall():
    print(f"  {r[0]} ({r[1]})")

print("\n=== Nulos/invalidos ERDAT_DATE en tramo ===")
try:
    cur.execute("""SELECT COUNT(*) AS total,
        SUM(CASE WHEN ERDAT_DATE IS NULL THEN 1 ELSE 0 END) AS nulos,
        SUM(CASE WHEN TRY_CAST(ERDAT_DATE AS datetime) IS NULL THEN 1 ELSE 0 END) AS invalidos
        FROM dbo.VBFA_SAP
        WHERE VBTYP_V IN ('M','J') AND VBTYP_N = 'C';""")
    r = cur.fetchone()
    print(f"  total={r[0]} nulos={r[1]} invalidos={r[2]}")
except Exception as e:
    print(f"ERROR: {str(e)[:300]}")

print("\n=== Formato ERDAT muestra ===")
cur.execute("SELECT TOP 5 ERDAT, ERDAT_DATE FROM dbo.VBFA_SAP WHERE ERDAT IS NOT NULL;")
for r in cur.fetchall():
    print(f"  ERDAT={repr(r[0])} ERDAT_DATE={r[1]}")

conn.close()
