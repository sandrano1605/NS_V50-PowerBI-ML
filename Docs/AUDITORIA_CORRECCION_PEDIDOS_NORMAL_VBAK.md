# Auditoría: Corrección de `Pedidos_Normal_VBAK` (2026-08-03)

## Contexto
El usuario pidió revisar la tabla `Pedidos_Normal_VBAK` del modelo NS, que contiene
todo el universo FES + Normal ya normalizado con sus cruces. El requisito clave:
**el manifiesto debe cruzarse a todos los pedidos** (`fecha_salida`).

## Estado inicial (modelo en vivo)
| Columna | Con dato | Cobertura |
|---|---|---|
| Filas | 2.158 | 100% |
| fecha_pedido | 2.158 | 100% |
| fecha_entrega | 1.988 | 92% |
| fecha_contabiliza | 1.988 | 92% |
| fecha_factura | 2.081 | 96% |
| fecha_fes | 371 | 17% |
| **fecha_salida** | **1.537** | **71%** |

Faltaban 621 pedidos sin fecha_salida, de los cuales 346 eran FES (con fecha_fes
pero sin manifiesto).

## Bugs encontrados en la columna condicional `Fecha_manifiesto`

Lógica original (incorrecta):
```m
if [VTTP_NORMAL.FECHA_MANI] <> null then [VTTP_NORMAL.FECHA_MANI]         -- OK (manifiesto SAP normal)
else if [NORMAL.Fecha_mani_manual] <> null then [VTTP_NORMAL.FECHA_MANI]  -- BUG 1
else if [FES_salida_sap] = null then [FES_salida_sap]                     -- BUG 2
else if [FES_Fecha_mani_manual] <> null then [FES_Fecha_mani_manual]      -- OK (manifiesto WMS FES)
else null
```

### Bug 1: Manifiesto manual NORMAL perdido
- **Problema**: cuando existía `NORMAL.Fecha_mani_manual`, devolvía
  `VTTP_NORMAL.FECHA_MANI` (que ya era null al llegar al else).
- **Fix**: devolver `[NORMAL.Fecha_mani_manual]`.

### Bug 2: FES salida SAP perdida (condición invertida)
- **Problema**: `else if [FES_salida_sap] = null then [FES_salida_sap]` era
  condición invertida: si era null devolvía null (inútil). Nunca capturaba la
  salida SAP de FES cuando existía.
- **Fix**: `else if [FES_salida_sap] <> null then [FES_salida_sap]`.

### Bug 3 (evaluado, NO aplicado): cruce por NRO_SAP/PEDIDO
- **Análisis**: `Dim_WMS_Manifiesto_NORMAL` agrupa solo por `ENTREGA_WMS`.
  Se evaluó cruzar por `NRO_SAP_WMS` y `PEDIDO_WMS` para recuperar los 112 con
  entrega sin manifiesto.
- **Decisión**: NO aplicar. La auditoría SQL de PASO_WMS mostró que NRO_SAP y
  PEDIDO del WMS suelen ser números internos WMS (11, 111, 1, 2...) que NO son
  entregas SAP 82xxxxxx ni pedidos NS 116xxxx/117xxxx. Cruzar por ellos genera
  falsos positivos (uniría con números internos que no corresponden al modelo).

## Corrección aplicada
```m
if [VTTP_NORMAL.FECHA_MANI] <> null then [VTTP_NORMAL.FECHA_MANI]
else if [NORMAL.Fecha_mani_manual] <> null then [NORMAL.Fecha_mani_manual]   -- FIX BUG 1
else if [FES_salida_sap] <> null then [FES_salida_sap]                       -- FIX BUG 2
else if [FES_Fecha_mani_manual] <> null then [FES_Fecha_mani_manual]
else null
```

Archivo: `NS.SemanticModel/definition/tables/Pedidos_Normal_VBAK.tmdl` (línea 103).

## Resultado final (verificado en modelo en vivo)
| Métrica | ANTES | DESPUÉS | Δ |
|---|---|---|---|
| Filas | 2.158 | 2.158 | = |
| **Con fecha_salida** | **1.537 (71%)** | **1.876 (87%)** | **+339** |
| Sin fecha_salida | 621 | 282 | -339 |
| FES sin salida | 346 | **10** | **-336** |
| fecha_entrega | 1.988 | 1.988 | = |
| fecha_factura | 2.081 | 2.081 | = |

- Ninguna columna se degradó.
- Los 282 restantes sin manifiesto son legítimos: no existe manifiesto en
  ninguna fuente confiable (ni VTTP SAP, ni WMS por entrega SAP, ni pedido NS).
- 10 FES sin salida: casos reales sin manifiesto en el WMS.

## Respaldo
- Backup creado: `_backup_20260803_004356/` (Pedidos_Normal_VBAK.tmdl,
  expressions.tmdl, model.tmdl, relationships.tmdl).
- Restauración: copiar el .tmdl del backup a la ubicación original.

## Validaciones
- Diff verificado: cambio exacto y mínimo (2 fragmentos en 1 línea).
- Modelo en vivo: cobertura 87% de manifiesto, 0 regresiones.
- Commit: `ae9b020` (fix(modelo): corregir columna condicional Fecha_manifiesto).
