# Próxima auditoría local — Certificación P1 master 88 columnas

## Objetivo

Certificar el estado funcional y de rendimiento del modelo después de:

- P0 VBFA 3M: `3f4c5995016bc98398725ff9818937940c884729`;
- P1 actual: reducción de salida de `Fact_Pedidos_Auditoria` a 88 columnas mediante `Table.SelectColumns` / `ColumnasFinales`.

La rama esperada es:

`work/ns-lienzo-01-analisis-fuera-sla`

No implementar ninguna optimización adicional durante esta corrida.

---

# Regla operativa obligatoria

**No pedir al usuario que transcriba métricas, tiempos ni resultados.**

Obtener directamente desde Power BI Desktop / modelo vivo todo lo disponible.

Si hay un refresh manual activo, observarlo y reutilizarlo; no lanzar un segundo refresh en paralelo.

---

# P0 — Preflight y correspondencia modelo vivo / HEAD

Ejecutar:

```powershell
git fetch origin
git switch work/ns-lienzo-01-analisis-fuera-sla
git pull --ff-only origin work/ns-lienzo-01-analisis-fuera-sla
git rev-parse HEAD
git status --short
```

Registrar SHA local/remoto y working tree.

Verificar estáticamente que `Fact_Pedidos_Auditoria.tmdl` termina en:

- `ColumnasFinales = Table.SelectColumns(...)`;
- exactamente 88 columnas seleccionadas;
- `in ColumnasFinales`.

Verificar en el **modelo vivo** que `Fact_Pedidos_Auditoria` corresponde al HEAD actual y expone 88 columnas.

Si el modelo vivo todavía expone 181 columnas, está cargado con una versión anterior: no certificar P1 sobre esa instancia. Recargar/reabrir el proyecto al HEAD actual si el entorno lo permite; si no, emitir `MODEL_HEAD_MISMATCH=RED` sin pedir intervención manual al usuario.

Guardar:

`raw/p1_preflight.csv`

---

# P1 — Refresh completo

Con la instancia correspondiente al HEAD actual, ejecutar o reutilizar un refresh completo.

Recuperar técnicamente cuando sea posible:

- inicio;
- término;
- duración total;
- errores por tabla;
- `SemanticError`;
- `DataSource.Error`;
- tabla/consulta dominante en tiempo.

Guardar:

`raw/p1_refresh_timing.csv`

Si el inicio exacto de un refresh manual no es recuperable, usar `TIMING_PARTIAL`; no pedirlo al usuario.

---

# P2 — Regresión funcional obligatoria

Consultar directamente el modelo vivo con el alcance vigente 43/45:

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

Comparar contra el baseline **pre-P0** publicado en la evidencia anterior a `3f4c599`, especialmente la corrida:

`20260819_120000_extraccion_sql_modelo_completo`

Si existe evidencia técnica recuperable de un refresh **P0-only** anterior a P1, usarla adicionalmente para separar P0 de P1. Si no existe, no inventar atribución: certificar la equivalencia funcional combinada P0+P1 contra el baseline pre-P0.

Guardar:

`raw/p1_regresion_metricas.csv`

Columnas mínimas:

- metrica
- baseline_pre_p0
- p0_only_si_disponible
- post_p1
- delta_pre_p0_vs_post_p1
- estado
- observacion

---

# P3 — Regresión específica FES/VBFA

Validar directamente:

1. cantidad FES;
2. FES con `PRIMERA_FECHA_PEDIDO_POSTERIOR`;
3. FES con `PRIMERA_FECHA_ENTREGA_POSTERIOR`;
4. FES con `PRIMERA_FECHA_MANIFIESTO`;
5. FES sin pedido posterior;
6. FES sin entrega posterior;
7. FES sin manifiesto real;
8. pedidos cuyo estado FES difiera del baseline.

Guardar:

- `raw/p1_fes_regresion_resumen.csv`
- `raw/p1_fes_diferencias.csv`

