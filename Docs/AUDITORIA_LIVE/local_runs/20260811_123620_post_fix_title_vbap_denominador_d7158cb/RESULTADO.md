# RESULTADO AUDITORÍA LOCAL DIRIGIDA

RUN_ID: 20260811_123620_post_fix_title_vbap_denominador_d7158cb
SHA auditado: d7158cbf16db385c012d114676d1c5f047997a41
Timestamp: 2026-08-11 12:36:20
Estado: COMPLETED

## Hallazgo principal

**FIND-002A (ROJO):** El fix de RE TT Título (commit cdeda8bb) introdujo un error DAX.
`CONCATENATEX(VALUES(Dim_Rango_Entrega[Rango]), ..., Dim_Rango_Entrega[OrdenRango], ASC)`
falla con "No se puede determinar un valor único para la columna OrdenRango" en cualquier contexto.
Los valores numéricos NO cambiaron (multiselect RE/FA siguen correctos); solo el título está roto.

## Números confirmados

| Métrica | Valor | Estado |
|---------|-------|--------|
| Total pedidos | 2.048 | ✅ |
| Evaluables | 1.898 | ✅ |
| En SLA | 1.547 | ✅ |
| Fuera SLA | 351 | ✅ |
| RE NS | 81,5% | ✅ |
| Diferidos corte | 946 | ✅ |
| FES con manifiesto | 437 | ✅ |
| VBAP cobertura | 58,3% (1.107/1.898) | ⚠️ |
| Diferencia U-RE | 64 | ⚠️ |

## Multiselect RE/FA — sin regresión

| Combinación | RE Pedidos | RE Valor | FA Líneas | FA Unidades |
|-------------|-----------|----------|-----------|-------------|
| Todos | 1.898 | 2.274M | 22.869 | 2.421.491 |
| Normal+FES | 1.896 | 2.272M | 22.801 | 2.420.479 |

Valores correctos: Normal+FES ≠ Todos. El fix de título no afectó los números.

## Limitación técnica de la corrida

El tool MCP `dax_query_operations` falla sistemáticamente en esta sesión (incluso
`EVALUATE ROW(x,1)` y `Validate`). Por eso no fue posible ejecutar:
- clasificación individual de los 64 pedidos INC-011;
- match normalizado VBAP (ceros a la izquierda) INC-015;
- comparación pedido a pedido Fact_Tracking vs Fact_Hitos.

Se recomienda reiniciar la sesión MCP y re-ejecutar esas queries específicas en una corrida corta complementaria.

## Decisiones de negocio pendientes

1. ¿FES solo cierra por manifiesto VBFA/VTTP? (FIND-001)
2. ¿NS oficial 81,5% o 78,8%? (FIND-004)
3. ¿Feriados regionales? (INC-013)

## Acción inmediata recomendada

**P0:** Corregir FIND-002A en Medidas.tmdl — reemplazar `Dim_Rango_Entrega[OrdenRango]` por
`MIN(Dim_Rango_Entrega[OrdenRango])` o quitar el sort-by en CONCATENATEX de RangoTexto.
