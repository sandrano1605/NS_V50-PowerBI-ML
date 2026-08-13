# Próxima auditoría local — Lienzo 01 / coherencia de filtros e interacción

## Alcance

Página objetivo:

`01 Análisis Fuera SLA`

Page ID:

`a1b2c3d4e5f6071829`

El reporte tiene filtro global obligatorio:

- `Fact_Tracking[PED_CANAL_CODIGO] IN {"43","45"}`

No reabrir INC-015 ni IN02; ambos quedaron GREEN en la evidencia anterior.

El auditor local mantiene rol **READ_ONLY_FUNCTIONAL_EVIDENCE_WRITER**. No modificar TMDL, JSON/PBIR ni PBIP.

---

# Objetivo principal

Auditar la coherencia funcional del Lienzo 01 cuando el usuario selecciona un vendedor en:

`3. VENDEDORES · IMPACTO DE CLIENTES REINCIDENTES SEGÚN FLUJO`

Caso obligatorio de prueba:

`Carlos Garrido`

Responder exactamente cómo se comportan el resto de las tablas/visuales y si la interacción representa lo que el usuario cree estar filtrando.

---

# Hallazgos estáticos que deben validarse en vivo

## H1 — La tabla 3 no usa vendedor histórico del pedido

`fa_vendedores_reincidentes` usa como primera dimensión:

`Dim_Cliente[VENDEDOR_NOMBRE]`

Ese campo proviene del maestro `CLIENTE_VENDEDOR` y representa el **vendedor actualmente asignado al cliente** a la fecha de refresh.

No es necesariamente igual a:

`Fact_Tracking[PED_RESPONSABLE]`

Por lo tanto hay que cuantificar la diferencia entre:

- `VENDEDOR_ACTUAL_CLIENTE` = `Dim_Cliente[VENDEDOR_NOMBRE]`
- `RESPONSABLE_PEDIDO` = `Fact_Tracking[PED_RESPONSABLE]`

No decidir todavía cuál concepto debe quedar en el visual; primero medir la discrepancia.

## H2 — Una fila seleccionada de la tabla 3 contiene Vendedor + Flujo

La tabla 3 proyecta conjuntamente:

- `Dim_Cliente[VENDEDOR_NOMBRE]`
- `Fact_Tracking[CLASIFICACION]`

Por lo tanto una selección de fila puede equivaler a:

`Carlos Garrido + Flujo específico`

no solamente a:

`Carlos Garrido`

Esto debe probarse porque puede cambiar materialmente los otros visuales.

## H3 — La tabla 4 puede distorsionarse bajo un filtro de flujo

Visual:

`4. FES VS CARGA · COHORTE CERRADA POR MOMENTO DEL MES`

Usa medidas como:

- `FA Carga Pedidos Creados`
- `FA Carga % FES`
- `FA NS %`
- `FA DH Promedio`

Estas medidas respetan el contexto de `Fact_Tracking`.

Si una fila de tabla 3 impone además `CLASIFICACION=NORMAL`, la métrica `% FES` puede caer a 0/blank por intersección de filtros; si impone `CLASIFICACION=FES`, puede tender a 100%. Hay que demostrar si esto ocurre en vivo.

---

# P0 — Preflight

Trabajar en:

`work/ns-lienzo-01-analisis-fuera-sla`

Ejecutar:

```powershell
git fetch origin
git switch work/ns-lienzo-01-analisis-fuera-sla
git pull --ff-only origin work/ns-lienzo-01-analisis-fuera-sla
git rev-parse HEAD
git ls-remote origin refs/heads/work/ns-lienzo-01-analisis-fuera-sla
```

LOCAL y REMOTO deben coincidir.

No hacer refresh salvo que el modelo vivo no corresponda al HEAD actual. Si el modelo ya está post-refresh y coincide con el código actual, registrar `REFRESH_REUTILIZADO` con `lastProcessed`.

---

# P1 — Inventario funcional del Lienzo 01

Auditar al menos estos visuales:

1. `fa_clientes_recurrentes`
   - título: `1. CLIENTES FUERA SLA · FRECUENCIA EN LOS Últimos 3 MESES`
