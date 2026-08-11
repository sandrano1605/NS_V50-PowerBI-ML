# Próxima auditoría local dirigida

## Objetivo

Validar el fix remoto de `RE TT Título` y resolver técnicamente los pendientes cuantificables sin implementar reglas de negocio.

## Estado de partida

- Último paquete local validado: `20260811_115352_auditoria_integral_cbcff02`
- SHA auditado por ese paquete: `cbcff026432f6bd3e5d5bfb3072688ad95039077`
- SHA evidencia: `8eb969789cd98fc8accebf7ff8a87827f07f2d3c`
- Fix remoto posterior: `cdeda8bb9ad242f95944997ef660a35ae1e49489`
  - `fix(lienzo-00): título tooltip respeta multiselect`
- El auditor debe usar `git rev-parse HEAD` al iniciar. No asumir que los SHA anteriores siguen siendo HEAD.

## Regla de rol

El LLM local sigue siendo auditor read-only funcional: no modifica `NS.SemanticModel/**`, `NS.Report/**` ni `NS.pbip`. Solo genera evidencia bajo `Docs/AUDITORIA_LIVE/local_runs/<RUN_ID>/**` y actualiza `LOCAL_LATEST.json`.

---

## P0 — Validar FIND-002 corregido

### Objeto

`Medidas.tmdl` → medida `RE TT Título`.

### Pruebas vivas mínimas

Evaluar el texto del título y las métricas RE con estas selecciones:

1. Todos / sin filtro de flujo → debe conservar `Universo cerrado`.
2. Normal.
3. FES.
4. Saldo.
5. Normal + FES → el título debe contener ambos flujos y NO `Universo cerrado`.
6. Normal + Saldo.
7. FES + Saldo.
8. Santiago.
9. Regiones.
10. Santiago + Regiones.
11. Normal + FES + Santiago.
12. Normal + FES + Santiago + Regiones.

Para cada caso guardar:

- `RE TT Título`;
- `RE Pedidos contexto`;
- `RE Valor contexto`;
- `RE Promedio contexto DH`;
- `RE P90 contexto DH`;
- `RE Pedidos fuera SLA contexto`.

Los valores numéricos deben permanecer consistentes con la cohorte filtrada; el fix solo debe cambiar el texto contextual.

---

## P0 — Resolver causa de INC-015 / cobertura VBAP

La auditoría anterior midió 1.107/1.898 pedidos con match exacto (58,3%) y 791 sin match. No asumir que falta información en VBAP: probar primero incompatibilidad de formato de clave.

### Hipótesis obligatoria a probar

`Lineas_y_unidades_por_pedidos[Pedido]` proviene de `VBAP.VBELN` como texto, mientras el universo usa `Fact_Tracking[PED_NUMERO_PEDIDO]` derivado de `ZVBELN_PED`. Verificar si una fuente conserva ceros a la izquierda y la otra no.

### Comparaciones obligatorias

Para los 1.898 evaluables construir evidencia pedido a pedido con:

- `PED_NUMERO_PEDIDO` original;
- longitud original;
- clave normalizada removiendo ceros a la izquierda;
- `VBAP Pedido` exacto si existe;
- longitud VBAP;
- clave VBAP normalizada;
- `MATCH_EXACTO`;
- `MATCH_NORMALIZADO`;
- flujo;
- zona;
- mes;
- responsable;
- líneas;
- unidades.

Calcular:

1. cobertura por match exacto;
2. cobertura por match normalizado;
3. cantidad recuperada solo por normalización;
4. pedidos que siguen sin match después de normalizar;
5. cobertura normalizada por flujo, zona y mes;
6. líneas/unidades actuales vs líneas/unidades usando match normalizado;
7. impacto porcentual en `IN Líneas`, `IN Unidades`, `FA Líneas`, `FA Unidades` y cualquier KPI derivado.

### Criterio de diagnóstico

- Si la cobertura normalizada sube materialmente (idealmente >90%), registrar root cause como incompatibilidad de formato/ceros a la izquierda y proponer normalización de claves antes de `TREATAS` o en la tabla de volumen.
- Si no sube, identificar la verdadera causa de los no-match restantes (pedido inexistente en VBAP, fecha/filtro AEDAT, tipo de documento, otra fuente, etc.).
- No implementar el fix localmente.

Guardar la lista completa de faltantes y recuperados por normalización en `raw/`.

---

## P0 — Resolver causa exacta de INC-011 / 64 cerrados sin DH

No basta con reportar 1.962 vs 1.898. Para cada cerrado con `DIAS_INTERNOS_DH = BLANK()` generar:

- pedido;
- flujo;
- zona;
- `PED_FECHA_HORA`;
- `FECHA_CIERRE`;
- `FECHA_DESPACHO`;
- `FECHA_MANIFIESTO`;
- `ES_CERRADO`;
- `DIAS_INTERNOS_DH`;
- `CUMPLE_SLA_INTERNO`;
- fuente de cierre;
- TRP_P/TRP_U;
- manifiesto primero/último;
- factura primera/última;
- diferencia calendario entre creación y cierre;
- causa técnica de BLANK.

Clasificar cada caso en una causa mutuamente exclusiva, por ejemplo:

- `CIERRE_ANTES_DE_CREACION`;
- `CREACION_NULA`;
- `CIERRE_INVALIDO`;
- `OTRA_CAUSA`.

Recordatorio estructural: `Fact_Tracking.FnDH` devuelve `null` si Inicio/Fin es nulo o si Fin < Inicio. Como `ES_CERRADO = TRUE` implica `FECHA_CIERRE` no nula, comprobar explícitamente si los 64 corresponden a cierres anteriores a creación o a otra anomalía.

También mapear qué visuales/medidas usan:

- `U NS observado interno`;
- `RE NS contexto`.

No cambiar denominadores hasta decisión de negocio.

---

## P1 — INC-007B FES TRP

Solo revalidar y cuantificar:

- FES con manifiesto real;
- FES sin manifiesto real + TRP;
- FES sin manifiesto ni TRP;
- diferencias `Fact_Tracking.FECHA_CIERRE` vs `Fact_Hitos_Operacionales` para esos casos.

No eliminar fallback localmente. Sigue siendo decisión de negocio.

---

## P1 — Incidencias adicionales

Revalidar todos los INC-005 a INC-015 y buscar regresiones nuevas. En particular:

- que el fix de título no cambie números;
- que no aparezcan nuevas variables DAX huérfanas;
- bindings de visuales que usen U vs RE;
- relaciones/TREATAS de volumen;
- discrepancias de clave por padding/ceros;
- secuencias cierre < creación.

## Salida

Ejecutar el protocolo normal:

```powershell
./Scripts/audit_local/bootstrap_local_audit.ps1 -RunName "post_fix_title_vbap_denominador"
```

Completar toda la evidencia, ejecutar:

```powershell
python Scripts/audit_local/validate_local_evidence.py "<RUN_DIR>"
```

Publicar solo evidencia y dejar `LOCAL_LATEST.json` en `READY_FOR_CHATGPT`.
