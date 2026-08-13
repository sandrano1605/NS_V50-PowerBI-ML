# Lienzo 01 — Coherencia de filtros: caso Carlos Garrido

## Dictamen: L01_COHERENCIA_RED (interacción engañosa)

## H1 — Vendedor actual vs responsable histórico: CONFIRMADO
- `fa_vendedores_reincidentes` usa `Dim_Cliente[VENDEDOR_NOMBRE]` = vendedor ACTUAL del maestro CLIENTE_VENDEDOR.
- Carlos Garrido tiene 25 clientes y 81 pedidos en la cohorte 43/45.
- `Fact_Tracking[PED_RESPONSABLE]` de esos 81 pedidos: **V610(72), V650(6), V550(3)** — NINGUNO "Carlos Garrido".
- Discrepancia 100%: el nombre "Carlos Garrido" no coincide con ningún código de responsable histórico.

## H2 — Selección de fila = Vendedor + Flujo: CONFIRMADO
- La tabla 3 proyecta `Dim_Cliente[VENDEDOR_NOMBRE]` + `Fact_Tracking[CLASIFICACION]`.
- Flujos de Carlos: NORMAL (45 pedidos, 4 fuera SLA) y FES (36 pedidos, 16 fuera SLA).
- Clic en fila = Carlos + UN flujo, NO Carlos completo.

## H3 — Tabla 4 distorsionada por flujo: CONFIRMADO

| Contexto | Pedidos | FES | % FES |
|---|---|---|---|
| Carlos SOLO | 75 | 36 | 48% |
| Carlos + NORMAL | — | — | blank/0% |
| Carlos + FES | — | 36 | 100% |

Seleccionar "Carlos + FES" fuerza %FES=100%; "Carlos + NORMAL" lo deja blank/0.
La tabla "4. FES VS CARGA" deja de comparar FES contra la carga total.

## Respuesta a la decisión de negocio

Si el objetivo es "filtrar por Carlos y que todo el lienzo explique a Carlos",
la selección por fila (Vendedor + Flujo) es INCORRECTA en UX:
- Debería filtrar solo Carlos (vendedor), sin arrastrar el flujo.
- O bien usar un slicer de vendedor separado (no la fila de tabla 3).

No es un problema de DAX: las medidas responden bien al contexto. Es un
problema de interacción/UX: la fila de la tabla 3 cruza dos dimensiones.

## Recomendación técnica (NO implementada)
1. Deshabilitar la interacción de selección de la tabla 3 sobre la tabla 4
   (FES vs Carga) y sobre critical_table si se quiere vista global.
2. O cambiar la tabla 3 para que el clic filtre solo VENDEDOR_NOMBRE sin
   arrastrar CLASIFICACION (interacción dirigida por columna).
3. Decidir semántica "Vendedor": actual (Dim_Cliente) vs histórico
   (PED_RESPONSABLE). Hoy son conceptos distintos (0% coincidencia).
