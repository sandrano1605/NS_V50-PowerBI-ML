# Preflight — Fact_Pedidos_Auditoria (optimización)

RUN_ID: 20260818_155007_fact_pedidos_auditoria_optimizacion_preflight_946fb29
SHA: 946fb29db50b3fbf5caa01c38fb0f6d2643af16e
Rol: READ_ONLY_FUNCTIONAL_EVIDENCE_WRITER — no se aplicaron cambios.

## Dictamen

| Acción | Dictamen |
|---|---|
| Eliminar columnas AUD_* no consumidas | 🟢 Viable |
| Mantener ~68 columnas requeridas | 🔴 Obligatorio |
| Filtro temporal VBFA (P0) | 🟢 **EQUIVALENCIA DEMOSTRADA** (ver P0) |
| Cambiar joins/llaves (P2) | 🟡 Validar cardinalidad (ver P2) |
| Modificar visuales | ❌ No necesario |

---

# P0 — VBFA (filtro temporal de 3 meses)

## Los joins VBFA/VTTP en Fact_Pedidos_Auditoria

| # | Línea | Objeto | Condición | Columna fecha | Uso |
|---|---|---|---|---|---|
| 1 | 1670 | VBFA_SAP P1 | VBTYP_V='C' AND VBTYP_N='C' | ERDAT | Pedido posterior FES |
| 2 | 1698 | VBFA_SAP P2 (INNER JOIN) | VBTYP_N='J' | ERDAT | Entrega posterior |
| 3 | 4366 | VBFA_SAP F (EXISTS) | VBTYP_V='C' AND VBTYP_N='C' | (sin fecha, solo flag) | ES_FES |
| 4 | 1726 | VTTP_SAP (INNER JOIN) | VBELN match | ERDAT | Manifiesto |

## Filas procesadas (medición SQL real)

| Escenario | Filas | Tiempo |
|---|---|---|
| VBFA_SAP total | 34.925.607 | 8,42s |
| VBFA C→C | 78.575 | 0,03s |
| **VBFA C→J (el pesado)** | **6.339.038** | **4,47s** |
| VBFA C→C + ERDAT≥3m | 10.107 | 0,21s |
| VBFA C→J + ERDAT≥3m | 976.560 | 1,00s |

**El join #2 (C→J) es el cuello: 6,3M filas → 976K con filtro de 3 meses (6,5x).**

## Equivalencia de resultados (el punto crítico)

Universo ZART 3M = 2.083 pedidos.

| Join VBFA | Pedidos universo con ERDAT≥3m | Pedidos universo con ERDAT<3m |
|---|---|---|
| C→C (pedido posterior) | 477 | **0** |
| C→J (entrega posterior) | 2.021 | **0** |

**Conclusión P0: `ERDAT >= DATEADD(MONTH,-3,...)` NO pierde ningún registro.**
Todos los pedidos FES/entregas/manifiestos del universo actual tienen ERDAT
dentro de los últimos 3 meses. La ventana coincide con Dim_Periodo_3M.

Rango ERDAT en VBFA: 2025-08-01 a 2026-08-04 (~1 año), pero el universo del
reporte solo usa los últimos 3 meses.

## Comparación de negocio ANTES vs PROPUESTO

La equivalencia se demostró a nivel de **pedidos con enlaces FES** (0 pérdida).
La comparación de métricas agregadas (Pedidos, Líneas, Unidades, NS, etc.) queda
pendiente de ejecutarse TRAS aplicar P0 y refrescar, como ordena el protocolo
(no mezclar optimizaciones).

---

# P1 — Columnas (matriz conservar/eliminar)

Consolidado del mapeo previo (fact_pedidos_auditoria_mapeo_columnas.md):

- **181 columnas totales**
- **~68 conservar** (identificación, banderas, hitos, DH_*, auditoría mínima)
- **~113 eliminar** — cada una verificada: visual=NO, medida=NO, tabla hija=NO

### Bloques de columnas eliminables

