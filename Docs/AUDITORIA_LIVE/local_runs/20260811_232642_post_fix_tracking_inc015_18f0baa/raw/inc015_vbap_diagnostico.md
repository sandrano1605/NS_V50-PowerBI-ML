# INC-015 — Diagnóstico VBAP_SAP definitivo

## Clasificación de los 810 pedidos sin match (SHA 18f0baa, modelo post-refresh)

| Clasificación | Conteo | % |
|---|---|---|
| **DENTRO_730_EN_VBAK** (existen en VBAK con fecha_pedido ≥ 2024-08-12) | **782** | **96,5%** |
| AUSENTE_VBAK (no existen en VBAK; fuera de ventana 90-días) | 28 | 3,5% |
| EXCLUIDO_AEDAT_ANTIGUO (fecha_pedido < 2024) | 0 | 0% |

## Diagnóstico: CAUSA_VISTA_VBAP_SAP

- **782 pedidos** (96,5%) existen en `Pedidos_Normal_VBAK` como cabeceras con `fecha_pedido` entre 2026-05-11 y 2026-08-03.
- Todos tienen `fecha_pedido` MUY posterior a 2024-08-12 (hace 730 días desde hoy 2026-08-11).
- Por lo tanto, todos deberían estar presentes en `VBAP_SAP` si el filtro `AEDAT >= GETDATE()-730` fuera el único criterio.
- **No lo están.** La vista `VBAP_SAP` simplemente no contiene las líneas de estos pedidos.
- Esto descarta definitivamente la hipótesis `CAUSA_AEDAT`.

## Distribución de los 782 DENTRO_730_EN_VBAK por flujo

| Flujo | Pedidos sin match |
|---|---|
| NORMAL | 640 |
| FES | 141 |
| FES + SALDO | 1 |

## Los 28 AUSENTE_VBAK

Son pedidos de 2026-05-11/12 (ej: 1166486, 1166476, 1166493) que quedan fuera del filtro `ERDAT > GETDATE()-90` de `Pedidos_Normal_VBAK`. Probablemente también existen en la fuente pero VBAK no los captura por su ventana más corta. No se pueden clasificar sin acceso directo a la fuente SQL.

## Cobertura potencial

Si VBAP_SAP incluyera los 782 pedidos DENTRO_730_EN_VBAK:
- Con match: 1.131 → **1.131 + 782 = 1.913**
- Cobertura: 1.913 / 1.941 = **98,6%**

Los 28 restantes (AUSENTE_VBAK) probablemente también se recuperarían si VBAP_SAP estuviera completa.

## Recomendación (NO implementada)

1. Revisar la vista `VBAP_SAP` en la fuente `DMF_VTA_PRD`: ¿filtra por tipo de documento, canal, o centro que excluya pedidos del universo?
2. Comparar `SELECT DISTINCT VBELN FROM VBAP_SAP` contra `SELECT VBELN FROM VBAK WHERE ERDAT > GETDATE()-90` para cuantificar exactamente el gap.
3. Si VBAP_SAP es una vista con filtros internos, considerar usar directamente `VBAP` (tabla base SAP) para las líneas, o cruzar con `VBAK` para el universo y luego `VBAP` para líneas.
