# Protocolo de auditoría local — LLM como recolector de evidencia

## 1. Objetivo

Este protocolo separa estrictamente dos roles:

1. **LLM local = auditor / recolector**: recupera el estado real del repositorio y del modelo Power BI, inspecciona la implementación actual, ejecuta validaciones, diagnostica inconsistencias y genera evidencia reproducible.
2. **ChatGPT remoto = implementador**: interpreta la evidencia versionada, decide el cambio técnico junto con el usuario y modifica el repositorio desde el entorno conectado a GitHub.

El LLM local **NO debe corregir TMDL, M, DAX, JSON de visuales, Python, SQL ni archivos funcionales del modelo**. Su trabajo termina en evidencia y diagnóstico.

---

## 2. Rama y baseline de este handoff

- Repositorio: `sandrano1605/NS_V50-PowerBI-ML`
- Rama de trabajo: `work/ns-lienzo-02-ingreso-pedidos`
- Baseline de preparación del protocolo: `352fb33dc65938232a55003b7fe54fc1de61699e`
- Modelo PBIP: `NS.pbip`

**Regla de precedencia:** el SHA real de la rama al iniciar cada corrida manda sobre el baseline anterior. El auditor debe registrar el SHA exacto que realmente inspeccionó. Nunca debe asumir que el baseline sigue siendo HEAD.

---

## 3. Modo de operación obligatorio

### 3.1 Solo lectura funcional

El auditor puede leer y ejecutar consultas sobre:

- `NS.SemanticModel/**`
- `NS.Report/**`
- `NS.pbip`
- `Docs/AUDITORIA_LIVE/**`
- scripts SQL/Python/PowerShell existentes
- configuración del modelo y relaciones
- Power BI Desktop local y su modelo tabular, si está disponible

### 3.2 Escrituras permitidas

Solo puede crear/modificar:

- `Docs/AUDITORIA_LIVE/local_runs/<RUN_ID>/**`
- `Docs/AUDITORIA_LIVE/LOCAL_LATEST.json`

Opcionalmente puede realizar **un commit de evidencia** al final, siempre que el diff contenga exclusivamente esas rutas.

### 3.3 Escrituras prohibidas

No modificar:

- `NS.SemanticModel/**`
- `NS.Report/**`
- `NS.pbip`
- `.github/**`
- `Scripts/**`
- archivos de configuración funcional
- `regression_cases.csv`
- `DICTAMEN.md`
- `15_incoherencias.csv`
- cualquier código productivo o de negocio

Si detecta un fix evidente, debe **documentarlo**, no implementarlo.

---

## 4. Principios de evidencia

Toda conclusión debe ser verificable por otra persona o por ChatGPT remoto.

Para cada hallazgo incluir obligatoriamente:

- objeto afectado;
- ruta de archivo;
- líneas o bloque relevante cuando aplique;
- regla de negocio o expectativa;
- comportamiento real;
- evidencia que lo demuestra;
- severidad;
- confianza;
- si requiere decisión de negocio;
- recomendación técnica, sin aplicar el cambio.

No marcar como error algo solo porque “parece raro”. Separar siempre:

- **CONFIRMADO**: evidencia suficiente;
- **FALSO_POSITIVO**: hipótesis descartada con evidencia;
- **NECESITA_DATOS**: no se puede concluir;
- **DECISION_NEGOCIO**: la implementación puede ser coherente, pero falta regla formal.

---

## 5. Preflight obligatorio

Antes de analizar el modelo:

1. Ejecutar `Scripts/audit_local/bootstrap_local_audit.ps1`.
2. Registrar:
   - rama;
   - SHA local;
   - SHA remoto de la rama;
   - `git status --porcelain`;
   - remote;
   - últimos commits;
   - archivos ya modificados antes de la corrida;
   - proceso Power BI Desktop;
   - puerto/modelo vivo si puede resolverse;
   - fecha/hora local.
3. Si el working tree ya contiene cambios funcionales no relacionados, **no alterarlos** y declararlos en el manifest.
4. Si SHA local != SHA remoto, declarar el desfase antes de continuar.

---

## 6. Orden de auditoría

### Fase A — Inventario estructural

Reconstruir el estado actual, no confiar ciegamente en documentación histórica.

Revisar al menos:

- tablas, columnas, medidas y relaciones;
- particiones M;
- referencias entre medidas;
- medidas/columnas huérfanas o duplicadas;
- variables DAX declaradas pero no usadas;
- referencias a nombres inexistentes;
- filtros con `SELECTEDVALUE` que puedan romper multiselect;
- `TREATAS`, `REMOVEFILTERS`, `ALL`, `ALLSELECTED`, `KEEPFILTERS` y cambios de contexto relevantes;
- reglas de fecha/cierre en `Fact_Tracking` y `Fact_Hitos_Operacionales`;
- dependencias de `Lineas_y_unidades_por_pedidos` / VBAP;
- visuales y campos enlazados en lienzos 00, 01 y 02;
- bookmarks/slicers cuando sean relevantes a una medida auditada.

Generar `03_model_inventory.csv` y `04_code_findings.csv`.

