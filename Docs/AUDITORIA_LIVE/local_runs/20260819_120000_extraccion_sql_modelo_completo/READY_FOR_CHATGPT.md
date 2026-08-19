# READY_FOR_CHATGPT — Auditoría de Extracción SQL/M

**Fecha:** 2026-08-19
**SHA:** a13c125326441d63ab0792a3f6e61390b681aa2e
**Rama:** work/ns-lienzo-01-analisis-fuera-sla
**Run:** 20260819_120000_extraccion_sql_modelo_completo

---

## 1. ¿Cuáles son todas las consultas que extraen datos directamente de SQL?

| # | Tabla modelo | Tipo | Tablas SAP referenciadas | Servidor |
|---|-------------|------|--------------------------|----------|
| 1 | **Fact_Pedidos_Auditoria** (master) | SQL_DIRECTA | ZART_TRACK_DATA_SAP, VBFA_SAP, VTTP_SAP | 128.1.3.21 / DMF_VTA_PRD |
| 2 | **Fact_Pedidos_Auditoria** (VBAK append) | SQL_DIRECTA | VBAK_SAP, KNA1_SAP | 128.1.3.21 / DMF_VTA_PRD |
| 3 | **Pedidos_Normal_VBAK** | SQL_DIRECTA | VBAK_SAP | 128.1.3.21 / DMF_VTA_PRD |
| 4 | **Dim_Cliente** (lookup) | SQL_DIRECTA | KNA1_SAP, CLIENTE_VENDEDOR, VENDEDOR | 128.1.3.21 / DMF_VTA_PRD |
| 5 | **Lineas_y_unidades_por_pedidos** | SQL_DIRECTA | VBAP_SAP, ZART_TRACK_DATA_SAP | 128.1.3.21 / DMF_VTA_PRD |
| 6 | **Bloque_comercial** | API_EXTERNA | API: apis.nacional.cl (REST) | Externo |

---

## 2. ¿Cuál es el TOP de consultas más costosas por filas/tiempo?

| Rank | Tabla | Filas fuente | Filas retornadas | Tiempo est. | Problema principal |
|------|-------|-------------|-----------------|------------|-------------------|
| **1** | Fact_Pedidos_Auditoria (VBFA C→C) | ~6.3M | ~976K (con 3M) | ~40-60s | Sin ventana temporal |
| **2** | Fact_Pedidos_Auditoria (VBFA C→J) | ~6.3M | ~976K (con 3M) | ~40-60s | Sin ventana temporal |
| **3** | Fact_Pedidos_Auditoria (ZART master) | ~2M | ~2M | ~30-40s | SELECT 181 columnas |
| **4** | Pedidos_Normal_VBAK | ~500K | ~500K | ~15s | SELECT * (~100+ cols) |
| **5** | Dim_Cliente (KNA1+CV+V) | ~300K | ~100K | ~5s | Maestro completo sin filtro |
| **6** | Bloque_comercial (API) | ALL | ALL | Variable | Sin filtro por universo |

---

## 3. ¿Qué tablas/consultas traen columnas que nadie consume?

| Tabla | Columnas actuales | Columnas consumidas | Eliminables | % Reducción |
|-------|------------------|--------------------|-----------:|------------|
| **Fact_Pedidos_Auditoria** | 181 | ~79-85 | ~96-102 | ~53-56% |
| **Pedidos_Normal_VBAK** | ~100+ (SELECT *) | 7 | ~93+ | ~93% |
| **Bloque_comercial** | 4 | 4 | 0 | 0% (ya mínimo) |
| **Dim_Cliente** | 6 | 6 | 0 | 0% (ya mínimo) |

---

## 4. ¿Qué consultas pueden limitarse a canales 43/45?

| Tabla | Filtro canal actual | Puede pushdown SQL | Observación |
|-------|--------------------|--------------------|-------------|
| Fact_Pedidos_Auditoria (master) | En M (post-carga) | **SI** | Mover a WHERE en SQL |
| Fact_Pedidos_Auditoria (VBAK append) | En M (post-carga) | **SI** | Mover a WHERE en SQL |
| Pedidos_Normal_VBAK | **NO tiene filtro** | **SI** | Agregar WHERE VWEG IN (43,45) |
| Dim_Cliente (lookup) | No aplica (deriva de master) | Hereda de master | Ya filtrado |
| Lineas_y_unidades_por_pedidos | No tiene filtro de canal | **Evaluar** | Puede necesitar filtro |
| Bloque_comercial | No tiene filtro de canal | **NO** | API no soporta filtros SQL |

---

## 5. ¿Cuáles pueden limitarse a 3M?

| Tabla | Ventana actual | Puede limitar a 3M | Prevalidado |
|-------|---------------|-------------------|-------------|
| Fact_Pedidos_Auditoria (ZART) | 3M (ya tiene) | Ya tiene | GREEN |
| Fact_Pedidos_Auditoria (VBFA C→C) | **SIN FILTRO** | **SI** | GREEN (0 pedidos perdidos) |
| Fact_Pedidos_Auditoria (VBFA C→J) | **SIN FILTRO** | **SI** | GREEN (0 pedidos perdidos) |
| Fact_Pedidos_Auditoria (VBAK append) | 3M (ya tiene) | Ya tiene | GREEN |
| Pedidos_Normal_VBAK | 90D | SI (consistenciar) | PENDIENTE |
| Dim_Cliente (KNA1) | Sin filtro | SI (filtrar a clientes 3M) | PENDIENTE |
| Dim_Cliente (CV+V) | Sin filtro | SI (filtrar a clientes 3M) | PENDIENTE |
| Lineas_y_unidades_por_pedidos | 3M (ya tiene) | Ya tiene | GREEN |

---

## 6. ¿Cuáles pueden usar semi-join al universo ZART?

