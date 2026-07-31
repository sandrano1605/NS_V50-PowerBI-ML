# REQ-006 · Migración inicial del lienzo 00 a visuales nativos

## Base

- Rama: `work/ns-live-audit`
- Commit base: `8be7824fb7895f7553fa068c58df697769115d9f`

## Problema confirmado

Power BI Desktop muestra el valor crudo `data:image/svg+xml` al hacer hover sobre visuales `tableEx` que proyectan medidas SVG/ImageUrl. La eliminación de `visualTooltip` no corrige el comportamiento.

## Corrección aplicada por ChatGPT

Se reemplazaron en `00 Resumen Ejecutivo Mayorista`:

1. `f07bd2d60e407e2ddd01`: SVG de pedidos → `cardVisual` nativo con `[RE Pedidos contexto]`.
2. `sla_panel`: SVG de SLA → `cardVisual` nativo con `[RE NS contexto]`.
3. `kpi_promesa`: SVG estático → `textbox` nativo con promesas Santiago 5 DH y Regiones 7 DH.
4. `donut_flujo`: SVG → `donutChart` nativo con `Fact_Tracking[CLASIFICACION]` y `[RE Pedidos contexto]`.
5. Pregunta general del lienzo y matriz de trazabilidad actualizadas.

## Corrección de coherencia de negocio

El SVG anterior mostraba la distribución de los 566 pedidos evaluados por flujo, pero la pregunta decía “qué flujo concentra más pedidos fuera SLA”. La pregunta correcta para ese visual es:

> ¿Cómo se distribuyen los pedidos evaluados entre NORMAL, FES, FES + SALDO y SALDO?

## No modificado

- DAX del modelo.
- SLA 4/5 DH.
- Promesa cliente 5/7 DH.
- Cierre FES.
- Power Query y Python.
- Cohorte cerrada y evaluable.
- Medidas aprobadas.

## Validación que debe ejecutar el LLM local

El LLM no debe editar archivos. Solo debe hacer `pull`, abrir `NS.pbip`, ejecutar Actualizar todo y validar:

- Los cuatro visuales renderizan.
- No aparece código SVG en hover.
- Pedidos evaluados = 566 en junio bajo el contexto mostrado en la captura, o el valor correcto según filtros actuales.
- Modelo global: 1.616 evaluables, 360 fuera SLA, NS 77,72%, 251 clientes fuera SLA.
- La suma del donut coincide con `[RE Pedidos contexto]`.
- Las categorías del donut son NORMAL, FES, FES + SALDO y SALDO.

Si Power BI normaliza propiedades visuales, solo debe documentarlo; no debe rediseñar ni modificar medidas.
