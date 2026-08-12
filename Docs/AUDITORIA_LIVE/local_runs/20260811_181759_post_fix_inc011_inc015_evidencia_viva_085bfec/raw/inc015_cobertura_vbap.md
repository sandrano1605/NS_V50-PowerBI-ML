# INC-015 — Cobertura VBAP / Lineas_y_unidades_por_pedidos

## Resumen cuantitativo (modelo vivo, SHA 085bfec)

| Métrica | Valor |
|---|---|
| Pedidos evaluables (RE Pedidos contexto, sin filtro) | 1.934 |
| Con match exacto en Lineas_y_unidades_por_pedidos | **1.128 (58,3%)** |
| Sin match | **806 (41,7%)** |
| Match normalizado por valor numérico | 1.128 (sin mejora) |
| Pedidos con clave con ceros a la izquierda en Tracking | 0 |
| Pedidos con clave con ceros a la izquierda en VBAP | 0 |
| Match derivado 10→7 (RIGHT 7) | 0 |
| Match derivado 7→10 (000+7) | 0 |
| Sin match que existen en Pedidos_Normal_VBAK (VBELN) | 778 |

## Hipótesis descartada (FALSO_POSITIVO)

La hipótesis de ceros a la izquierda (VBAP.VBELN texto con padding vs
ZVBELN_PED sin padding) **NO se sostiene**: ninguna tabla tiene claves con
ceros a la izquierda (0 filas con LEFT='0'), el match por valor numérico no
mejora (1.128), y los derivados 7↔10 dan 0. La causa de los 806 sin match no
es formato de clave.

## Causa real identificada

778 de los 806 sin match (96,5%) SÍ existen en `Pedidos_Normal_VBAK` (cabecera
SAP VBELN), pero NO existen en `Lineas_y_unidades_por_pedidos`. Esto indica que
la vista `VBAP_SAP` usada en la consulta M de `Lineas_y_unidades_por_pedidos`
no contiene esos pedidos (el filtro `AEDAT >= GETDATE() - 730` en la fuente
SQL, o la vista misma, los excluye). El problema está en la fuente de líneas,
no en el join.

## Distribución de los 806 sin match

Por mes:
- 2026-05: 192
- 2026-06: 297
- 2026-07: 270
- 2026-08: 47

Por flujo:
- NORMAL: 663
- FES: 142
- FES + SALDO: 1

Por canal:
- 42: 3
- 43: 545
- 45: 113
- 46: 145

Por largo de clave:
- 7 dígitos: 335
- 10 dígitos: 471

## Cobertura por mes (evaluables / con match)

| Mes | Evaluados | ConMatch | Cobertura |
|---|---|---|---|
| 2026-05 | 454 | 262 | 57,7% |
| 2026-06 | 758 | 461 | 60,8% |
| 2026-07 | 599 | 329 | 54,9% |
| 2026-08 | 123 | 76 | 61,8% |

## Impacto en medidas de volumen

- `IN Líneas` y `FA Líneas`: usan SUM(Lineas) con TREATAS por pedido → quedan
  subestimadas en los pedidos sin match (no aportan líneas).
- `FA Unidades` (modelo vivo, sin filtro): 2.426.670.
- `IN Unidades`: usa SUM(Suma_Unidades) → subestimada igualmente.
- Porcentaje de pedidos del universo sin líneas/unidades: 41,7%.

## Ejemplos de sin match (7 dígitos)

1166508, 1166507, 1166496, 1166495, 1166502, 1166476, 1166487, 1166494, 1166493, 1166486 (NORMAL, mayo 2026)

## Recomendación (NO implementada, solo diagnóstico)

1. Revisar la fuente `VBAP_SAP` y el filtro `AEDAT >= GETDATE()-730`: si el
   universo analizado es 2026 y la vista excluye por AEDAT, la cobertura nunca
   llegará a 100%.
2. Verificar si el join debe hacerse contra `Pedidos_Normal_VBAK` (que cubre
   778/806) o si faltan filas de VBAP por tipo de documento.
3. Cuantificar líneas/unidades omitidas una vez corregida la fuente.
