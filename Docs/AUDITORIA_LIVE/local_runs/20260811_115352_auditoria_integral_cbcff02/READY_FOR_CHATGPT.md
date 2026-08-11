# READY FOR CHATGPT

RUN_ID: 20260811_115352_auditoria_integral_cbcff02
Rama: work/ns-lienzo-02-ingreso-pedidos
SHA auditado: cbcff026432f6bd3e5d5bfb3072688ad95039077
SHA remoto al iniciar: cbcff026432f6bd3e5d5bfb3072688ad95039077
Commit evidencia: POR_PUBLICAR_TRAS_VALIDACION
Working tree sucio al iniciar: true (themes no commiteados)
Power BI: puerto 56878, refresh OK, Tracking=2048

## Resumen

Auditoría integral del modelo NS_V50 ejecutada contra SHA cbcff02. El modelo carga correctamente, el refresh no produce errores M/DAX/TMDL, y los números baseline se confirman: 2.048 pedidos totales, 1.898 evaluables, 1.547 en SLA, 351 fuera SLA, NS 81,5%. Las correcciones multiselect RE (14 medidas) y FA (14 medidas) están funcionando correctamente. Se identifican 2 hallazgos RED y 3 ORANGE que requieren acción.

## Hallazgos RED confirmados

### FIND-001 — FECHA_MANIFIESTO permite TRP fallback (INC-007B)

- **Archivo:** `Fact_Tracking.tmdl`, Power Query M, sección `FECHA_MANIFIESTO`
- **Objeto:** Columna calculada `FECHA_MANIFIESTO`
- **Líneas:** Cadena Man = Table.AddColumn(...) con else if TRP_U_FECHA_HORA / TRP_P_FECHA_HORA
- **Regla violada:** FES debe cerrar exclusivamente con manifiesto VBFA/VTTP
- **Datos actuales:** 0 FES afectados (437 cerrados = 437 con manifiesto real)
- **Riesgo:** Si un FES llega sin manifiesto VBFA pero con TRP, el tracking lo cerraría sin manifiesto
- **Cambio recomendado:** Eliminar `else if [TRP_U_FECHA_HORA]<>null then [TRP_U_FECHA_HORA] else [TRP_P_FECHA_HORA]` de la cadena de FECHA_MANIFIESTO
- **Requiere decisión de negocio:** SÍ — confirmar que la regla es "FES solo cierra por manifiesto VBFA/VTTP"

### FIND-004 — Denominadores U vs RE distintos (INC-011)

- **Archivo:** `Medidas.tmdl`, medidas U NS observado interno vs RE NS contexto
- **Objeto:** Denominadores de NS
- **U NS:** 1.547 / 1.962 = 78,8% (incluye 64 cerrados sin DH válido)
- **RE NS:** 1.547 / 1.898 = 81,5% (solo evaluables con DH válido)
- **Diferencia:** 64 pedidos cerrados sin DIAS_INTERNOS_DH válidos
- **Causa:** Pedidos cerrados sin fecha de cierre operativo válida (posiblemente cierre manual o legacy)
- **Cambio recomendado:** Documentar que NS oficial es 81,5% sobre 1.898 evaluables; los 64 no deberían estar en denominador mientras no tengan medición válida
- **Requiere decisión de negocio:** SÍ — confirmar cuál es el NS oficial

## Hallazgos ORANGE confirmados

### FIND-002 — RE TT Título no refleja multiselect (INC-008 residual)

- **Archivo:** `Medidas.tmdl`, línea 1689
- **Objeto:** `RE TT Título`
- **Problema:** Usa `SELECTEDVALUE(Dim_Vista_Ejecutiva[Flujo])` para el texto del título. Con multiselect devuelve BLANK → muestra "Universo cerrado" en vez de los flujos seleccionados
- **Impacto:** Cosmético — el título no representa el filtro real con selección múltiple
- **Cambio recomendado:** Reemplazar `SELECTEDVALUE(Flujo)` por `CONCATENATEX(VALUES(Flujo), ...)` para mostrar los flujos seleccionados

### FIND-003 — Cobertura VBAP 58,3% (INC-015)

- **Archivo:** `Lineas_y_unidades_por_pedidos.tmdl`
- **Objeto:** Tabla de líneas y unidades por pedido
- **Cobertura:** 1.107 de 1.898 evaluables tienen match VBAP (58,3%)
- **Pedidos sin match:** 791
- **Impacto:** Métricas de líneas/unidades en lienzo 01/02 pueden quedar subestimadas para esos 791 pedidos
- **Cambio recomendado:** Identificar los pedidos sin match VBAP, documentar causa (posiblemente pedidos de canales sin desglose VBAP) y cuantificar el impacto en KPIs

