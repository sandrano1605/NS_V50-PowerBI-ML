# READY FOR CHATGPT — Cierre INC-015

RUN_ID: 20260811_232642_post_fix_tracking_inc015_18f0baa
Rama: work/ns-lienzo-02-ingreso-pedidos
SHA auditado: 18f0baa24089742dab35f00300506cb8ce10856f
Power BI: puerto 58610, base 512b1fa5, post-refresh

## Resumen

Corrida focalizada en INC-015. Diagnostico definitivo: CAUSA_VISTA_VBAP_SAP.
782 de 810 pedidos sin match (96.5%) existen en VBAK con fecha_pedido dentro
de 730 dias. La vista VBAP_SAP simplemente no contiene esos pedidos.
Cobertura potencial si se corrige: 1913/1941 = 98.6%.

## Hallazgos RED confirmados

Ninguno. Los tres fixes (FIND-002A, INC-011, INC-007B) siguen GREEN.

## Hallazgos ORANGE confirmados

- INC-015: CAUSA_VISTA_VBAP_SAP. Cobertura 58.3% -> potencial 98.6%.

## Falsos positivos relevantes

- Hipotesis ceros a la izquierda: FALSO_POSITIVO (confirmado en 3 corridas).
- Hipotesis CAUSA_AEDAT: DESCARTADA (0 pedidos EXCLUIDO_AEDAT).

## Decisiones de negocio necesarias

- Revisar la vista VBAP_SAP en DMF_VTA_PRD para entender por que
  faltan 782 pedidos que SI existen en VBAK como cabeceras recientes.

## Cambios recomendados para implementación remota

- Comparar SELECT DISTINCT VBELN FROM VBAP_SAP vs VBAK WHERE ERDAT > GETDATE()-90
- Si VBAP_SAP tiene filtros internos, usar tabla base VBAP

- Comparar SELECT DISTINCT VBELN FROM VBAP_SAP vs
  SELECT VBELN FROM VBAK WHERE ERDAT > GETDATE()-90
  para cuantificar exactamente el gap.
- Si VBAP_SAP tiene filtros internos, usar tabla base VBAP directamente.

## Evidencia principal

- raw/inc015_vbap_diagnostico.md — clasificacion 810 pedidos
- 07_live_results.csv — 10 pruebas tabuladas
- 09_inc_status.csv — INC-015 -> CAUSA_VISTA_VBAP_SAP

## No resuelto

- Causa raiz exacta de por que VBAP_SAP no tiene los pedidos
  (requiere acceso directo a la vista SQL en DMF_VTA_PRD).
- INC-013: feriados regionales (necesita fuente de datos).
