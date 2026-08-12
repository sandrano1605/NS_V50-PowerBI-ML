# Próxima auditoría local — cierre dirigido INC-015

## Objetivo único

Cerrar técnicamente `INC-015` sin modificar el modelo desde el LLM local.

Los fixes anteriores ya quedaron validados en vivo y NO necesitan repetirse salvo una comprobación corta de regresión:

- FIND-002A = GREEN
- INC-011 = GREEN
- INC-007B = GREEN

Baseline vivo de referencia del último paquete:

- `Fact_Tracking`: 2.097
- RE evaluables: 1.941
- RE en SLA: 1.580
- RE fuera SLA: 361
- RE NS: 81,4%
- Match exacto VBAP: 1.131 / 1.941 = 58,3%
- Sin match actual: 810

Paquete fuente: `20260811_225907_post_fix_validacion_viva_00756db`.

---

## Regla de rol

El LLM local sigue siendo auditor read-only funcional.

No modificar:

- `NS.SemanticModel/**`
- `NS.Report/**`
- `NS.pbip`

Solo generar evidencia bajo:

- `Docs/AUDITORIA_LIVE/local_runs/<RUN_ID>/**`
- `Docs/AUDITORIA_LIVE/LOCAL_LATEST.json`

---

## Preflight obligatorio

```powershell
git fetch origin
git pull --ff-only origin work/ns-lienzo-02-ingreso-pedidos
git rev-parse HEAD
git ls-remote origin refs/heads/work/ns-lienzo-02-ingreso-pedidos
```

LOCAL y REMOTO deben coincidir.

Conectar al modelo Power BI post-refresh y registrar puerto, database id, `lastSchemaUpdate` y `FECHA_ACTUALIZACION`.

---

# P0 — Construir universo exacto de los 810 sin match

Desde el modelo vivo obtener los 1.941 RE evaluables y generar la lista exacta de pedidos que NO existen en `Lineas_y_unidades_por_pedidos[Pedido]`.

Guardar:

`raw/inc015_missing_orders.csv`

Columnas mínimas:

- Pedido
- Flujo
- Zona
- Canal
- PED_FECHA_HORA
- largo_clave
- existe_en_Pedidos_Normal_VBAK

Validar que el conteo sea exactamente el del refresh actual. Si ya no son 810 por un refresh posterior, usar el nuevo conteo y explicar la diferencia.

---

# P0 — Prueba SQL discriminante directa sobre VBAP_SAP

La consulta M actual de `Lineas_y_unidades_por_pedidos` es:

```sql
SELECT
    VBAP.VBELN AS Pedido,
    COUNT(*) AS Lineas,
    SUM(ISNULL(VBAP.KWMENG, 0)) AS Suma_Unidades
FROM VBAP_SAP AS VBAP
WHERE VBAP.AEDAT >= GETDATE() - 730
GROUP BY VBAP.VBELN;
```

La hipótesis de padding/ceros ya está descartada. La prueba pendiente debe separar fuente, filtro e import.

## Paso 1 — cargar los faltantes en temporal SQL

Usar una tabla temporal de sesión, no una tabla persistente:

```sql
CREATE TABLE #Missing (
    VBELN varchar(20) NOT NULL PRIMARY KEY
);

INSERT INTO #Missing (VBELN)
VALUES
    ('<pedido_1>'),
    ('<pedido_2>');
-- completar con toda la lista del refresh actual
```

La lista completa cabe en un único INSERT de hasta 1.000 filas si el faltante sigue alrededor de 810.

## Paso 2 — clasificar cada pedido

Ejecutar:

```sql
SELECT
    M.VBELN,
    COUNT(V.VBELN) AS FILAS_VBAP_TOTAL,
    SUM(CASE WHEN V.AEDAT >= GETDATE() - 730 THEN 1 ELSE 0 END) AS FILAS_VBAP_730,
    MIN(V.AEDAT) AS MIN_AEDAT,
    MAX(V.AEDAT) AS MAX_AEDAT,
    CASE
        WHEN COUNT(V.VBELN) = 0
            THEN 'AUSENTE_VBAP_SAP'
        WHEN SUM(CASE WHEN V.AEDAT >= GETDATE() - 730 THEN 1 ELSE 0 END) = 0
            THEN 'EXCLUIDO_AEDAT'
        ELSE 'EXISTE_DENTRO_730'
    END AS CAUSA_INC015
FROM #Missing AS M
LEFT JOIN VBAP_SAP AS V
    ON CONVERT(varchar(20), V.VBELN) = M.VBELN
GROUP BY M.VBELN
ORDER BY CAUSA_INC015, M.VBELN;
```

Guardar resultado completo en:

`raw/inc015_vbap_classification.csv`

### Interpretación obligatoria

- `AUSENTE_VBAP_SAP`: el problema está en la vista/contenido de `VBAP_SAP` o en que el documento no tiene posiciones allí.
- `EXCLUIDO_AEDAT`: el pedido sí está en la vista pero el filtro `AEDAT >= GETDATE()-730` lo elimina.
- `EXISTE_DENTRO_730`: el pedido debería haber sido importado por la consulta M. Si aparece esta categoría, investigar refresh/import/modelo antes de tocar SQL.

---

# P0 — Resumen cuantitativo por causa

Ejecutar y guardar:

```sql
WITH Clasificacion AS (
    SELECT
        M.VBELN,
        CASE
            WHEN COUNT(V.VBELN) = 0
                THEN 'AUSENTE_VBAP_SAP'
            WHEN SUM(CASE WHEN V.AEDAT >= GETDATE() - 730 THEN 1 ELSE 0 END) = 0
                THEN 'EXCLUIDO_AEDAT'
            ELSE 'EXISTE_DENTRO_730'
        END AS CAUSA_INC015
    FROM #Missing AS M
    LEFT JOIN VBAP_SAP AS V
        ON CONVERT(varchar(20), V.VBELN) = M.VBELN
    GROUP BY M.VBELN
)
SELECT
    CAUSA_INC015,
    COUNT(*) AS PEDIDOS
FROM Clasificacion
GROUP BY CAUSA_INC015
ORDER BY PEDIDOS DESC;
```

Guardar en:

`raw/inc015_vbap_summary.csv`

---

# P0 — Cruzar con VBAK_SAP

Para todos los faltantes, obtener cabecera SAP:

```sql
SELECT
    M.VBELN,
    K.AUART,
    K.ERDAT,
    C.CAUSA_INC015
FROM #Missing AS M
LEFT JOIN VBAK_SAP AS K
    ON CONVERT(varchar(20), K.VBELN) = M.VBELN
LEFT JOIN (
    SELECT
        M2.VBELN,
        CASE
            WHEN COUNT(V2.VBELN) = 0
                THEN 'AUSENTE_VBAP_SAP'
            WHEN SUM(CASE WHEN V2.AEDAT >= GETDATE() - 730 THEN 1 ELSE 0 END) = 0
                THEN 'EXCLUIDO_AEDAT'
            ELSE 'EXISTE_DENTRO_730'
        END AS CAUSA_INC015
    FROM #Missing AS M2
    LEFT JOIN VBAP_SAP AS V2
        ON CONVERT(varchar(20), V2.VBELN) = M2.VBELN
    GROUP BY M2.VBELN
) AS C
    ON C.VBELN = M.VBELN
ORDER BY C.CAUSA_INC015, K.AUART, M.VBELN;
```

Guardar en:

`raw/inc015_vbak_crosscheck.csv`

Resumir por:

- `CAUSA_INC015`
- `AUART`
- mes de `ERDAT`
- flujo
- canal
- largo de pedido

---

# P0 — Verificar los casos EXISTE_DENTRO_730

Si `EXISTE_DENTRO_730 > 0`, comparar esos pedidos contra la misma agregación exacta usada por Power BI:

```sql
SELECT
    V.VBELN AS Pedido,
    COUNT(*) AS Lineas,
    SUM(ISNULL(V.KWMENG, 0)) AS Suma_Unidades,
    MIN(V.AEDAT) AS MIN_AEDAT,
    MAX(V.AEDAT) AS MAX_AEDAT
FROM VBAP_SAP AS V
INNER JOIN #Missing AS M
    ON CONVERT(varchar(20), V.VBELN) = M.VBELN
WHERE V.AEDAT >= GETDATE() - 730
GROUP BY V.VBELN
ORDER BY V.VBELN;
```

Si devuelve filas que Power BI no tiene en `Lineas_y_unidades_por_pedidos`, marcar:

`CAUSA_IMPORT_REFRESH_MODEL`

y NO modificar el SQL fuente hasta aislar por qué el import no coincide con la consulta.

---

# P0 — Diagnóstico final obligatorio

Emitir exactamente uno de estos dictámenes o una combinación cuantificada:

- `CAUSA_AEDAT`
- `CAUSA_VISTA_VBAP_SAP`
- `CAUSA_IMPORT_REFRESH_MODEL`
- `CAUSA_MIXTA`

El dictamen debe incluir:

1. total evaluables;
2. con match actual;
3. sin match actual;
4. cantidad `AUSENTE_VBAP_SAP`;
5. cantidad `EXCLUIDO_AEDAT`;
6. cantidad `EXISTE_DENTRO_730`;
7. cobertura potencial si se elimina solo el filtro AEDAT;
8. cobertura potencial si se usa una fuente de posiciones que sí contenga los ausentes;
9. lista de AUART predominantes de los faltantes;
10. recomendación técnica concreta para ChatGPT.

No implementar el fix localmente.

---

# P1 — Sanidad mínima de regresión

Sin repetir toda la auditoría anterior, confirmar:

- `RE TT Título` sin SemanticError;
- cerrados sin DH = 0;
- FES cerrado sin manifiesto real = 0;
- baseline RE del refresh actual;
- cobertura VBAP actual antes de cualquier cambio.

---

# Salida

Crear corrida:

```powershell
./Scripts/audit_local/bootstrap_local_audit.ps1 -RunName "inc015_vbap_direct_sql"
```

Completar paquete normal y agregar en `raw/`:

- `inc015_missing_orders.csv`
- `inc015_vbap_classification.csv`
- `inc015_vbap_summary.csv`
- `inc015_vbak_crosscheck.csv`
- `inc015_sql_queries.sql`

Validar:

```powershell
python Scripts/audit_local/validate_local_evidence.py "<RUN_DIR>"
git diff --check
```

Publicar solo evidencia y actualizar `LOCAL_LATEST.json` a `READY_FOR_CHATGPT`.
