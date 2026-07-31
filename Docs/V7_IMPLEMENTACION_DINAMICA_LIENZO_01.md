# V7 · Implementación dinámica del lienzo 01

## Implementado

- Parámetro de campos **Parámetro Agrupación SLA**: Cliente, Vendedor, Canal, Flujo, Mes, Hito actual y Pedido.
- Parámetro de campos **Parámetro Indicadores SLA**: Pedidos, Fuera SLA, % Fuera SLA, Líneas, Unidades, Promedio DH, FES y FES fuera SLA.
- Matriz dinámica conectada a ambos parámetros.
- Selectores profesionales dentro del bloque central.
- Botón de drillthrough **Auditar pedido seleccionado** hacia `01.1 Auditoría por Pedido`.
- Se conserva el acceso alternativo por clic derecho.
- Se mantiene la cohorte oficial heredada del lienzo 00 mediante las medidas FA/RE.

## Uso

1. Seleccionar una agrupación.
2. Seleccionar una o varias métricas.
3. Revisar la matriz dinámica.
4. Seleccionar un pedido en la tabla inferior.
5. Usar el botón de auditoría o clic derecho → Drillthrough.

## Nota técnica

Los parámetros se implementaron como tablas calculadas `NAMEOF` con `ParameterMetadata` y `groupByColumn`, forma nativa de Power BI.
