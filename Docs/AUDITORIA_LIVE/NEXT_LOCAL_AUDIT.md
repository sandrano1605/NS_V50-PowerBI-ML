# Próxima auditoría local — Optimización integral de extracción SQL/M

## Objetivo principal

Volver al objetivo prioritario del proyecto: **reducir el costo de extracción y refresh del modelo**, trayendo desde SQL solamente las filas y columnas que realmente terminan siendo consumidas por el modelo activo y sus lienzos.

No profundizar UX/interacciones del Lienzo 01 durante esta corrida.

El auditor local mantiene rol **READ_ONLY_FUNCTIONAL_EVIDENCE_WRITER**: medir, mapear y publicar evidencia. No modificar TMDL, PBIR/JSON ni PBIP.

---

# Estado ya certificado — NO repetir desde cero

## Fact_Pedidos_Auditoria

Evidencia formal:

`Docs/AUDITORIA_LIVE/local_runs/20260818_155007_fact_pedidos_auditoria_optimizacion_preflight_946fb29/raw/fact_pedidos_auditoria_preflight.md`

Hallazgos aceptados:

- 181 columnas actuales.
- ~68 columnas necesarias.
- ~113 columnas eliminables porque no son consumidas por visuales, medidas ni tablas hijas.
- VBFA C→J es el principal cuello: ~6,3M filas sin filtro.
- `ERDAT >= DATEADD(MONTH,-3,...)` reduce VBFA C→J a ~976K y la equivalencia fue demostrada sobre el universo ZART 3M con **0 pedidos perdidos**.
- VBFA C→C también conserva 100% del universo relevante con ventana 3M.
- `Lineas_y_unidades_por_pedidos` ya fue optimizada mediante semi-join a `ZART_TRACK_DATA_SAP` 3M y quedó GREEN.

No reabrir INC-015 ni IN02.

---

# Meta de arquitectura

La extracción objetivo debe seguir este principio:

```text
SQL Server
  -> WHERE lo más temprano posible
  -> SELECT solo columnas necesarias
  -> semi-join al universo real cuando corresponda
  -> mínima transferencia SQL -> Power Query
  -> mínima materialización M
  -> modelo semántico
  -> lienzos
```

Optimizar cuatro costos por separado:

1. filas escaneadas en SQL;
2. filas transferidas a Power Query;
3. columnas transferidas/materializadas;
4. filas/columnas finalmente importadas al modelo.

---

# P0 — Preflight

Trabajar en:

`work/ns-lienzo-01-analisis-fuera-sla`

Registrar:

- SHA local;
- SHA remoto;
- estado del working tree;
- Power BI activo/puerto/database;
- `lastProcessed` si existe.

No mezclar resultados de otro HEAD.

---

# P1 — Inventario completo de consultas del modelo

Recorrer **todas** las tablas TMDL del modelo y clasificar cada partición como:

- `SQL_DIRECTA`
- `DERIVADA_DE_MASTER`
- `DERIVADA_DE_OTRA_TABLA_M`
- `ESTATICA_CONFIG`
- `CALCULADA_DAX`
- `OTRA`

Crear:

`raw/extraccion_modelo_inventario.csv`

Columnas mínimas:

- tabla_modelo
- modo
- tipo_fuente
- origen_principal
- objetos_sql
- ventana_actual
- filtros_sql_actuales
- columnas_fuente_estimadas
- columnas_modelo
- consumidor_visual_directo
- consumidor_medida
- consumidor_relacion
- consumidor_tabla_hija
- candidata_optimizacion
- prioridad

**No limitar el análisis a Fact_Pedidos_Auditoria.**

---

# P2 — Mapa de dependencia real: fuente -> columna -> consumidor

Para cada tabla importada construir el conjunto mínimo de columnas requerido por la unión de:

1. visuales activos, incluyendo tooltips/drillthrough activos;
2. medidas DAX;
3. relaciones;
4. columnas usadas por otras consultas M;
5. sort-by / claves / campos auxiliares realmente necesarios;
6. reglas funcionales vigentes de SLA/FES/SALDO.

Crear:

`raw/extraccion_columnas_consumo.csv`

Columnas:

- tabla_modelo
- columna
- visual
- medida_dax
- relacion
- consulta_m_hija
- regla_funcional
- conservar
- razon

