# 01 Análisis Fuera SLA · Diseño normalizado

## Propósito
Explicar la caída del nivel de servicio usando exactamente la misma cohorte cerrada y medible del lienzo 00.

## Filtros de contexto
- Mes–Año
- Zona
- Flujo
- Clasificación

## Preguntas y objetos
1. **¿Cuál es la magnitud?** — banda KPI: pedidos, FES, normal, líneas, unidades y fuera SLA.
2. **¿Existe patrón de cierre?** — tabla mensual de FES, fin de mes, arrastre y líneas.
3. **¿Qué vendedores explican el problema?** — ranking por pedidos, fuera SLA, porcentaje y líneas.
4. **¿FES tarda más que normal?** — comparación mensual de días hábiles y FES fuera SLA.
5. **¿Qué pedidos requieren intervención?** — tabla auditable con pedido, cliente, vendedor, clasificación, días, hito crítico, exceso y motivo.
6. **¿Qué ocurrió en cada hito?** — drillthrough a `01.1 Auditoría por Pedido`.

## Regla de coherencia
`FA Pedidos = RE Pedidos contexto`; líneas y unidades se filtran por la misma lista de pedidos mediante `Dim_Pedido`/`TREATAS`.
