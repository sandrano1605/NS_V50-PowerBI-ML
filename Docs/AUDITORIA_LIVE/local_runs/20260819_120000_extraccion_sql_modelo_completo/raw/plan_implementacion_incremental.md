# Plan de implementación incremental — Optimización de extracción SQL

## Estado

```
EXTRACTION_AUDIT_STATUS=GREEN
MASTER_COLUMN_REDUCTION=READY
MASTER_VBFA_3M=READY
NEXT_HIGHEST_IMPACT_QUERY=Fact_Pedidos_Auditoria (master)
```

## Orden de implementación

### Fase 1: Fact_Pedidos_Auditoria (mayor impacto)

| Paso | Cambio | Capa | Estimación |
|------|--------|------|------------|
| 1.1 | Agregar ventana 3M a VBFA C→C y C→J en SQL | SQL_WHERE | ~6.3M → ~976K filas |
| 1.2 | Refresh + regresión métricas | — | Validar NS, FES, SLA, pedidos |
| 1.3 | Reducir columnas SELECT de 181 a ~79 | SQL_SELECT | ~57% menos datos |
| 1.4 | Refresh + regresión completa | — | Validar todas las tablas hijas |
| 1.5 | Filtrar canales 43/45 en SQL (mover desde M) | SQL_WHERE | ~20-30% menos filas |
| 1.6 | Refresh + validación canales | — | — |

### Fase 2: Consultas complementarias

| Paso | Cambio | Capa | Estimación |
|------|--------|------|------------|
| 2.1 | Pedidos_Normal_VBAK: reducir SELECT * | SQL_SELECT | ~95% menos columnas |
| 2.2 | Refresh + regresión | — | — |
| 2.3 | Evaluar consolidación en Fact_Pedidos | ELIMINAR_TABLA | Posible eliminación completa |
| 2.4 | Refresh + regresión | — | — |

### Fase 3: Lookups y dimensiones

| Paso | Cambio | Capa | Estimación |
|------|--------|------|------------|
| 3.1 | Dim_Cliente: filtrar KNA1 a clientes ZART 3M | SEMI_JOIN | ~95% menos filas |
| 3.2 | Dim_Cliente: filtrar CLIENTE_VENDEDOR a clientes ZART 3M | SEMI_JOIN | ~95% menos filas |
| 3.3 | Refresh + validación lookup | — | — |
| 3.4 | Cliente_Vendedor: DISABLE_LOAD | DISABLE_LOAD | Eliminar carga |
| 3.5 | Refresh | — | — |

### Fase 4: API y optimizaciones menores

| Paso | Cambio | Capa | Estimación |
|------|--------|------|------------|
| 4.1 | Bloque_comercial: filtrar API por universo | API_FILTER | Variable |
| 4.2 | TRY_CONVERT → CONVERT en joins FES | SQL_JOIN | ~10-20% mejora |
| 4.3 | Refresh + regresión final | — | — |

## Métricas de regresión obligatorias

| Métrica | Valor baseline | Después P0 | Después P1 | Después P2 | Después P3+P4 |
|---------|---------------|------------|------------|------------|---------------|
| Pedidos total 43/45 | TBD | TBD | TBD | TBD | TBD |
| Clientes | TBD | TBD | TBD | TBD | TBD |
| FES | TBD | TBD | TBD | TBD | TBD |
| SALDO | TBD | TBD | TBD | TBD | TBD |
| NORMAL | TBD | TBD | TBD | TBD | TBD |
| FES+SALDO | TBD | TBD | TBD | TBD | TBD |
| Cerrados | TBD | TBD | TBD | TBD | TBD |
| Fuera SLA | TBD | TBD | TBD | TBD | TBD |
| NS | TBD | TBD | TBD | TBD | TBD |
| Líneas | TBD | TBD | TBD | TBD | TBD |
| Unidades | TBD | TBD | TBD | TBD | TBD |
| Cobertura hitos | TBD | TBD | TBD | TBD | TBD |
| SemanticErrors | 0 | 0 | 0 | 0 | 0 |

## Reglas de validación

- Cada paso requiere: refresh + comparación contra baseline.
- Si alguna métrica cambia sin explicación documentada → ROJO → revertir.
- No combinar cambios funcionales con cambios de performance en un mismo paso.
- Cada cambio se publica como commit separado.
- Si un paso produce ROJO, se documenta pero NO se revierte automáticamente; se espera decisión del usuario.

## Tiempo estimado total

- Fase 1: 30 min (3 cambios + 3 refreshes)
- Fase 2: 20 min (2 cambios + 2 refreshes)
- Fase 3: 20 min (3 cambios + 2 refreshes)
- Fase 4: 15 min (2 cambios + 1 refresh)
- **Total estimado: ~85 min de trabajo interactivo**
