# READY FOR CHATGPT — INC-015 CERRADO TÉCNICAMENTE

RUN_ID: 20260811_235057_inc015_vbap_direct_sql_2f3c0f9
Rama: work/ns-lienzo-02-ingreso-pedidos
SHA auditado: 2f3c0f9bfb384ca2928242467bec1de827486309
Power BI: puerto 58610 · SQL: DMF_VTA_PRD (A_MOYA, SQL auth, OK)

## Resumen

INC-015 queda **técnicamente cerrado**. Se ejecutó SQL directo contra
`DMF_VTA_PRD` y se identificó la causa raíz definitiva.

## Diagnóstico final: YV01_EXCLUIDO_DE_VBAP_SAP

- `VBAP_SAP` es una **USER_TABLE (tabla física)**, no una vista ni sinónimo.
- `dbo.VBAP` **no existe** en `DMF_VTA_PRD`.
- VBAK_SAP tiene 366.091 headers en últimos 90 días; VBAP_SAP solo tiene 1.524 (0,42%).
- **349.215 headers son YV01** (95,4% del universo VBAK) — **0 tienen posiciones en VBAP_SAP**.
- Los ~1.131 pedidos con match en Power BI corresponden a AUART que VBAP_SAP sí cubre parcialmente (ZMAY 65,8%, ZPDA 47,5%, YPA 79%, ZVGM 73%).
- Los ~810 sin match son YV01 y otros AUART excluidos.

## Hallazgos RED confirmados
Ninguno.

## Hallazgos ORANGE confirmados
INC-015 cerrado: YV01_EXCLUIDO_DE_VBAP_SAP. Ver raw/inc015_vbap_diagnostico_final.md.

## Falsos positivos relevantes
- Ceros a la izquierda: descartado (3 corridas).
- CAUSA_AEDAT: descartado (0 EXCLUIDO_AEDAT).
- CAUSA_VISTA_VBAP_SAP → refinado a YV01_EXCLUIDO_DE_VBAP_SAP.

## Decisiones de negocio necesarias
- Definir fuente de posiciones para AUART YV01 (95,4% del universo).
- Opciones: exponer VBAP estándar SAP, crear vista YV01, o usar fuente alternativa.

## Cambios recomendados para implementación remota
- NO modificar `Lineas_y_unidades_por_pedidos` para usar VBAP_SAP (no resolverá nada).
- Buscar/crear fuente de líneas que cubra AUART YV01.
- Mientras tanto, la cobertura 58,3% es estructural y no mejorará sin nueva fuente.

## Evidencia principal
- `raw/inc015_vbap_diagnostico_final.md` — diagnóstico SQL completo
- `raw/inc015_vbap_source_audit.sql` — script SQL ejecutado
- Tabla AUART con gap cuantificado (349.215 YV01 → 0 en VBAP_SAP)

## No resuelto
- Dónde están las posiciones de los pedidos YV01 (requiere acceso a fuente SAP o BW).
