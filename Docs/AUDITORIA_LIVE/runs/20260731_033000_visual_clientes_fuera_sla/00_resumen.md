# RUN 20260731_033000_visual_clientes_fuera_sla

## Resumen

- **Requerimiento**: Visual "CLIENTES QUE REPITEN FUERA SLA" — mostrar todos los clientes fuera SLA (>= 1 mes), ordenar por recurrencia, actualizar título.
- **Modelo**: NS — NS_V50_v15_Error_Python_ndarray_Corregido
- **Fecha**: 2026-07-31 (validación en vivo previa 30-07-2026 22:54, persistencia en disco confirmada 31-07-2026)
- **Rama**: work/ns-live-audit

## Cambios aplicados

### P1 — Medidas Visible (5) cambian de `>= 2` a `>= 1`

Archivo: `NS.SemanticModel/definition/tables/Medidas.tmdl`

1. `FA Meses Fuera SLA Cliente Visible` → `IF([FA Meses Fuera SLA Cliente] >= 1, [FA Meses Fuera SLA Cliente])`
2. `FA Recurrencia Cliente Visible` → `IF([FA Meses Fuera SLA Cliente] >= 1, [FA Recurrencia Cliente])`
3. `FA Pedidos Fuera SLA Cliente Visible` → `IF([FA Meses Fuera SLA Cliente] >= 1, [FA Fuera SLA])`
4. `FA % Fuera SLA Cliente Visible` → `IF([FA Meses Fuera SLA Cliente] >= 1, [FA % Fuera SLA])`
5. `FA DH Fuera SLA Cliente Visible` → `IF([FA Meses Fuera SLA Cliente] >= 1, [FA DH Promedio Fuera SLA])`

### P2 — Ordenamiento por recurrencia

Archivo: `NS.Report/definition/pages/a1b2c3d4e5f6071829/visuals/fa_clientes_recurrentes/visual.json`

1. `FA Meses Fuera SLA Cliente Visible` Descending
2. `FA Pedidos Fuera SLA Cliente Visible` Descending
3. `FA DH Fuera SLA Cliente Visible` Descending

### P3 — Título

Título: `1. CLIENTES FUERA SLA · FRECUENCIA EN LOS ÚLTIMOS 3 MESES → Recurrente 3M → 2M → 1M`

## Resultados validados en modelo vivo (antes del cierre de instancia)

| Métrica | Esperado | Resultado |
|---|---|---|
| Recurrente 3M | 3 | 3 ✅ |
| Recurrente 2M | 27 | 27 ✅ |
| Puntual 1M | 221 | 221 ✅ |
| Total clientes fuera SLA | 251 | 251 ✅ |
| Pedidos evaluados | 1.616 | 1.616 ✅ |
| Pedidos fuera SLA | 360 | 360 ✅ |
| NS | 77,72% | 77,72% ✅ |
| Diferencia lienzo 00 vs 01 | 0 | 0 ✅ |

## Nota sobre persistencia

- Las 5 medidas quedaron persistidas en el TMDL en disco por Power BI Desktop al cerrar (confirmado con grep: todas con `>= 1`).
- El visual.json (sort + título) fue sobrescrito por Power BI Desktop al cerrar (perdió la edición directa previa); se reaplicó en disco con Power BI Desktop cerrado y se validó JSON.
- Los resultados del modelo vivo fueron exportados antes del cierre de la instancia (30-07 22:54 / 31-07 03:31).