Esperado: 0 diferencias funcionales no explicadas.

---

# P4 — Líneas y unidades

Validar directamente:

- líneas total;
- unidades total;
- pedidos con cobertura;
- pedidos sin cobertura;
- diferencias contra baseline.

Guardar:

`raw/p1_lineas_unidades.csv`

No reabrir INC-015 salvo regresión demostrable.

---

# P5 — Qué optimizó realmente P1

Este punto es crítico para el objetivo del proyecto.

El P1 actual aplica `Table.SelectColumns` **después** de que la consulta SQL nativa ya produjo la master. Verificar si la SQL contenida en `Sql.Database([Query=...])` sigue terminando en algo equivalente a:

```sql
SELECT *
FROM #FACT_NS_MASTER_AUD_V3
```

Determinar por evidencia:

- columnas generadas dentro de SQL;
- columnas devueltas por SQL a Power Query;
- columnas presentes después de `ColumnasFinales`;
- columnas finalmente importadas al modelo;
- si existe o no query folding capaz de empujar `ColumnasFinales` dentro de la SQL nativa;
- bytes/volumen SQL -> Power Query si puede medirse;
- tamaño del modelo / memoria antes y después si puede medirse.

**No asumir que 181 -> 88 en M implica 181 -> 88 en transferencia SQL.**

Clasificar:

- `P1_MODEL_PROJECTION=GREEN` si el modelo vivo queda correctamente en 88 columnas;
- `P1_SQL_TRANSFER_REDUCTION=GREEN` solo si se demuestra que SQL devuelve únicamente el mínimo requerido;
- en caso contrario `P1_SQL_TRANSFER_REDUCTION=NOT_YET_IMPLEMENTED`.

Guardar:

`raw/p1_projection_layers.csv`

---

# P6 — Dictamen y próximo paso

`READY_FOR_CHATGPT.md` debe terminar con:

```text
MODEL_HEAD_MISMATCH=<GREEN|RED>
P1_REFRESH_STATUS=<GREEN|RED|PARTIAL>
P0_P1_FUNCTIONAL_EQUIVALENCE=<GREEN|RED|PARTIAL>
P1_FES_EQUIVALENCE=<GREEN|RED|PARTIAL>
P1_LINES_UNITS_EQUIVALENCE=<GREEN|RED|PARTIAL>
P1_MODEL_COLUMNS=<numero>
P1_MODEL_PROJECTION=<GREEN|RED>
P1_SQL_COLUMNS_RETURNED=<numero|NA>
P1_SQL_TRANSFER_REDUCTION=<GREEN|NOT_YET_IMPLEMENTED|RED|PARTIAL>
REFRESH_SECONDS_POST_P1=<valor|NA>
P1_CERTIFICATION=<GREEN|RED|PARTIAL>
NEXT_STEP=<P1_SQL_PROJECTION|FIX_P1|NEED_DATA>
```

## Regla de decisión

`P1_CERTIFICATION=GREEN` requiere:

- modelo vivo correspondiente al HEAD actual;
- refresh completo sin error;
- 88 columnas expuestas por `Fact_Pedidos_Auditoria`;
- métricas de negocio sin regresión no explicada;
- FES/VBFA sin pérdida funcional;
- líneas/unidades sin regresión.

La reducción de transferencia SQL puede quedar `NOT_YET_IMPLEMENTED` sin invalidar la equivalencia funcional de P1; en ese caso el siguiente paso obligatorio es `P1_SQL_PROJECTION`, antes de pasar a `Pedidos_Normal_VBAK`.

---

# Salida

Crear corrida:

```powershell
./Scripts/audit_local/bootstrap_local_audit.ps1 -RunName "p1_master_88_refresh_regresion"
```

Publicar solo evidencia. No modificar funcionalmente:

- `NS.SemanticModel/**`
- `NS.Report/**`
- `NS.pbip`

Actualizar `Docs/AUDITORIA_LIVE/LOCAL_LATEST.json` y publicar commit de evidencia.
