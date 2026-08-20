# Próxima auditoría local — Certificación P0 VBFA 3M

## Objetivo

Certificar funcional y técnicamente el cambio P0 ya implementado en `Fact_Pedidos_Auditoria`.

Commit funcional a certificar:

`3f4c5995016bc98398725ff9818937940c884729`

Cambio aplicado únicamente:

- `P1.ERDAT >= @FechaDesde` en VBFA C→C;
- `P2.ERDAT >= @FechaDesde` en VBFA C→J;
- `F.ERDAT >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))` en el EXISTS VBFA del append VBAK.

No implementar P1 de columnas ni ninguna otra optimización durante esta corrida.

## Regla operativa obligatoria

**No pedir al usuario que transcriba métricas, tiempos ni resultados del modelo.**

El auditor local debe obtener directamente desde Power BI Desktop / modelo vivo todo lo que pueda consultar:

- estado del refresh;
- `lastProcessed` / timestamps disponibles;
- errores de procesamiento;
- Pedidos, Clientes, NORMAL, FES, SALDO, FES+SALDO;
- Cerrados, Fuera SLA, NS;
- Líneas y Unidades;
- métricas específicas FES/VBFA.

Si el usuario ya inició manualmente el refresh, no iniciar un segundo refresh en paralelo: detectar/esperar su término mediante el modelo/instancia activa y, apenas finalice, consultar directamente las métricas post-refresh.

Si el tiempo exacto de inicio del refresh manual no puede recuperarse desde la instancia/telemetría disponible, registrar `TIMING_PARTIAL` y usar los timestamps técnicos disponibles; **no pedir al usuario que mida o copie el tiempo**.

---

# P0 — Preflight obligatorio

Trabajar en:

`work/ns-lienzo-01-analisis-fuera-sla`

Ejecutar:

```powershell
git fetch origin
git switch work/ns-lienzo-01-analisis-fuera-sla
git pull --ff-only origin work/ns-lienzo-01-analisis-fuera-sla
git rev-parse HEAD
git status --short
```

El HEAD debe contener `3f4c599` como ancestro y no debe existir ningún cambio funcional adicional sin documentar.

Registrar:

- SHA local;
- SHA remoto;
- estado working tree;
- instancia/puerto/database de Power BI Desktop;
- timestamp de inicio y término del refresh cuando sea recuperable técnicamente.

---

# P1 — Refresh completo Power BI Desktop

Si no hay refresh activo, ejecutar refresh completo del modelo correspondiente al HEAD actual.

Si el usuario ya inició un refresh manual, observar la instancia activa y reutilizar ese refresh; no lanzar otro.

Medir/recuperar técnicamente:

- hora inicio, si está disponible;
- hora término;
- duración total segundos, si puede derivarse;
- errores por tabla;
- `SemanticError` o `DataSource.Error` si aparece;
- tabla o consulta que más demora si puede obtenerse.

Guardar:

`raw/p0_refresh_timing.csv`

Columnas mínimas:

- inicio
- termino
- duracion_segundos
- estado
- error
- tabla_error
- fuente_timing

No considerar P0 GREEN si el refresh no termina correctamente.

---

# P2 — Regresión funcional después del refresh

Obtener **directamente desde el modelo vivo**, con el alcance vigente del reporte 43/45, como mínimo:

- Pedidos total;
- Clientes;
- NORMAL;
- FES;
- SALDO;
- FES + SALDO;
- Cerrados;
- Fuera SLA;
- NS %;
- Líneas;
- Unidades;
- Pedidos sin líneas;
- FES cerrados sin manifiesto real;
- Cerrados sin DH;
- cobertura de hitos si está disponible.

Guardar:

`raw/p0_regresion_metricas.csv`

Columnas:

- metrica
- baseline_pre_p0
- post_p0
- delta_abs
- delta_pct
- esperado_igual
- estado
- observacion

## Baseline