Y resumen:

`raw/extraccion_columnas_resumen.csv`

con:

- columnas actuales;
- columnas mínimas;
- eliminables;
- porcentaje reducción.

## Regla

Una columna solo puede marcarse `ELIMINABLE` si todos estos consumidores son NO.

---

# P3 — Auditoría de consultas SQL directas

Para cada `SQL_DIRECTA`, extraer y documentar la consulta real.

Crear:

`raw/extraccion_sql_detalle.md`

Para cada consulta indicar:

- tabla modelo;
- SQL actual;
- tablas/vistas físicas;
- joins;
- conversiones en joins;
- filtros temporales;
- filtros de canal;
- `SELECT *` o columnas explícitas;
- agregaciones;
- DISTINCT;
- ordenamientos innecesarios;
- filas fuente aproximadas;
- filas retornadas;
- tiempo SQL;
- propuesta de reducción.

Buscar especialmente:

- scans de tablas SAP completas;
- consultas sin ventana temporal;
- consultas con ventanas mayores a la necesaria;
- `SELECT *`;
- joins contra maestros completos cuando basta el universo actual;
- `TRY_CONVERT`/funciones sobre la columna de join que impidan usar índices;
- `ORDER BY` innecesario en tablas importadas;
- duplicación de una misma fuente SQL en varias consultas.

---

# P4 — Universo operativo real del modelo

Validar si el universo activo completo puede empujarse a SQL como:

- canales `43` y `45`;
- ventana móvil 3M;
- solo pedidos presentes en `ZART_TRACK_DATA_SAP` cuando la consulta es complementaria por pedido.

No asumir: probar cada consulta.

Crear:

`raw/extraccion_pushdown_universo.csv`

Columnas:

- tabla_modelo
- puede_filtrar_43_45
- puede_filtrar_3m
- puede_semijoin_zart
- filas_actual
- filas_propuesta
- cobertura_actual
- cobertura_propuesta
- perdidos
- dictamen

## Criterio GREEN

Una reducción de filas solo es candidata si mantiene 100% del conjunto de claves requerido o deja residuales previamente documentados y aceptados.

---

# P5 — Revisar consultas complementarias por pedido

Dar prioridad a consultas que pueden resolverse mediante **semi-join al universo real** en vez de leer históricos completos.

Patrón de referencia ya certificado:

```sql
WHERE <CLAVE_PEDIDO> IN (
    SELECT DISTINCT CONVERT(BIGINT, ZVBELN_PED)
    FROM ZART_TRACK_DATA_SAP
    WHERE ZERDAT_PED >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))
)
```

Evaluar, sin implementar localmente, si este patrón aplica a:

- VBAK;
- VBAP (ya optimizada, solo verificar que siga GREEN);
- VBFA;
- VTTP;
- LIPS/LIKP si alguna consulta directa los usa;
- otras tablas SAP por pedido encontradas en el inventario.

Para tablas maestras por cliente/vendedor, probar equivalente por **clientes realmente presentes en ZART 3M**, no traer el maestro completo si no es necesario.

---

# P6 — Revisar dimensiones y lookups SQL

Auditar especialmente dimensiones/consultas lookup que puedan estar leyendo maestros completos:

- `Dim_Cliente`;
- `Cliente_Vendedor`;
- cualquier consulta KNA1/CLIENTE_VENDEDOR/VENDEDOR;
- condiciones de expedición/canales si provienen de SQL;
- cualquier lookup duplicado.

Responder:

1. ¿se necesita la tabla completa o solo códigos presentes en el universo 3M 43/45?
2. ¿hay dos consultas trayendo la misma información?
3. ¿puede consolidarse el lookup en una sola extracción?
4. ¿pueden eliminarse columnas no consumidas antes de transferirlas?

Crear:

`raw/extraccion_dimensiones_lookups.csv`

---

# P7 — Tablas cargadas que podrían no necesitar importarse

Detectar tablas con carga habilitada que no tengan consumo funcional actual.

No eliminar automáticamente.

Clasificar:

- `NECESARIA`
- `SOLO_STAGING_M`
- `SIN_CONSUMO_ACTIVO`
- `DUPLICADA`
- `DECISION_NEGOCIO`

Crear:

