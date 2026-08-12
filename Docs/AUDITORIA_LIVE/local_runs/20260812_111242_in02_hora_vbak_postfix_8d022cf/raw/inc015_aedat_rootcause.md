# INC-015 ROOT CAUSE DEFINITIVA — filtro AEDAT

## Hallazgo

La baja cobertura de `Lineas_y_unidades_por_pedidos` (58,3%) NO es por falta de datos
en VBAP_SAP, sino por el filtro `AEDAT >= GETDATE() - 730` en la query M.

## Evidencia (comparación coherente, sin TOP, sin filtros distorsionantes)

| Medición | Valor |
|---|---|
| VBAP_SAP pedidos distintos (SIN filtro AEDAT) | 8.858.283 |
| VBAP_SAP pedidos distintos (CON AEDAT >= 730d) | 22.799 (0,26%) |
| ZART_TRACK 3M (universo real) | 2.055 |
| ZART_TRACK 3M → en VBAP SIN filtro AEDAT (clave exacta) | 2.053 (99,9%) |

## Cobertura por largo de clave (clave exacta, sin filtro AEDAT)

| Grupo | Pedidos ZART 3M | En VBAP | Cobertura |
|---|---|---|---|
| 7 dígitos (116xxxx) | 1.047 | 1.045 | 99,8% |
| 10 dígitos (4190xxx) | 1.008 | 1.008 | 100% |
| Total | 2.055 | 2.053 | 99,9% |

## Las 2 causas de la baja cobertura

1. **Filtro `AEDAT >= GETDATE()-730`** → elimina el 99,74% de las posiciones.
   AEDAT es la fecha de actualización de la posición en SAP, NO la fecha del pedido.
   La mayoría de posiciones tienen AEDAT antiguo (>730d) aunque el pedido siga vigente.
   → Quitar el filtro sube la cobertura de 58,3% a 99,9%.

2. **Prefijo de clave (menor)** → 2 pedidos de 7 dígitos (`1168066`, `1168568`)
   no están en VBAP con clave exacta. El `1221168066` que aparece en VBAP es un
   pedido DISTINTO (AUART=YV01, VTWEG=52, ERDAT=2023) — falso positivo de LIKE.

## Fix correcto (NO aplicado aún — auditor read-only)

En `NS.SemanticModel/definition/tables/Lineas_y_unidades_por_pedidos.tmdl`:

```sql
SELECT
    VBAP.VBELN AS Pedido,
    COUNT(*) AS Lineas,
    SUM(ISNULL(VBAP.KWMENG, 0)) AS Suma_Unidades
FROM VBAP_SAP AS VBAP
GROUP BY VBAP.VBELN
-- QUITAR: WHERE VBAP.AEDAT >= GETDATE() - 730
```

## Impacto esperado

- Cobertura de líneas/unidades: 58,3% → 99,9% (2.053/2.055)
- Quedan 2 pedidos (1168066, 1168568) sin posiciones — casos de calidad de dato aislados.

## Ganancia de rendimiento

El filtro por canal 43/45 (semi-join VBAK) reduce el escaneo de 30M filas a
~1.083 pedidos (0,54s vs 2,32s). NO es necesario reducir la ventana temporal
(reducir a 4 meses rompería cobertura porque AEDAT no refleja la fecha real).
