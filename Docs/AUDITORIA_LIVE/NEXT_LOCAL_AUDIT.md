# Próxima auditoría local — Lienzo 01 / FASE B2 coherencia Carlos vs flujo

## Estado previo ya formalizado

Página objetivo:

`01 Análisis Fuera SLA`

Page ID:

`a1b2c3d4e5f6071829`

Filtro global obligatorio del reporte:

`Fact_Tracking[PED_CANAL_CODIGO] IN {"43","45"}`

Evidencia formal previa:

`bc70e8dc4ad809a4f5b10a3a55c826068f7cd29c`

Dictamen previo:

`L01_COHERENCIA_RED`

Hallazgos ya demostrados:

1. una fila de `fa_vendedores_reincidentes` combina `Dim_Cliente[VENDEDOR_NOMBRE]` + `Fact_Tracking[CLASIFICACION]`;
2. por tanto, el clic de fila representa **Vendedor + Flujo**, no Vendedor solamente;
3. `fa_fes_carga_tiempo` puede quedar conceptualmente distorsionado porque `% FES` tiende a 0/blank bajo NORMAL y a 100% bajo FES;
4. `critical_table` hereda también el flujo de la fila;
5. el visual usa vendedor actual del cliente (`Dim_Cliente[VENDEDOR_NOMBRE]`), no responsable histórico del pedido (`PED_RESPONSABLE`).

No duplicar esa auditoría. Esta corrida debe **revalidar el comportamiento sobre el HEAD actual** y profundizar la coherencia entre tabla 1, tabla 3, tabla 4 y Pedidos críticos.

El auditor local sigue siendo `READ_ONLY_FUNCTIONAL_EVIDENCE_WRITER`.

No modificar:

- `NS.SemanticModel/**`
- `NS.Report/**`
- `NS.pbip`

---

# Baseline funcional vigente a contrastar

Modelo vivo reportado:

## Global 43/45

- Pedidos: `2.097`
- Clientes: `745`
- Reincidentes 2M+: `22`
- Fuera SLA: `372`
- NS: `80,8%`

## Carlos Garrido — vendedor actual del cliente

- Clientes: `25`
- Pedidos Fact_Tracking: `78`
- Pedidos Fact_Hitos_Operacionales: `78`
- Fuera SLA: `24`
- Reincidentes 2M+: `3`
- NS: `68,4%`

La equivalencia `78 = 78` entre hechos ya se considera señal positiva de propagación por cliente; revalidar solo si el universo cambió por refresh.

---

# Objetivo de esta corrida

Responder una pregunta concreta de experiencia de usuario:

> Si el usuario quiere analizar a Carlos Garrido, ¿las otras tablas muestran a Carlos completo o únicamente a Carlos dentro del flujo de la fila seleccionada?

Y determinar si cada interacción del visual 3 debe:

- mantenerse;
- deshabilitarse;
- reemplazarse por un filtro/slicer de vendedor independiente;
- o requerir un rediseño del visual 3.

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

Registrar HEAD exacto auditado.

Usar modelo Power BI vivo correspondiente al HEAD actual. Si hace falta refresh, ejecutarlo y documentarlo. No mezclar resultados de un modelo anterior.

---

# P1 — Verificar semántica actual de los cuatro visuales

Auditar bindings actuales de:

1. `fa_clientes_recurrentes`
   - `1. CLIENTES FUERA SLA · FRECUENCIA EN LOS ÚLTIMOS 3 MESES`
2. `fa_vendedores_reincidentes`
   - `3. VENDEDORES · IMPACTO DE CLIENTES REINCIDENTES SEGÚN FLUJO`
3. `fa_fes_carga_tiempo`
   - `4. FES VS CARGA · COHORTE CERRADA POR MOMENTO DEL MES`
4. `critical_table`
   - `PEDIDOS CRÍTICOS DE LA SELECCIÓN ...`

Guardar:

`raw/l01_b2_visual_bindings.csv`

Columnas:

- visual
- dimensiones
- medidas
- filtros visual
- interaction_source
- expected_business_scope
- status

Confirmar especialmente que tabla 3 sigue proyectando simultáneamente:

- `Dim_Cliente[VENDEDOR_NOMBRE]`
- `Fact_Tracking[CLASIFICACION]`

---

# P2 — Carlos SOLO

Construir contexto equivalente exclusivamente a:

```text
Dim_Cliente[VENDEDOR_NOMBRE] = "Carlos Garrido"
```

No imponer `CLASIFICACION`.

Obtener:

- pedidos;
- clientes;
- fuera SLA;
- NS;
- recurrentes 2M+;
- recurrentes 3M;
- distribución por `CLASIFICACION`;
- tabla 1 completa;
- tabla 4 completa;
- critical_table completa.

Guardar:

- `raw/l01_b2_carlos_solo_resumen.csv`
- `raw/l01_b2_carlos_solo_clientes.csv`
- `raw/l01_b2_carlos_solo_fes_carga.csv`
- `raw/l01_b2_carlos_solo_criticos.csv`

Comparar con baseline esperado 25 clientes / 78 pedidos / 24 fuera SLA / 3 recurrentes 2M+ / NS 68,4%, admitiendo variación explicable por ventana móvil.

---

# P3 — Carlos + cada flujo real de tabla 3

Obtener las filas visibles de Carlos en `fa_vendedores_reincidentes`.

Para cada flujo realmente presente, ejecutar el contexto equivalente a la selección completa de fila:

```text
Dim_Cliente[VENDEDOR_NOMBRE] = "Carlos Garrido"
Fact_Tracking[CLASIFICACION] = <FLUJO>
```

Evaluar por separado según existan:

- NORMAL
- FES
- SALDO
- FES + SALDO

Guardar:

`raw/l01_b2_carlos_por_flujo.csv`

