# Próxima auditoría local — Lienzo 00 SLA zonal + tooltip Flujo Operativo

## Objetivo

Validar en Power BI Desktop los cambios aplicados sobre el checkpoint local rescatado `f798586b1a4882be15618bbcc0e6435d108b8fc7`.

Rama a validar:

`fix/resumen-ejecutivo-sla-tooltip`

Los cambios son exclusivamente de presentación/UX del lienzo `00 Resumen Ejecutivo Mayorista` y de una etiqueta de jerarquía. **No se modificó la lógica de cálculo del NS ni ninguna consulta SQL.**

## Regla operativa obligatoria

- No pedir al usuario que transcriba métricas ni resultados.
- Obtener todo lo posible directamente desde Power BI Desktop / modelo vivo.
- No hacer `merge`, `reset`, `restore` ni aplicar cambios de otra rama.
- No implementar `Pedidos_Normal_VBAK` ni optimizaciones de performance en esta corrida.

---

## P0 — Sincronizar exactamente esta rama

```powershell
git fetch origin
git switch fix/resumen-ejecutivo-sla-tooltip
git pull --ff-only origin fix/resumen-ejecutivo-sla-tooltip
git rev-parse HEAD
git status --short
```

El working tree debe quedar limpio antes de abrir Power BI.

---

## P1 — Cargar el PBIP y validar modelo

1. Cerrar cualquier instancia anterior del proyecto si mantiene una definición vieja en memoria.
2. Abrir el PBIP desde esta rama.
3. Esperar que el modelo termine de cargar.
4. No ejecutar refresh completo salvo que Power BI lo requiera para materializar `Medidas_Resumen_UI`.
5. Registrar cualquier `SemanticError`, error TMDL, visual roto o referencia de medida no resuelta.

Criterio: `MODEL_LOAD=GREEN` solamente con 0 errores.

---

## P2 — Validación semántica del SLA

Confirmar directamente en el modelo vivo que la lógica sigue siendo:

- Santiago: `SLA_INTERNO_DH = 4`.
- Regiones: `SLA_INTERNO_DH = 5`.
- `CUMPLE_SLA_INTERNO = DIAS_INTERNOS_DH <= SLA_INTERNO_DH`.
- Promesa cliente estimada: Santiago 5 DH y Regiones 7 DH.

Consultar las mismas medidas antes/después del cambio de UI:

- `RE Pedidos contexto`
- `RE Pedidos en SLA contexto`
- `RE Pedidos fuera SLA contexto`
- `RE NS contexto`
- `RE Promedio contexto DH`
- `RE P90 contexto DH`

No exigir igualdad contra números históricos si la fuente avanzó; sí exigir que no exista diferencia atribuible a las nuevas medidas UI, porque éstas reutilizan las medidas RE anteriores.

---

## P3 — Validación visual del lienzo 00

Abrir `00 Resumen Ejecutivo Mayorista` y verificar:

### Panel Indicadores SLA

Debe mostrar explícitamente:

- `INDICADORES SLA ZONAL`
- `EN SLA`
- `STGO ≤4 · REG ≤5 DH`
- `FUERA DE SLA`
- `STGO >4 · REG >5 DH`

Los porcentajes y cantidades deben coincidir con `RE NS contexto`, `RE Pedidos en SLA contexto` y `RE Pedidos fuera SLA contexto`.

### Resumen mensual

Debe mostrar:

- `Valor neto evaluado`
- `NS interno · SLA zonal`
- `En SLA · Stgo ≤4 / Reg ≤5 DH`
- `Fuera SLA · Stgo >4 / Reg >5 DH`

### Promesa cliente

Debe verse completa, sin texto cortado:

- `Santiago: 4 DH internos + 1 DH = 5 DH cliente`
- `Regiones: 5 DH internos + 2 DH = 7 DH cliente`
- Debe quedar claro que es estimada / sin POD.

### Matriz macroproceso

La fila de Operaciones debe decir:

`2. Operaciones · SLA zonal 3/4 DH`

Administrativo conserva `SLA total 1 DH`.

### Títulos inferiores

Confirmar:

- `PROMEDIO DE DÍAS POR CANAL DE VENTA`
- `PROMEDIO DE DÍAS POR ZONA · SANTIAGO Y REGIONES`

No debe quedar ningún `POR POR`.

---

## P4 — Tooltip de Flujo Operativo Referencial

El visual `flow_operativo` debe reutilizar la página tooltip existente:

- página: `TT Flujo Operativo Referencial`
- page id: `cb613066ebaf4e749a13`

Prueba obligatoria:

1. Pasar el mouse por encima de `FLUJO OPERATIVO (REFERENCIA)` en el lienzo 00.
2. Debe abrirse el tooltip de página con el flujo ampliado.
3. Verificar que el tooltip no requiere clic y no navega fuera del lienzo.
4. Verificar que no bloquea filtros ni interacciones del resto de la página.

Si Power BI no dispara un report-page tooltip directamente sobre el visual tipo `image`, **no crear otro tooltip**. Registrar `IMAGE_TOOLTIP_UNSUPPORTED` y como única corrección permitida agregar una capa transparente exactamente sobre el visual que apunte a la misma página `cb613066ebaf4e749a13`; conservar el SVG original debajo. Publicar esa corrección en la misma rama y volver a probar.

---

## P5 — Evidencia y dictamen

Crear corrida:

```powershell
./Scripts/audit_local/bootstrap_local_audit.ps1 -RunName "l00_sla_zonal_tooltip"
```

Guardar como mínimo:

- captura o evidencia textual de los textos SLA corregidos;
- resultado del hover tooltip;
- métricas RE de control;
- errores de modelo/visuales = 0;
- SHA validado.

`READY_FOR_CHATGPT.md` debe terminar con:

```text
L00_MODEL_LOAD=<GREEN|RED>
L00_SLA_TEXTS=<GREEN|RED>
L00_SLA_SEMANTICS=<GREEN|RED>
L00_PROMESA_CLIENTE=<GREEN|RED>
L00_FLOW_TOOLTIP=<GREEN|RED>
L00_METRIC_REGRESSION=<GREEN|RED>
L00_CERTIFICATION=<GREEN|RED|PARTIAL>
NEXT_STEP=<DONE|FIX_TOOLTIP_OVERLAY|FIX_MODEL|FIX_TEXT>
```

Actualizar `Docs/AUDITORIA_LIVE/LOCAL_LATEST.json`, crear commit de evidencia y hacer push a `origin/fix/resumen-ejecutivo-sla-tooltip`.
