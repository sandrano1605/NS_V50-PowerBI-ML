# READY FOR CHATGPT — IN02 Hora Ingreso 43/45

RUN_ID: 20260812_100137_in02_hora_ingreso_43_45_549fea2
SHA: 549fea224d7fa36b3c5d7d0addd87633c2684ea6
SQL: DMF_VTA_PRD (A_MOYA), Power BI: puerto 64215

## Resumen

Auditoria de hora de ingreso para canales 43 y 45. 154 pedidos en ZART con ZERZET_PED=000000 ("Sin hora valida"). **153 (99.35%) son recuperables desde VBAK.ERZET** con hora valida. Solo 1 sin entrada VBAK.

## Hallazgos RED confirmados
Ninguno.

## Hallazgos ORANGE confirmados
IN02-001: ZART_HORA_000000 recuperable desde VBAK. 153/154 pedidos 43/45.

## Falsos positivos relevantes
Ninguno.

## Decisiones de negocio necesarias
Ninguna. El fix es tecnico (fallback VBAK).

## Cambios recomendados para implementación remota
En Fact_Tracking.tmdl linea 330 (TramoHoraIngreso): cuando ZERZET_PED=000000, usar VBAK.ERZET como fallback antes de marcar "Sin hora valida".

## Evidencia principal
- raw/in02_diagnostico.md — resumen y recomendacion
- raw/in02_hora_ingreso_result.txt — salida SQL completa con 154 pedidos

## No resuelto
- 1 pedido SIN_VBAK (1168066) sin fuente de hora alternativa
- 43 pedidos de diferencia entre Power BI (197) y SQL ZART (154)
