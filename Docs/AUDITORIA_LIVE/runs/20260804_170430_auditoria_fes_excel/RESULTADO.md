# RESULTADO: Auditoría pedidos FES del Excel data_sap.xlsx vs modelo (2026-08-04)

**Rama:** work/ns-lienzo-02-ingreso-pedidos
**SHA:** 40602323b15fc722db27b2e917c16d8e03eb15bc
**Dictamen:** 🔴 ROJO — discrepancia de clasificación FES confirmada

## Fuente analizada

`C:\Users\alonso.moya\OneDrive - ARTEL S.A\Escritorio\data_sap.xlsx`
- Hoja: Export
- 524 filas (1 cabecera + 523 datos)
- Columnas: "Pedidos FES" (col 1) y "Pedido Original" (col 2)
- 523 pedidos FES listados por el negocio
- 253 pedidos originales únicos

## Hallazgo principal

Los pedidos que el negocio lista como FES en el Excel **NO están clasificados como FES en el modelo**.

Ejemplos verificados en Fact_Pedidos_Auditoria:

| Pedido | ES_FES | REGLA_CLASIFICACION_FES | SEGMENTO | PED_TEXTO_ESTADO | Fecha |
|---|---|---|---|---|---|
| 1168016 | **False** | NO FES; VALIDADO VBFA C-C | FLUJO NORMAL | CERRADO VBAK | 02-07-2026 |
| 1168012 | **False** | NO FES; VALIDADO VBFA C-C | FLUJO NORMAL | CERRADO VBAK | 02-07-2026 |
| 1168009 | **False** | NO FES; VALIDADO VBFA C-C | FLUJO NORMAL | ABIERTO VBAK | 02-07-2026 |
| 1168010 | **False** | NO FES; VALIDADO VBFA C-C | FLUJO NORMAL | ABIERTO VBAK | 02-07-2026 |
| 1168006 | **False** | NO FES; VALIDADO VBFA C-C | FLUJO NORMAL | ABIERTO VBAK | 02-07-2026 |

## Interpretación

- El Excel asocia cada pedido posterior (1168xxx) con su original (41901399xx).
- En el modelo, esos pedidos aparecen como **NO FES; VALIDADO VBFA C-C** y
  **FLUJO NORMAL** — la clasificación FES NO fue aplicada.
- El texto "NO FES; VALIDADO VBFA C-C" indica que la query de clasificación
  **no encontró el flujo VBFA C→C** para el original, o el pedido quedó en la
  integración VBAK sin reclasificación.
- Estos pedidos están marcados como `VBAK SIN ZART` (integrados por el append
  de VBAK) y NO fueron reclasificados a FES.

## Impacto

- El universo FES del modelo está **subestimado** (estos pedidos van como NORMAL).
- NS y lienzo 01 pueden distorsionarse.
- Las tendencias de FES del lienzo 02 no los incluyen.
- 523 pedidos del negocio no coinciden con la clasificación del modelo.

## Pendiente (corresponde a ChatGPT)

- Revisar la query de clasificación FES (VBFA C→C) para estos originales.
- Determinar por qué el flujo C→C no se detectó para 41901399xx.
- Si corresponde, reclasificar como FES y validar el impacto en NS.

## Archivos

- 00_git.txt
- RESULTADO.md
