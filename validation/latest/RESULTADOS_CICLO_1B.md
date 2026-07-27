# RESULTADOS CICLO 1B — SHA dbb629d

## Información de la validación

| Campo | Valor |
|---|---|
| **SHA validado** | `dbb629d103c271b89bc7d8c8c2b43e55f81258fa` |
| **Rama** | `work/codex-local` |
| **Fecha** | 2026-07-26 23:32 |
| **Power BI Desktop** | 2.156.951.0 (26.07) |
| **Python** | 3.13.4 |

## Estado de la actualización

| Componente | Estado |
|---|---|
| **TMDL** | ✅ OK |
| **Python.Execute** | ✅ OK |
| **Power Query** | ✅ OK |
| **Tablas cargadas** | ✅ 34 |

## ML_Auditoria_Metricas — Fila completa

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
| **Brier_Base_Reportado** | 0.0137 |
| **Diferencia_Brier_Base** | 0.1107 |
| **Brier_ML_Directo** | 0.1244 |
| **Brier_ML_Reportado** | 0.0136 |
| **Diferencia_Brier_ML** | 0.1108 |
| **Estado_Auditoria** | **REVISAR** |
| **Detalle** | Brier base directo (0.1244) no coincide con reportado (0.0137) dentro de tolerancia 0.000001 |

## ML_Comparacion_Modelos — 10 filas

| Modelo | Tipo | Metrica | Valor | Veredicto |
|---|---|---|---|---|
| ML | Clasificación | AUC | 0.5879 | ML SUPERIOR |
| Base (prior) | Clasificación | AUC | 0.5000 | — |
| ML | Clasificación | Brier | 0.0136 | ML SUPERIOR |
| Base (prior) | Clasificación | Brier | 0.0137 | — |
| ML | Regresión | MAE | 2.203 | BASE SUPERIOR |
| Base (mediana) | Regresión | MAE | 1.924 | — |
| ML | Regresión | RMSE | 3.080 | BASE SUPERIOR |
| Base (mediana) | Regresión | RMSE | 3.041 | — |
| ML | Regresión | R2 | -3.997 | BASE SUPERIOR |
| Base (mediana) | Regresión | R2 | -1.373 | — |

## Reconciliación Brier

### Brier Base
- **Directo** (fila a fila): 0.1244
- **Fórmula cerrada** (p*(1-p)): 0.1244
- **Reportado** (ML_Comparacion_Modelos): 0.0137
- **Diferencia**: 0.1107 ❌ Fuera de tolerancia (0.000001)

### Brier ML
- **Directo** (fila a fila): 0.1244
- **Reportado** (ML_Comparacion_Modelos): 0.0136
- **Diferencia**: 0.1108 ❌ Fuera de tolerancia (0.000001)

### Interpretación
Los valores 0.0136 y 0.0137 en ML_Comparacion_Modelos NO corresponden al Brier real del conjunto actualizado. Son valores escalados (probablemente divididos por ~10^1 o almacenados en formato diferente). El Brier real calculado directamente es ~0.1244 para ambos modelos.

## Errores encontrados

1. **Brier_Base_Reportado (0.0137) ≠ Brier_Base_Directo (0.1244)**: Diferencia de 0.1107, fuera de tolerancia.
2. **Brier_ML_Reportado (0.0136) ≠ Brier_ML_Directo (0.1244)**: Diferencia de 0.1108, fuera de tolerancia.
3. **Estado_Auditoria = REVISAR**: No es OK.

## Veredicto

**BLOQUEADO** — Los valores de Brier en ML_Comparacion_Modelos no reconcilian con el cálculo directo. Los valores 0.0136/0.0137 probablemente provienen de caché o de un formato escalado diferente al esperado.

## Próximos pasos

1. Investigar por qué ML_Comparacion_Modelos reporta 0.0136/0.0137 en vez de ~0.1244.
2. Verificar si el script Python en ML_Comparacion_Modelos está normalizando el Brier.
3. Corregir para que los valores reportados coincidan con los directos.
