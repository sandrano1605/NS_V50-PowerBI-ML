# RUN 20260801_170000_vbfa_reconciliacion - Reconciliacion VBFA

## Fecha: 2026-08-01 16:56

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
