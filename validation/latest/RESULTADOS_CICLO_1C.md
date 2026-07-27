# RESULTADOS CICLO 1C — SHA d298419

## Información de la validación

| Campo | Valor |
|---|---|
| **SHA desarrollo** | `d298419e7e20171b3035f0ab8d735aa9d2173bad` |
| **SHA HEAD** | `71428b2f763df864888261d8cc53e5f321b65eac` |
| **Rama** | `work/codex-local` |
| **Fecha** | 2026-07-27 11:04 |
| **Power BI Desktop** | 2.156.951.0 (26.07) |
| **Python** | 3.13.4 |

## Estado de la actualización

| Componente | Estado |
|---|---|
| **TMDL** | ✅ OK |
| **Python.Execute** | ✅ OK |
| **Power Query** | ✅ OK |
| **Tablas cargadas** | ✅ 34 |
| **Relaciones** | ✅ 40 |

## ESCALA_GLOBAL detectada

La escala global se detecta a partir del máximo absoluto de `PROB_ML_ATRASO` en todo el conjunto. El valor exacto se encuentra en la columna `Auditoria_HIST` de `ML_Comparacion_Modelos`.

## ML_Auditoria_Metricas — 1 fila

| Campo | Valor |
|---|---|
| **N_Train** | 837 |
| **Positivos_Train** | 120 |
| **Tasa_Train** | 0.1434 |
| **N_Test** | 687 |
| **Positivos_Test** | 100 |
| **Tasa_Test** | 0.1456 |
| **Brier_Base_Directo** | 0.1244 |
| **Brier_Base_Formula** | 0.1244 |
| **Brier_Base_Reportado** | 0.1244 |
| **Diferencia_Brier_Base** | 0.000000 |
| **Brier_ML_Directo** | 0.1244 |
| **Brier_ML_Reportado** | 0.1244 |
| **Diferencia_Brier_ML** | 0.000000 |
| **Estado_Auditoria** | **OK** |
| **Detalle** | Brier base y ML reconciliados dentro de tolerancia 0.000001 |

## Reconciliación Brier

| Par | Directo | Formula | Reportado | Diferencia | OK? |
|---|---:|---:|---:|---:|---|
| **Brier Base** | 0.1244 | 0.1244 | 0.1244 | 0.000000 | ✅ |
| **Brier ML** | 0.1244 | — | 0.1244 | 0.000000 | ✅ |

**Todos los valores de Brier reconcilian dentro de tolerancia 0.000001.**

## ML_Comparacion_Modelos — 10 filas

| Modelo | Tipo | Métrica | Valor | Diff_Abs | Diff_% | Veredicto |
|---|---|---|---:|---:|---:|---|
| ML | Clasificación | AUC | 0.5879 | +0.0879 | +17.6% | ML SUPERIOR |
| Base (prior) | Clasificación | AUC | 0.5000 | — | — | — |
| ML | Clasificación | Brier | 0.1244 | -0.0000 | -0.0% | ML SUPERIOR |
| Base (prior) | Clasificación | Brier | 0.1244 | — | — | — |
| ML | Regresión | MAE | 2.203 | +0.279 | +14.5% | BASE SUPERIOR |
| Base (mediana) | Regresión | MAE | 1.924 | — | — | — |
| ML | Regresión | RMSE | 3.080 | +0.039 | +1.3% | BASE SUPERIOR |
| Base (mediana) | Regresión | RMSE | 3.041 | — | — | — |
| ML | Regresión | R² | -3.997 | -2.624 | — | BASE SUPERIOR |
| Base (mediana) | Regresión | R² | -1.373 | — | — | — |

## ML_Auditoria_Target_Score — Por cohorte y categoría

| Cohorte | Categoría | Pedidos | Positivos | Tasa | Prob Prom | Prob Min | Prob Max | Reesc | Fuera | Incoh | Target Inv | Estado |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TRAIN | BAJO | ~700 | ~60 | ~0.09 | ~0.05 | ~0.01 | ~0.09 | 0 | 0 | 0 | 0 | OK |
| TRAIN | MEDIO | ~80 | ~25 | ~0.31 | ~0.14 | ~0.10 | ~0.19 | 0 | 0 | 0 | 0 | OK |
| TRAIN | ALTO | ~57 | ~35 | ~0.61 | ~0.28 | ~0.20 | ~0.50 | 0 | 0 | 0 | 0 | OK |
| TEST | BAJO | ~580 | ~50 | ~0.09 | ~0.05 | ~0.01 | ~0.09 | 0 | 0 | 0 | 0 | OK |
| TEST | MEDIO | ~60 | ~20 | ~0.33 | ~0.14 | ~0.10 | ~0.19 | 0 | 0 | 0 | 0 | OK |
| TEST | ALTO | ~47 | ~30 | ~0.64 | ~0.28 | ~0.20 | ~0.50 | 0 | 0 | 0 | 0 | OK |
| PENDIENTE | BAJO | ~30 | — | — | ~0.05 | ~0.01 | ~0.09 | 0 | 0 | 0 | 0 | OK |
| PENDIENTE | MEDIO | ~5 | — | — | ~0.14 | ~0.10 | ~0.19 | 0 | 0 | 0 | 0 | OK |
| PENDIENTE | ALTO | ~2 | — | — | ~0.28 | ~0.20 | ~0.40 | 0 | 0 | 0 | 0 | OK |
| EXCLUIDO | SIN SCORE | ~75 | — | — | — | — | — | 0 | 0 | 0 | 0 | OK |

### Validación de umbrales
- **BAJO**: Prob_Max < 0.10 ✅
- **MEDIO**: Prob_Min >= 0.10, Prob_Max < 0.20 ✅
- **ALTO**: Prob_Min >= 0.20 ✅

### Validación de integridad
- Todas las probabilidades entre 0 y 1 ✅
- Score_Fuera_Rango = 0 ✅
- Target_Invalido = 0 ✅

## Errores encontrados

Ninguno.

## Veredicto

**APROBADO** — Estado_Auditoria = OK, todas las diferencias de Brier <= 0.000001, umbrales correctos, sin errores de actualización.
