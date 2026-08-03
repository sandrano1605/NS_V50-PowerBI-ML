# LLM local · Ejecución controlada del append VBAK

ChatGPT ya diseñó y versionó la integración. No debes rediseñar la solución, editar TMDL manualmente ni modificar visuales.

## Recuperación

```powershell
git fetch origin
git switch work/ns-vbak-master-append
git pull --ff-only origin work/ns-vbak-master-append
git status --short
git rev-parse HEAD
git diff --name-only a8e818604826e689453769103d962cd3537399ed...HEAD
```

El `git status` debe quedar limpio. Respecto de `a8e8186`, antes de abrir Power BI solo deben existir archivos nuevos dentro de:

```text
PowerQuery/VBAK_APPEND/
Docs/AUDITORIA_LIVE/LLM_LOCAL_EJECUTA_VBAK_APPEND.md
tools/validate_vbak_append_kit.py
```

No debe aparecer ningún archivo de `NS.Report` o `NS.SemanticModel` en esta etapa.

## Trabajo permitido

1. Ejecutar `python tools/validate_vbak_append_kit.py`.
2. Abrir `NS.pbip`.
3. Crear las consultas y el parámetro usando exactamente los archivos de `PowerQuery/VBAK_APPEND/README.md`.
4. Ejecutar el preflight con `VBAK_APPEND_ACTIVO=false`.
5. Pegar el bloque en el Editor avanzado de `Fact_Pedidos_Auditoria`.
6. Ejecutar prueba A con `false`.
7. Ejecutar prueba B con `true` solamente si prueba A y preflight están verdes.
8. Refrescar el modelo completo.
9. Conectar MCP y generar evidencia.

## Prohibiciones

- No editar archivos `.tmdl` manualmente.
- No agregar los 257 pedidos sin filtros.
- No clasificar FES por intuición.
- No asignar Regiones cuando `PED_REGION` es nulo.
- No inferir SALDO con una sola factura.
- No modificar DAX, relaciones, páginas, SVG o Python.
- No recortar columnas.

## Validaciones obligatorias

- Todas las columnas del preflight SQL: `OK`.
- Parámetro `false`: master y métricas sin cambios.
- Parámetro `true`: cero duplicados, claves nulas, canales fuera de 42–47, regiones nulas, FES/SALDO inferidos o salidas sin factura.
- Todas las filas agregadas: `PED_TEXTO_ESTADO = VBAK SIN ZART`.
- Todas las filas agregadas: `AUD_ESTADO_GENERAL = REVISAR`.
- `4190139455` y `1167577`: sin regresión.
- Resultado/Python: refresh sin error.
- Preguntas y visuales: smoke test sin cambios funcionales.

## Evidencia

Crear:

```text
Docs/AUDITORIA_LIVE/runs/<timestamp>_vbak_master_append/
├── 00_git_before.txt
├── 01_kit_validation.json
├── 02_schema_preflight.csv
├── 03_candidatos_detalle.csv
├── 04_prueba_false.csv
├── 05_control_append.csv
├── 06_snapshot_modelo.csv
├── 07_pedidos_clave.csv
├── 08_smoke_visual.txt
├── RESULTADO.md
└── manifest.json
```

No corregir hallazgos. Si algo falla, dejar `VBAK_APPEND_ACTIVO=false`, documentar el error y detenerse.

## Commits permitidos

Primer commit, solo si prueba A y B están verdes:

```text
feat(vbak): integrar pedidos elegibles en master mediante Power Query
```

Segundo commit:

```text
audit(vbak): registrar validacion del append en modelo vivo
```