Columnas mínimas:

- flujo
- pedidos
- clientes
- fuera_sla
- ns
- recurrentes_2m_mas
- recurrentes_3m
- carga_pedidos
- carga_fes
- pct_fes
- dh_promedio
- filas_tabla1
- filas_critical_table

---

# P4 — Prueba específica de Tabla 1

Para `fa_clientes_recurrentes` comparar:

A. sin filtro vendedor;
B. Carlos SOLO;
C. Carlos + NORMAL;
D. Carlos + FES;
E. otros flujos si existen.

Validar:

1. todos los clientes pertenecen al vendedor actual seleccionado;
2. el flujo mostrado coincide con el filtro heredado cuando hay selección de fila;
3. `FA Meses Fuera SLA Cliente` sigue midiendo meses de incumplimiento dentro de la ventana 3M;
4. explicar si la reincidencia se recalcula dentro del flujo o conserva la definición transversal de 3 meses.

Este punto es crítico: no asumir. Demostrar con DAX/modelo vivo si el contexto `CLASIFICACION` afecta o no el conteo de meses fuera SLA.

Guardar:

`raw/l01_b2_tabla1_semantica_reincidencia.csv`

---

# P5 — Prueba específica de Tabla 4 FES vs carga

Comparar los mismos escenarios A-E.

Registrar por mes/momento:

- `FA Carga Pedidos Creados`
- `FA Carga Pedidos FES`
- `FA Carga % FES`
- `FA NS %`
- `FA DH Promedio`
- `FA Delta NS vs Resto`

Guardar:

`raw/l01_b2_tabla4_carlos_vs_flujo.csv`

Dictamen esperado:

- si Carlos SOLO entrega un mix de flujo razonable pero Carlos+NORMAL fuerza `%FES=0/blank`, marcar la interacción como `SEMANTICAMENTE_ENGANOSA`;
- si Carlos+FES fuerza `%FES=100%`, marcar `SEMANTICAMENTE_ENGANOSA`;
- si la tabla deja de poder comparar carga/FES por heredar el flujo de tabla 3, confirmar `L01-001`.

---

# P6 — Pedidos críticos

Comparar:

- Carlos SOLO;
- Carlos + cada flujo.

Validar:

1. cantidad de pedidos;
2. pedido más crítico;
3. vendedor mostrado por `RE TT Vendedor`;
4. `PED_RESPONSABLE` real del pedido;
5. clasificación/flujo.

Guardar:

`raw/l01_b2_criticos_vendedor_vs_responsable.csv`

No confundir:

- vendedor actual del cliente;
- responsable histórico/código del pedido.

---

# P7 — Dictamen UX / interacción

Construir matriz final:

`raw/l01_b2_interacciones_recomendadas.csv`

Columnas:

- source_visual
- target_visual
- current_effect
- business_reading
- semantic_risk
- recommendation

Para `fa_vendedores_reincidentes` evaluar al menos:

### -> Tabla 1

Posibles dictámenes:

- `MANTENER_VENDEDOR_Y_FLUJO`
- `CAMBIAR_A_VENDEDOR_SOLO`

### -> Tabla 4

Posibles dictámenes:

- `DESHABILITAR_INTERACCION`
- `CAMBIAR_A_VENDEDOR_SOLO`
- `MANTENER`

### -> critical_table

Posibles dictámenes:

- `MANTENER_VENDEDOR_Y_FLUJO`
- `CAMBIAR_A_VENDEDOR_SOLO`
- `DESHABILITAR_INTERACCION`

Justificar cada uno con números.

---

# P8 — Semántica de la palabra Vendedor

No volver a descubrir la estructura; ya está conocida.

Cuantificar en el universo actual:

- pedidos de clientes cuyo vendedor actual es Carlos;
- distribución de `PED_RESPONSABLE` para esos pedidos;
- porcentaje de pedidos donde vendedor actual y responsable histórico representan conceptos diferentes.

Guardar:

`raw/l01_b2_vendedor_actual_vs_responsable.csv`

Emitir uno de:

- `VENDEDOR_ACTUAL_ES_INTENCIONAL`
- `VENDEDOR_HISTORICO_REQUERIDO`
- `DECISION_NEGOCIO_PENDIENTE`

No implementar cambio funcional localmente.

---

# Dictamen final requerido

`READY_FOR_CHATGPT.md` debe declarar:

```text
L01_B2_STATUS=<GREEN|PARTIAL|RED>
L01_001_INTERACCION=<CONFIRMADO|NO_REPRODUCIDO>
VENDEDOR_SEMANTICA=<ACTUAL|HISTORICO|DECISION_NEGOCIO>
```

Y responder de forma explícita:

1. Carlos SOLO: pedidos/clientes/fuera SLA/NS/reincidentes.
2. Flujos reales de Carlos.
3. Qué ocurre en tabla 1 al seleccionar una fila de tabla 3.
4. Qué ocurre en tabla 4 y cuánto cambia `%FES`.
5. Qué ocurre en Pedidos críticos.
6. Qué interacciones deben mantenerse y cuáles no.
7. Si se necesita DAX o únicamente UX/interacciones.
8. Si la definición de reincidencia se ve alterada por el filtro de flujo.

---

# Salida

Crear una corrida nueva:

```powershell
./Scripts/audit_local/bootstrap_local_audit.ps1 -RunName "l01_b2_carlos_vs_flujo"
```

Validar y publicar únicamente evidencia:

```powershell
$env:PYTHONIOENCODING="utf-8"
python Scripts/audit_local/validate_local_evidence.py "<RUN_DIR>"
git diff --check
```

Actualizar `Docs/AUDITORIA_LIVE/LOCAL_LATEST.json`.

No realizar cambios funcionales durante esta corrida.
