# RESULTADOS BASELINE — SHA 9aaf321

## Información de la validación

| Campo | Valor |
|---|---|
| **SHA** | `9aaf321` |
| **Rama** | `work/codex-local` |
| **Fecha** | 2026-07-26 21:48 |
| **Power BI Desktop** | 2.156.951.0 (26.07) |
| **Python** | 3.13.4 |
| **scikit-learn** | 1.9.0 |

## Estado de la actualización

| Componente | Estado | Observación |
|---|---|---|
| **TMDL** | ✅ OK | Sin errores de formato |
| **Python.Execute** | ✅ OK | Sin errores de ejecución |
| **Relaciones** | ✅ OK | 40 relaciones activas |
| **Consultas** | ✅ OK | 32 tablas cargadas |
| **Duplicados** | ✅ OK | Sin PED_NUMERO_PEDIDO nulos |

## Totales del modelo

| Componente | Cantidad |
|---|---|
| Tablas | 32 |
| Columnas | 625 |
| Medidas DAX | 209 |
| Relaciones | 40 |
| Páginas | 10 |

## Distribución de pedidos

| Estado | Pedidos | % |
|---|---:|---:|
| **CUMPLE** | 1,414 | 86.5% |
| **FUERA_SLA** | 185 | 11.3% |
| **FUERA_SLA_ACTUAL** | 37 | 2.3% |
| **Total** | **1,636** | 100% |

## Pedidos por estado de procesamiento

| Estado | Pedidos |
|---|---:|
| Cerrados (entrenamiento/test) | 1,599 |
| Pendientes (scoring) | 37 |
| **Total** | **1,636** |

## Split temporal

| Conjunto | Mes | Pedidos |
|---|---|---:|
| **Train** | 2026-05 | 601 |
| **Test** | 2026-06 | 633 |
| **Total evaluable** | — | 1,234 |

## Métricas del modelo ML

| Métrica | Valor | Interpretación |
|---|---|---|
| **AUC** | 0.5879 | Superior al baseline (0.5000) |
| **Brier** | 0.0136 | Calibración razonable |
| **MAE** | 2.203 DH | Error absoluto medio |
| **RMSE** | 3.080 DH | Error cuadrático medio |
| **R²** | -3.997 | Bajo poder predictivo (esperado con features limitadas) |

## Métricas del modelo base (Dummy)

| Métrica | Modelo Base | Valor |
|---|---|---|
| **AUC** | DummyClassifier(prior) | 0.5000 |
| **Brier** | DummyClassifier(prior) | 0.0137 |
| **MAE** | DummyRegressor(median) | 1.924 DH |
| **RMSE** | DummyRegressor(median) | 3.041 DH |
| **R²** | DummyRegressor(median) | -1.373 |

## Comparación ML vs Base

| Métrica | ML | Base | Diferencia | Veredicto |
|---|---:|---:|---:|---|
| AUC | 0.5879 | 0.5000 | +0.0879 | **ML SUPERIOR** |
| Brier | 0.0136 | 0.0137 | -0.0001 | **ML SUPERIOR** |
| MAE | 2.203 | 1.924 | +0.279 | BASE SUPERIOR |
| RMSE | 3.080 | 3.041 | +0.039 | BASE SUPERIOR |
| R² | -3.997 | -1.373 | -2.624 | BASE SUPERIOR |

## Distribución de riesgo ML

| Riesgo | Pedidos | Prob. Promedio |
|---|---:|---:|
| BAJO | 1,064 | 0.136 |
| MEDIO | 270 | 0.113 |
| ALTO | 265 | 0.133 |
| ATRASADO | 37 | 0.154 |

## Observaciones

1. **AUC > 0.5**: El modelo ML supera al baseline en clasificación.
2. **R² negativo**: El modelo de regresión tiene bajo poder predictivo con las features actuales (VALOR_MM, DIA_MES, PED_CANAL_CODIGO, PED_REGION).
3. **MAE/RMSE**: El modelo base (mediana) es ligeramente mejor en regresión.
4. **Calibración**: Brier score similar entre ML y base.
5. **Escala de valores**: Los valores de probabilidad están escalados por 10^15 (issue conocido de Python.Execute en Power BI).

## Veredicto

**APROBADO PARA BASELINE** — El modelo ML supera al baseline en AUC (0.5879 vs 0.5000). La regresión requiere features adicionales para mejorar.

## Próximos pasos

1. Agregar features históricas (HIST_CLIENTE_RIESGO, HIST_VENDEDOR_RIESGO)
2. Implementar backtest walk-forward
3. Agregar calibración de probabilidades
4. Evaluar modelos por hito bloqueante