Usar como autoridad el baseline pre-P0 publicado en la corrida de extracción inmediatamente anterior a `3f4c599`, incluyendo los artefactos del run:

`20260819_120000_extraccion_sql_modelo_completo`

Si una métrica no está disponible en ese run, buscar la última evidencia pre-P0 equivalente y registrar exactamente qué archivo/SHA se usó.

No inventar baseline y no pedir al usuario que lo complete manualmente.

---

# P3 — Regresión específica FES/VBFA

P0 modifica exclusivamente el universo VBFA, por lo que validar explícitamente desde el modelo vivo:

1. cantidad de pedidos FES;
2. pedidos con `PRIMERA_FECHA_PEDIDO_POSTERIOR`;
3. pedidos con `PRIMERA_FECHA_ENTREGA_POSTERIOR`;
4. pedidos con `PRIMERA_FECHA_MANIFIESTO`;
5. pedidos FES sin pedido posterior;
6. pedidos FES sin entrega posterior;
7. pedidos FES sin manifiesto real;
8. lista de pedidos cuyo estado FES difiera del baseline, si existe alguno.

Guardar:

- `raw/p0_fes_regresion_resumen.csv`
- `raw/p0_fes_diferencias.csv`

Criterio esperado: **0 cambios funcionales atribuibles a P0**.

---

# P4 — Líneas y unidades

Confirmar directamente en el modelo que las medidas/tabla de líneas y unidades permanecen iguales al baseline pre-P0.

Guardar:

`raw/p0_lineas_unidades.csv`

Incluir:

- líneas total;
- unidades total;
- pedidos con cobertura de líneas/unidades;
- pedidos sin cobertura;
- diferencias contra baseline.

No reabrir INC-015 salvo que P0 produzca una regresión demostrable.

---

# P5 — Rendimiento

Comparar, cuando exista medición pre-P0:

- tiempo refresh total pre vs post;
- tiempo SQL de `Fact_Pedidos_Auditoria` pre vs post;
- filas VBFA C→C / C→J procesadas si puede medirse sin alterar el modelo.

Registrar por separado **medido** vs **estimado**.

Guardar:

`raw/p0_performance_comparison.csv`

---

# Dictamen

`READY_FOR_CHATGPT.md` debe terminar con:

```text
P0_REFRESH_STATUS=<GREEN|RED>
P0_FUNCTIONAL_REGRESSION=<GREEN|RED|PARTIAL>
P0_FES_EQUIVALENCE=<GREEN|RED|PARTIAL>
P0_LINES_UNITS_EQUIVALENCE=<GREEN|RED|PARTIAL>
P0_PERFORMANCE_SECONDS_PRE=<valor|NA>
P0_PERFORMANCE_SECONDS_POST=<valor|NA>
P0_PERFORMANCE_IMPROVEMENT_PCT=<valor|NA>
P0_CERTIFICATION=<GREEN|RED|PARTIAL>
NEXT_STEP=<P1_MASTER_COLUMNS|FIX_P0|NEED_DATA>
```

## Regla de decisión

`P0_CERTIFICATION=GREEN` solo si:

- refresh completo termina sin error;
- Pedidos/FES/SALDO/NORMAL/FES+SALDO/NS no presentan diferencias no explicadas;
- líneas y unidades no presentan regresión;
- no aparecen nuevas pérdidas de hitos FES/manifiesto atribuibles a la ventana VBFA.

Una mejora de tiempo **no compensa** una diferencia funcional.

---

# Salida

Crear corrida:

```powershell
./Scripts/audit_local/bootstrap_local_audit.ps1 -RunName "p0_vbfa_3m_refresh_regresion"
```

Publicar solamente evidencia de certificación. No modificar funcionalmente:

- `NS.SemanticModel/**`
- `NS.Report/**`
- `NS.pbip`

Actualizar `Docs/AUDITORIA_LIVE/LOCAL_LATEST.json` y publicar commit de evidencia.
