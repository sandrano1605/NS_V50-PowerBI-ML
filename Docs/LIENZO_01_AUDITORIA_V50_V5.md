# Auditoría lienzo 01 · Análisis Fuera SLA

## Cohorte
- `FA Pedidos = RE Pedidos contexto`.
- `FA Fuera SLA = RE Pedidos fuera SLA contexto`.
- Cohorte: pedidos cerrados con `DIAS_INTERNOS_DH` informado, respetando filtros del lienzo 00.

## Relación de volumen
- `Dim_Pedido[PED_NUMERO_PEDIDO]` (1) → `Lineas_y_unidades_por_pedidos[Pedido]` (*).
- Dirección de filtro desde `Dim_Pedido`.
- Las medidas de líneas/unidades aplican la cohorte con `TREATAS`.

## Correcciones
- FES incluye `FES` y `FES + SALDO`.
- Fin de mes usa los últimos 7 días hábiles de `Dim_Fecha`.
- Arrastre significa cierre en un mes posterior al mes de creación.
- Ranking de vendedores usa el mismo numerador y denominador de la cohorte.
- Top crítico muestra solamente pedidos con más de 5 DH.
- Se eliminaron 10 visuales heredados de 1×1 que ejecutaban consultas innecesarias.

## Validación visual
- Lienzo 1600×900.
- Barra lateral y filtros iguales al lienzo 00.
- Sin superposición entre bloques visibles.
- Tabla final disponible para drillthrough por pedido.
