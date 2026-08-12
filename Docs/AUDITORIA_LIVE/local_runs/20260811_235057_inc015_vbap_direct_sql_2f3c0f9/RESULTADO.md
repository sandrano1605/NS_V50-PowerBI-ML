# RESULTADO — INC-015 SQL (pendiente ejecución)

RUN_ID: 20260811_235057_inc015_vbap_direct_sql_2f3c0f9
SHA: 2f3c0f9bfb384ca2928242467bec1de827486309
Estado: COMPLETED (SQL pendiente de ejecución manual por error SSPI)

## Regresión (OK)
- RE TT Título: sin SemanticError
- Cerrados sin DH: 0
- FES cerrados sin manifiesto: 0
- Evaluables: 1.941, Match VBAP: 1.131 (58.3%)

## INC-015
- Sin match: 810
- En VBAK con fecha reciente: 782
- SQL generado en raw/inc015_sql_queries.sql
- No ejecutado: error autenticación Windows SSPI contra 128.1.3.21

## Próximo paso
Ejecutar manualmente el SQL contra DMF_VTA_PRD y clasificar los 810 pedidos en AUSENTE_VBAP_SAP / EXCLUIDO_AEDAT / EXISTE_DENTRO_730.
