# -*- coding: utf-8 -*-
"""Prueba la query del tramo VBFA directa (replica logica del SP sin ejecutarlo).

Lee credenciales desde variables de entorno (NS_SQL_UID / NS_SQL_PWD).
"""
import pyodbc, sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import conexion_sql

conn = conexion_sql.conectar()
cur = conn.cursor()

# Q1: valores distintos de VBTYP_V y VBTYP_N en VBFA
print("=== Valores VBTYP_V / VBTYP_N en VBFA_SAP ===")
try:
    cur.execute("""SELECT TOP 50 VBTYP_V, VBTYP_N, COUNT(*) AS N
        FROM dbo.VBFA_SAP
        GROUP BY VBTYP_V, VBTYP_N
        ORDER BY N DESC;""")
    for r in cur.fetchall():
        print(f"  V={r[0]} N={r[1]} -> {r[2]}")
except Exception as e:
    print(f"ERROR: {str(e)[:300]}")

# Q2: conteo tramo con filtro M-J -> C
print("\n=== Conteo VBFA VBTYP_V IN ('M','J') y VBTYP_N='C' ===")
try:
    cur.execute("""SELECT COUNT(*) AS TOTAL,
        COUNT(DISTINCT VBELV) AS PEDIDOS_ORIGINALES,
        COUNT(DISTINCT VBELN) AS DOCUMENTOS_POSTERIORES
        FROM dbo.VBFA_SAP
        WHERE VBTYP_V IN ('M','J') AND VBTYP_N = 'C';""")
    r = cur.fetchone()
    print(f"  TOTAL={r[0]} PED_ORIG={r[1]} DOC_POST={r[2]}")
except Exception as e:
    print(f"ERROR: {str(e)[:300]}")

# Q3: datos en la ventana 01-07 a 02-07?
print("\n=== Datos VBFA 01-07 a 02-07 ===")
try:
    cur.execute("""SELECT COUNT(*) AS N
        FROM dbo.VBFA_SAP
        WHERE TRY_CONVERT(date, ERDAT, 105) BETWEEN '2026-07-01' AND '2026-07-02';""")
    print(f"  Filas ventana = {cur.fetchone()[0]}")
except Exception as e:
    print(f"ERROR: {str(e)[:300]}")

conn.close()
