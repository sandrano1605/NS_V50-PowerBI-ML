# Próxima auditoría local — IN02 post-fix hora ingreso 43/45

## Estado de referencia

Fix funcional implementado por ChatGPT en:

`eb07b64a709348661459c9195c2a30d8c56f2a5c`

Archivo funcional modificado:

`NS.SemanticModel/definition/tables/Fact_Tracking.tmdl`

Cambio:

- `PED_FECHA_HORA` permanece intacto para SLA, fechas y trazabilidad.
- Solo `TRAMO_HORA_INGRESO` incorpora fallback de hora desde `VBAK_SAP.ERZET`.
- El fallback aplica únicamente a canales `43` y `45`.
- Solo se activa cuando la hora original de `PED_FECHA_HORA` es exactamente `00:00:00` y VBAK contiene una hora válida distinta de `00:00:00`.
- No cambia SLA, FES, despacho, cierre ni días hábiles.

Evidencia pre-fix:

- modelo vivo: 197 pedidos `Sin hora válida` en 43/45;
- SQL ZART: 154 pedidos con `ZERZET_PED=000000`;
- recuperables desde `VBAK.ERZET`: 153/154 = 99,35%;
- residual ZART conocido: pedido `1168066` sin VBAK;
- existe además una diferencia pre-fix de 43 pedidos entre Power BI (197) y ZART (154), que debe explicarse post-fix y no asumirse resuelta.

## Decisiones de negocio cerradas

No reabrir en esta corrida:

- `INC-015`: **NO APLICA al alcance del reporte**, cuyo análisis efectivo se restringe a canales 43 y 45.
- `INC-013`: **CERRADO POR REGLA DE NEGOCIO**; usar solo feriados nacionales de Chile ya contenidos en `Dim_Feriados_Chile`.

No buscar YV01 ni feriados regionales/comunales.

---

# Objetivo único

Validar en Power BI vivo que el fallback VBAK corrige la clasificación horaria de `02 Ingreso de Pedidos` sin alterar otros indicadores.

El auditor local continúa en rol read-only funcional: no modificar TMDL/JSON/PBIP. Solo refrescar, consultar y publicar evidencia.

---

# P0 — Preflight

```powershell
git fetch origin
git pull --ff-only origin work/ns-lienzo-02-ingreso-pedidos
git rev-parse HEAD
git ls-remote origin refs/heads/work/ns-lienzo-02-ingreso-pedidos
```

LOCAL y REMOTO deben coincidir en:

`eb07b64a709348661459c9195c2a30d8c56f2a5c`

Si no coinciden, detener la corrida.

---

# P1 — Refresh obligatorio

Abrir/refrescar el modelo Power BI con el código `eb07b64`.

Registrar:

- fecha/hora de refresh;
- puerto;
- resultado del refresh;
- cualquier error M/SQL/TMDL.

Si el refresh falla, no continuar con resultados pre-fix. Publicar el error exacto.

---

# P2 — Recuento post-fix del gráfico 14:30

Restringir explícitamente a canales `43` y `45` y obtener:

1. total `[IN Pedidos]`;
2. `Hasta 14:30`;
3. `Después de 14:30`;
4. `Sin hora válida`;
5. cobertura hora válida = `(Hasta + Después) / Total`;
6. `% Después de 14:30` sobre medibles.

Guardar:

`raw/in02_postfix_resumen.csv`

Comparar contra pre-fix:

- `Sin hora válida` pre-fix = 197.
- recuperables probados = 153.

No exigir que el post-fix termine en 1. El resultado esperado aproximado es una reducción cercana a 153 casos, pero el residual exacto debe salir del refresh y ser explicado.

---

# P3 — Validación de los 153 recuperables

Tomar la evidencia SQL pre-fix de los 153 pedidos recuperables y comprobar en el modelo post-fix que:

