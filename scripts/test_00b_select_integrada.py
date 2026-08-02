# -*- coding: utf-8 -*-
"""Prueba queries SELECT directas contra DMF_VTA_PRD sin ejecutar SP."""
import pyodbc, sys
sys.stdout.reconfigure(encoding="utf-8")

# Intentar autenticacion integrada Windows (la conexion puede estar activa ahora)
conn_strs = [
    ("Windows integrada", "DRIVER={ODBC Driver 17 for SQL Server};SERVER=128.1.3.21;DATABASE=DMF_VTA_PRD;Trusted_Connection=Yes;Connection Timeout=15;"),
]
conn = None
for label, cs in conn_strs:
    try:
        conn = pyodbc.connect(cs)
        print(f"OK conexion [{label}]")
        break
    except Exception as e:
        print(f"FAIL [{label}]: {str(e)[:200]}")

if not conn:
    print("\nNo se pudo conectar con Windows integrada.")
    print("Necesito credenciales SQL (UID/PWD) o una conexion activa.")
    sys.exit(1)

cur = conn.cursor()

# Query 1: Definicion del procedimiento (SELECT a sys.procedures - solo lectura)
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

# Query 2: Parametros
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

# Query 3: Verificar que existen las tablas VBFA/VTTP (solo lectura)
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
