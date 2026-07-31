# V8 — Validación final del lienzo 01 dinámico

## Correcciones finales

- `FA DH Promedio` hereda `RE Promedio contexto DH`, asegurando la misma cohorte cerrada y medible del lienzo 00.
- Se creó `FA % Fuera SLA` como medida genérica para parámetros dinámicos.
- El parámetro de indicadores usa la medida genérica y no la medida nombrada por vendedor.
- Se eliminó el texto de ayuda que se superponía con la banda de auditoría.
- Se incorporó la instrucción de drillthrough dentro del encabezado de auditoría.
- Se normalizó el orden de tabulación de los selectores dinámicos.

## Validaciones

- 231 archivos JSON válidos; 0 errores.
- 28 objetos visibles en el lienzo 01.
- 0 objetos fuera del lienzo 1600×900.
- 0 superposiciones inesperadas entre objetos de primer plano.
- 0 referencias a medidas inexistentes.
- Relación única de volumen: `Lineas_y_unidades_por_pedidos[Pedido]` → `Dim_Pedido[PED_NUMERO_PEDIDO]`.
- Botón de drillthrough dirigido a `01.1 Auditoría por Pedido`.

## Validación requerida en Power BI Desktop

Después de `Actualizar todo`, comprobar:

- `FA Pedidos = RE Pedidos contexto`.
- `FA Fuera SLA = RE Pedidos fuera SLA contexto`.
- `FA Pedidos sin Volumen = 0`.
- `FA Cobertura Volumen % = 100 %`.
- Los parámetros de agrupación e indicadores cambian la matriz sin perder filtros de contexto.
- El botón de auditoría se habilita al seleccionar un único pedido.