2. `fa_vendedores_reincidentes`
   - título: `3. VENDEDORES · IMPACTO DE CLIENTES REINCIDENTES SEGÚN FLUJO`
3. `fa_fes_carga_tiempo`
   - título: `4. FES VS CARGA · COHORTE CERRADA POR MOMENTO DEL MES`
4. `critical_table`
   - título: `PEDIDOS CRÍTICOS DE LA SELECCIÓN · ...`
5. cualquier otro visual visible que cambie al seleccionar una fila de la tabla 3.

Guardar:

`raw/l01_visual_inventory.csv`

Columnas mínimas:

- visual
- título
- campos dimensión
- medidas
- filtros visual
- filtro reporte efectivo
- responde a selección tabla3 esperado

---

# P2 — Baseline sin selección de vendedor

Canales 43/45, sin selección adicional.

Guardar resultados completos de los cuatro visuales principales.

Archivos:

- `raw/l01_baseline_clientes.csv`
- `raw/l01_baseline_vendedores.csv`
- `raw/l01_baseline_fes_carga.csv`
- `raw/l01_baseline_criticos.csv`

Además registrar:

- total pedidos cohorte cerrada;
- pedidos fuera SLA;
- NS contexto;
- cantidad de clientes recurrentes 2M+;
- cantidad clientes recurrentes 3M.

---

# P3 — Caso Carlos Garrido: vendedor SOLO

Construir contexto DAX equivalente a:

`Dim_Cliente[VENDEDOR_NOMBRE] = "Carlos Garrido"`

sin imponer manualmente `Fact_Tracking[CLASIFICACION]`.

Obtener nuevamente:

- tabla 1 clientes;
- tabla 3 vendedores;
- tabla 4 FES vs carga;
- pedidos críticos;
- KPIs generales relevantes.

Guardar:

- `raw/l01_carlos_solo_clientes.csv`
- `raw/l01_carlos_solo_vendedores.csv`
- `raw/l01_carlos_solo_fes_carga.csv`
- `raw/l01_carlos_solo_criticos.csv`
- `raw/l01_carlos_solo_resumen.csv`

Responder:

1. ¿Cuántos clientes quedan?
2. ¿Cuántos pedidos cerrados quedan?
3. ¿Cuántos fuera SLA?
4. ¿Qué NS queda?
5. ¿Qué flujos tiene Carlos?
6. ¿Qué pedidos críticos aparecen?

---

# P4 — Caso Carlos Garrido: selección REAL por fila de tabla 3

Obtener las filas actuales de Carlos en `fa_vendedores_reincidentes`.

Para cada flujo presente de Carlos, simular la selección completa de fila:

- `Dim_Cliente[VENDEDOR_NOMBRE] = "Carlos Garrido"`
- `Fact_Tracking[CLASIFICACION] = <FLUJO_DE_LA_FILA>`

Probar por separado, según existan:

- NORMAL
- FES
- SALDO
- FES + SALDO

Para cada escenario capturar tabla 1, tabla 4 y critical_table.

Guardar:

`raw/l01_carlos_por_flujo.csv`

Debe incluir como mínimo:

- flujo
- pedidos
- pedidos fuera SLA
- NS
- clientes recurrentes 2M+
- clientes recurrentes 3M
- FA Carga Pedidos Creados
- FA Carga Pedidos FES
- FA Carga % FES
- FA DH Promedio
- número de filas critical_table

Comparar explícitamente contra `Carlos SOLO`.

---

# P5 — Coherencia semántica vendedor actual vs responsable del pedido

Para todos los pedidos 43/45 asociados a clientes cuyo `Dim_Cliente[VENDEDOR_NOMBRE] = "Carlos Garrido"`, exportar:

- pedido
- cliente código
- cliente nombre
- vendedor actual cliente
- `Fact_Tracking[PED_RESPONSABLE]`
- flujo
- fecha pedido
- estado SLA
- DH

Guardar:

`raw/l01_carlos_vendedor_vs_responsable.csv`

Calcular:

- total pedidos de clientes actualmente asignados a Carlos;
- pedidos donde `PED_RESPONSABLE` coincide con Carlos;
- pedidos donde difiere;
- porcentaje de discrepancia;
- lista de responsables distintos encontrados.

Repetir el mismo control a nivel global para todos los vendedores:

`raw/l01_vendedor_actual_vs_responsable_resumen.csv`

No corregir nada aún.

---

# P6 — Prueba de coherencia de cada visual

Clasificar cada visual bajo selección de Carlos como:

- `COHERENTE_VENDEDOR_SOLO`
- `COHERENTE_VENDEDOR_Y_FLUJO`
- `NO_RESPONDE_AL_FILTRO`
- `RESPONDE_PERO_SEMANTICA_AMBIGUA`
- `INCONSISTENTE`

Evaluar especialmente:

## Tabla 1 — clientes recurrentes
Debe mostrar únicamente clientes compatibles con el contexto de Carlos y, si la selección real incluye flujo, solo ese flujo.

## Tabla 4 — FES vs carga
Debe determinarse si tiene sentido de negocio que una selección de fila vendedor+flujo la filtre.

Marcar RED si ocurre algo conceptualmente engañoso, por ejemplo:

- seleccionar Carlos + NORMAL provoca `% FES = 0%` y el usuario interpreta que Carlos no tiene FES;
- seleccionar Carlos + FES provoca `% FES = 100%` y el usuario interpreta que toda su cartera es FES;
- la tabla deja de servir para comparar FES vs carga por haber heredado el flujo de la fila.

## Pedidos críticos
Deben corresponder exactamente al contexto seleccionado. Verificar que la columna mostrada `Vendedor` no oculte discrepancias con `PED_RESPONSABLE`.

---

# P7 — Auditoría de DAX que rompe filtros

Revisar todas las medidas usadas por los visuales del Lienzo 01 y detectar:

- `ALL(...)`
- `ALLSELECTED(...)`
- `REMOVEFILTERS(...)`
- `TREATAS(...)`

Determinar si alguno elimina accidentalmente:

- vendedor;
- cliente;
- flujo;
- canales 43/45;
- ventana 3M.

Guardar:

`raw/l01_filter_semantics_measures.csv`

No marcar como error un `REMOVEFILTERS` intencional de `Dim_Fecha[Momento_Mes]` o del mes si la medida documenta que calcula denominador mensual/ventana 3M; explicar el propósito.

---

# Dictamen requerido

`READY_FOR_CHATGPT.md` debe responder claramente:

1. ¿Qué significa técnicamente hacer clic en la fila de Carlos Garrido de la tabla 3?
2. ¿Filtra solo Carlos o Carlos + flujo?
3. ¿Cómo cambia exactamente la tabla 1?
4. ¿Cómo cambia exactamente la tabla 4?
5. ¿Cómo cambia critical_table?
6. ¿Cuántos pedidos de clientes asignados actualmente a Carlos tienen otro `PED_RESPONSABLE`?
7. ¿La palabra “Vendedor” en el lienzo es semánticamente correcta o ambigua?
8. ¿Qué interacciones deberían mantenerse?
9. ¿Qué interacciones deberían deshabilitarse o reemplazarse por slicer?
10. ¿Hay algún cambio DAX necesario o basta un cambio de interacción/UX?

Emitir:

- `L01_COHERENCIA_GREEN`
- `L01_COHERENCIA_PARTIAL`
- `L01_COHERENCIA_RED`

No implementar fixes localmente.

---

# Salida

Crear una corrida nueva:

```powershell
./Scripts/audit_local/bootstrap_local_audit.ps1 -RunName "l01_coherencia_carlos_garrido"
```

Completar evidencia normal, validar y publicar solo evidencia:

```powershell
$env:PYTHONIOENCODING="utf-8"
python Scripts/audit_local/validate_local_evidence.py "<RUN_DIR>"
git diff --check
```

Actualizar `Docs/AUDITORIA_LIVE/LOCAL_LATEST.json`.

No modificar:

- `NS.SemanticModel/**`
- `NS.Report/**`
- `NS.pbip`