`raw/extraccion_tablas_carga.csv`

Para una tabla `SOLO_STAGING_M`, indicar si técnicamente puede quedar como staging/no load sin romper dependencias.

---

# P8 — Benchmark SQL real

Para cada candidato P0/P1 de alto impacto medir, cuando sea posible:

- filas leídas/retornadas actual;
- filas propuesta;
- tiempo actual;
- tiempo propuesta;
- reducción %;
- cobertura de claves;
- resultados agregados de control.

Crear:

`raw/extraccion_benchmark.csv`

No ejecutar consultas destructivas.

---

# P9 — Ranking de optimizaciones

Crear:

`raw/extraccion_recomendaciones.csv`

Columnas:

- prioridad
- tabla_modelo
- cambio
- capa (`SQL_WHERE`, `SQL_SELECT`, `SQL_JOIN`, `SEMI_JOIN`, `M_SELECTCOLUMNS`, `DISABLE_LOAD`, etc.)
- filas_antes
- filas_despues
- columnas_antes
- columnas_despues
- tiempo_antes
- tiempo_despues_estimado_o_medido
- riesgo
- validacion_requerida

Priorizar por impacto real:

1. scans de millones de filas evitables;
2. columnas masivas no consumidas;
3. maestros completos reducibles al universo actual;
4. consultas duplicadas;
5. transformaciones M que pueden empujarse a SQL.

---

# P10 — Plan de implementación incremental

El resultado debe producir un plan de cambios **uno por uno**, no un mega cambio.

Orden base esperado, sujeto a evidencia:

1. `Fact_Pedidos_Auditoria` — P0 filtro VBFA 3M ya prevalidado;
2. refresh + regresión;
3. `Fact_Pedidos_Auditoria` — P1 181 -> ~68 columnas;
4. refresh + regresión;
5. siguiente consulta SQL de mayor costo demostrada por benchmark;
6. refresh + regresión;
7. repetir hasta cerrar inventario.

No tocar P2 de joins KNA1 hasta tener solución de clave alfanumérica certificada.

---

# Métricas de regresión obligatorias para cada futura implementación

Guardar baseline actual para poder comparar después de cada cambio:

- pedidos total 43/45;
- clientes;
- FES;
- SALDO;
- NORMAL;
- FES+SALDO;
- cerrados;
- fuera SLA;
- NS;
- líneas;
- unidades;
- pedidos sin líneas;
- FES cerrados sin manifiesto real;
- cerrados sin DH;
- cobertura de hitos;
- cualquier SemanticError.

Crear:

`raw/extraccion_baseline_regresion.csv`

---

# Dictamen requerido

`READY_FOR_CHATGPT.md` debe responder:

1. ¿Cuáles son todas las consultas que extraen datos directamente de SQL?
2. ¿Cuál es el TOP de consultas más costosas por filas/tiempo?
3. ¿Qué tablas/consultas traen columnas que nadie consume?
4. ¿Qué consultas pueden limitarse a canales 43/45?
5. ¿Cuáles pueden limitarse a 3M?
6. ¿Cuáles pueden usar semi-join al universo ZART?
7. ¿Qué maestros pueden limitarse a clientes/pedidos presentes?
8. ¿Qué tablas cargadas no tienen consumo activo?
9. ¿Cuánto se puede reducir filas y columnas por consulta?
10. ¿Cuál es el orden exacto recomendado de implementación?

Emitir:

```text
EXTRACTION_AUDIT_STATUS=<GREEN|PARTIAL|RED>
MASTER_COLUMN_REDUCTION=<READY|BLOCKED>
MASTER_VBFA_3M=<READY|BLOCKED>
NEXT_HIGHEST_IMPACT_QUERY=<tabla/consulta>
```

---

# Salida

Crear nueva corrida:

```powershell
./Scripts/audit_local/bootstrap_local_audit.ps1 -RunName "extraccion_sql_modelo_completo"
```

Validar y publicar solo evidencia:

```powershell
$env:PYTHONIOENCODING="utf-8"
python Scripts/audit_local/validate_local_evidence.py "<RUN_DIR>"
git diff --check
```

Actualizar `Docs/AUDITORIA_LIVE/LOCAL_LATEST.json`.

No modificar funcionalmente el modelo durante esta auditoría.
