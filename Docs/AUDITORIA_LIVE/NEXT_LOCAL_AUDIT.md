# Próxima auditoría local — Certificación P1_SQL_PROJECTION

## Objetivo

Certificar que la optimización SQL de proyección funciona correctamente:

- P1_SQL_PROJECTION: `321be39` — SELECT * → 88 columnas explícitas en SQL
- P1 (anterior): `8f26dd9` — Table.SelectColumns en M (safety net)
- P0: `3f4c599` — VBFA ventana 3M

## Regla operativa obligatoria

**No pedir al usuario que transcriba métricas, tiempos ni resultados del modelo.**

El auditor local debe obtener directamente desde Power BI Desktop / modelo vivo todo lo que pueda consultar.

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

El HEAD debe contener `321be39` como ancestro.

---

# P1 — Refresh completo Power BI Desktop

Si no hay refresh activo, ejecutar refresh completo del modelo correspondiente al HEAD actual.

Medir/recuperar técnicamente:

- hora inicio, si está disponible;
- hora término;
- duración total segundos;
- errores por tabla;
- SemanticError o DataSource.Error si aparece.

---

# P2 — Verificar capa SQL

La optimización P1_SQL_PROJECTION modifica la query SQL final para traer solo 88 columnas en vez de SELECT *.

Para verificar que funciona, el LLM local debe:

1. **Contar columnas en el modelo vivo** después del refresh
   - Debe ser ≤ 88 columnas (idealmente 88 + RowNumber)
   - Si sigue en ~181, la optimización SQL no se aplicó

2. **Comparar métricas contra baseline** (misma tabla que antes):
   - Pedidos, FES, Fuera SLA, NS, Cerrados, Líneas, Unidades
   - Debe ser idéntico

3. **Medir tiempo de refresh** si es posible
   - Comparar contra el tiempo anterior (antes de P1_SQL_PROJECTION)
   - La reducción esperada es ~30-50% del tiempo de Fact_Pedidos_Auditoria

---

# P3 — Regresión funcional completa

Obtener directamente desde el modelo vivo:

- Pedidos total;
- FES;
- SALDO;
- Fuera SLA;
- NS %;
- Cerrados;
- Cerrados en SLA;
- Líneas;
- Unidades;
- DH Promedio;
- P90 Interno;
- Cobertura Hitos.

Guardar:

`raw/p1_sql_regresion_metricas.csv`

---

# P4 — Regresión FES/VBFA específica

Validar explícitamente:

1. FES con Pedido Posterior;
2. FES con Entrega Posterior;
3. FES con Manifiesto.

Criterio esperado: **0 cambios funcionales**.

---

# Dictamen

`READY_FOR_CHATGPT.md` debe terminar con:

```text
P1_SQL_REFRESH_STATUS=<GREEN|RED>
P1_SQL_FUNCTIONAL_REGRESSION=<GREEN|RED>
P1_SQL_COLUMN_REDUCTION=<GREEN|RED|NOT_APPLIED>
P1_SQL_TRANSFER_MEASUREMENT=<MEASURED|ESTIMATED|NA>
P1_SQL_CERTIFICATION=<GREEN|RED|PARTIAL>
NEXT_STEP=<P2_NORMAL_VBAK|FIX_P1_SQL|NEED_DATA>
```

## Regla de decisión

`P1_SQL_CERTIFICATION=GREEN` solo si:

- refresh completo termina sin error;
- columnas en modelo ≤ 88;
- Pedidos/FES/SALDO/Fuera SLA/NS no presentan diferencias;
- líneas y unidades no presentan regresión.

---

# Salida

Crear corrida:

```powershell
./Scripts/audit_local/bootstrap_local_audit.ps1 -RunName "p1_sql_projection_certificacion"
```

Actualizar `Docs/AUDITORIA_LIVE/LOCAL_LATEST.json` y publicar commit de evidencia.