- ninguno siga en `Sin hora válida` si su `VBAK.ERZET` es válido;
- cada pedido quede en la franja correcta según `VBAK.ERZET`:
  - `<= 14:30:00` → `Hasta 14:30`;
  - `> 14:30:00` → `Después de 14:30`.

Guardar:

`raw/in02_postfix_153_validacion.csv`

Columnas mínimas:

- pedido;
- canal;
- ZERZET_PED;
- ERZET_VBAK;
- tramo esperado;
- tramo Power BI post-fix;
- status.

Criterio GREEN:

`153/153 MATCH`

Si el universo cambió por ventana móvil, documentar exactamente qué pedido salió/entró y validar todos los que sigan dentro del modelo.

---

# P4 — Explicar todos los residuales `Sin hora válida`

Exportar la lista completa post-fix de pedidos 43/45 que todavía queden como `Sin hora válida`.

Guardar:

`raw/in02_postfix_residuales.csv`

Para cada uno determinar:

- pedido;
- canal;
- origen `ZART` / `VBAK_APPEND` / otro;
- `ZERZET_PED` si aplica;
- `VBAK.ERZET`;
- causa final.

Causas esperadas:

- `SIN_VBAK`;
- `VBAK_ERZET_000000`;
- `VBAK_ERZET_NULL_BLANK`;
- `VBAK_ERZET_INVALIDA`;
- `FUERA_COHORTE_SQL_PREVIO`;
- `INCONSISTENCIA_MODELO_SQL`;
- `OTRA_CAUSA` solo con explicación concreta.

Validar específicamente el pedido conocido:

`1168066`

Debe permanecer `Sin hora válida` salvo que la fuente haya cambiado desde la corrida anterior.

---

# P5 — Regresión mínima obligatoria

Comprobar que el fix no modificó métricas ajenas al tramo horario:

1. total de pedidos 43/45 antes vs después, salvo cambio justificable por ventana/refresh;
2. `PED_FECHA_HORA` de una muestra de >=20 pedidos recuperados permanece igual a pre-fix (`00:00:00` en el campo original); el fallback solo modifica la clasificación de tramo;
3. cerrados sin DH = 0;
4. FES cerrados sin manifiesto real = 0;
5. FIND-002A título sin SemanticError.

Guardar:

`raw/in02_postfix_regresion.csv`

---

# P6 — Binding del visual

Confirmar que el visual:

`02 Ingreso de Pedidos > Disponibilidad para Logística por día · % hasta/después de 14:30`

continúa usando:

- categoría `Dim_Fecha[Dia_Semana]`;
- serie `Fact_Tracking[TRAMO_HORA_INGRESO]`;
- valor `[IN Pedidos]`.

No modificar el título en esta corrida.

---

# Dictamen requerido

Emitir exactamente uno:

## `IN02_HORA_FALLBACK_GREEN`

Usar si:

- refresh OK;
- todos los recuperables presentes quedan correctamente reclasificados;
- no aparecen regresiones;
- residuales están explicados por ausencia/calidad de fuente y no por defecto del fallback.

## `IN02_HORA_FALLBACK_PARTIAL`

Usar si el fallback recupera una parte material pero quedan pedidos con VBAK.ERZET válido aún marcados `Sin hora válida`.

## `IN02_HORA_FALLBACK_RED`

Usar si hay error de refresh, error de M/SQL o regresión funcional.

---

# Salida

Crear corrida, por ejemplo:

```powershell
./Scripts/audit_local/bootstrap_local_audit.ps1 -RunName "in02_hora_fallback_postfix"
```

Completar paquete normal y validar:

```powershell
$env:PYTHONIOENCODING="utf-8"
python Scripts/audit_local/validate_local_evidence.py "<RUN_DIR>"
git diff --check
```

Publicar únicamente evidencia y `LOCAL_LATEST.json`.

No modificar `NS.SemanticModel/**`, `NS.Report/**` ni `NS.pbip`.
