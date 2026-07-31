# RUN 20260731_010600_svg_hover_final

## Requerimiento
REQ-003: desactivar tooltip tecnico en todos los visuales que renderizan SVG/Image URL para evitar codigo en hover.

## Ejecucion
- Script oficial: `tools/fix_svg_hover_req003.py` (commit 9495cea)
- Visuales SVG detectados: 43 (descubiertos desde archivos, no solo la lista previa)
- Visuales que requerian ajuste: 39
- Visuales ya OK (REQ-002): 4 (chart_mensual_3m_v39, summary_month, card_4e4fe7d672d840, table_c57572c4abbe4d)

## Cambio aplicado
- `visualTooltip.show = false` en los 39 visuales pendientes
- Sin duplicar bloques; si existia, solo se cambio show a false
- No se modifico DAX, expresiones SVG, posiciones, filtros, cohorte, SLA, cierre FES

## Casos documentados (paginas tooltip de negocio)
- critical_table (00 y 01): tenia tooltip de pagina 22a1 (negocio, sin SVG en campos). Se desactivo show para garantizar cero codigo en hover. La pagina tooltip permanece en el repo.
- kpi_promesa / sla_panel: pagina 652385 con SVG en tt_status (UI Indicador ejecutivo SVG) -> desactivado correctamente.
- donut_flujo: pagina 45f3 con SVG en fes_diag_card -> desactivado correctamente.
- f07bd2d60e407e2ddd01: pagina 22a1 -> desactivado, documentado.

## Regresion (MCP modelo vivo)
- 1616 / 360 / 77,72% / 251 (3+27+221) - OK
- 4190139455 = OK, 1167577 = OK
