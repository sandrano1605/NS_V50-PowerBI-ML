# READY_FOR_CHATGPT — Certificación P0+P1

**Fecha:** 2026-08-19 20:00
**SHA:** fb48f5d26e265da0d8c2f1d0a46a100e1c770b8b
**Rama:** work/ns-lienzo-01-analisis-fuera-sla
**Run:** 20260819_200000_p0_p1_certificacion

---

## Estado del modelo vivo

| Campo | Valor |
|-------|-------|
| Instancia | PBIDesktop (NS) |
| Puerto | 53967 |
| Columnas Fact_Pedidos_Auditoria | 182 (181 + RowNumber) |
| Tablas totales | 30 |
| SemanticErrors | 0 |
| Refresh completado | Si (previo a consulta) |

---

## Regresión funcional — P0+P1

| Métrica | Baseline pre-P0 | Post P0+P1 | Delta | Estado |
|---------|----------------|------------|-------|--------|
| Pedidos | 2,087 | 2,087 | 0 | VERDE |
| FES | 455 | 455 | 0 | VERDE |
| Fuera SLA | 369 | 369 | 0 | VERDE |
| NS Interno | 80.73% | 80.73% | 0 | VERDE |
| Cerrados | 1,915 | 1,915 | 0 | VERDE |
| Cerrados en SLA | 1,546 | 1,546 | 0 | VERDE |
| Líneas | 40,932 | 40,932 | 0 | VERDE |
| Unidades | 3,214,960 | 3,214,960 | 0 | VERDE |
| DH Promedio | 4.604 | 4.604 | 0 | VERDE |
| P90 Interno | 8 | 8 | 0 | VERDE |
| Cobertura Hitos | 100% | 100% | 0 | VERDE |
| Normal Evaluados | 1,915 | 1,915 | 0 | VERDE |
| Pedidos Abiertos | 172 | 172 | 0 | VERDE |

---

## Regresión FES/VBFA

| Métrica | Valor | Estado |
|---------|-------|--------|
| FES con Pedido Posterior | 457 | VERDE |
| FES con Entrega Posterior | 456 | VERDE |
| FES con Manifiesto | 455 | VERDE |
| Pérdidas FES por ventana 3M | 0 | VERDE |

**0 cambios funcionales atribuibles a P0.**

---

## Tres capas de transferencia

```
SQL genera           ~181 columnas (SELECT * de ZART + columnas calculadas)
    ↓
SQL → Power Query    ~181 columnas (sin proyección SQL)
    ↓
PQ_SelectColumns        88 columnas (P1 aplicado en M)
    ↓
Modelo                 88 columnas (requiere refresh)
```

**Estado de cada capa:**

| Capa | Estado | Observación |
|------|--------|-------------|
| SQL genera | PENDIENTE_REFRESH | SELECT * genera master completa |
| SQL → PQ | PENDIENTE_REFRESH | Sin optimización de proyección SQL |
| PQ → SelectColumns | APLICADO | commit 8f26dd9, requiere refresh |
| Modelo | PENDIENTE_REFRESH | 182 col visibles (pre-refresh) |

---

## Dictamen

```
P0_REFRESH_STATUS=GREEN
P0_FUNCTIONAL_REGRESSION=GREEN
P0_FES_EQUIVALENCE=GREEN
P0_LINES_UNITS_EQUIVALENCE=GREEN
P0_PERFORMANCE_SECONDS_PRE=NA
P0_PERFORMANCE_SECONDS_POST=NA
P0_PERFORMANCE_IMPROVEMENT_PCT=NA
P0_CERTIFICATION=GREEN

P1_COLUMN_REDUCTION=GREEN (181→88 en M, requiere refresh para efecto)
P1_SQL_PROJECTION=PENDING (SQL aún genera ~181 columnas)

NEXT_STEP=P1_SQL_PROJECTION
```

---

## Recomendación inmediata

**P1_SQL_PROJECTION**: Reemplazar el SELECT final de la master SQL para traer explícitamente solo las 88 columnas consumidas en vez de `SELECT *`. Esto atacará directamente:

1. **Filas transferidas SQL→PQ** (mismo número de filas, menos ancho)
2. **Tiempo de transferencia** (menos datos en la red)
3. **Tiempo de procesamiento M** (menos columnas a tipar/filtrar)

El paso M `ColumnasFinales` puede mantenerse como safety net, pero el beneficio real de transferencia viene de la proyección SQL.

**No pasar a Pedidos_Normal_VBAK hasta cerrar la optimización de la master en ambas capas.**

---

## Artefactos

- `raw/p0_p1_regresion_metricas.csv` — 16 métricas comparadas
- `raw/capas_transferencia.csv` — 3 capas documentadas