| Tabla | Semi-join aplicable | Patrón | Estado |
|-------|--------------------|--------|----|
| Fact_Pedidos_Auditoria (VBFA C→C) | SI | `WHERE VBELV IN (SELECT ZVBELN_PED FROM ZART_TRACK_DATA_SAP WHERE ZERDAT_PED >= -3M)` | GREEN (prevalidado) |
| Fact_Pedidos_Auditoria (VBFA C→J) | SI | `WHERE VBELV IN (SELECT ZVBELN_PED FROM ZART_TRACK_DATA_SAP WHERE ZERDAT_PED >= -3M)` | GREEN (prevalidado) |
| Dim_Cliente (KNA1) | SI | `WHERE KUNNR IN (SELECT ZKUNNR FROM ZART_TRACK_DATA_SAP WHERE ZERDAT_PED >= -3M)` | PENDIENTE |
| Dim_Cliente (CV+V) | SI | `WHERE VCLT_SUCURSAL IN (SELECT ZKUNNR FROM ZART_TRACK_DATA_SAP WHERE ZERDAT_PED >= -3M)` | PENDIENTE |
| Pedidos_Normal_VBAK | SI | `WHERE VBELN IN (SELECT ZVBELN_PED FROM ZART_TRACK_DATA_SAP WHERE ZERDAT_PED >= -3M)` | PENDIENTE |
| Bloque_comercial | SI (en M) | `Table.SelectRows(..., each List.Contains(universo, [Pedido]))` | PENDIENTE |

---

## 7. ¿Qué maestros pueden limitarse a clientes/pedidos presentes?

| Maestro | Filas actuales | Filas con filtro 3M | Reducción | Aplica |
|---------|---------------|--------------------|-----------|----|
| KNA1_SAP | ~100K | ~5K | ~95% | SI |
| CLIENTE_VENDEDOR | ~200K | ~10K | ~95% | SI |
| VENDEDOR | ~5K | ~2K | ~60% | SI |
| VBAK_SAP (completo) | ~2M | ~1.5M | ~25% | SI (ya parcialmente filtrado) |
| VBFA_SAP (completo) | ~6.3M | ~976K | ~85% | SI (prevalidado) |

---

## 8. ¿Qué tablas cargadas no tienen consumo activo?

| Tabla | Clasificación | Puede eliminarse |
|-------|--------------|-----------------|
| **Cliente_Vendedor** | SOLO_STAGING_M | SI (DISABLE_LOAD) - derivada de Dim_Cliente |
| **auditoria** | SOLO_STAGING_M | Evaluar - metadata de esquema |
| **Pedidos_Normal_VBAK** | DUPLICADA (parcial) | Evaluar - puede consolidarse en Fact_Pedidos |

---

## 9. ¿Cuánto se puede reducir filas y columnas por consulta?

| Tabla | Filas antes | Filas después | Columnas antes | Columnas después | Reducción total |
|-------|------------|--------------|---------------|-----------------|----------------|
| Fact_Pedidos_Auditoria (VBFA) | 6.3M | ~976K | 181 | 181 | ~85% filas |
| Fact_Pedidos_Auditoria (master) | ~2M | ~1.5M (con 43/45) | 181 | ~79 | ~25% filas + ~56% columnas |
| Pedidos_Normal_VBAK | ~500K | ~200K | ~100+ | 7 | ~60% filas + ~93% columnas |
| Dim_Cliente | ~300K | ~15K | 6 | 6 | ~95% filas |
| **TOTAL ESTIMADO** | — | — | — | — | **~70-80% reducción** |

---

## 10. ¿Cuál es el orden exacto recomendado de implementación?

```
Paso 1: Fact_Pedidos_Auditoria — VBFA ventana 3M        → P0, riesgo BAJO
Paso 2: Refresh + regresión
Paso 3: Fact_Pedidos_Auditoria — Reducir columnas 181→79 → P1, riesgo BAJO
Paso 4: Refresh + regresión
Paso 5: Pedidos_Normal_VBAK — Reducir SELECT *           → P1, riesgo BAJO
Paso 6: Refresh + regresión
Paso 7: Fact_Pedidos_Auditoria — Filtros 43/45 en SQL    → P2, riesgo BAJO
Paso 8: Refresh + validación
Paso 9: Dim_Cliente — Semi-join a ZART 3M                → P2, riesgo BAJO
Paso 10: Refresh + validación
Paso 11: Evaluar eliminación de Pedidos_Normal_VBAK      → P3, riesgo MEDIO
Paso 12: Refresh + regresión completa
Paso 13: Cliente_Vendedor — DISABLE_LOAD                 → P3, riesgo BAJO
Paso 14: Bloque_comercial — Filtro universo              → P4, riesgo MEDIO
Paso 15: Refresh + regresión final
```

---

## Dictamen final

```
EXTRACTION_AUDIT_STATUS=GREEN
MASTER_COLUMN_REDUCTION=READY
MASTER_VBFA_3M=READY
NEXT_HIGHEST_IMPACT_QUERY=Fact_Pedidos_Auditoria (master VBFA ventana 3M)
```

**Artefactos generados:**
- `raw/extraccion_modelo_inventario.csv` — 29 tablas clasificadas
- `raw/extraccion_sql_detalle.md` — 6 consultas SQL auditadas
- `raw/extraccion_pushdown_universo.csv` — 9 consultas evaluadas para pushdown
- `raw/extraccion_dimensiones_lookups.csv` — 4 lookups auditados
- `raw/extraccion_tablas_carga.csv` — 29 tablas clasificadas por consumo
- `raw/extraccion_recomendaciones.csv` — 10 optimizaciones priorizadas
- `raw/plan_implementacion_incremental.md` — Plan de 15 pasos
