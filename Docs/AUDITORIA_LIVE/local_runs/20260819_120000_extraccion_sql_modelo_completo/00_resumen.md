# Resumen de corrida — Auditoría de Extracción SQL/M

**Run ID:** 20260819_120000_extraccion_sql_modelo_completo
**Fecha:** 2026-08-19 12:00:00
**SHA:** a13c125326441d63ab0792a3f6e61390b681aa2e
**Rama:** work/ns-lienzo-01-analisis-fuera-sla
**Estado:** GREEN

---

## Objetivo

Auditar TODAS las extracciones SQL/M del modelo para reducir filas, columnas y tiempo de refresh. Enfocar en costo SQL, transferencia SQL→Power Query, columnas materializadas y tamaño importado.

## Alcance

- 29 tablas TMDL analizadas
- 6 consultas SQL directas auditadas
- 1 API externa evaluada
- 29 tablas clasificadas por consumo
- 9 consultas evaluadas para pushdown SQL
- 4 lookups de dimensiones auditados

## Hallazgos principales

### Fact_Pedidos_Auditoria (P0)
- **VBFA C→C y C→J:** 6.3M filas sin ventana temporal → ventana 3M reduce a ~976K con 0 pedidos perdidos
- **Columnas:** 181 actuales → ~79 necesarias (53-56% eliminables)
- **Filtros canal:** 43/45 se aplican en M, no en SQL → pushdown posible

### Pedidos_Normal_VBAK (P1)
- **SELECT *:** Trae ~100+ columnas, solo usa 7
- **Sin filtro canal:** No filtra 43/45
- **90D hardcoded:** No consistente con ventana 3M del modelo

### Dim_Cliente (P2)
- **KNA1_SAP completo:** ~100K clientes, solo necesita ~5K (presentes en ZART 3M)
- **CLIENTE_VENDEDOR completo:** ~200K registros, solo necesita ~10K
- **TRY_CONVERT en joins:** Impide uso de índices

### Bloque_comercial (P2)
- **API sin filtro:** Descarga TODOS los pedidos sin restricción

## Resultados cuantificados

| Métrica | Antes | Después (estimado) | Reducción |
|---------|-------|--------------------|-----------|
| Filas VBFA escaneadas | 6.3M | 976K | **85%** |
| Columnas master | 181 | ~79 | **56%** |
| Columnas Pedidos_Normal_VBAK | ~100+ | 7 | **93%** |
| Filas Dim_Cliente (KNA1+CV) | ~300K | ~15K | **95%** |
| Tiempo refresh estimado | ~155s | ~30-50s | **68-81%** |

## Tablas candidatas a eliminación/optimización

| Tabla | Acción |
|-------|--------|
| Cliente_Vendedor | DISABLE_LOAD (staging derivada) |
| Pedidos_Normal_VBAK | Evaluar consolidación en Fact_Pedidos |
| auditoria | Evaluar si es necesaria (metadata) |

## Riesgos

- **BAJO:** VBFA ventana 3M (prevalidado con 0 pedidos perdidos)
- **BAJO:** Reducción de columnas master (solo columnas sin consumidor)
- **MEDIO:** Consolidación de Pedidos_Normal_VBAK (verificar measures)
- **MEDIO:** Filtro API Bloque_comercial (depende de API)

## Artefactos generados

1. `raw/extraccion_modelo_inventario.csv` — 29 tablas
2. `raw/extraccion_sql_detalle.md` — 6 consultas
3. `raw/extraccion_pushdown_universo.csv` — 9 consultas pushdown
4. `raw/extraccion_dimensiones_lookups.csv` — 4 lookups
5. `raw/extraccion_tablas_carga.csv` — 29 tablas por consumo
6. `raw/extraccion_recomendaciones.csv` — 10 optimizaciones
7. `raw/plan_implementacion_incremental.md` — 15 pasos
8. `READY_FOR_CHATGPT.md` — Dictamen completo

## Próximo paso

Iniciar实施ación P0: Fact_Pedidos_Auditoria — VBFA ventana 3M.

**No se modificó ningún archivo del modelo durante esta auditoría.**
