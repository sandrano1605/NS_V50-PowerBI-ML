# RESULTADO — INC-015 CERRADO (SQL ejecutado)

RUN_ID: 20260811_235057_inc015_vbap_direct_sql_2f3c0f9
Estado: COMPLETED

## INC-015 → YV01_EXCLUIDO_DE_VBAP_SAP (definitivo)

SQL ejecutado contra DMF_VTA_PRD (A_MOYA). VBAP_SAP es USER_TABLE.
dbo.VBAP no existe. Cobertura VBAK→VBAP: 0,42%.

Causa raíz: YV01 = 349.215 headers (95,4%) tienen 0 posiciones en VBAP_SAP.
Los 810 pedidos sin match en Power BI son predominantemente YV01.
No es AEDAT, no es ceros, no es refresh: es que VBAP_SAP no fue diseñado
para contener posiciones YV01.

## Regresión
FIND-002A/INC-011/INC-007B siguen GREEN.
