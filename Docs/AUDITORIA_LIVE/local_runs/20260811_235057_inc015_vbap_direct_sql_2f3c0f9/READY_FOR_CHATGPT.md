READY_FOR_CHATGPT — INC-015 SQL diagnóstico

RUN_ID: 20260811_235057_inc015_vbap_direct_sql_2f3c0f9
Rama: work/ns-lienzo-02-ingreso-pedidos
SHA auditado: 2f3c0f9bfb384ca2928242467bec1de827486309
Power BI: puerto 58610, base 512b1fa5, post-refresh
SQL DMF_VTA_PRD: NO_EJECUTADO (error SSPI/autenticación Windows desde esta máquina)

## Resumen

No fue posible ejecutar el SQL directamente contra DMF_VTA_PRD desde el LLM local
por error de autenticación SSPI con el controlador de dominio. Se generó el script
SQL completo (`raw/inc015_sql_queries.sql`) listo para ejecución manual.

Desde el modelo Power BI se confirmó:
- 810 pedidos sin match en VBAP (1.941 eval - 1.131 match)
- 782 existen en VBAK con fecha_pedido dentro de 730 días
- 28 no existen en VBAK (fuera de ventana 90-días)
- 0 pedidos EXCLUIDO_AEDAT_ANTIGUO

La evidencia previa (cb899df) ya estableció CAUSA_VISTA_VBAP_SAP con 96.5% de
los faltantes en VBAK con fechas recientes. El SQL solo falta para precisar
la naturaleza exacta de VBAP_SAP (VIEW/TABLE/SYNONYM) y si dbo.VBAP existe.

## Hallazgos RED confirmados
Ninguno.

## Hallazgos ORANGE confirmados
INC-015: CAUSA_VISTA_VBAP_SAP. 782/810 en VBAK. SQL pendiente.

## Falsos positivos relevantes
- Ceros a la izquierda: descartado (3 corridas)
- CAUSA_AEDAT: descartado (0 EXCLUIDO_AEDAT)

## Decisiones de negocio necesarias
Ejecutar `Scripts/audit_local/inc015_vbap_source_audit.sql` contra DMF_VTA_PRD
para determinar la naturaleza exacta de VBAP_SAP y decidir el fix.

## Cambios recomendados para implementación remota
Ejecutar manualmente el SQL y clasificar según:
- BASE_VBAP_COMPLETA_VISTA_INCOMPLETA → cambiar Power BI a VBAP
- BASE_VBAP_TAMBIEN_INCOMPLETA → corregir réplica/ETL
- VBAP_BASE_NO_DISPONIBLE → analizar dependencias de VBAP_SAP
- VBAP_SAP_ES_TABLA_REPLICADA → corregir proceso de carga

## Evidencia principal
- raw/inc015_sql_queries.sql — script SQL completo listo para ejecutar
- raw/inc015_missing_orders.csv — lista de 810 pedidos sin match

## No resuelto
- Naturaleza exacta de VBAP_SAP (VIEW/TABLE/SYNONYM)
- Si dbo.VBAP existe y tiene los pedidos faltantes
