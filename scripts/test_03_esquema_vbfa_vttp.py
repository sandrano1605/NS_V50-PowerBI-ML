# -*- coding: utf-8 -*-
"""Explora esquema de VBFA_SAP y VTTP_SAP y prueba queries del tramo (solo SELECT).

Lee credenciales desde variables de entorno (NS_SQL_UID / NS_SQL_PWD).
"""
import pyodbc, sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import conexion_sql

conn = conexion_sql.conectar()
cur = conn.cursor()

print("=== Esquema VBFA_SAP ===")
try:
    cur.execute("""SELECT c.name AS COLUMNA, t.name AS TIPO
        FROM sys.columns c
        JOIN sys.types t ON c.user_type_id = t.user_type_id
        WHERE c.object_id = OBJECT_ID('dbo.VBFA_SAP')
        ORDER BY c.column_id;""")
    for r in cur.fetchall():
        print(f"  {r[0]} ({r[1]})")
except Exception as e:
    print(f"ERROR: {str(e)[:300]}")

print("\n=== Esquema VTTP_SAP ===")
try:
    cur.execute("""SELECT c.name AS COLUMNA, t.name AS TIPO
        FROM sys.columns c
        JOIN sys.types t ON c.user_type_id = t.user_type_id
        WHERE c.object_id = OBJECT_ID('dbo.VTTP_SAP')
        ORDER BY c.column_id;""")
    for r in cur.fetchall():
        print(f"  {r[0]} ({r[1]})")
except Exception as e:
    print(f"ERROR: {str(e)[:300]}")

conn.close()
