# -*- coding: utf-8 -*-
"""Genera evidencia del run VBFA con hallazgo de permisos."""
import io, sys, os, json, datetime, csv
sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"C:\Users\alonso.moya\OneDrive - ARTEL S.A\Escritorio\💼 Proyectos\Modelo datos power BI\NS\NS_V50_v15_Error_Python_ndarray_Corregido\NS_V50"
TS = "20260801_170000_vbfa_reconciliacion"
RUN = os.path.join(ROOT, "Docs", "AUDITORIA_LIVE", "runs", TS)
os.makedirs(RUN, exist_ok=True)

# 00_resumen / RESULTADO / manifest
resumen = """# RUN {ts} - Reconciliacion VBFA

## Fecha: {fecha}

## Ejecucion
1. Copia temporal NS_V50_VBFA_AUDIT_TEMP creada FUERA del repositorio
2. Copia abierta en Power BI Desktop (mismas credenciales SQL de usuario)
3. 4 consultas creadas via MCP: VBFA_PROCEDIMIENTO, VBFA_PARAMETROS, VBFA_TRAMO_20260701_20260702, VBFA_TRAMO_BORDE_20260630_20260703
4. Refresh intentado en las 4 tablas

## HALLAZGO CRITICO - VBFA NO EJECUTABLE
Error SQL recibido:
"Se denego el permiso EXECUTE en el objeto 'STP_GET_VBFA_TRAMO_FILTRO',
 base de datos 'DMF_VTA_PRD', esquema 'dbo'."

Las credenciales de Power BI Desktop NO tienen permiso EXECUTE sobre el procedimiento.
Por lo tanto NO se pudo ejecutar el SP ni obtener la definicion completa.

## Errores latentes detectados en el modelo temporal
Las medidas heredadas presentan formatString invalido que rompe el commit del refresh:
- RE Estado ultimo mes: 'formatString: 0' incorrecto
- RE Ventana analisis texto: 'formatString: 0' incorrecto
Esto es un hallazgo separado del VBFA (heredado de sesiones previas), no introducido por esta tarea.

## Estado VBFA
- Definicion del SP: NO obtenida (permiso denegado)
- Parametros: NO obtenidos
- Ventana 01-07 a 02-07: NO ejecutada
- Ventana borde 30-06 a 03-07: NO ejecutada
- Reconciliacion SP vs modelo: PENDIENTE

## Accion requerida
Se necesita un usuario SQL con permiso EXECUTE sobre dbo.STP_GET_VBFA_TRAMO_FILTRO
(ej. usuario a_moya en SSMS, que si tiene permisos de lectura/ejecucion ampliados).
Ejecutar sql/AUDIT_STP_GET_VBFA_TRAMO_FILTRO.sql desde SSMS con ese usuario.
""".format(ts=TS, fecha=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
with io.open(os.path.join(RUN, "00_resumen.md"), "w", encoding="utf-8") as f:
    f.write(resumen)

resultado = """# RESULTADO - Reconciliacion VBFA

## Estado: ROJO (VBFA) / AMARILLO (trazabilidad general)

## VBFA: PENDIENTE - PERMISO EXECUTE DENEGADO
- Las credenciales de Power BI Desktop no pueden ejecutar dbo.STP_GET_VBFA_TRAMO_FILTRO
- Se requiere usuario con permiso EXECUTE (SSMS)

## Dictamen general (sin cambios)
| Area | Estado |
|---|---|
| Auditor estatico | VERDE |
| Modelo vivo | VERDE |
| Pedidos clave | VERDE |
| Contrato Python | AMARILLO (5 categorias clasificadas) |
| Procedimiento VBFA | PENDIENTE (permiso denegado) |
| Recorte de columnas | BLOQUEADO |
| Columnas autorizadas | 0 |
"""
with io.open(os.path.join(RUN, "RESULTADO.md"), "w", encoding="utf-8") as f:
    f.write(resultado)

with io.open(os.path.join(RUN, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump({
        "project": "NS_V50-PowerBI-ML",
        "run_id": TS,
        "timestamp_local": datetime.datetime.now().isoformat(),
        "branch": "work/ns-lineage-audit",
        "status": "ROJO_VBFA",
        "vbfa": "PENDIENTE_PERMISO_EXECUTE_DENEGADO",
        "vbfa_definition": "NO_OBTENIDA",
        "vbfa_params": "NO_OBTENIDOS",
        "vbfa_window": "NO_EJECUTADA",
        "vbfa_border": "NO_EJECUTADA",
        "model_temp": "NS_V50_VBFA_AUDIT_TEMP (fuera del repo, se eliminara)",
        "python_contract": "5 CATEGORIAS: 11 REQUIRED + 28 OPTIONAL + 32 DERIVED + 19 OUTPUT + 10 LITERAL",
        "columnas_autorizadas": 0,
    }, f, ensure_ascii=False, indent=2)

# archivos CSV placeholder con estado
def wcsv(name, header, rows):
    with io.open(os.path.join(RUN, name), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

wcsv("01_procedimiento_definicion.csv", ["ESQUEMA", "PROCEDIMIENTO", "FECHA_MODIFICACION", "DEFINICION", "ESTADO"], [
    {"ESQUEMA": "dbo", "PROCEDIMIENTO": "STP_GET_VBFA_TRAMO_FILTRO", "FECHA_MODIFICACION": "", "DEFINICION": "", "ESTADO": "PERMISO_EXECUTE_DENEGADO"}
])
wcsv("02_procedimiento_parametros.csv", ["PARAMETRO", "TIPO", "ESTADO"], [{"PARAMETRO": "", "TIPO": "", "ESTADO": "PERMISO_EXECUTE_DENEGADO"}])
wcsv("03_vbfa_tramo_raw.csv", ["COLUMNA", "VALOR", "ESTADO"], [{"COLUMNA": "", "VALOR": "", "ESTADO": "NO_EJECUTADO"}])
wcsv("04_vbfa_tramo_borde.csv", ["COLUMNA", "VALOR", "ESTADO"], [{"COLUMNA": "", "VALOR": "", "ESTADO": "NO_EJECUTADO"}])
wcsv("05_vbfa_esquema_salida.csv", ["COLUMNA", "TIPO", "ESTADO"], [{"COLUMNA": "", "TIPO": "", "ESTADO": "PENDIENTE"}])
wcsv("06_vbfa_granularidad.csv", ["METRICA", "VALOR", "ESTADO"], [{"METRICA": "", "VALOR": "", "ESTADO": "PENDIENTE"}])
wcsv("07_vbfa_duplicados.csv", ["PEDIDO", "REPETICIONES", "ESTADO"], [{"PEDIDO": "", "REPETICIONES": "", "ESTADO": "PENDIENTE"}])
wcsv("08_vbfa_primera_ultima_fecha.csv", ["PEDIDO", "PRIMERA", "ULTIMA", "ESTADO"], [{"PEDIDO": "", "PRIMERA": "", "ULTIMA": "", "ESTADO": "PENDIENTE"}])
wcsv("09_comparacion_sp_modelo.csv", ["PEDIDO", "SP_MANIFIESTO", "MODELO_CIERRE", "COINCIDE", "ESTADO"], [
    {"PEDIDO": "4190139455", "SP_MANIFIESTO": "PENDIENTE", "MODELO_CIERRE": "28-05-2026", "COINCIDE": "", "ESTADO": "PENDIENTE_SP"},
    {"PEDIDO": "1167577", "SP_MANIFIESTO": "PENDIENTE", "MODELO_CIERRE": "02-07-2026", "COINCIDE": "", "ESTADO": "PENDIENTE_SP"},
])
wcsv("10_pedidos_clave.csv", ["PEDIDO", "FLUJO", "ZONA", "CIERRE", "DIAS", "SLA", "CUMPLE", "ESTADO"], [
    {"PEDIDO": "4190139455", "FLUJO": "FES", "ZONA": "Regiones", "CIERRE": "28-05-2026", "DIAS": "2", "SLA": "5", "CUMPLE": "TRUE", "ESTADO": "OK_MODELO"},
    {"PEDIDO": "1167577", "FLUJO": "FES", "ZONA": "Santiago", "CIERRE": "02-07-2026", "DIAS": "2", "SLA": "4", "CUMPLE": "TRUE", "ESTADO": "OK_MODELO"},
])
print("Evidencia VBFA generada en", RUN)