### Fase B — Matriz de reglas de negocio

No asumir que una regla documentada sigue implementada. Para cada regla registrar **documentado vs código actual vs datos actuales**.

Reglas mínimas:

1. Universo Mayorista: canales 42–47.
2. Clasificación exclusiva: NORMAL / FES / SALDO / FES+SALDO.
3. Cierre NORMAL/SALDO: despacho válido.
4. Cierre FES/FES+SALDO: manifiesto oficial VBFA/VTTP.
5. SLA interno: Santiago 4 DH / Regiones 5 DH.
6. Operación: Santiago 3 DH / Regiones 4 DH.
7. Cliente: Santiago 5 DH / Regiones 7 DH.
8. Días hábiles: calendario nacional implementado; verificar tratamiento regional.
9. Filtro multiselect de flujo y zona.
10. Líneas/unidades: cobertura real del cruce con VBAP.
11. Corte de ingreso 14:00 L–J / 12:00 viernes: verificar exactamente qué KPI usa `FECHA_INGRESO_SLA`.
12. Corte 14:30 del lienzo 02: análisis de carga, no SLA.

Generar `05_business_rule_matrix.csv`.

### Fase C — Revisión dirigida de INCs

Estado conocido al crear este protocolo; debe **revalidarse en el SHA actual**:

- `INC-005` multiselect RE: cerrado/verde, revisar regresión.
- `INC-006` corte SLA: reevaluado/verde; 946 diferidos afectan preparación/promesa, impacto atribuido al corte sobre NS interno = 0. Revalidar que la implementación actual siga así.
- `INC-007A` datos FES sin manifiesto: verde en la muestra anterior.
- `INC-007B` fallback TRP en `Fact_Tracking.FECHA_MANIFIESTO`: rojo estructural pendiente de decisión/implementación.
- `INC-008` proxy factura Santiago: documentación corregida; revisar implementación actual.
- `INC-009` multiselect FA: verde validado en vivo, revisar regresión.
- `INC-010` multiselect RE: cubierto por INC-005, revisar regresión.
- `INC-011` denominadores U vs RE: pendiente; cuantificar y explicar los cerrados no evaluables.
- `INC-012` SLA legacy 5 DH: verde mientras no alimente visuales NS oficiales.
- `INC-013` feriados regionales: pendiente de regla de negocio.
- `INC-014` corte 14:30: verde si solo representa carga.
- `INC-015` cobertura VBAP: pendiente de cuantificación.

Generar `09_inc_status.csv` sin editar el dictamen oficial.

### Fase D — Pruebas vivas Power BI

Si Power BI Desktop y el modelo vivo están disponibles:

1. Registrar PID, puerto y nombre de base/modelo.
2. No refrescar automáticamente si eso puede sobrescribir cambios locales. Si se refresca, documentarlo.
3. Ejecutar consultas pequeñas y reproducibles.
4. Guardar texto de consulta en `06_live_queries.md`.
5. Guardar resultados tabulares en `07_live_results.csv` o archivos separados bajo `raw/`.
6. No declarar VERDE una métrica numérica sin prueba viva cuando la prueba sea posible.

Pruebas mínimas:

#### Universo y clasificación
- total pedidos fuente;
- cerrados;
- evaluables;
- NORMAL/FES/SALDO/FES+SALDO;
- Santiago/Regiones;
- identidad de sumas.

#### NS
- pedidos evaluables;
- pedidos en SLA;
- fuera SLA;
- NS total;
- NS por zona;
- denominador U vs RE;
- lista exacta de pedidos que explican cualquier diferencia de denominador.

#### Multiselect
Flujo:
- Todos;
- Normal;
- FES;
- Saldo;
- Normal+FES;
- Normal+Saldo;
- FES+Saldo.

Zona:
- Santiago;
- Regiones;
- Santiago+Regiones.

Validar RE y FA al menos en pedidos, valor, DH, P90, líneas, unidades, volumen y métricas postfactura que correspondan.

#### FES
- FES cerrados;
- con manifiesto real;
- sin manifiesto real y con TRP;
- abiertos;
- fuente real usada por `FECHA_CIERRE`.

#### VBAP / volumen
- pedidos evaluables;
- pedidos con match en volumen;
- pedidos sin match;
- cobertura %;
- líneas/unidades potencialmente omitidas;
- segmentación de faltantes por flujo/zona/mes.

### Fase E — Casos de regresión

Leer `Docs/AUDITORIA_LIVE/regression_cases.csv`, pero tratarlo como **hipótesis histórica**, no como verdad garantizada.

Para cada fila:

- verificar que el pedido aún exista;
- recalcular flujo, zona, fecha/fuente de cierre, SLA y cumplimiento;
- comparar esperado histórico vs implementación/datos actuales;
- si el CSV contradice la regla actual, registrar el hallazgo; **no editar el CSV**.

Generar `08_regression_cases_results.csv`.

### Fase F — Reporte visual

Para visuales críticos de lienzos 00/01/02:

- identificar página y visual;
- medidas/campos usados;
- filtros visual/página/reporte;
- sort;
- interacción con slicers relevantes;
- si el visual consume una medida oficial o una variante legacy;
- detectar bindings rotos o referencias a medidas inexistentes.

Generar `10_visual_bindings.csv`.

### Fase G — Calidad de datos y consistencia

Generar `11_data_quality.csv` con:

- duplicados por pedido en tablas que deberían ser 1:1;
- nulos críticos;
- secuencias de fecha inválidas;
- clasificación inconsistente;
- cierres sin fuente válida;
- regiones blank/inválidas;
- clientes sin match;
- volumen sin match;
- cualquier discrepancia Fact_Tracking vs Fact_Hitos para el mismo concepto.

---

## 7. Paquete de evidencia obligatorio

Cada corrida debe crear:

```text
Docs/AUDITORIA_LIVE/local_runs/<RUN_ID>/
├── 00_manifest.json
├── 01_git_state.txt
├── 02_environment.txt
├── 03_model_inventory.csv
├── 04_code_findings.csv
├── 05_business_rule_matrix.csv
├── 06_live_queries.md
├── 07_live_results.csv
├── 08_regression_cases_results.csv
├── 09_inc_status.csv
├── 10_visual_bindings.csv
├── 11_data_quality.csv
├── 12_recommendations.csv
├── READY_FOR_CHATGPT.md
├── RESULTADO.md
└── raw/
    └── ... evidencia auxiliar ...
```

Si una categoría no puede ejecutarse, el archivo **igual debe existir** con estado `NO_EJECUTADO` y motivo.

---

## 8. Formato de hallazgos

`04_code_findings.csv` debe usar:

```text
FINDING_ID,SEVERITY,STATUS,LAYER,OBJECT_TYPE,OBJECT_NAME,FILE_PATH,LINE_START,LINE_END,RULE,EXPECTED,ACTUAL,EVIDENCE_FILE,CONFIDENCE,REQUIRES_BUSINESS_DECISION,RECOMMENDED_CHANGE,NOTES
```

Valores recomendados:

- `SEVERITY`: `RED`, `ORANGE`, `YELLOW`, `INFO`.
- `STATUS`: `CONFIRMADO`, `FALSO_POSITIVO`, `NECESITA_DATOS`, `DECISION_NEGOCIO`.
- `CONFIDENCE`: `ALTA`, `MEDIA`, `BAJA`.

No usar `RED` solo porque existe una diferencia; debe existir impacto material o riesgo estructural demostrado.

---

## 9. READY_FOR_CHATGPT.md

Este archivo es la interfaz principal para el trabajo remoto. Debe contener, en este orden:

1. `RUN_ID`.
2. rama.
3. SHA local auditado.
4. SHA remoto al iniciar.
5. SHA del commit de evidencia si se realizó.
6. estado del working tree al iniciar.
7. estado Power BI/puerto/refresh.
8. resumen numérico del universo.
9. hallazgos RED confirmados.
10. hallazgos ORANGE confirmados.
11. falsos positivos relevantes.
12. decisiones de negocio necesarias.
13. archivos exactos que deberían modificarse para cada fix sugerido.
14. consultas/evidencias que soportan cada conclusión.
15. lista de dudas que NO pudieron resolverse.

Debe ser factual y compacto. No implementar cambios en este archivo.

---

## 10. Commit/push de evidencia

Para que ChatGPT remoto pueda recuperar el resultado desde GitHub, al terminar:

1. Ejecutar el validador:
   ```powershell
   python Scripts/audit_local/validate_local_evidence.py "<RUN_DIR>"
   ```
2. Revisar:
   ```powershell
   git status --short
   git diff -- Docs/AUDITORIA_LIVE/local_runs Docs/AUDITORIA_LIVE/LOCAL_LATEST.json
   ```
3. Confirmar que **no haya modificaciones funcionales creadas por el auditor**.
4. Stage únicamente:
   ```powershell
   git add "Docs/AUDITORIA_LIVE/local_runs/<RUN_ID>" "Docs/AUDITORIA_LIVE/LOCAL_LATEST.json"
   ```
5. Commit:
   ```powershell
   git commit -m "audit(local): evidencia integral <RUN_ID>"
   ```
6. Push a la misma rama auditada.
7. Registrar SHA local y remoto en `READY_FOR_CHATGPT.md` y/o `LOCAL_LATEST.json`.

Si el repositorio tenía cambios funcionales previos del usuario, esos cambios **no deben incluirse** en el commit de evidencia.

---

## 11. Criterio de finalización

Una corrida local está completa solo si:

- identifica inequívocamente el SHA auditado;
- distingue código, datos y decisión de negocio;
- cada hallazgo tiene evidencia;
- los pendientes principales se cuantifican cuando es posible;
- no se modificó código funcional;
- el paquete pasa `validate_local_evidence.py`;
- la evidencia queda accesible en GitHub o se informa explícitamente por qué no pudo publicarse.

El objetivo no es “dar una opinión del modelo”, sino producir un **dataset de auditoría reproducible** que permita al implementador remoto cambiar exactamente lo necesario y nada más.
