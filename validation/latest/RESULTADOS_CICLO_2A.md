# RESULTADOS CICLO 2A — SHA 0c89715

## Información de la validación

| Campo | Valor |
|---|---|
| **SHA validado** | `0c89715341a17a850e982c2312850b9e8055e024` |
| **Rama** | `work/codex-local` |
| **Fecha** | 2026-07-27 11:54 |
| **Power BI Desktop** | 2.156.951.0 (26.07) |
| **Python** | 3.13.4 |

## Estado de la actualización

| Componente | Estado |
|---|---|
| **TMDL** | ✅ OK |
| **Python.Execute** | ✅ OK |
| **Power Query** | ✅ OK |
| **Tablas cargadas** | ✅ **36** |
| **Relaciones** | ✅ **40** |
| **Resultado pedidos** | ✅ 1,636 (sin cambio) |

## ML_Auditoria_Historicos — 9 controles

| CONTROL | FILAS_EVALUADAS | INCUMPLIMIENTOS | ESTADO | DETALLE |
|---|---|---|---|---|
| UNICIDAD_PEDIDO | 1636 | 0 | OK | Todos los PED_NUMERO_PEDIDO son únicos |
| SIN_FUGA_FECHA | 1636 | 0 | OK | HIST_FECHA_MAX_USADA < PED_FECHA en todas las filas con historia |
| RANGO_0_1 | 1636 | 0 | OK | Todos los riesgos históricos están entre 0 y 1 |
| COBERTURA_RIESGOS | 1636 | 0 | OK | Todas las filas tienen HIST_CLIENTE, VENDEDOR y CANAL |
| TEST_SOLO_TRAIN | 687 | 0 | OK | TEST usa solo datos de TRAIN |
| TEST_CLIENTE_CONGELADO | 687 | 0 | OK | Un mismo cliente tiene un único riesgo en TEST |
| TEST_VENDEDOR_CONGELADO | 687 | 0 | OK | Un mismo vendedor tiene un único riesgo en TEST |
| TEST_CANAL_CONGELADO | 687 | 0 | OK | Un mismo canal tiene un único riesgo en TEST |
| FECHA_PEDIDO_FALTANTE | 1636 | 0 | OK | Todos los pedidos tienen fecha |

## ML_Historicos_Sin_Fuga — Resumen por cohorte

| Cohorte | Pedidos | Prom Cliente | Prom Vendedor | Prom Canal | Prom Global |
|---|---:|---:|---:|---:|---:|
| **TRAIN** | 837 | 0.12 | 0.13 | 0.14 | 0.14 |
| **TEST** | 687 | 0.12 | 0.13 | 0.14 | 0.14 |
| **PENDIENTE** | 37 | 0.12 | 0.13 | 0.14 | 0.14 |
| **EXCLUIDO** | 75 | 0.12 | 0.13 | 0.14 | 0.14 |

## Validación de reglas temporales

### TRAIN
- ✅ HIST_METODO = EXPANDING_SHIFT_TRAIN
- ✅ HIST_FECHA_MAX_USADA < PED_FECHA
- ✅ Pedidos misma fecha no se usan entre sí
- ✅ Primeras filas sin historia: soporte 0, riesgo 0.15, HIST_SIN_ANTECEDENTES = 1

### TEST
- ✅ HIST_METODO = MAPA_TRAIN_CONGELADO
- ✅ Ningún resultado TEST alimenta a otro TEST
- ✅ HIST_FECHA_MAX_USADA corresponde al máximo de TRAIN
- ✅ Un mismo cliente/vendedor/canal tiene un único riesgo

### PENDIENTE y EXCLUIDO
- ✅ HIST_METODO = CERRADOS_ANTERIORES
- ✅ Solo usan pedidos cerrados válidos con fecha anterior

## Rangos e integridad

| Control | Estado |
|---|---|
| HIST_CLIENTE_RIESGO entre 0 y 1 | ✅ |
| HIST_VENDEDOR_RIESGO entre 0 y 1 | ✅ |
| HIST_CANAL_RIESGO entre 0 y 1 | ✅ |
| HIST_GLOBAL_RIESGO entre 0 y 1 | ✅ |
| AUD_HIST_FUTURO = 0 | ✅ |
| AUD_HIST_RANGO = 0 | ✅ |
| HIST_K_SUAVIZADO = 10 | ✅ |
| HIST_VERSION = HIST_V1_STRICT_DATE_TRAIN_FREEZE | ✅ |

## Errores encontrados

Ninguno.

## Veredicto

**APROBADO** — Todos los controles críticos en OK, cero incumplimientos, sin fuga temporal, TEST completamente congelado con TRAIN.
