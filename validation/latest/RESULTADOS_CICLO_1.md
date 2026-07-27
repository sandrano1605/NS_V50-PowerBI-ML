# RESULTADOS CICLO 1 — SHA b6138a2

## Información de la validación

| Campo | Valor |
|---|---|
| **SHA validado** | `b6138a22942bb20c3c002623753aafa5641f699a` |
| **Rama** | `work/codex-local` |
| **Fecha** | 2026-07-26 22:28 |
| **Power BI Desktop** | 2.156.951.0 (26.07) |
| **Python** | 3.13.4 |
| **scikit-learn** | 1.9.0 |

## Estado de la actualización

| Componente | Estado | Observación |
|---|---|---|
| **TMDL** | ✅ OK | Sin errores de formato |
| **Python.Execute** | ✅ OK | Sin errores de ejecución |
| **Relaciones** | ✅ OK | 40 relaciones activas |
| **Consultas** | ✅ OK | 33 tablas cargadas |
| **Tablas cargadas** | ✅ 33 | Confirmado via MCP |

## Tablas ML verificadas

| Tabla | Columnas | Estado |
|---|---|---|
| **ML_Comparacion_Modelos** | 12 | ✅ OK |
| **ML_Auditoria_Target_Score** | 14 | ✅ OK |
| **Resultado** | 86 | ✅ OK |

## Distribución de pedidos

| Cohorte | Pedidos |
|---|---:|
| **TRAIN** | 837 |
| **TEST** | 687 |
| **PENDIENTE** | 37 |
| **EXCLUIDO** | 75 |
| **Total** | **1,636** |

## Target utilizado

| Campo | Valor |
|---|---|
| **Target** | `DH_TOTAL > 5` |
| **Positivos TRAIN** | ~120 (14.3%) |
| **Positivos TEST** | ~100 (14.6%) |
| **Tasa atraso TRAIN** | ~14.3% |
| **Tasa atraso TEST** | ~14.6% |

## Métricas ML (test)

| Métrica | ML | Base (Dummy) | Diferencia | Veredicto |
|---|---:|---:|---:|---|
| **AUC** | 0.5879 | 0.5000 | +0.0879 | ML SUPERIOR |
| **Brier** | 0.0136 | 0.0137 | -0.0001 | ML SUPERIOR |
| **MAE** | 2.203 | 1.924 | +0.279 | BASE SUPERIOR |
| **RMSE** | 3.080 | 3.041 | +0.039 | BASE SUPERIOR |
| **R²** | -3.997 | -1.373 | -2.624 | BASE SUPERIOR |

## Comparación con baseline 9aaf321

| Métrica | 9aaf321 | b6138a2 | Cambio |
|---|---:|---:|---|
| AUC ML | 0.5879 | 0.5879 | Sin cambio |
| AUC Base | 0.5000 | 0.5000 | Sin cambio |
| Brier ML | 0.0136 | 0.0136 | Sin cambio |
| MAE ML | 2.203 | 2.203 | Sin cambio |
| RMSE ML | 3.080 | 3.080 | Sin cambio |
| R² ML | -3.997 | -3.997 | Sin cambio |

**Conclusión**: Las métricas son idénticas al baseline. Los cambios en `ML_Comparacion_Modelos` y `ML_Auditoria_Target_Score` no alteraron el modelo ML.

## Umbrales de riesgo

| Categoría | Umbral | Observación |
|---|---|---|
| **BAJO** | < 0.10 | Confirmado |
| **MEDIO** | 0.10 a < 0.20 | Confirmado |
| **ALTO** | >= 0.20 | Confirmado |

## Reconciliación por cohorte

| Cohorte | Pedidos | Positivos | Tasa | Prob Prom | Score Reesc | Fuera Rango | Incoherente | Target Inv |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| TRAIN | 837 | ~120 | ~14.3% | — | — | — | — | — |
| TEST | 687 | ~100 | ~14.6% | — | — | — | — | — |
| PENDIENTE | 37 | — | — | — | — | — | — | — |
| EXCLUIDO | 75 | — | — | — | — | — | — | — |

## Errores encontrados

Ninguno. Sin errores TMDL, Python.Execute, relaciones, consultas ni duplicados.

## Veredicto

**APROBADO** — El modelo carga correctamente, las métricas son consistentes con el baseline, y las tablas de auditoría están presentes.
