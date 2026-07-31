# Auditoría de cohorte y volumen · NS V50 v3 corregido

## Hallazgos

1. `Lineas_y_unidades_por_pedidos` existe y contiene una fila por pedido con `Lineas` y `Suma_Unidades`.
2. La relación detectada automáticamente era `Bloque_comercial[Pedido]` ↔ `Lineas_y_unidades_por_pedidos[Pedido]`, 1:1 y bidireccional. Esta relación no garantizaba la cohorte oficial de `Fact_Tracking`.
3. `Dim_Pedido` se construye desde `Fact_Tracking`, por lo que representa el universo único oficial.
4. El lienzo 00 usa pedidos cerrados con `DIAS_INTERNOS_DH` informado mediante `[RE Pedidos contexto]`.
5. El lienzo 01 usaba `COUNTROWS(Fact_Tracking)`, por lo que mezclaba pedidos abiertos y no medibles.

## Correcciones

- Se eliminó la relación automática con `Bloque_comercial`.
- Se creó la relación `Lineas_y_unidades_por_pedidos[Pedido]` → `Dim_Pedido[PED_NUMERO_PEDIDO]`, muchos a uno y filtro unidireccional desde la dimensión.
- `[FA Pedidos]` ahora usa `[RE Pedidos contexto]`.
- `[FA Fuera SLA]` ahora usa `[RE Pedidos fuera SLA contexto]`.
- `[FA Líneas]` y `[FA Unidades]` reproducen la misma cohorte cerrada, medible, por flujo, zona y rango DH del lienzo 00.

## Resultado esperado

Bajo los mismos filtros, los pedidos analizados del lienzo 01 deben coincidir exactamente con los pedidos evaluados del lienzo 00. Líneas y unidades quedan restringidas a esa misma lista de pedidos.
