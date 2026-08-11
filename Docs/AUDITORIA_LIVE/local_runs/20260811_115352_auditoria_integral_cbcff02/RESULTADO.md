# RESULTADO AUDITORÍA LOCAL

RUN_ID: 20260811_115352_auditoria_integral_cbcff02
SHA auditado: cbcff026432f6bd3e5d5bfb3072688ad95039077
Timestamp: 2026-08-11 11:53:52
Estado: COMPLETED

## Resultado global

El modelo NS_V50 en SHA cbcff02 carga correctamente, refresca sin errores, y los números baseline se confirman exactamente. Las correcciones multiselect RE y FA están funcionando correctamente en todas las combinaciones probadas.

## Números confirmados (baseline fresco)

| Métrica | Valor | Baseline anterior | Estado |
|---------|-------|-------------------|--------|
| Total pedidos | 2.048 | 2.048 | ✅ |
| Cerrados evaluables | 1.898 | 1.898 | ✅ |
| En SLA | 1.547 | 1.547 | ✅ |
| Fuera SLA | 351 | 351 | ✅ |
| RE NS | 81,5% | 81,5% | ✅ |
| U cerrados | 1.962 | 1.962 | ✅ |
| U NS | 78,8% | 78,8% | ✅ |
| Diferencia U-RE | 64 | 64 | ✅ |
| Diferidos corte | 946 | 946 | ✅ |
| FES con manifiesto | 437 | 437 | ✅ |
| FES sin manifiesto | 0 | 0 | ✅ |
| VBAP cobertura | 58,3% | N/A | NUEVO |

## Multiselect RE (INC-005) — GREEN

| Combinación | Pedidos | Valor | PromDH | P90 |
|-------------|---------|-------|--------|-----|
| Todos | 1.898 | 2.274M | 3,502 | 8 |
| Normal | 1.459 | 1.204M | 2,580 | 5 |
| FES | 437 | 1.068M | 6,574 | 14 |
| Saldo | 2 | 2,4M | 5,0 | 6,6 |
| Normal+FES | 1.896 | 2.272M | 3,501 | 8 |
| Santiago+Regiones | 1.898 | 2.274M | 3,502 | 8 |

Normal+FES Valor = 2.272M ≠ 2.274M (Todos). **Multiselect funciona correctamente.**

## Multiselect FA (INC-009) — GREEN

| Combinación | Pedidos | Líneas | Unidades |
|-------------|---------|--------|----------|
| Todos | 1.898 | 22.869 | 2.421.491 |
| Normal | 1.459 | 14.778 | 997.671 |
| FES | 437 | 8.023 | 1.422.808 |
| Normal+FES | 1.896 | 22.801 | 2.420.479 |
| Santiago+Regiones | 1.898 | 22.869 | 2.421.491 |

Normal+FES Líneas = 22.801 (14.778+8.023) ≠ 22.869 (Todos). **Multiselect funciona correctamente.**

## Hallazgos

| ID | Severidad | Estado | Descripción |
|----|-----------|--------|-------------|
| FIND-001 | RED | CONFIRMADO | FECHA_MANIFIESTO permite TRP fallback (0 afectados actualmente) |
| FIND-002 | ORANGE | CONFIRMADO | RE TT Título no refleja multiselect en texto |
| FIND-003 | ORANGE | CONFIRMADO | Cobertura VBAP 58,3% (791 pedidos sin match) |
| FIND-004 | RED | CONFIRMADO | Denominadores U vs RE distintos (64 pedidos) |
| FIND-005 | INFO | CONFIRMADO | SLA 5 DH legacy solo en ML Python |

## Regresión

12 pedidos probados: 11 OK, 1 FAIL (pedido 4190139455 cambió de FES a NORMAL en datos actuales — no es error del modelo).

## Decisiones de negocio pendientes

1. ¿FES solo cierra por manifiesto VBFA/VTTP? → Eliminar TRP fallback
2. ¿NS oficial es 81,5% o 78,8%? → Documentar denominador
3. ¿Feriados regionales afectan cálculo DH? → Confirmar con fuente oficial
