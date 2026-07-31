# REQ-006 · Migración de visuales SVG analíticos a visuales nativos

## Estado estructural

### Migrados en `00 Resumen Ejecutivo Mayorista`

- Pedidos evaluados → `cardVisual` con `[RE Pedidos contexto]`.
- Nivel de servicio → `cardVisual` con `[RE NS contexto]`.
- Promesa cliente → `textbox` nativo con regla Santiago 5 DH / Regiones 7 DH.
- Distribución por flujo → `donutChart` con `Fact_Tracking[CLASIFICACION]` y `[RE Pedidos contexto]`.
- Evolución 3 meses → `lineStackedColumnComboChart` con medidas M3 administrativas, operacionales y totales.
- Resumen del período → `cardVisual` múltiple con 7 indicadores.
- Pedidos críticos → `tableEx` sin la medida `RE TT Estado SVG`.

### Migrado en `01 Análisis Fuera SLA`

- Tabla de pedidos críticos → `tableEx` sin la medida `RE TT Estado SVG`.

## Corrección de pregunta de negocio

El antiguo SVG de distribución contaba todos los pedidos evaluados por clasificación. Por eso la pregunta correcta es:

> ¿Cómo se distribuyen los pedidos evaluados entre NORMAL, FES, FES + SALDO y SALDO?

No corresponde afirmar que ese visual identifica por sí solo el flujo con más pedidos fuera SLA.

## Sin cambios en el modelo

- No se modificó DAX.
- No se modificó Power Query ni Python.
- No se modificó el cierre FES.
- No se modificó SLA 4/5 ni promesa 5/7.
- No se modificó la cohorte.

## Validación pendiente

Los objetos están estructuralmente reemplazados en PBIR, pero deben abrirse en Power BI Desktop. El LLM local solo debe ejecutar `pull`, `Actualizar todo`, validar el render y generar evidencia. No puede corregir medidas ni rediseñar objetos.

## Inventario restante

`Docs/AUDITORIA_LIVE/latest/svg_inventory.csv` contiene exclusivamente las medidas SVG dinámicas todavía pendientes en Tracking, tooltips y Auditoría por Pedido. Los logos, flujos e iconos registrados como recursos estáticos no se consideran medidas DAX SVG.
