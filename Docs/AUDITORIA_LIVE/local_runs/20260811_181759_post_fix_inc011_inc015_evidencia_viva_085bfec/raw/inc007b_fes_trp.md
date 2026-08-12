# FIND-001 / INC-007B — Fallback TRP en FECHA_MANIFIESTO (cuantificación viva)

## Código (Fact_Tracking.tmdl, líneas 353-358)

```powerquery
Man = Table.AddColumn(Desp, "FECHA_MANIFIESTO", each
    if [ES_FES]<>true then null
    else if [ULTIMA_FECHA_MANIFIESTO]<>null then DateTime.From([ULTIMA_FECHA_MANIFIESTO])
    else if [PRIMERA_FECHA_MANIFIESTO]<>null then DateTime.From([PRIMERA_FECHA_MANIFIESTO])
    else if [TRP_U_FECHA_HORA]<>null then [TRP_U_FECHA_HORA]
    else [TRP_P_FECHA_HORA],
    type nullable datetime)
```

Confirmado: el fallback TRP existe estructuralmente (TRP_U/TRP_P como respaldo
cuando VBFA/VTTP no entrega manifiesto).

## Cuantificación (modelo vivo, SHA 085bfec)

| Grupo FES | Cantidad |
|---|---|
| FES total | 439 |
| FES cerrados | 437 |
| FES con manifiesto real (PRIMERA/ULTIMA_FECHA_MANIFIESTO no nula) | **437 (100% de cerrados)** |
| FES sin manifiesto real pero con TRP | **0** |
| FES sin manifiesto ni TRP | 2 (1167574, 4190139472 — ambos AUD_ESTADO_FLUJO_FES = INCOMPLETO, no cerrados) |

## Conclusión

El fallback TRP existe en el código pero **NO está cerrando ningún FES** en los
datos actuales: 437 de 437 cerrados usan manifiesto real VBFA/VTTP. Los 2 sin
manifiesto ni TRP quedan abiertos/INCOMPLETO. Impacto actual = 0.
La eliminación del fallback sigue siendo decisión de negocio (riesgo futuro si
llegaran datos con TRP sin manifiesto).

## Comparación Fact_Tracking vs Fact_Hitos_Operacionales

Fact_Hitos_Operacionales usa exclusivamente PRIMERA/ULTIMA_FECHA_MANIFIESTO
(no tiene fallback TRP) en los hitos FES_*_MANIFIESTO (líneas 574-578 del TMDL).
Coherente con Fact_Tracking en el 100% de los casos cerrados actuales.
