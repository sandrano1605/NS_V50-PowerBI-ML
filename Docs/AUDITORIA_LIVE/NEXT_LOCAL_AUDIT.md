# Próxima auditoría local dirigida

## Objetivo

Validar en vivo los fixes remotos aplicados después de la evidencia `0614604` y cerrar técnicamente INC-015 sin modificar el modelo desde el LLM local.

## Regla de SHA

El auditor debe ejecutar al inicio:

```powershell
git fetch origin
git pull --ff-only origin work/ns-lienzo-02-ingreso-pedidos
git rev-parse HEAD
git ls-remote origin refs/heads/work/ns-lienzo-02-ingreso-pedidos
```

LOCAL y REMOTO deben coincidir. No usar como HEAD los SHA históricos de los paquetes anteriores.

## Rol

El LLM local sigue siendo auditor read-only funcional. No modificar `NS.SemanticModel/**`, `NS.Report/**` ni `NS.pbip`. Solo generar evidencia bajo `Docs/AUDITORIA_LIVE/local_runs/<RUN_ID>/**` y actualizar `LOCAL_LATEST.json`.

---

## P0 — Validar RE TT Título

El HEAD remoto ya contiene el fix que elimina la referencia inválida a `Dim_Rango_Entrega[OrdenRango]` dentro de `RangoTexto`.

Validar que `RE TT Título` ya NO esté en `SemanticError` y ejecutar las mismas 12 combinaciones usadas en `raw/find002_titulo_12_combinaciones.csv`.

Para cada combinación guardar:

- `RE TT Título`;
- `RE Pedidos contexto`;
- `RE Valor contexto`;
- `RE Promedio contexto DH`;
- `RE P90 contexto DH`;
- `RE Pedidos fuera SLA contexto`.

Criterio: título correcto para multiselect y métricas sin regresión frente al mismo refresh.

---

## P0 — Validar INC-011 después del fix de despacho imposible

El modelo remoto ahora trata como inválido cualquier `TRP_U/TRP_P` anterior a `PED_FECHA_HORA`; no existe hardcode de la fecha `2020-09-24`.

Después de refresh completo, medir:

1. cantidad de filas con `FECHA_DESPACHO < PED_FECHA_HORA`;
2. cantidad de `ES_CERRADO=TRUE` con `DIAS_INTERNOS_DH=BLANK()`;
3. cantidad de pedidos que conservan la fecha centinela `2020-09-24 22:47` en las columnas TRP crudas;
4. para esos pedidos, confirmar que `FECHA_DESPACHO` queda BLANK y `ES_CERRADO=FALSE` salvo que exista otra fuente de cierre válida;
5. denominadores actuales de `U NS observado interno` y `RE NS contexto`;
6. explicar cualquier diferencia restante pedido a pedido.

Criterio esperado: los 55 casos identificados en la corrida anterior dejan de contarse como cierres válidos y no generan `FnDH=null` por cierre anterior a creación.

---

## P0 — Validar INC-007B / cierre FES oficial

El modelo remoto ahora define `FECHA_MANIFIESTO` exclusivamente desde `ULTIMA_FECHA_MANIFIESTO` / `PRIMERA_FECHA_MANIFIESTO` provenientes de VBFA/VTTP. TRP ya no puede reemplazar el manifiesto.

Después de refresh medir:

- FES cerrados;
- FES cerrados con manifiesto real;
- FES sin manifiesto real + TRP;
- FES sin manifiesto ni TRP;
- FES cuyo `FECHA_CIERRE` provenga de TRP: debe ser 0;
- comparación con `Fact_Hitos_Operacionales` para los casos sin manifiesto.

Criterio: ningún FES debe quedar `ES_CERRADO=TRUE` sin manifiesto VBFA/VTTP.

---

## P0 — Resolver definitivamente INC-015 / VBAP

La corrida anterior descartó padding/ceros: cobertura exacta = normalizada = 1.128/1.934. Hay 806 evaluables sin match; 778 existen en `Pedidos_Normal_VBAK`.

La prueba discriminante pendiente es consultar `VBAP_SAP` directamente sin depender de la tabla Power BI agregada.

Para el conjunto de 806 pedidos sin match, obtener:

1. cuántos existen en `VBAP_SAP` SIN filtro `AEDAT`;
2. cuántos existen en `VBAP_SAP` CON `AEDAT >= GETDATE()-730`;
3. para los encontrados sin filtro pero excluidos con filtro: `MIN(AEDAT)`, `MAX(AEDAT)`, cantidad por mes/año de `AEDAT`;
4. para los ausentes incluso sin filtro: comprobar si existe una tabla/vista base alternativa de posiciones SAP y documentar cuál;
5. separar los 28 que tampoco existen en `Pedidos_Normal_VBAK`;
6. calcular cobertura potencial si se elimina/corrige solo el filtro `AEDAT`;
7. NO modificar la consulta M localmente.

Diagnóstico final obligatorio:

- `CAUSA_AEDAT` si los pedidos están en `VBAP_SAP` sin filtro pero desaparecen con el filtro;
- `CAUSA_VISTA_VBAP_SAP` si faltan incluso sin filtro;
- `CAUSA_MIXTA` si ocurren ambas cosas.

Guardar SQL, conteos y muestras en `raw/inc015_vbap_direct_sql.md`.

---

## P1 — Regresión general

Revalidar INC-005 a INC-015, especialmente:

- multiselect RE/FA;
- baseline del refresh actual;
- 4190139455 como cambio de datos/regla C-C, no error del modelo;
- que los fixes de tracking no cambien clasificación NORMAL/FES/SALDO salvo el estado de cierre derivado de fechas inválidas;
- que no aparezcan nuevas secuencias cierre < creación;
- bindings de visuales U vs RE.

## Salida

```powershell
./Scripts/audit_local/bootstrap_local_audit.ps1 -RunName "post_fix_tracking_inc015"
```

Completar evidencia, ejecutar:

```powershell
python Scripts/audit_local/validate_local_evidence.py "<RUN_DIR>"
```

Publicar solo evidencia y dejar `LOCAL_LATEST.json` en `READY_FOR_CHATGPT`.
