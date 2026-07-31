# Auditoría NS_V36

Estado: **OK**

- JSON válidos: 146
- Páginas visibles: 4
- Tooltips: 4
- Visuales: 129
- Botones de navegación/acción: 18
- Medidas activas: 153
- Medidas con prefijo de versión: 0
- Medidas legacy activas: 0
- Medidas duplicadas: 0
- Referencias rotas: 0
- QuerySort inválidos: 0

## Lienzo 00
- Tarjetas con valores exactos, sin abreviaturas automáticas ambiguas.
- Barra de navegación rotulada y con estado activo visible.
- Fecha/hora de actualización legible en el encabezado.
- Participación por flujo conserva la selección de zona/rango.
- Matriz de hitos conserva la misma cohorte territorial y de flujo.
- Valor neto defensivo: una contribución por pedido.
- Tooltip: subproceso crítico real, excluyendo macroprocesos agregados.

## Reconciliación
- Normal 1.251 + FES/FES+Saldo 571 + Saldo puro 1 = **1.823**.
- Santiago 797 + Regiones 1.026 = **1.823**.
- En SLA 1.486 + Fuera SLA 337 = **1.823**.
- NS interno = **81,5%**.
- Promedio = **3,9 DH**.
- P90 = **8,0 DH**.

## Regla Santiago
La factura emitida hasta las 16:00 puede cerrar operativamente el pedido solo cuando el corte de las 16:00 ya se cumplió. Una factura del día no se cierra anticipadamente antes del corte.

La validación del paquete es estructural y lógica. La actualización SQL y el renderizado final deben comprobarse al abrir el proyecto en Power BI Desktop.
