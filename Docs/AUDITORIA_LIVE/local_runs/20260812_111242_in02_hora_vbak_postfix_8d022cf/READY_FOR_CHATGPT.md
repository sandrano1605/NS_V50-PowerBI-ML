# READY FOR CHATGPT — IN02 fallback VBAK post-fix

RUN_ID: 20260812_111242_in02_hora_vbak_postfix_8d022cf
SHA: 8d022cf1f322e4fb4f5867084170de0e40836424
Power BI: puerto 63977, modelo con fix eb07b64 cargado

## Resumen

El fix `eb07b64` (fallback VBAK.ERZET para canales 43/45) fue aplicado y cargado en Power BI, pero **NO recupera ningún pedido**: los 184 "Sin hora válida" (43:149, 45:35) siguen igual.

## Hallazgo principal: IN02-002 BUG_CONVERSION_ERZET (RED)

`VBAK_SAP.ERZET` es **varchar(8)** con formato texto `'16:03:02'` (con `:`).

El SQL del fix hace `CONVERT(VARCHAR(6), ERZET)` que trunca a `'16:03:'` (deja `:` al final). El `RIGHT('000000' + '16:03:', 6)` = `'16:03:'` y el `STUFF/STUFF` produce formato inválido → `TRY_CONVERT(TIME(0))` = **NULL**.

Evidencia SQL:
```
ERZET       conv6      right6     hora_vbak
'16:03:02'  '16:03:'   '16:03:'   NULL
```

Solución correcta: `TRY_CONVERT(TIME(0), V.ERZET)` directo (parsea `'16:03:02'` a TIME correctamente) o `TRY_CONVERT(TIME(0), CONVERT(VARCHAR(8), ERZET, 108))`.

## Hallazgos RED confirmados
IN02-002: bug conversion ERZET. Fix eb07b64 no recupera ningun pedido.

## Hallazgos ORANGE confirmados
IN02-003: tras corregir conversion, ~153 pedidos 43/45 deberian salir de Sin hora.

## Falsos positivos relevantes
El join PED_KEY funciona correctamente (los pedidos estan en VBAK con VTWEG 43/45). El unico problema es la conversion de formato.

## Decisiones de negocio necesarias
Ninguna.

## Cambios recomendados para implementación remota
En Fact_Tracking.tmdl, reemplazar el bloque HORA_VBAK por:
TRY_CONVERT(TIME(0), V.ERZET) AS HORA_VBAK

## Evidencia principal
- raw/in02_bug_hora_vbak.md — causa raiz con evidencia SQL
- 07_live_results.csv — 8 pruebas

## No resuelto
- ~44 pedidos residuales tras corregir el bug (diferencia Power BI 197 vs ZART 154 + 20 VBAK)