### FIND-004b — Feriados regionales no implementados (INC-013)

- **Estado:** NECESITA_DATOS
- **Calendario actual:** 50 feriados nacionales en Dim_Feriados_Chile
- **Problema:** No se contemplan feriados regionales/comunales que puedan afectar días hábiles
- **Impacto:** Desconocido sin fuente oficial de feriados regionales
- **Cambio recomendado:** Confirmar con negocio si la operación logística regional usa feriados regionales; si no, no cambiar

## Falsos positivos relevantes

1. **INC-006 — Doble reloj SLA:** Los 946 pedidos diferidos por corte en Fact_Hitos afectan preparación/promesa, NO el NS interno. El corte 14:00 L-J / 12:00 Viernes es correcto para Hitos pero Fact_Tracking usa PED_FECHA_HORA. El impacto sobre NS interno es 0 porque Fact_Tracking es la fuente del NS oficial.

2. **INC-007A — FES sin manifiesto:** 0 FES cierran sin manifiesto VBFA real en datos actuales. El concern era estructural (el código lo permite) no actual (no hay casos).

3. **Pedido 4190139455 (regresión):** El caso de regresión esperaba clasificación FES pero en datos actuales es NORMAL. Esto NO es un error del modelo — el pedido cambió de clasificación en la fuente de datos.

## Decisiones de negocio necesarias

1. **FECHA_MANIFIESTO fallback TRP:** ¿Se confirma la regla "FES solo cierra por manifiesto VBFA/VTTP"? Si SÍ, eliminar el fallback TRP. Si NO, documentar la excepción.

2. **NS oficial:** ¿El NS interno oficial es 81,5% (1.898 evaluables) o 78,8% (1.962 cerrados)? Recomendación: 81,5% porque los 64 sin DH válido no tienen medición.

3. **Feriados regionales:** ¿La operación logística regional usa feriados regionales para calcular días hábiles? Si SÍ, necesitamos fuente oficial. Si NO, mantener calendario nacional.

## Cambios recomendados para implementación remota

| # | Archivo | Objeto | Cambio | Prioridad |
|---|---------|--------|--------|-----------|
| 1 | Fact_Tracking.tmdl | FECHA_MANIFIESTO | Eliminar fallback TRP_U/TRP_P | P0 (requiere decisión negocio) |
| 2 | Medidas.tmdl | RE TT Título | CONCATENATEX para multiselect | P1 |
| 3 | Lineas_y_unidades_por_pedidos | Cobertura | Documentar 791 pedidos sin match | P1 |
| 4 | Medidas.tmdl | U NS observado interno | Documentar denominador | P1 (requiere decisión negocio) |
| 5 | Resultado.tmdl | SLA_DEFAULT_DH | Sin cambio (legacy ML) | P2 |

## Evidencia principal

| Archivo | Contenido |
|---------|-----------|
| 07_live_results.csv | 23 pruebas vivas: baseline, multiselect RE/FA, diferidos, VBAP, feriados |
| 08_regression_cases_results.csv | 12 pedidos de regresión: 11 OK, 1 FAIL (cambio de datos) |
| 09_inc_status.csv | 12 INCs revalidados: 7 GREEN, 2 RED, 3 ORANGE |
| 04_code_findings.csv | 5 hallazgos con archivo/línea/recomendación |
| 11_data_quality.csv | 6 checks de calidad de datos |

## No resuelto

1. **Cobertura VBAP desagregada:** No se identificaron los 791 pedidos individuales sin match VBAP. Requiere query adicional con pedido + mes + flujo + zona.

2. **Comparación Fact_Tracking vs Fact_Hitos pedido a pedido:** No se ejecutó la comparación completa de FECHA_CIERRE entre las dos facts para los 946 pedidos diferidos.

3. **Uso real de cada medida en visuales:** No se mapeó qué visual usa qué medida. Se verificaron los bindings de las tablas críticas pero no de todos los visuales.

4. **Feriados regionales con impacto:** Se marcó NECESITA_DATOS. No hay fuente confiable de feriados regionales en el modelo.

5. **Fact_Hitos_Operacionales — FES sin manifiesto:** No se verificó si Fact_Hitos tiene pedidos FES sin cierre MAN_E para comparar con Fact_Tracking.
