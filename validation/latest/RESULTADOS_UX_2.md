# RESULTADOS UX-2 — SHA 2f6d3c4

## Información de la validación

| Campo | Valor |
|---|---|
| **SHA validado** | `2f6d3c49f86f6fa329a8a120841c285dcd09819c` |
| **Rama** | `work/codex-local` |
| **Fecha** | 2026-07-27 14:24 |
| **Power BI Desktop** | 2.156.951.0 (26.07) |

## Estado de la actualización

| Componente | Estado |
|---|---|
| **TMDL** | ✅ OK |
| **Python.Execute** | ✅ OK |
| **Power Query** | ✅ OK |
| **Tablas cargadas** | ✅ **42** |
| **Relaciones** | ✅ **40** |

## Tablas nuevas verificadas

| Tabla | Columnas | Estado |
|---|---|---|
| Config_Niveles_Intervencion | 6 | ✅ |
| ML_Pedidos_Pendientes_Intervencion | 41 | ✅ |
| Config_Tramos_Intervencion_Diaria | 7 | ✅ |
| ML_Cola_Intervencion_Diaria | 33 | ✅ |

## ML_Cola_Intervencion_Diaria — Distribución

| NIVEL_COLA | Pedidos | Valor CLP |
|---|---:|---:|
| P1 · INTERVENIR | 5 | $49.8M |
| P2 · REVISAR | 5 | $111.5M |
| P3 · PLAN 24H | 10 | $202.0M |
| P4 · MONITOREAR | 17 | $130.3M |
| **Total** | **37** | **$493.6M** |

## Top 10 pedidos

| # | Nivel | Pedido | Cliente | Hito | Foco | DH | Exceso | Score | Valor | Motivo | Acción |
|---|---|---|---|---|---|---:|---:|---:|---:|---|---|
| 1 | P1 | 4190139778 | BERNARDA VELIZ DIAZ. | FACTURACIÓN | FACTURA/DESPACHO | 230 | 225 | 100 | $17.9M | Atraso extremo | Escalar ahora |
| 2 | P1 | 1168064 | IMPORTADORA Y DISTRIBUIDORA KING LT | FACTURACIÓN | FACTURA/DESPACHO | 130 | 125 | 100 | $8.5M | Atraso extremo | Escalar ahora |
| 3 | P1 | 4190140023 | SOC PEDRO GUAJARDO R. Y CIA LTDA | FACTURACIÓN | FACTURA/DESPACHO | 80 | 75 | 96 | $2.9M | Atraso extremo | Escalar ahora |
| 4 | P1 | 4190139472 | IMP.Y EXP. ALISTORE 5 LIMITADA | FACTURACIÓN | FACTURA/DESPACHO | 410 | 405 | 95 | $10.3M | Atraso extremo | Escalar ahora |
| 5 | P1 | 4190139481 | IMPORT. Y DISTRIBUIDORA ECOCRAFT SP | MANIFIESTO FES | FACTURA/DESPACHO | 410 | 405 | 95 | $10.2M | Atraso extremo | Escalar ahora |
| 6 | P2 | 4190139492 | CHRISTIAN REYES Y COMPAÑIA LTDA | FACTURACIÓN | FACTURA/DESPACHO | 400 | 395 | 95 | $7.5M | Atraso extremo | Revisar hoy |
| 7 | P2 | 1167477 | IMPORT. Y EXPORT. DURBAN LIMITADA | MANIFIESTO FES | FACTURA/DESPACHO | 190 | 185 | 95 | $32.0M | Atraso extremo | Revisar hoy |
| 8 | P2 | 4190139897 | DISTRIBUIDORA SUR LTDA | MANIFIESTO FES | FACTURA/DESPACHO | 180 | 175 | 95 | $32.9M | Atraso extremo | Revisar hoy |
| 9 | P2 | 1168130 | SLIME HUUM SPA | FACTURACIÓN | FACTURA/DESPACHO | 80 | 75 | 90 | $27.1M | Atraso extremo | Revisar hoy |
| 10 | P2 | 1168125 | PROVEEDORES INTEGRALES PRISA S.A. | FACTURACIÓN | FACTURA/DESPACHO | 80 | 75 | 90 | $12.0M | Atraso extremo | Revisar hoy |

## Página creada

| Archivo | Estado |
|---|---|
| `NS.Report/definition/pages/f1a2b3c4d5e6f7081920/page.json` | ✅ Creado |
| `NS.Report/definition/pages/pages.json` | ✅ Actualizado |

## Visuales creados

| Visual | Tipo | Fuente |
|---|---|---|
| Título principal | Textbox | — |
| Logo ARTEL | Image | Assets/logo_artel.svg |
| KPI Cola Total | Card | ML_Cola_Intervencion_Diaria |
| KPI Intervenir Hoy | Card | ML_Cola_Intervencion_Diaria (filtro P1) |
| KPI Revisar Hoy | Card | ML_Cola_Intervencion_Diaria (filtro P2) |
| KPI Valor Top 10 | Card | ML_Cola_Intervencion_Diaria (filtro rank<=10) |
| KPI Exceso Promedio | Card | ML_Cola_Intervencion_Diaria |
| Tabla principal | TableEx | ML_Cola_Intervencion_Diaria (17 columnas) |
| Slicer Cola | Slicer | NIVEL_COLA |
| Slicer Foco | Slicer | FOCO_INTERVENCION |

## Errores encontrados

Ninguno.

## Veredicto

**APROBADO** — 42 tablas cargadas, página creada en NS.Report, Top 10 real con datos completos.
