# Próxima auditoría local — INC-015 origen SQL VBAP_SAP

## Objetivo único

Cerrar la causa raíz física de `INC-015` en `DMF_VTA_PRD` sin modificar Power BI ni objetos SQL.

Estado ya confirmado por evidencia `20260811_232642_post_fix_tracking_inc015_18f0baa`:

- RE evaluables: 1.941
- Match actual en `Lineas_y_unidades_por_pedidos`: 1.131 / 1.941 = 58,3%
- Sin match: 810
- 782/810 existen como cabeceras recientes en `VBAK_SAP`
- 0 casos atribuibles al filtro externo `AEDAT >= GETDATE()-730`
- hipótesis padding/ceros: descartada
- dictamen actual: `CAUSA_VISTA_VBAP_SAP`

Los fixes FIND-002A, INC-011 e INC-007B ya están GREEN y no deben reauditarse salvo sanidad mínima.

---

## Rol

El LLM local sigue siendo auditor read-only funcional.

No modificar:

- `NS.SemanticModel/**`
- `NS.Report/**`
- `NS.pbip`
- vistas, tablas, procedimientos o sinónimos SQL

Solo puede generar evidencia bajo:

- `Docs/AUDITORIA_LIVE/local_runs/<RUN_ID>/**`
- `Docs/AUDITORIA_LIVE/LOCAL_LATEST.json`

---

## Preflight

```powershell
git fetch origin
git pull --ff-only origin work/ns-lienzo-02-ingreso-pedidos
git rev-parse HEAD
git ls-remote origin refs/heads/work/ns-lienzo-02-ingreso-pedidos
```

LOCAL y REMOTO deben coincidir.

---

# P0 — Ejecutar auditoría SQL de fuente

Usar exclusivamente el script versionado:

`Scripts/audit_local/inc015_vbap_source_audit.sql`

Ejecutarlo contra:

- servidor usado por el modelo: `128.1.3.21`
- base: `DMF_VTA_PRD`

El script es read-only respecto de objetos persistentes. Solo usa `#RecentHeaders` temporal de sesión.

Guardar la salida íntegra en:

`raw/inc015_vbap_source_audit.txt`

Si alguna sección falla por permisos, registrar el error exacto y continuar con las siguientes secciones posibles.

---

# P0 — Dictamen sobre el tipo de objeto

Determinar exactamente qué es `VBAP_SAP`:

- `VIEW`
- `USER_TABLE`
- `SYNONYM`
- otro

Guardar:

- schema;
- `type_desc`;
- `create_date` / `modify_date` cuando aplique;
- `base_object_name` si es synonym;
- `OBJECT_DEFINITION` si es view y existe permiso;
- dependencias devueltas por `sys.sql_expression_dependencies`.

Si la definición contiene filtros, joins, mandante, sociedad, canal, centro, fecha u otra condición, copiar esas condiciones literalmente en la evidencia y explicar cuáles pueden excluir pedidos recientes.

---

# P0 — Gap directo VBAK_SAP → VBAP_SAP

El script construye el universo reciente usando los mismos AUART de `Pedidos_Normal_VBAK` y `ERDAT > GETDATE()-90`.

Reportar:

1. `headers_recent`;
2. `headers_with_vbap_sap`;
3. `headers_missing_vbap_sap`;
4. cobertura %;
5. gap por `AUART`;
6. gap por mes `ERDAT`;
7. muestra de 100 pedidos ausentes.

Comparar el patrón con los 782 faltantes ya detectados en el modelo.

---

# P0 — Comparación con fuente base VBAP

Si existe y es accesible `dbo.VBAP`, el mismo script compara cobertura.

Emitir uno de estos resultados:

### A. `BASE_VBAP_COMPLETA_VISTA_INCOMPLETA`

Si `dbo.VBAP` recupera materialmente los pedidos que faltan en `VBAP_SAP`.

Recomendación para ChatGPT:

- migrar `Lineas_y_unidades_por_pedidos` a la fuente base `VBAP`, preservando solamente las columnas necesarias (`VBELN`, `KWMENG`, fecha adecuada) y el universo temporal requerido;
- antes de implementar, cuantificar cobertura esperada y volumen de filas.

### B. `BASE_VBAP_TAMBIEN_INCOMPLETA`

Si `dbo.VBAP` tiene el mismo gap.

Recomendación:

- no cambiar Power BI;
- investigar proceso de réplica/carga SAP que alimenta DMF_VTA_PRD.

### C. `VBAP_BASE_NO_DISPONIBLE`

Si `dbo.VBAP` no existe o no es visible.

Recomendación:

- usar definición/dependencias de `VBAP_SAP` para identificar el origen físico real;
- si falta permiso `VIEW DEFINITION`, registrar que se requiere al DBA la definición de la vista/sinónimo.

### D. `VBAP_SAP_ES_TABLA_REPLICADA`

Si `VBAP_SAP` es `USER_TABLE`, no llamarla vista en el dictamen.

Recomendación:

- investigar ETL/replicación y fecha máxima/cobertura de carga;
- no reemplazar la fuente del modelo hasta identificar una tabla de posiciones más completa.

---

# P0 — AEDAT como control, no como hipótesis principal

Para pedidos que sí existen en `VBAP_SAP`, registrar:

- cuántos tienen posiciones dentro de 730 días;
- cuántos presentan `AEDAT` antiguo o nulo.

El objetivo es confirmar que `AEDAT` no explica el gap principal. No volver a proponer eliminación del filtro salvo evidencia nueva contradictoria.

---

# Entregables

Crear corrida:

```powershell
./Scripts/audit_local/bootstrap_local_audit.ps1 -RunName "inc015_vbap_source_rootcause"
```

Además del paquete normal, guardar en `raw/`:

- `inc015_vbap_source_audit.txt`
- `inc015_vbap_object_definition.sql` si la definición está disponible
- `inc015_vbap_missing_sample.csv`
- `inc015_vbap_gap_by_auart.csv`
- `inc015_vbap_gap_by_month.csv`
- `inc015_vbap_base_comparison.csv` si existe `dbo.VBAP`

Actualizar `09_inc_status.csv` con el dictamen físico exacto.

Validar:

```powershell
python Scripts/audit_local/validate_local_evidence.py "<RUN_DIR>"
git diff --check
```

Publicar solo evidencia y actualizar `LOCAL_LATEST.json` a `READY_FOR_CHATGPT`.

## Criterio de cierre

No marcar `INC-015` GREEN todavía. Solo puede cerrarse después de:

1. identificar la fuente física correcta de posiciones;
2. implementar el cambio remoto si corresponde;
3. refresh del modelo;
4. comprobar cobertura y líneas/unidades post-fix en vivo.