1. Auditoría granular (~90): AUD_TIENE_*, AUD_INC_*, AUD_HORA_00_*, AUD_FES_*,
   AUD_NO_FES_*, AUD_SALDO_*, AUD_CRITICAS/ADVERTENCIAS/FALTANTES_*, AUD_CANTIDAD_*,
   AUD_HITOS_*, AUD_ALERTAS_*, AUD_OBS_*.
2. Intermedias no consumidas (~20): HRS_COMERCIAL_PDA_SAC, DIAS_EQ_COMERCIAL_9_5H,
   FES_FECHA_CIERRE_OPERATIVO_100, FAC_FECHA_OPERATIVA_AJUSTADA, PARAM_FECHA_DESDE/HASTA,
   FECHA_CARGA_MASTER, REGLA_CLASIFICACION_FES/SALDO, TSTTO_*, CED_*, GER_*.

### Consumidores de las 68 conservadas

| Tabla hija | Columnas |
|---|---|
| Fact_Tracking | 25 |
| Fact_Hitos_Operacionales | 32 |
| Fact_Pedidos | 54 |
| Fact_Tiempos_Hitos | 39 |
| Dim_Cliente | 3 |
| Medidas DAX | 8 |

---

# P2 — Joins con TRY_CONVERT/CONVERT(BIGINT)

## Conversiones encontradas

1. `TRY_CONVERT(BIGINT, P1.VBELV)` — VBFA C→C (línea 1661, 1673)
2. `TRY_CONVERT(BIGINT, P2.VBELV)` — VBFA C→J join (línea 1699)
3. `TRY_CONVERT(BIGINT, VTTP.VBELN)` — VTTP join (línea 1727)
4. `TRY_CONVERT(BIGINT, F.VBELV)` — VBFA EXISTS (línea 4369)
5. `TRY_CONVERT(BIGINT, K.KUNNR)` — KNA1 join cliente (línea 4373)

## Cardinalidad y NULLs (medición real)

| Columna | NULL/blank | No convertible | Distintos |
|---|---|---|---|
| VBFA.VBELV | 0 | **0** | 3.769.754 |
| VBFA.VBELN | — | — | — |
| VTTP.VBELN | — | **0** | 724.689 |
| VBAK.KUNNR | — | **7.824.316** ⚠️ | — |
| KNA1.KUNNR | — | 648 | — |

### Hallazgo P2

- **VBFA.VBELV y VTTP.VBELN son 100% convertibles a BIGINT** (0 no-convertibles).
  El `TRY_CONVERT(BIGINT, ...)` no pierde registros en VBFA/VTTP.
- **Duplicados**: VBFA C→C tiene 4.300 grupos VBELV+VBELN duplicados — el
  `SELECT DISTINCT` actual los deduplica correctamente.
- **⚠️ VBAK.KUNNR tiene 7.824.316 no-convertibles** (formato alfanumérico como
  'AGU2', 'ALC1', '|17356'). El join de cliente (línea 4373) hace
  `TRY_CONVERT(BIGINT, K.KUNNR) = TRY_CONVERT(BIGINT, V.KUNNR)`, que **no matchea**
  para clientes con KUNNR alfanumérico. Este join solo trae `PED_REGION`, y el
  cliente real se resuelve por `Dim_Cliente` (join por PED_CODIGO_CLIENTE).
  → No es crítico para el negocio, pero es un defecto latente a documentar.

---

## Orden de ejecución propuesto (NO aplicado)

1. Evidencia formal (este paquete) ✅
2. Preflight P0 ✅ (equivalencia demostrada)
3. Aplicar P0 (filtro VBFA 3 meses) → refresh → comparación de negocio
4. P1 (eliminar ~113 columnas) → refresh → regresión
5. P2 (normalizar joins) → refresh → regresión

No mezclar las 3 optimizaciones en un solo cambio.

## No resuelto

- Comparación de métricas agregadas (Pedidos/Líneas/Unidades/NS/FES/etc.)
  ANTES vs DESPUÉS de P0: solo se puede medir tras aplicar P0 y refrescar.
- El join KNA1 (línea 4373) con KUNNR alfanumérico: documentado, no crítico.
