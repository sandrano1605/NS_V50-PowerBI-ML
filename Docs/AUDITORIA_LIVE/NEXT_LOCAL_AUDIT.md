# Próxima auditoría local — validación conjunta INC-015 + IN02

## Cambios funcionales a validar

### 1. IN02 — parser ERZET
Commit funcional:

`efbfda74f8fba2bfe5219219c09aa0cef94876b7`

En `Fact_Tracking.tmdl`, `VBAK_SAP.ERZET` se convierte directamente desde su formato real `varchar(8) HH:MM:SS`:

```sql
TRY_CONVERT(TIME(0), NULLIF(LTRIM(RTRIM(V.ERZET)), '')) AS HORA_VBAK
```

Objetivo: recuperar los pedidos 43/45 con ZART `ZERZET_PED=000000` y VBAK.ERZET válido.

Baseline anterior:

- `Sin hora válida`: 184
- `Hasta 14:30`: 687
- `Después de 14:30`: 692
- recuperables probados desde VBAK: 153

### 2. INC-015 — líneas/unidades
Commit funcional:

`41c0f2b478ebe6bf87732e72561e7b94bba28133`

En `Lineas_y_unidades_por_pedidos.tmdl` se eliminó:

```sql
WHERE VBAP.AEDAT >= GETDATE() - 730
```

Razón confirmada por evidencia local:

- `AEDAT` es fecha de actualización de posición, no fecha del pedido;
- el filtro dejaba solo 22.799 de 8.858.283 pedidos VBAP distintos (0,26%);
- ZART 3M: 2.055 pedidos;
- ZART 3M presentes en VBAP sin filtro AEDAT: 2.053 = 99,9%;
- únicos residuales conocidos: `1168066` y `1168568`.

No modificar funcionalmente el modelo durante esta corrida. El auditor local sigue siendo read-only y publica solo evidencia.

---

# P0 — Preflight

```powershell
git fetch origin
git pull --ff-only origin work/ns-lienzo-02-ingreso-pedidos
git rev-parse HEAD
git ls-remote origin refs/heads/work/ns-lienzo-02-ingreso-pedidos
```

LOCAL y REMOTO deben coincidir en el HEAD actual de la rama y contener ambos commits funcionales anteriores.

---

# P1 — Refresh completo obligatorio

Abrir el PBIP y ejecutar refresh completo.

Registrar:

- fecha/hora inicio y término del refresh;
- duración total;
- puerto y database del modelo vivo;
- resultado por tabla si está disponible;
- cualquier error M/SQL/memoria/timeout.

Si el refresh falla, no usar resultados antiguos. Publicar error exacto y dictamen RED.

Guardar:

`raw/refresh_postfix_resumen.md`

---

# P2 — INC-015 cobertura líneas/unidades en modelo vivo

Restringir el análisis al universo efectivo del reporte: canales 43 y 45 y la misma ventana temporal usada por el modelo.

Obtener:

1. pedidos del universo;
2. pedidos con match en `Lineas_y_unidades_por_pedidos`;
3. pedidos sin match;
4. cobertura %;
5. lista completa de pedidos sin match;
6. cantidad de filas importadas en `Lineas_y_unidades_por_pedidos`;
7. tamaño aproximado de la tabla si DMV permite obtenerlo.

Esperado SQL de referencia:

- 2.055 pedidos ZART 3M;
- 2.053 con posiciones;
- cobertura 99,9%;
- residuales conocidos: `1168066`, `1168568`.

Guardar:

- `raw/inc015_postfix_cobertura.csv`
- `raw/inc015_postfix_sin_lineas.csv`
- `raw/inc015_postfix_model_size.csv`

Dictamen INC-015:

- `INC015_AEDAT_GREEN`: cobertura >=99% y residuales explicados;
- `INC015_AEDAT_PARTIAL`: mejora material pero <99% o aparecen pedidos con VBAP existente sin match en modelo;
- `INC015_AEDAT_RED`: refresh falla, cobertura no mejora o hay regresión.

## Control de rendimiento obligatorio

El fix funcional actual elimina AEDAT de forma literal para validar primero la consistencia.

Como la consulta sin filtro puede devolver millones de pedidos históricos, medir obligatoriamente:

