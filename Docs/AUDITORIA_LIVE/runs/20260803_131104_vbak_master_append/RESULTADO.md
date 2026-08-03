# RESULTADO: Ejecución local del append VBAK — DETENIDA

**Fecha:** 2026-08-03
**Rama:** work/ns-vbak-master-append (HEAD 54a28d1)
**Base estable:** a8e8186

## Estado: DETENIDA por hallazgo (según instrucción cerrada)

La instrucción cerrada establece:
> "No corregir hallazgos. Si algo falla, dejar VBAK_APPEND_ACTIVO=false, documentar el error y detenerse."

## Pasos completados

1. ✅ Rama recuperada: `54a28d1fd62b2ce9e2819bc047d122bd41f7fab9`
2. ✅ Validador: `status=VERDE`, `pbip_changes=[]`
3. ✅ Consultas creadas en el modelo en vivo (vía MCP):
   - `VBAK_SCHEMA_PREFLIGHT` (00)
   - `VBAK_APPEND_ACTIVO` (01, parámetro)
   - `VBAK_ATRIBUTOS_MAYORISTA` (02)
   - `VBAK_APPEND_PREFLIGHT_DETALLE` (05)
   - `VBAK_APPEND_CONTROL` (04)
4. ❌ Preflight SQL: NO EJECUTADO (refresh completo lanzado, modelo quedó con conteo alterado)

## Hallazgo 1: Parámetro serializado como Text en lugar de Logical

El MCP creó `VBAK_APPEND_ACTIVO` con:
```
expression: "false" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
```
En lugar de:
```
false meta [IsParameterQuery=true, Type="Logical", IsParameterQueryRequired=true]
```

**Impacto**: el bloque del append (`if VBAK_APPEND_ACTIVO then ... else ...`) espera un booleano. Con `Type="Text"` el diseño del kit se rompe. La serialización vía MCP no respetó el tipo declarado en `01_VBAK_APPEND_ACTIVO.pq`.

## Hallazgo 2: Conteo de la master alterado (1973 → 1241)

Antes de crear las consultas: master = 1.973 pedidos (snapshot documentado).
Después de crear las 5 named expressions + refresh completo: master = **1.241 pedidos** en todas las tablas (master, Fact_Tracking, Dim_Pedido).

- Ventana de fechas verificada correcta: 03-05-2026 a 03-08-2026 (3 meses móviles).
- El TMDL en disco está limpio (sin bloque de integración, sin cambios vs HEAD).
- La causa raíz no fue corregida (prohibido por instrucción).

**Causa probable**: la creación de named expressions que referencian `Fact_Pedidos_Auditoria`
(`VBAK_APPEND_PREFLIGHT_DETALLE` y `VBAK_APPEND_CONTROL`) vía MCP pudo alterar la
evaluación del refresh, o el refresh completo con el parámetro mal tipado afectó el modelo.

## Acción tomada

- `VBAK_APPEND_ACTIVO` permanece en `false` (no se activó el append).
- No se pegó el bloque `03_FACT_PEDIDOS_AUDITORIA_APPEND_BLOCK.pq` en la master.
- No se modificó NS.Report ni NS.SemanticModel en disco (git status limpio).
- Modelo vivo: master 1.241 pedidos (conteo alterado respecto del snapshot).

## Recomendación para continuar (en ChatGPT)

1. **Revisar la serialización del parámetro**: crear `VBAK_APPEND_ACTIVO` desde la
   interfaz de Power Query (no vía MCP) para garantizar `Type="Logical"`.
2. **Investigar el conteo 1241 vs 1973**: verificar si la creación de named expressions
   que referencian la master causó la caída, o si la ventana móvil cambió el universo.
3. **Restaurar el snapshot**: si el conteo no vuelve a 1973/1992, restaurar la master
   desde el backup limpio antes de continuar.
4. **Reintentar el flujo** desde la interfaz de Power BI Desktop siguiendo el README.

## Archivos de evidencia

- Este archivo: `RESULTADO.md`
- Kit validado: `01_kit_validation.json` (ver Docs/AUDITORIA_LIVE/latest/)
