# -*- coding: utf-8 -*-
"""Prueba queries del tramo VBFA con interpretacion correcta de codigos (solo SELECT).

Lee credenciales desde variables de entorno (NS_SQL_UID / NS_SQL_PWD).
Interpretacion: 'M-J' = rango VBTYP_V IN ('M','J'); 'C' = pedido posterior (VBTYP_N='C').
"""
import pyodbc, sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import conexion_sql

conn = conexion_sql.conectar()
cur = conn.cursor()

print("=== VBTYP_N='C' (pedido posterior) agrupado por VBTYP_V ===")
try:
    cur.execute("""SELECT VBTYP_V, COUNT(*) AS N
        FROM dbo.VBFA_SAP
        WHERE VBTYP_N = 'C'
        GROUP BY VBTYP_V ORDER BY N DESC;""")
    for r in cur.fetchall():
        print(f"  V={r[0]} -> {r[1]}")
except Exception as e:
    print(f"ERROR: {str(e)[:300]}")

print("\n=== Tramo: VBTYP_V IN ('M','J') y VBTYP_N='C' ===")
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

print("\n=== VBTYP_V='M-J' literal (debe ser 0) ===")
try:
    cur.execute("SELECT COUNT(*) FROM dbo.VBFA_SAP WHERE VBTYP_V = 'M-J';")
    print(f"  Filas = {cur.fetchone()[0]}")
except Exception as e:
    print(f"ERROR: {str(e)[:300]}")

print("\n=== Muestra VBFA pedido posterior -> C ===")
try:
    cur.execute("""SELECT TOP 10 VBELV, VBTYP_V, VBELN, VBTYP_N, ERDAT, ERZET
        FROM dbo.VBFA_SAP
        WHERE VBTYP_N = 'C'
        ORDER BY ERDAT DESC;""")
    for r in cur.fetchall():
        print(f"  {r[0]} {r[1]} -> {r[2]} {r[3]} {r[4]} {r[5]}")
except Exception as e:
    print(f"ERROR: {str(e)[:300]}")

conn.close()
