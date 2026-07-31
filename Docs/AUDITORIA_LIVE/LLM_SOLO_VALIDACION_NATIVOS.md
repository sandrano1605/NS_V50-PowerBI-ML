# VALIDACIÓN FINAL DEL MODELO VIVO — SOLO PRUEBA Y EVIDENCIA

## Regla absoluta

El LLM local no debe modificar `NS.Report`, `NS.SemanticModel`, DAX, TMDL, Power Query, Python, relaciones, preguntas, títulos, posiciones ni visuales. ChatGPT ya realizó la migración funcional.

## Recuperación

```powershell
git switch work/ns-live-audit
git fetch origin
git pull --ff-only origin work/ns-live-audit
git status --short
git rev-parse HEAD
```

El working tree debe estar limpio. El SHA debe coincidir con el último commit remoto indicado por ChatGPT.

## Pruebas obligatorias

1. Abrir `NS.pbip`.
2. Ejecutar **Actualizar todo**.
3. Conectar MCP al modelo vivo.
4. Confirmar que Power BI carga todas las páginas sin visual roto.
5. Confirmar que ningún visual muestra `data:image/svg+xml`, XML, URI o código DAX en hover.
6. Revisar las 26 filas de `Docs/AUDITORIA_LIVE/latest/business_questions_matrix.csv` y validar que título, pregunta, medida y cohorte coincidan con el resultado real.
7. Validar especialmente:
   - `00 Resumen Ejecutivo Mayorista`: tarjetas, donut, evolución 3M, resumen y pedidos críticos.
   - `01 Análisis Fuera SLA`: cuatro preguntas y tabla crítica.
   - `01.1 Auditoría por Pedido`: estado general y trazabilidad por hito.
   - `05 Tracking Operativo`: KPI, ruta, auditoría, clasificación y pedido seleccionado.
   - Tooltips FES, indicador y auditoría.
8. Confirmar que los visuales nativos responden a filtros y que los tooltips muestran valores de negocio, nunca código.

## Reconciliaciones

- La suma del donut `DISTRIBUCIÓN POR FLUJO` debe coincidir con `[RE Pedidos contexto]`.
- El combo 3M debe coincidir por mes con:
  - `[M3 Promedio administrativo DH]`
  - `[M3 Promedio operaciones DH]`
  - `[M3 Promedio total DH]`
- La tarjeta `RESUMEN DEL PERÍODO` debe coincidir con las siete medidas proyectadas.
- Las tablas críticas deben contener hasta 15 pedidos, ordenados por `[RE TT Días Top 10]` descendente, sin `RE TT Estado SVG`.
- Las tablas de hitos deben ordenar por `ORDEN_HITO` y mostrar `ESTADO_KPI` textual.
- La ficha de pedido debe mostrar flujo, zona, DH, SLA, cumplimiento y cierre del pedido seleccionado.

## Regresión obligatoria

- Pedidos evaluables: `1.616`
- Pedidos fuera SLA: `360`
- NS: `77,72%`
- Clientes fuera SLA: `251`
- Recurrente 3M: `3`
- Recurrente 2M: `27`
- Puntual 1M: `221`
- Santiago: SLA interno `4 DH`
- Regiones: SLA interno `5 DH`
- Promesa Santiago: `5 DH`
- Promesa Regiones: `7 DH`
- `4190139455`: OK
- `1167577`: OK
- FES/FES + SALDO: último manifiesto; última fecha de transporte válida solo como respaldo cuando el manifiesto no esté informado y represente el cierre oficial.

## Evidencia

Crear:

`Docs/AUDITORIA_LIVE/runs/<timestamp>_validacion_nativos_modelo_vivo/`

Con:

- `00_resumen.md`
- `01_refresh.txt`
- `02_visuales_nativos.csv`
- `03_preguntas_negocio.csv`
- `04_reconciliacion_medidas.csv`
- `05_hover_sin_codigo.csv`
- `06_regresion_global.csv`
- `07_pedidos_clave.csv`
- `08_limitaciones.md`
- `RESULTADO.md`
- `manifest.json`

## Protección del trabajo funcional

Si Power BI Desktop normaliza archivos al abrir o cerrar:

```powershell
git restore NS.Report NS.SemanticModel
```

Después confirmar que solo `Docs/AUDITORIA_LIVE` tenga cambios.

## Único commit permitido

```powershell
git add Docs/AUDITORIA_LIVE
git commit -m "audit(modelo): validar visuales nativos y modelo vivo"
git push origin work/ns-live-audit
```

## Estado

- **VERDE:** refresh OK, 26/26 preguntas coherentes, métricas reconciliadas, regresión exacta y cero hover técnico.
- **AMARILLO:** cálculos correctos pero existe problema de render, ajuste de espacio o formato.
- **ROJO:** refresh falla, una medida difiere, una pregunta no coincide, aparece código o un visual queda roto.
