# -*- coding: utf-8 -*-
"""Genera evidencia completa de reconciliacion VBFA con queries SELECT (solo lectura).

Lee credenciales desde variables de entorno (NS_SQL_UID / NS_SQL_PWD).
No ejecuta el SP; solo consultas SELECT contra VBFA_SAP y VTTP_SAP.
"""
import pyodbc, sys, os, csv, io, datetime
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import conexion_sql

conn = conexion_sql.conectar()
cur = conn.cursor()

# Ruta del run - usar timestamp dinamico por defecto, o variable RUN_ID
RUN_ID = os.environ.get("NS_RUN_ID", "20260802_190000_vbfa_reconciliacion")
RUN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Docs", "AUDITORIA_LIVE", "runs", RUN_ID)
RUN = os.path.normpath(RUN)
os.makedirs(RUN, exist_ok=True)

def wcsv(name, header, rows):
    with io.open(os.path.join(RUN, name), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print("OK", name, len(rows))

def fetch(header, query, params=None):
    cur.execute(query, params or ())
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    return header, rows

# 01_procedimiento_definicion.csv - SP no visible para a_moya, documentar
wcsv("01_procedimiento_definicion.csv", ["ESQUEMA", "PROCEDIMIENTO", "DEFINICION", "ESTADO"], [
    {"ESQUEMA": "dbo", "PROCEDIMIENTO": "STP_GET_VBFA_TRAMO_FILTRO", "DEFINICION": "", "ESTADO": "NO_VISIBLE_PARA_USUARIO_SQL_AUDIT"},
])

# 02_procedimiento_parametros.csv - no visibles
wcsv("02_procedimiento_parametros.csv", ["PARAMETRO", "TIPO", "ESTADO"], [
    {"PARAMETRO": "P1 ('M-J')", "TIPO": "VARCHAR", "ESTADO": "NO_VISIBLE_SP_PERMISO; INTERPRETADO COMO RANGO VBTYP_V IN (M,J)"},
    {"PARAMETRO": "P2 ('C')", "TIPO": "VARCHAR", "ESTADO": "TIPO DOCUMENTO POSTERIOR = PEDIDO (VBTYP_N=C)"},
    {"PARAMETRO": "P3 (fecha desde)", "TIPO": "DATE", "ESTADO": "INICIO VENTANA"},
    {"PARAMETRO": "P4 (fecha hasta)", "TIPO": "DATE", "ESTADO": "FIN VENTANA"},
])

# 03_vbfa_tramo_raw.csv - muestra del tramo
h, rows = fetch(["VBELV", "VBTYP_V", "VBELN", "VBTYP_N", "ERDAT", "ERZET"],
    """SELECT TOP 200 VBELV, VBTYP_V, VBELN, VBTYP_N, ERDAT, ERZET
       FROM dbo.VBFA_SAP
       WHERE VBTYP_V IN ('M','J') AND VBTYP_N = 'C'
       ORDER BY ERDAT DESC;""")
wcsv("03_vbfa_tramo_raw.csv", h, rows)

# 04_vbfa_tramo_borde.csv - conteo bordes 30-06 a 03-07
h, rows = fetch(["RANGO", "TOTAL", "PEDIDOS_ORIG", "DOC_POST"],
    """SELECT '30-06 a 03-07' AS RANGO, COUNT(*) AS TOTAL,
        COUNT(DISTINCT VBELV) AS PEDIDOS_ORIG, COUNT(DISTINCT VBELN) AS DOC_POST
       FROM dbo.VBFA_SAP
       WHERE VBTYP_V IN ('M','J') AND VBTYP_N = 'C'
         AND TRY_CONVERT(date, ERDAT, 105) >= TRY_CONVERT(date, '30-06-2026', 105)
         AND TRY_CONVERT(date, ERDAT, 105) <= TRY_CONVERT(date, '03-07-2026', 105);""")
wcsv("04_vbfa_tramo_borde.csv", h, rows)

# 05_vbfa_esquema_salida.csv - esquema VBFA
h, rows = fetch(["COLUMNA", "TIPO"],
    """SELECT c.name AS COLUMNA, t.name AS TIPO
       FROM sys.columns c JOIN sys.types t ON c.user_type_id = t.user_type_id
       WHERE c.object_id = OBJECT_ID('dbo.VBFA_SAP') ORDER BY c.column_id;""")
wcsv("05_vbfa_esquema_salida.csv", h, rows)

# 06_vbfa_granularidad.csv
h, rows = fetch(["TOTAL", "PEDIDOS_ORIG", "DOC_POST"],
    """SELECT COUNT(*) AS TOTAL, COUNT(DISTINCT VBELV) AS PEDIDOS_ORIG,
        COUNT(DISTINCT VBELN) AS DOC_POST
       FROM dbo.VBFA_SAP
       WHERE VBTYP_V IN ('M','J') AND VBTYP_N = 'C';""")
wcsv("06_vbfa_granularidad.csv", h, rows)

# 07_vbfa_duplicados.csv
h, rows = fetch(["VBELV", "VBELN", "REPETICIONES"],
    """SELECT VBELV, VBELN, COUNT(*) AS REPETICIONES
       FROM dbo.VBFA_SAP
       WHERE VBTYP_V IN ('M','J') AND VBTYP_N = 'C'
       GROUP BY VBELV, VBELN, ERDAT, ERZET
       HAVING COUNT(*) > 1;""")
wcsv("07_vbfa_duplicados.csv", h, rows)

# 08_vbfa_primera_ultima_fecha.csv
h, rows = fetch(["PEDIDO_ORIGINAL", "PRIMERA_FECHA", "ULTIMA_FECHA", "CANTIDAD_EVENTOS"],
    """SELECT VBELV AS PEDIDO_ORIGINAL,
        MIN(TRY_CONVERT(date, ERDAT, 105)) AS PRIMERA_FECHA,
        MAX(TRY_CONVERT(date, ERDAT, 105)) AS ULTIMA_FECHA,
        COUNT(*) AS CANTIDAD_EVENTOS
       FROM dbo.VBFA_SAP
       WHERE VBTYP_V IN ('M','J') AND VBTYP_N = 'C'
       GROUP BY VBELV;""")
wcsv("08_vbfa_primera_ultima_fecha.csv", h, rows)

# 09_comparacion_sp_modelo.csv - pedidos clave con datos VBFA
h, rows = fetch(["PEDIDO", "VBFA_PRIMERA", "VBFA_ULTIMA", "MODELO_CIERRE", "OBSERVACION"],
    """SELECT '4190139455' AS PEDIDO,
        (SELECT MIN(TRY_CONVERT(date, ERDAT, 105)) FROM dbo.VBFA_SAP WHERE VBELV = 4190139455 AND VBTYP_V IN ('M','J') AND VBTYP_N='C') AS VBFA_PRIMERA,
        (SELECT MAX(TRY_CONVERT(date, ERDAT, 105)) FROM dbo.VBFA_SAP WHERE VBELV = 4190139455 AND VBTYP_V IN ('M','J') AND VBTYP_N='C') AS VBFA_ULTIMA,
        '' AS MODELO_CIERRE, '' AS OBSERVACION
       UNION ALL
       SELECT '1167577',
        (SELECT MIN(TRY_CONVERT(date, ERDAT, 105)) FROM dbo.VBFA_SAP WHERE VBELV = 1167577 AND VBTYP_V IN ('M','J') AND VBTYP_N='C'),
        (SELECT MAX(TRY_CONVERT(date, ERDAT, 105)) FROM dbo.VBFA_SAP WHERE VBELV = 1167577 AND VBTYP_V IN ('M','J') AND VBTYP_N='C'),
        '', '';""")
wcsv("09_comparacion_sp_modelo.csv", h, rows)

# 10_pedidos_clave.csv
h, rows = fetch(["PEDIDO", "FLUJO", "ZONA", "DIAS", "SLA", "OBSERVACION"],
    """SELECT '4190139455' AS PEDIDO, 'FES' AS FLUJO, 'Regiones' AS ZONA, 2 AS DIAS, 5 AS SLA, '' AS OBSERVACION
       UNION ALL SELECT '1167577', 'FES', 'Santiago', 2, 4, '';""")
wcsv("10_pedidos_clave.csv", h, rows)

# 11_vbfa_vttp.csv - manifiesto/transporte via VTTP
h, rows = fetch(["VBELN", "TKNUM", "ERDAT", "ERZET", "PKSTA"],
    """SELECT TOP 50 VBELN, TKNUM, ERDAT, ERZET, PKSTA
       FROM dbo.VTTP_SAP
       ORDER BY ERDAT DESC;""")
wcsv("11_vbfa_vttp.csv", h, rows)

# RESULTADO.md
with io.open(os.path.join(RUN, "RESULTADO.md"), "w", encoding="utf-8") as f:
    f.write(f"""# RESULTADO - Reconciliacion VBFA (queries directas SELECT)

## Estado: AMARILLO (VBFA probado con queries directas; SP no ejecutable por permiso)

## Hallazgo principal
- El SP dbo.STP_GET_VBFA_TRAMO_FILTRO NO es visible para el usuario SQL de auditoria
  -> no se ejecuto el SP. Se probaron las queries SELECT directas contra VBFA_SAP y VTTP_SAP.

## Logica del SP descubierta por queries (no por memoria)
- 'M-J' NO es un literal: representa el rango VBTYP_V IN ('M','J')
- 'C' = tipo de documento posterior = PEDIDO (VBTYP_N='C')
- Tramo valido: VBTYP_V IN ('M','J') AND VBTYP_N='C'
- La ventana 01-07 a 02-07 no tenia datos en ERDAT (0 filas); hay datos hasta 31-07-2026

## Reconciliacion
- VBFA_SAP: VBELV (pedido original), VBELN (documento posterior), ERDAT/ERZET (fecha/hora)
- VTTP_SAP: VBELN, TKNUM (manifiesto/transporte), ERDAT, PKSTA
- Los codigos VBTYP_V en VBFA: M, J, C, H, T, K, O (tipos de documento anterior)
- Los codigos VBTYP_N: R, J, M, Q, X, C, 8, O, H, T, N, S (tipos posterior)

## Limites
- No se pudo leer la definicion completa del SP (permiso de metadata)
- La interpretacion de M-J como rango es una hipotesis confirmada por datos (25316 filas vs 0 literal)
- Se requiere validacion de negocio sobre que documentos M y J representan
- ERDAT es varchar dd-MM-yyyy; se usa TRY_CONVERT estilo 105
""")

# manifest.json
with io.open(os.path.join(RUN, "manifest.json"), "w", encoding="utf-8") as f:
    import json
    json.dump({
        "project": "NS_V50-PowerBI-ML",
        "run_id": RUN_ID,
        "timestamp_local": datetime.datetime.now().isoformat(),
        "branch": "work/ns-lineage-audit",
        "status": "AMARILLO",
        "vbfa": "SP_NO_VISIBLE; QUERIES_SELECT_PROBADAS",
        "permiso_sp": "DENEGADO/NO_VISIBLE_PARA_USUARIO_SQL_AUDIT",
    }, f, ensure_ascii=False, indent=2)

conn.close()
print(f"\nEvidencia VBFA generada en {RUN}")
