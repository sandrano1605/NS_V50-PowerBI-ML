# -*- coding: utf-8 -*-
"""Prueba conexion SQL Server y ejecuta definicion del SP VBFA.

Intenta en orden: Windows integrada, SQL auth sin password, y SQL auth por variables de entorno.
"""
import pyodbc, sys, os
sys.stdout.reconfigure(encoding="utf-8")

conn_strs = [
    ("Windows integrada", "DRIVER={ODBC Driver 17 for SQL Server};SERVER=128.1.3.21;DATABASE=DMF_VTA_PRD;Trusted_Connection=Yes;"),
    ("SQL auth (variables entorno)", None),  # se arma despues con helper
]
for label, cs in conn_strs:
    try:
        if cs is None:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import conexion_sql
            conn = conexion_sql.conectar()
        else:
            conn = pyodbc.connect(cs, timeout=15)
        cur = conn.cursor()
        cur.execute("SELECT DB_NAME(), SYSTEM_USER")
        row = cur.fetchone()
        print(f"OK [{label}]: DB={row[0]} login={row[1]}")
        conn.close()
        break
    except Exception as e:
        print(f"FAIL [{label}]: {str(e)[:250]}")
