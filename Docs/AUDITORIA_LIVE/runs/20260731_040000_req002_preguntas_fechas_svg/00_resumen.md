# RUN 20260731_040000_req002_preguntas_fechas_svg

## Resumen

- **Requerimiento**: REQ-002 — Preguntas de negocio, ventana temporal y comportamiento SVG.
- **Modelo**: NS — NS_V50_v15_Error_Python_ndarray_Corregido
- **Rama**: work/ns-live-audit
- **Fecha**: 2026-07-31

## Qué cambió

### 1. Ventana temporal (4 medidas nuevas)
- `RE Fecha mínima contexto` — MINX(ALLSELECTED(Fact_Tracking), PED_FECHA_HORA)
- `RE Fecha máxima contexto` — MAXX(ALLSELECTED(...))
- `RE Estado último mes` — parcial/completo
- `RE Ventana análisis texto` — "Período analizado: X al Y · N meses · estado"
- Carpeta: `02. Resumen Ejecutivo\14. Ventana Temporal`
- Leyendas `window_note` en los 3 lienzos (00, 01, 01.1) usando la medida

### 2. Preguntas de negocio visibles
- Lienzo 00: textbox `bq_preguntas_negocio` con preguntas REQ-002 4.1
- Lienzo 01: `fa_question_header` actualizado con preguntas REQ-002 4.2
- Lienzo 01.1: `text_272b8969e32647` con pregunta principal REQ-002 4.3

### 3. SVG / tooltips
- Tooltip desactivado en 4 visuales con SVG (chart_mensual_3m_v39, summary_month, card_4e4fe7d672d840, table_c57572c4abbe4d) — evita código SVG en hover
- `dataCategory: ImageUrl` en medidas SVG (verificado 19 medidas)
- Páginas tooltip 22a1/652385/45f3 verificadas sin SVG en campos

## Qué NO cambió

- SLA interno (4/5 zonal)
- Cierre FES (manifiesto) / NORMAL/SALDO (despacho)
- Cohorte histórica (1.616 pedidos evaluables)
- Medidas de recurrencia aprobadas (P1/P2/P3 del REQ-001)
- Power Query, Python, relaciones

## Resultados validados en modelo vivo

| Métrica | Valor |
|---|---|
| Pedidos evaluados | 1.616 |
| Fuera SLA | 360 |
| NS | 77,72% |
| Diferencia lienzos | 0 |
| Clientes fuera SLA | 251 (3+27+221) |
| Fecha mín | 30-04-2026 |
| Fecha máx | 14-07-2026 |
| Último mes | Parcial |
| Regresión | 4190139455 ✅ 1167577 ✅ |

## Incidentes resueltos

1. Power BI Desktop sobrescribió TMDL/JSON desde memoria al abrir → se cerró PBI, se aplicaron cambios en disco, se reabrió.
2. Medidas duplicadas en TMDL (creadas vía MCP + script) → se eliminaron duplicados.
3. `formatString:` vacío en 2 medidas → corregido a `0`.
