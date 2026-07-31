# REQ-004 · Restauración selectiva de tooltips de negocio

Objetivo: mantener desactivado el tooltip técnico en SVG decorativos, de navegación e indicadores sin contexto; restaurar los tooltips de página existentes en visuales analíticos que ya entregaban información de negocio.

Criterio aplicado:
- SVG decorativo/navegación: `visualTooltip.show = false`.
- Visual analítico con tooltip ReportPage preexistente: restaurar exactamente su configuración anterior.
- No modificar DAX, medidas, filtros, ordenamiento, posiciones, SLA, cierres ni cohortes.

La validación final debe ejecutarse en Power BI Desktop y documentar que no aparece código SVG y que los tooltips de negocio siguen disponibles donde corresponde.
