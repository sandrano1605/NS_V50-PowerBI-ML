# LLM local · Implementación del lienzo 02

## Recuperación

```powershell
git fetch origin
git switch work/ns-lienzo-02-ingreso-pedidos
git pull --ff-only origin work/ns-lienzo-02-ingreso-pedidos
git status --short
git rev-parse HEAD
```

Leer completamente:

```text
Docs/AUDITORIA_LIVE/REQ011_LIENZO_02_INGRESO_PEDIDOS.md
Docs/AUDITORIA_LIVE/latest/lienzo_02_visual_matrix.csv
```

## Tarea única

Implementar y validar la página existente:

```text
ID: df1cb253a6314642a469
Nombre actual: 02 Entrada y Cierre
Nombre final: 02 Ingreso de Pedidos
```

No crear otra página.

## Orden obligatorio

1. Abrir `NS.pbip`.
2. Ejecutar un refresh de baseline y registrar conteos actuales.
3. Auditar la calidad de `Fact_Tracking[PED_FECHA_HORA]`:
   - cantidad con hora válida;
   - cantidad `00:00:00`;
   - desglose entre master original y `VBAK SIN ZART`.
4. Verificar que los pedidos VBAK combinen `ERDAT + ERZET`.
5. Si los VBAK contienen solo fecha, corregirlo desde Power Query Desktop. No editar TMDL manualmente.
6. Crear en `Fact_Tracking` las columnas `TRAMO_HORA_INGRESO` y `ORDEN_TRAMO_HORA_INGRESO`.
7. Buscar medidas existentes equivalentes a `IN Pedidos`, `IN Líneas` e `IN Unidades`.
8. Crear únicamente las que no existan y ubicarlas en el display folder existente `04. Análisis Fuera SLA\Carga y SLA`.
9. Construir la página usando visuales nativos.
10. Mantener la página oculta mientras se construye.
11. Ejecutar refresh completo.
12. Conectar MCP y reconciliar métricas.
13. Hacer smoke test visual.
14. Mostrar la página en vista normal solo cuando todo esté verde.

## Visuales obligatorios

### V01 · Matriz día de semana

- Filas: `Dim_Fecha[Dia_Semana]`.
- Valores: pedidos, líneas y unidades.
- Barras de datos por medida.
- Orden lunes a domingo.

### V02 · Corte logístico 14:30

- Columnas 100% apiladas.
- Eje: día de semana.
- Leyenda: hasta 14:30, después de 14:30, sin hora válida.
- Valor: pedidos.
- Tooltips: pedidos, líneas y unidades.

### V03 · Pedidos por día del mes

- Columnas apiladas por clasificación.
- Eje 1–31.
- Línea promedio del panel Analytics.

### V04 · Líneas por día del mes

- Misma estructura que V03.

### V05 · Unidades por día del mes

- Misma estructura que V03.

## Decisiones ya tomadas

- No usar Python.
- No usar SVG DAX.
- No usar Image URL.
- No usar field parameters en esta primera versión.
- Usar tres gráficos mensuales separados; es más rápido, auditable y permite comparar escalas sin medidas dinámicas.
- La línea de promedio se configura en Analytics; no crear medidas de promedio.
- Segmentar las barras mensuales por `Fact_Tracking[CLASIFICACION]`.
- Usar `Dim_Fecha[Momento_Mes]` como segmentador para identificar cierre de mes con últimos 7 días hábiles reales.

## Prohibiciones

- No crear una página nueva.
- No modificar páginas 00, 01 o 01.1 salvo smoke test.
- No cambiar reglas SLA, FES, SALDO o cierre.
- No modificar Python de `Resultado`.
- No recortar columnas.
- No clasificar `00:00:00` como antes de 14:30 sin demostrar que la hora es real.
- No ocultar la categoría `Sin hora válida`.
- No crear más de tres medidas nuevas.
- No crear nuevas tablas de medidas ni nuevos grupos de display folders.
- No guardar visuales rotos o con campos no resueltos.

## Evidencia

Crear:

```text
Docs/AUDITORIA_LIVE/runs/<timestamp>_lienzo_02_ingreso/
├── 00_git_before.txt
├── 01_baseline_modelo.csv
├── 02_calidad_hora.csv
├── 03_medidas_reutilizadas_creadas.csv
├── 04_reconciliacion_dia_semana.csv
├── 05_reconciliacion_hora_1430.csv
├── 06_reconciliacion_dia_mes.csv
├── 07_cobertura_lineas_unidades.csv
├── 08_visual_inventory.csv
├── 09_smoke_test.txt
├── RESULTADO.md
└── manifest.json
```

## Controles de cierre

- Proyecto abre sin error.
- Refresh completo verde.
- Matriz semanal reconcilia con total.
- Tramos horarios reconcilian con total.
- Tendencias mensuales reconcilian con total.
- Flujo apilado reconcilia con cada barra.
- Cobertura de líneas/unidades documentada.
- Página 02 visible y profesional.
- Página 00, 01 y 01.1 sin regresión.
- Ningún hover muestra código.

## Commits

Primer commit funcional:

```text
feat(lienzo-02): implementar analisis de ingreso de pedidos
```

Segundo commit de evidencia:

```text
audit(lienzo-02): validar ingreso semanal horario y mensual
```

No corregir hallazgos fuera del alcance. Documentarlos y detenerse si impiden la reconciliación.
