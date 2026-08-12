# READY FOR CHATGPT

RUN_ID: 20260811_225907_post_fix_validacion_viva_00756db
Rama: work/ns-lienzo-02-ingreso-pedidos
SHA local auditado: 00756dbe763335879daf14ec466dcc7514361023
SHA remoto al iniciar: 00756dbe763335879daf14ec466dcc7514361023
Commit evidencia: POR_PUBLICAR_TRAS_VALIDACION
Power BI: puerto 58610, base 512b1fa5, post-refresh 2026-08-11 22:21

## Resumen

Corrida de validación post-fix. Los tres fixes confirmados en modelo vivo:
1. **FIND-002A → GREEN**: RE TT Título renderiza sin SemanticError en 12/12 contextos.
2. **INC-011 → GREEN**: 0 cerrados sin DH. Los 55 pedidos con fecha centinela ahora ES_CERRADO=FALSE.
3. **INC-007B → GREEN**: fallback TRP eliminado. 437/437 FES con manifiesto VBFA/VTTP. 0 sin.
4. **INC-015 → ORANGE / pendiente AEDAT**: cobertura 1131/1941 = 58,3%. Requiere prueba VBAP_SAP sin filtro AEDAT.

## Hallazgos RED confirmados

Ninguno. Los tres hallazgos RED de la corrida anterior (FIND-002A, FIND-001, INC-011) están cerrados.

## Hallazgos ORANGE confirmados

- **INC-015**: cobertura VBAP 58,3% constante. Hipótesis ceros descartada definitivamente. Pendiente: consulta VBAP_SAP sin `AEDAT>=GETDATE()-730` para aislar causa.
- **INC-013**: feriados regionales sin fuente validada.

## Falsos positivos relevantes

- **INC-015 hipótesis de ceros a la izquierda**: FALSO_POSITIVO (confirmado en 2 corridas). 0 ceros en ambas tablas.

## Decisiones de negocio necesarias

1. **INC-015**: ¿corregir fuente VBAP_SAP o normalizar join? (requiere resultado de prueba AEDAT)
2. **INC-013**: ¿feriados regionales? (necesita fuente de datos)

## Cambios recomendados para implementación remota

Ninguno inmediato. Los fixes ya están aplicados (commits 3742d32 y 89bfee5). La prioridad es resolver INC-015 con prueba AEDAT.

## Evidencia principal

- `raw/find002_titulo_12.csv` — 12 combinaciones, todos GREEN
- `07_live_results.csv` — 30 pruebas vivas tabuladas
- `09_inc_status.csv` — FIND-002A/INC-011/INC-007B → GREEN; INC-015 → PENDIENTE_AEDAT
- `04_code_findings.csv` — 5 hallazgos actualizados

## No resuelto

- INC-015: causa exacta de los 810 sin match (AEDAT vs vista VBAP_SAP)
- INC-013: feriados regionales
