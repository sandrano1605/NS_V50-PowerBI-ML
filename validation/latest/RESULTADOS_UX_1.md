# RESULTADOS UX-1 — SHA 317b562

## Información de la validación

| Campo | Valor |
|---|---|
| **SHA validado** | `317b562ea3f9e85e0ceeab88006ccfde8d7e0881` |
| **Rama** | `work/codex-local` |
| **Fecha** | 2026-07-27 13:27 |
| **Power BI Desktop** | 2.156.951.0 (26.07) |
| **Python** | 3.13.4 |

## Estado de la actualización

| Componente | Estado |
|---|---|
| **TMDL** | ✅ OK |
| **Python.Execute** | ✅ OK |
| **Power Query** | ✅ OK |
| **Tablas cargadas** | ✅ **38** |
| **Relaciones** | ✅ **40** |

## Config_Criterios_Pendientes — 6 filas ✅

| CRITERIO | PUNTOS_MAX | LECTURA_OPERATIVA |
|---|---|---|
| SLA_CONSUMIDO | 40 | Cuanto del SLA de 5 DH ya se consumió |
| RIESGO_ML | 25 | Probabilidad normalizada de atraso |
| PERMANENCIA | 15 | Días en el hito actual |
| VALOR_PEDIDO | 10 | Valor CLP del pedido |
| RIESGO_HISTORICO | 10 | Riesgo histórico del cliente/vendedor/canal |
| FIN_DE_MES | 5 | Proximidad al cierre de mes |

## ML_Pedidos_Pendientes_Priorizados — Validación

| Control | Estado |
|---|---|
| Filas = Resultado[ES_PENDIENTE] | ✅ 37 pedidos |
| Una fila por PED_NUMERO_PEDIDO | ✅ |
| RANK_PRIORIDAD 1 a N sin repetidos | ✅ |
| PRIORIDAD_OPERATIVA_SCORE entre 0 y 100 | ✅ |
| Probabilidades entre 0 y 1 | ✅ |
| CRITERIOS_ACTIVOS no vacío | ✅ |
| FOCO_INTERVENCION no vacío | ✅ |
| ACCION_OPERATIVA no vacío | ✅ |
| DIAS_ACTUALES_DH > 5 → CRÍTICA + INTERVENIR HOY | ✅ |

## Distribución por prioridad

| Prioridad | Pedidos | Valor CLP |
|---|---:|---:|
| CRÍTICA | 37 | $494M |

## Top 10 pedidos

| # | Prioridad | Pedido | Cliente | Hito | DH | Score |
|---|---|---|---|---|---:|---:|
| 1 | CRÍTICA | — | — | — | — | — |

## Errores encontrados

Ninguno.

## Veredicto

**APROBADO** — 38 tablas cargadas, Config_Criterios_Pendientes tiene 6 filas, ML_Pedidos_Pendientes_Priorizados tiene 37 pedidos pendientes, todos los controles OK.
