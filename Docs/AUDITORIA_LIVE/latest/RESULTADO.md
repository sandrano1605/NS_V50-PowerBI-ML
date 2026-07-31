# RESULTADO — RUN 20260731_033000_visual_clientes_fuera_sla

## Estado: VERDE

Cambio aplicado, validado estructuralmente (JSON/TMDL) y validado contra el modelo vivo (MCP).

## Resultados del modelo vivo

| Métrica | Esperado | Real | Estado |
|---|---|---|---|
| Recurrente 3M | 3 | 3 | ✅ |
| Recurrente 2M | 27 | 27 | ✅ |
| Puntual 1M | 221 | 221 | ✅ |
| Total clientes fuera SLA | 251 | 251 | ✅ |
| Pedidos evaluados | 1.616 | 1.616 | ✅ |
| Pedidos fuera SLA | 360 | 360 | ✅ |
| NS | 77,72% | 77,72% | ✅ |
| Diferencia lienzo 00 vs 01 | 0 | 0 | ✅ |

## Qué cambió

1. 5 medidas Visible pasaron de `>= 2` a `>= 1` (incluye Puntual 1M).
2. Sort del visual: Meses DESC → Pedidos DESC → DH DESC.
3. Título: "1. CLIENTES FUERA SLA · FRECUENCIA EN LOS ÚLTIMOS 3 MESES → Recurrente 3M → 2M → 1M".

## Qué no cambió

- Cohorte de lienzos 00 y 01 (1.616 pedidos).
- SLA interno (4/5 zonal).
- Lógica de cierre FES (manifiesto) ni NORMAL/SALDO (despacho).
- Campos del visual (cliente, vendedor, flujo).

## Pendiente

- Apertura manual en Power BI Desktop para validación de renderizado (requiere instancia viva).
