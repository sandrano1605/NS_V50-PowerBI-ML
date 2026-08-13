# Cierre conjunto INC-015 + IN02 (post-fix, refresh final)

RUN_ID: 20260813_094039_inc015_in02_postfix_94133e0
SHA: 94133e023205698d89e34458b32e10abdc48598a
Modelo vivo: localhost:55508, refresh 2026-08-13 10:17

## INC-015 — cobertura líneas/unidades (semi-join ZART 3M)

| Métrica | Valor |
|---|---|
| Filas en Lineas_y_unidades_por_pedidos | 2.075 |
| Pedidos ZART 3M (ventana móvil) | 2.077 |
| Cobertura | 99,9% |
| Residuales sin líneas | 1168066, 1168568 |
| Tiempo SQL (referencia) | 0,98s (antes 155s) |

Dictamen: INC015_AEDAT_GREEN

## IN02 — parser ERZET (fallback VBAK 43/45)

| Canal | Sin hora válida (antes) | Sin hora válida (después) |
|---|---|---|
| 43 | 149 | 1 |
| 45 | 35 | 0 |
| Total | 184 | 1 |

El único residual en 43/45 es 1168066 (sin VBAK, causa conocida).
Los "Sin hora válida" restantes en el modelo pertenecen a canales 46/47/42,
fuera del alcance del fallback (diseño correcto: fallback solo 43/45).

Dictamen: IN02_ERZET_PARSER_GREEN

## Regresión mínima

- Cerrados sin DH: 0
- FES cerrados sin manifiesto real: 0
- FIND-002A (RE TT Título): sin SemanticError, renderiza "Universo cerrado"
- RE Pedidos contexto: 1.953 (ventana móvil actualizada)

## Dictamen final

INC015_STATUS=INC015_AEDAT_GREEN
IN02_STATUS=IN02_ERZET_PARSER_GREEN
