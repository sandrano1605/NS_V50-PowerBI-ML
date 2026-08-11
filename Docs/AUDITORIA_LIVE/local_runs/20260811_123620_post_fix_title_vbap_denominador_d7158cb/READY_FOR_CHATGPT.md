# READY FOR CHATGPT

RUN_ID: 20260811_123620_post_fix_title_vbap_denominador_d7158cb
Rama: work/ns-lienzo-02-ingreso-pedidos
SHA auditado: d7158cbf16db385c012d114676d1c5f047997a41
Commit evidencia: POR_PUBLICAR_TRAS_VALIDACION
Power BI: puerto 50439, refresh OK, Tracking=2048

## Resumen

Auditoría dirigida post-fix FIND-002. El hallazgo principal es que **el fix de RE TT Título (cdeda8bb) introdujo un error DAX**: `CONCATENATEX(VALUES(Dim_Rango_Entrega[Rango]), ..., Dim_Rango_Entrega[OrdenRango], ASC)` falla con "No se puede determinar un valor único para la columna OrdenRango" cuando hay multiselect. Los valores numéricos (Pedidos, Valor, PromDH, P90, FueraSLA) NO cambiaron y siguen correctos. INC-015 (VBAP 58.3%) y INC-011 (64 pedidos) quedan pendientes de cuantificación exacta por limitación del tool DAX en esta sesión.

## Hallazgos RED confirmados

### FIND-002A — RE TT Título: fix introdujo error DAX (REGRESIÓN)

- **Archivo:** `Medidas.tmdl`, medida `RE TT Título`
- **Objeto:** Variable `RangoTexto`
- **Línea:** `VAR RangoTexto = CONCATENATEX(VALUES(Dim_Rango_Entrega[Rango]), Dim_Rango_Entrega[Rango], " + ", Dim_Rango_Entrega[OrdenRango], ASC)`
- **Problema:** El 4º argumento de CONCATENATEX (columna de orden `OrdenRango`) no puede resolverse cuando hay múltiples Rangos seleccionados (error de valor único)
- **Origen:** Commit `cdeda8bb9ad242f95944997ef660a35ae1e49489` "fix(lienzo-00): título tooltip respeta multiselect"
- **Impacto:** RE TT Título lanza error DAX en CUALQUIER contexto (probado con y sin filtros)
- **Cambio recomendado:** Reemplazar `Dim_Rango_Entrega[OrdenRango]` por `MIN(Dim_Rango_Entrega[OrdenRango])` o eliminar el sort-by (usar el texto como criterio)
- **Prioridad:** P0 — el fix rompió una medida que antes funcionaba

### FIND-001 — FECHA_MANIFIESTO permite TRP fallback (INC-007B)

- **Archivo:** `Fact_Tracking.tmdl`, Power Query M
- **Objeto:** Columna `FECHA_MANIFIESTO`
- **Problema:** La cadena `else if [TRP_U_FECHA_HORA]<>null then [TRP_U_FECHA_HORA] else [TRP_P_FECHA_HORA]` permite que FES cierre sin manifiesto VBFA real
- **Datos actuales:** 0 FES afectados (437 cerrados = 437 con manifiesto)
- **Requiere decisión de negocio:** SÍ

## Hallazgos ORANGE confirmados

### FIND-003 — Cobertura VBAP 58,3% (INC-015)

- **Archivo:** `Lineas_y_unidades_por_pedidos.tmdl`
- **Cobertura:** 1.107/1.898 (58,3%), 791 sin match
- **Hipótesis del usuario:** Posible incompatibilidad de formato de clave (VBAP.VBELN texto vs ZVBELN_PED con ceros a la izquierda)
- **Pendiente:** Probar match normalizado quitando ceros a la izquierda — no ejecutado por limitación del tool DAX

### FIND-004 — Denominadores U vs RE (INC-011)

- **Archivo:** `Medidas.tmdl`
- **U NS:** 78,8% (1.962 denominador) vs **RE NS:** 81,5% (1.898 denominador)
- **Diferencia:** 64 pedidos cerrados sin DH válido
- **Pendiente:** Clasificar los 64 pedidos individualmente por causa (CIERRE_ANTES_DE_CREACION, CREACION_NULA, etc.) — no ejecutado por limitación del tool DAX

## Falsos positivos relevantes

1. **INC-005/INC-009 multiselect:** Los valores numéricos siguen correctos (Normal+FES Pedidos=1896, Valor=2271756623, Líneas=22801). El fix de FIND-002 solo afectó el título, no los números.
2. **Pedido 4190139455 (regresión):** Cambió de FES a NORMAL en datos actuales — es cambio de datos, no error del modelo.

## Decisiones de negocio necesarias

1. **FECHA_MANIFIESTO fallback TRP:** ¿Se confirma "FES solo cierra por manifiesto VBFA/VTTP"?
2. **NS oficial:** ¿81,5% (1.898 evaluables) o 78,8% (1.962 cerrados)?
3. **Feriados regionales:** ¿La operación logística usa feriados regionales?

## Cambios recomendados para implementación remota

| # | Archivo | Objeto | Cambio | Prioridad |
|---|---------|--------|--------|-----------|
| 1 | Medidas.tmdl | RE TT Título | Reemplazar OrdenRango por MIN(OrdenRango) o quitar sort-by | P0 |
| 2 | Fact_Tracking.tmdl | FECHA_MANIFIESTO | Eliminar fallback TRP (requiere decisión) | P1 |
| 3 | Lineas_y_unidades_por_pedidos | VBAP | Probar normalización de ceros | P1 |
| 4 | Medidas.tmdl | U NS observado interno | Documentar denominador oficial | P1 |

## Evidencia principal

| Archivo | Contenido |
|---------|-----------|
| 07_live_results.csv | 19 pruebas vivas (baseline, multiselect, VBAP, FIND-002A error) |
| 08_regression_cases_results.csv | 12 pedidos: 11 OK, 1 FAIL (cambio de datos) |
| 09_inc_status.csv | 13 INCs + FIND-002A: 7 GREEN, 3 RED, 3 ORANGE |
| 04_code_findings.csv | 4 hallazgos con archivo/línea/recomendación |
| 11_data_quality.csv | 7 checks de calidad |

## No resuelto

1. **Clasificación de los 64 pedidos U vs RE** — no ejecutado (tool DAX falló).
2. **Match normalizado VBAP (ceros a la izquierda)** — no ejecutado (tool DAX falló).
3. **Comparación pedido a pedido Fact_Tracking vs Fact_Hitos** — requiere tool DAX.
4. **Feriados regionales con impacto** — NECESITA_DATOS.
5. **Tool MCP DAX queries falla** — incluso EVALUATE ROW(x,1) falla en esta sesión; se recomienda reiniciar la sesión MCP o usar Power BI Desktop UI para verificar.
