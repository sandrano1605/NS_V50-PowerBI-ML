# -*- coding: utf-8 -*-
"""Prueba queries SELECT directas contra DMF_VTA_PRD (solo lectura, sin EXEC).

Lee credenciales desde variables de entorno (NS_SQL_UID / NS_SQL_PWD).
"""
import pyodbc, sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import conexion_sql

conn = conexion_sql.conectar()
print("OK conexion SQL auth")
cur = conn.cursor()

# Q1: Definicion del procedimiento
print("\n=== Q1: sys.procedures definicion ===")
try:
    cur.execute("""SELECT DB_NAME() AS BASE_DATOS,
        OBJECT_SCHEMA_NAME(p.object_id) AS ESQUEMA,
        p.name AS PROCEDIMIENTO,
        p.create_date AS FECHA_CREACION,
        p.modify_date AS FECHA_MODIFICACION
        FROM sys.procedures AS p
        WHERE p.name = 'STP_GET_VBFA_TRAMO_FILTRO';""")
    rows = cur.fetchall()
    print(f"Filas: {len(rows)}")
    for r in rows:
        print(f"  DB={r[0]} ESQ={r[1]} SP={r[2]} Creado={r[3]} Modif={r[4]}")
except Exception as e:
    print(f"ERROR Q1: {str(e)[:300]}")

# Q2: Parametros
print("\n=== Q2: sys.parameters ===")
try:
    cur.execute("""SELECT prm.parameter_id, prm.name AS PARAMETRO,
        TYPE_NAME(prm.user_type_id) AS TIPO, prm.max_length,
        prm.precision, prm.scale, prm.is_output
        FROM sys.parameters AS prm
        WHERE prm.object_id = OBJECT_ID('dbo.STP_GET_VBFA_TRAMO_FILTRO')
        ORDER BY prm.parameter_id;""")
    rows = cur.fetchall()
    print(f"Filas: {len(rows)}")
    for r in rows:
        print(f"  id={r[0]} {r[1]} tipo={r[2]} max={r[3]} prec={r[4]} scale={r[5]} out={r[6]}")
except Exception as e:
    print(f"ERROR Q2: {str(e)[:300]}")

# Q3: Tablas VBFA/VTTP
print("\n=== Q3: tablas VBFA_SAP / VTTP_SAP ===")
try:
    cur.execute("""SELECT t.name AS TABLA, s.name AS ESQUEMA
        FROM sys.tables t JOIN sys.schemas s ON t.schema_id = s.schema_id
        WHERE t.name IN ('VBFA_SAP','VTTP_SAP') ORDER BY t.name;""")
    rows = cur.fetchall()
    print(f"Filas: {len(rows)}")
    for r in rows:
        print(f"  {r[1]}.{r[0]}")
except Exception as e:
    print(f"ERROR Q3: {str(e)[:300]}")

conn.close()