- filas importadas en `Lineas_y_unidades_por_pedidos`;
- duración del refresh de esa tabla si es observable;
- impacto de memoria/tamaño.

Si la cobertura queda GREEN pero el volumen es excesivo, recomendar como siguiente optimización un semi-join SQL al universo real 43/45, **sin volver a usar AEDAT como filtro temporal**. No implementar localmente.

---

# P3 — Validación de líneas y unidades pedido a pedido

Tomar muestra mínima de 50 pedidos 43/45 con posiciones VBAP, incluyendo:

- pedidos de 7 dígitos;
- pedidos de 10 dígitos;
- ZMAY;
- ZPDA/ZPPO si están presentes;
- distintos meses de la ventana.

Comparar SQL vs modelo:

- `COUNT(*)` posiciones = `Lineas`;
- `SUM(ISNULL(KWMENG,0))` = `Suma_Unidades`.

Guardar:

`raw/inc015_postfix_muestra_lineas_unidades.csv`

Criterio GREEN: 50/50 MATCH o todos los pedidos presentes si el universo disponible fuera menor.

---

# P4 — IN02 parser ERZET post-fix

Para canales 43 y 45 obtener:

1. total `[IN Pedidos]`;
2. `Hasta 14:30`;
3. `Después de 14:30`;
4. `Sin hora válida`;
5. cobertura de hora válida;
6. desglose por canal.

Guardar:

`raw/in02_parser_postfix_resumen.csv`

Comparar con baseline:

```text
Sin hora válida = 184
Hasta 14:30     = 687
Después 14:30   = 692
```

Validar los recuperables conocidos con ZART `000000` + VBAK.ERZET válido.

Guardar:

`raw/in02_parser_postfix_recuperables.csv`

Para cada pedido:

- pedido;
- canal;
- `ZERZET_PED`;
- `ERZET_VBAK`;
- TIME convertido;
- tramo esperado;
- tramo modelo;
- status.

Criterio GREEN: todos los recuperables presentes hacen MATCH.

Dictamen IN02:

- `IN02_ERZET_PARSER_GREEN`
- `IN02_ERZET_PARSER_PARTIAL`
- `IN02_ERZET_PARSER_RED`

---

# P5 — Explicar residuales de hora

Exportar todos los pedidos 43/45 que sigan como `Sin hora válida` y determinar causa exacta.

Guardar:

`raw/in02_parser_postfix_residuales.csv`

Validar específicamente `1168066`.

---

# P6 — Regresión mínima

Comprobar:

1. total pedidos 43/45 estable salvo variación explicada por ventana móvil;
2. `PED_FECHA_HORA` no fue modificado por fallback ERZET;
3. cerrados sin DH = 0;
4. FES cerrados sin manifiesto real = 0;
5. FIND-002A sin SemanticError;
6. visual 02 continúa usando `Fact_Tracking[TRAMO_HORA_INGRESO]` + `[IN Pedidos]`;
7. líneas/unidades no modifican clasificación SLA ni estado de pedidos.

Guardar:

`raw/postfix_regresion_conjunta.csv`

---

# Dictamen final requerido

El `READY_FOR_CHATGPT.md` debe declarar por separado:

```text
INC015_STATUS=<INC015_AEDAT_GREEN|INC015_AEDAT_PARTIAL|INC015_AEDAT_RED>
IN02_STATUS=<IN02_ERZET_PARSER_GREEN|IN02_ERZET_PARSER_PARTIAL|IN02_ERZET_PARSER_RED>
```

Y responder:

- cobertura líneas/unidades antes vs después;
- número y causa de residuales sin líneas;
- cantidad de filas/tamaño de `Lineas_y_unidades_por_pedidos` post-fix;
- `Sin hora válida` antes vs después;
- número de pedidos recuperados por VBAK.ERZET;
- cualquier impacto de rendimiento del refresh.

---

# Salida

Crear una corrida nueva, por ejemplo:

```powershell
./Scripts/audit_local/bootstrap_local_audit.ps1 -RunName "inc015_in02_postfix"
$env:PYTHONIOENCODING="utf-8"
python Scripts/audit_local/validate_local_evidence.py "<RUN_DIR>"
git diff --check
```

Publicar únicamente evidencia y `LOCAL_LATEST.json`.

No modificar `NS.SemanticModel/**`, `NS.Report/**` ni `NS.pbip`.
