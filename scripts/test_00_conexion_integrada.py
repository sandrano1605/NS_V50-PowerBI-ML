# -*- coding: utf-8 -*-
"""Prueba conexion SQL Server 128.1.3.21/DMF_VTA_PRD con autenticacion integrada Windows."""
import pyodbc, sys
sys.stdout.reconfigure(encoding="utf-8")

conn_strs = [
    ("Windows integrada", "DRIVER={ODBC Driver 17 for SQL Server};SERVER=128.1.3.21;DATABASE=DMF_VTA_PRD;Trusted_Connection=Yes;"),
    ("Windows integrada + puerto", "DRIVER={ODBC Driver 17 for SQL Server};SERVER=128.1.3.21,1433;DATABASE=DMF_VTA_PRD;Trusted_Connection=Yes;"),
]
for label, cs in conn_strs:
    try:
        conn = pyodbc.connect(cs, timeout=10)
        cur = conn.cursor()
        cur.execute("SELECT DB_NAME(), SYSTEM_USER, CURRENT_USER")
        row = cur.fetchone()
        print(f"OK [{label}]: DB={row[0]} login={row[1]} user={row[2]}")
        conn.close()
        break
    except Exception as e:
        print(f"FAIL [{label}]: {str(e)[:200]}")
