# Próxima auditoría local — cierre final INC-015 + IN02

## Estado funcional a validar

### INC-015 — líneas y unidades

Fix definitivo implementado en:

`2205859fbc37dcc63102f5b94dfb975b70801b13`

Archivo:

`NS.SemanticModel/definition/tables/Lineas_y_unidades_por_pedidos.tmdl`

La consulta ya NO usa `VBAP.AEDAT`. El universo se acota mediante semi-join al tracking real de los últimos 3 meses:

```sql
SELECT
    VBAP.VBELN AS Pedido,
    COUNT(*) AS Lineas,
    SUM(ISNULL(VBAP.KWMENG,0)) AS Suma_Unidades
FROM VBAP_SAP AS VBAP
WHERE VBAP.VBELN IN (
    SELECT DISTINCT CONVERT(BIGINT, ZVBELN_PED)
    FROM ZART_TRACK_DATA_SAP
    WHERE ZERDAT_PED >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))
)
GROUP BY VBAP.VBELN
```

SQL prevalidado por auditor local:

- sin filtro AEDAT: ~8,858,821 pedidos agregados / ~154,9 s;
- semi-join VBAK 6M: 9.454 / ~5,2 s / 93,4% cobertura;
- **semi-join ZART 3M: 2.053 / ~10,1 s / 99,9% cobertura**;
- universo ZART 3M: 2.055 pedidos;
- residuales conocidos: `1168066`, `1168568`.

El commit anterior `41c0f2b` (sin AEDAT pero sin semi-join) queda SUPERSEDIDO por `2205859`.

### IN02 — hora 14:30

Parser `VBAK_SAP.ERZET` corregido en:

`efbfda74f8fba2bfe5219219c09aa0cef94876b7`

Código:

```sql
TRY_CONVERT(TIME(0), NULLIF(LTRIM(RTRIM(V.ERZET)), '')) AS HORA_VBAK
```

Baseline previo al parser correcto:

- `Sin hora válida`: 184;
- `Hasta 14:30`: 687;
- `Después de 14:30`: 692;
- recuperables VBAK comprobados: 153.

---

## Reglas de negocio cerradas

- Alcance operativo del reporte: canales 43 y 45.
- INC-013: usar solo feriados nacionales de Chile.
- No reabrir YV01 ni feriados regionales.
- Auditor local read-only funcional: no modificar TMDL, report JSON ni PBIP.

---

# P0 — Preflight

```powershell
git fetch origin
git pull --ff-only origin work/ns-lienzo-02-ingreso-pedidos
git rev-parse HEAD
git ls-remote origin refs/heads/work/ns-lienzo-02-ingreso-pedidos
```

LOCAL y REMOTO deben coincidir en el HEAD actual y contener `2205859` y `efbfda7`.

---

# P1 — Refresh completo obligatorio

Ejecutar refresh completo del PBIP.

Registrar en `raw/final_refresh_resumen.md`:

- inicio y término;
- duración total;
- puerto/database;
- resultado global;
- errores M/SQL/memoria/timeout;
- `lastProcessed` post-refresh.

Si falla, no usar resultados anteriores.

---

# P2 — Cierre INC-015

En modelo vivo, universo efectivo canales 43/45 y ventana operativa equivalente:

1. total pedidos;
2. pedidos con match en `Lineas_y_unidades_por_pedidos`;
3. pedidos sin match;
4. cobertura %;
5. lista exacta de residuales;
6. filas de `Lineas_y_unidades_por_pedidos` post-refresh;
7. tiempo de consulta/refresh de esa tabla si es observable.

Guardar:

- `raw/inc015_final_cobertura.csv`
- `raw/inc015_final_residuales.csv`
- `raw/inc015_final_rendimiento.csv`

Validar muestra mínima 50 pedidos SQL vs modelo:

- `COUNT(*)` posiciones = `Lineas`;
- `SUM(ISNULL(KWMENG,0))` = `Suma_Unidades`.

Guardar `raw/inc015_final_muestra.csv`.

Criterio GREEN:

- cobertura >= 99%;
- filas importadas del orden del universo ZART (no millones);
- todos los matches de muestra correctos;
- residuales explicados.

Dictamen: `INC015_GREEN` / `INC015_PARTIAL` / `INC015_RED`.

---

# P3 — Cierre IN02 hora 14:30

Canales 43/45:

- total `[IN Pedidos]`;
- `Hasta 14:30`;
- `Después de 14:30`;
- `Sin hora válida`;
- cobertura hora válida;
- desglose por canal.

Guardar `raw/in02_final_resumen.csv`.

Validar todos los pedidos presentes con ZART `000000` + VBAK.ERZET válido:

- TIME parseado;
- tramo esperado;
- tramo modelo;
- MATCH.

Guardar `raw/in02_final_recuperables.csv`.

Exportar y explicar todos los residuales `Sin hora válida` en `raw/in02_final_residuales.csv`.

Criterio GREEN:

- todos los recuperables presentes hacen MATCH;
- no quedan casos con `VBAK.ERZET` válido mal clasificados;
- `PED_FECHA_HORA` original no cambia.

Dictamen: `IN02_GREEN` / `IN02_PARTIAL` / `IN02_RED`.

---

# P4 — Regresión mínima

Comprobar:

1. total pedidos 43/45 sin variación injustificada;
2. cerrados sin DH = 0;
3. FES cerrados sin manifiesto real = 0;
4. FIND-002A sin SemanticError;
5. visual 02 sigue usando `Fact_Tracking[TRAMO_HORA_INGRESO]` + `[IN Pedidos]`;
6. líneas/unidades no alteran SLA ni clasificación operativa.

Guardar `raw/final_regresion.csv`.

---

# Dictamen final

`READY_FOR_CHATGPT.md` debe incluir:

```text
INC015_STATUS=<INC015_GREEN|INC015_PARTIAL|INC015_RED>
IN02_STATUS=<IN02_GREEN|IN02_PARTIAL|IN02_RED>
```

Y reportar:

- cobertura final líneas/unidades;
- filas finales de `Lineas_y_unidades_por_pedidos`;
- tiempo final de refresh/consulta;
- residuales sin líneas;
- Sin hora antes vs después;
- cantidad recuperada por VBAK.ERZET;
- residuales de hora y causa;
- resultado de regresión.

---

# Salida

Crear nueva corrida, validar y publicar solo evidencia:

```powershell
./Scripts/audit_local/bootstrap_local_audit.ps1 -RunName "inc015_in02_final"
$env:PYTHONIOENCODING="utf-8"
python Scripts/audit_local/validate_local_evidence.py "<RUN_DIR>"
git diff --check
```

No modificar `NS.SemanticModel/**`, `NS.Report/**` ni `NS.pbip`.
