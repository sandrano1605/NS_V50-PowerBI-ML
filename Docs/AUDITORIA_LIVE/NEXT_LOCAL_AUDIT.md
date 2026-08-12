# Próxima auditoría local — IN02 post-fix parser ERZET 43/45

## Estado de referencia

Bug confirmado por auditoría local en `a98e485c46524e7fb343f0801c57c407d3222e38`:

- `VBAK_SAP.ERZET` es `varchar(8)` con formato `HH:MM:SS` (ej. `16:03:02`).
- El fix anterior `eb07b64` truncaba a `VARCHAR(6)` y generaba textos como `16:03:`.
- Por eso `TRY_CONVERT(TIME(0), ...)` devolvía `NULL` y el fallback no recuperaba los pedidos.
- El join por pedido estaba correcto; el defecto era exclusivamente la conversión de `ERZET`.

Fix funcional corregido por ChatGPT:

`efbfda74f8fba2bfe5219219c09aa0cef94876b7`

Archivo modificado:

`NS.SemanticModel/definition/tables/Fact_Tracking.tmdl`

Cambio exacto:

```sql
TRY_CONVERT(TIME(0), NULLIF(LTRIM(RTRIM(V.ERZET)), '')) AS HORA_VBAK
```

El fix sigue limitado a la clasificación `TRAMO_HORA_INGRESO` para canales `43` y `45`. No modifica `PED_FECHA_HORA`, SLA, FES, despacho, cierre ni días hábiles.

## Baseline inmediatamente anterior

Modelo vivo antes del fix correcto:

- `Sin hora válida`: **184**
  - canal 43: **149**
  - canal 45: **35**
- `Hasta 14:30`: **687**
- `Después de 14:30`: **692**
- recuperables probados desde `VBAK.ERZET`: **153** pedidos.

Si el universo no cambia entre refreshes, el residual teórico sería aproximadamente `184 - 153 = 31`; el número real post-refresh es la fuente de verdad.

## Decisiones de negocio cerradas

No reabrir:

- `INC-015`: NO APLICA al alcance de este reporte; se trabaja con canales 43 y 45.
- `INC-013`: CERRADO POR REGLA DE NEGOCIO; usar únicamente feriados nacionales de Chile ya cargados.

No auditar YV01 ni feriados regionales.

---

# Objetivo único

Validar que el parser corregido de `VBAK_SAP.ERZET` permite que el fallback horario funcione realmente en `02 Ingreso de Pedidos`.

El auditor local es read-only funcional: refresca, consulta y publica evidencia; no modifica TMDL/JSON/PBIP.

---

# P0 — Preflight

```powershell
git fetch origin
git pull --ff-only origin work/ns-lienzo-02-ingreso-pedidos
git rev-parse HEAD
git ls-remote origin refs/heads/work/ns-lienzo-02-ingreso-pedidos
```

LOCAL y REMOTO deben coincidir en el HEAD que contenga `efbfda74f8fba2bfe5219219c09aa0cef94876b7` y este handoff. Si no coinciden, detener la corrida.

---

# P1 — Refresh obligatorio

Refrescar Power BI con el código nuevo.

Registrar:

- fecha/hora;
- puerto;
- resultado del refresh;
- errores M/SQL/TMDL si existen.

Si falla el refresh, dictamen RED y no usar resultados antiguos.

---

# P2 — Recuento post-fix del gráfico 14:30

Restringir a canales `43` y `45` y obtener:

1. total `[IN Pedidos]`;
2. `Hasta 14:30`;
3. `Después de 14:30`;
4. `Sin hora válida`;
5. cobertura hora válida;
6. `% Después de 14:30` sobre medibles;
7. desglose por canal.

Guardar:

`raw/in02_parser_postfix_resumen.csv`

Comparar explícitamente contra baseline:

```text
Sin hora válida = 184
Hasta 14:30     = 687
Después 14:30   = 692
```

La reducción esperada de `Sin hora válida` es cercana a 153 si el mismo universo permanece presente.

---

# P3 — Validar recuperables pedido a pedido

Para los pedidos previamente identificados con:

- ZART `ZERZET_PED = 000000`;
- `VBAK.ERZET` válido;

comprobar:

- `VBAK.ERZET` parsea a TIME;
- ya no quedan en `Sin hora válida`;
- `<= 14:30:00` => `Hasta 14:30`;
- `> 14:30:00` => `Después de 14:30`.

Guardar:

`raw/in02_parser_postfix_recuperables.csv`

Columnas mínimas:

- pedido;
- canal;
- ZERZET_PED;
- ERZET_VBAK;
- TIME_VBAK;
- tramo esperado;
- tramo Power BI;
- status.

Criterio GREEN: todos los recuperables presentes en el universo actual deben hacer MATCH.

---

# P4 — Explicar residuales

Exportar todos los pedidos 43/45 que aún queden `Sin hora válida` y clasificarlos.

Guardar:

`raw/in02_parser_postfix_residuales.csv`

Causas permitidas:

- `SIN_VBAK`;
- `VBAK_ERZET_000000`;
- `VBAK_ERZET_NULL_BLANK`;
- `VBAK_ERZET_INVALIDA`;
- `FUERA_VENTANA_VBAK_FALLBACK`;
- `INCONSISTENCIA_MODELO_SQL`;
- `OTRA_CAUSA` solo con evidencia concreta.

Validar especialmente el pedido `1168066`, que históricamente no tenía VBAK.

---

# P5 — Regresión mínima

Comprobar que el cambio no alteró otros procesos:

1. total pedidos 43/45 estable salvo variación explicada por refresh/ventana;
2. `PED_FECHA_HORA` no cambia en muestra >=20 recuperados;
3. cerrados sin DH = 0;
4. FES cerrados sin manifiesto real = 0;
5. FIND-002A sin SemanticError;
6. binding del visual sigue siendo `Fact_Tracking[TRAMO_HORA_INGRESO]` + `[IN Pedidos]`.

Guardar:

`raw/in02_parser_postfix_regresion.csv`

---

# Dictamen requerido

Emitir exactamente uno:

- `IN02_ERZET_PARSER_GREEN`: refresh OK, recuperables correctamente reclasificados y sin regresiones.
- `IN02_ERZET_PARSER_PARTIAL`: parser funciona pero quedan casos con `VBAK.ERZET` válido aún sin clasificar.
- `IN02_ERZET_PARSER_RED`: refresh/error SQL/M o regresión funcional.

---

# Salida

Crear una nueva corrida y validar el paquete normal:

```powershell
./Scripts/audit_local/bootstrap_local_audit.ps1 -RunName "in02_erzet_parser_postfix"
$env:PYTHONIOENCODING="utf-8"
python Scripts/audit_local/validate_local_evidence.py "<RUN_DIR>"
git diff --check
```

Publicar únicamente evidencia y `LOCAL_LATEST.json`.

No modificar `NS.SemanticModel/**`, `NS.Report/**` ni `NS.pbip`.
