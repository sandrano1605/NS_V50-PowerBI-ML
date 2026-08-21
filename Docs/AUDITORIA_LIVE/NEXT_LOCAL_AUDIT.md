# Próxima auditoría local — Tooltip real del Flujo Operativo

## Objetivo

Certificar en Power BI Desktop la implementación soportada del hover sobre `FLUJO OPERATIVO (REFERENCIA)` del lienzo `00 Resumen Ejecutivo Mayorista`.

La solución ya NO usa:

- visual nativo `image` como fuente del hover;
- overlay transparente;
- shape superpuesto.

La solución implementada usa:

```text
Medidas_Flujo_UI[RE UI Flujo Operativo SVG]
        ↓ ImageUrl
flow_operativo = tableEx de una sola celda
        ↓ report-page tooltip (Canvas)
TT Flujo Operativo Referencial
page id = cb613066ebaf4e749a13
```

Rama:

`fix/resumen-ejecutivo-sla-tooltip`

El HEAD debe contener como ancestro el cambio funcional `bbf6715fefc36a311eee4f86c60ce2695884ca59`.

---

## Regla operativa obligatoria

- No pedir al usuario que transcriba métricas ni resultados.
- No crear overlays, shapes, botones ni un segundo tooltip.
- No modificar SQL, Fact, relaciones, SLA ni medidas RE.
- No implementar `Pedidos_Normal_VBAK` en esta corrida.
- La tarea del LLM local es validar y publicar evidencia; si algo falla, reportar el error exacto para que ChatGPT lo corrija.

---

## P0 — Rescatar estado local antes de sincronizar

Ejecutar primero:

```powershell
git branch --show-current
git status --short
git diff --stat
```

Si el working tree está sucio, NO hacer pull/reset/restore. Crear antes un checkpoint de rescate en una rama separada y hacer push. Solo después volver a `fix/resumen-ejecutivo-sla-tooltip`.

Luego:

```powershell
git fetch origin
git switch fix/resumen-ejecutivo-sla-tooltip
git pull --ff-only origin fix/resumen-ejecutivo-sla-tooltip
git rev-parse HEAD
git status --short
```

Criterio: working tree limpio y `bbf6715fefc36a311eee4f86c60ce2695884ca59` ancestro del HEAD.

---

## P1 — Preflight estático

Verificar en archivos del HEAD:

### Modelo

Debe existir:

`NS.SemanticModel/definition/tables/Medidas_Flujo_UI.tmdl`

Debe contener:

- tabla oculta `Medidas_Flujo_UI`;
- medida `RE UI Flujo Operativo SVG`;
- `dataCategory: ImageUrl`;
- SVG con las mismas reglas visibles:
  - Administrativo 1 DH;
  - Operaciones STGO 3 DH / Regiones 4 DH;
  - Interno STGO 4 DH / Regiones 5 DH;
  - Promesa cliente STGO 5 DH / Regiones 7 DH.

`model.tmdl` debe registrar `Medidas_Flujo_UI`.

### Visual fuente

Archivo:

`NS.Report/definition/pages/71af1998e2cb472d9799/visuals/flow_operativo/visual.json`

Debe cumplir:

```text
visualType=tableEx
Entity=Medidas_Flujo_UI
Measure=RE UI Flujo Operativo SVG
visualTooltip.show=true
visualTooltip.type=Canvas
visualTooltip.section=cb613066ebaf4e749a13
```

No debe existir `flow_tooltip_overlay`.

### Página tooltip

`NS.Report/definition/pages/cb613066ebaf4e749a13/page.json`:

```text
displayName=TT Flujo Operativo Referencial
type=Tooltip
visibility=HiddenInViewMode
```

Guardar preflight en:

`raw/flow_tooltip_preflight.md`

---

## P2 — Abrir PBIP y validar modelo

1. Cerrar la instancia anterior del proyecto para no mantener definición vieja en memoria.
2. Abrir el PBIP desde el HEAD sincronizado.
3. Esperar carga completa.
4. No ejecutar refresh completo de fuentes salvo que Power BI lo requiera para materializar la nueva tabla UI de una fila.
5. Verificar:
   - `SemanticError = 0`;
   - errores TMDL = 0;
   - referencias rotas = 0;
   - existe `Medidas_Flujo_UI` en el modelo;
   - la medida `RE UI Flujo Operativo SVG` devuelve una URL de imagen válida.

Guardar:

`raw/flow_tooltip_model_load.md`

---

## P3 — Validación visual del flujo

Abrir `00 Resumen Ejecutivo Mayorista`.

Verificar que el bloque `FLUJO OPERATIVO (REFERENCIA)`:

- se vea completo;
- conserve los siete hitos;
- no tenga caja azul, overlay o shape encima;
- no muestre encabezado de tabla visible;
- no muestre total ni scrollbar;
- no altere la posición del resto de los visuales;
- muestre correctamente:
  - `ADMINISTRATIVO (1 DH)`;
  - `OPERACIONES: STGO 3 DH · REG. 4 DH`;
  - `INTERNO: STGO 4 DH · REGIONES 5 DH`;
  - `PROMESA CLIENTE: STGO 5 DH · REGIONES 7 DH`.

Guardar evidencia/captura si la automatización local lo permite.

---

## P4 — Prueba obligatoria del hover

Esta prueba define el cierre.

1. Posicionar el cursor sobre el SVG visible dentro de `flow_operativo`.
2. NO hacer clic.
3. Esperar el tiempo normal de aparición del tooltip.
4. Debe mostrarse la página `TT Flujo Operativo Referencial`.
5. Confirmar que desaparece al retirar el cursor.
6. Repetir en al menos dos zonas del SVG (título y zona de hitos) para comprobar que el área útil responde.

Criterio:

```text
FLOW_TOOLTIP_HOVER=GREEN
```

solo si el tooltip aparece realmente por hover en Power BI Desktop.

Si no aparece:

- NO crear overlay;
- NO convertir a shape;
- NO declarar GREEN;
- capturar el comportamiento real y cualquier propiedad que Power BI haya reescrito al guardar;
- reportar `FLOW_TOOLTIP_HOVER=RED` para corrección de ChatGPT.

Guardar:

`raw/flow_tooltip_hover.md`

---

## P5 — Regresión mínima del lienzo 00

Consultar directamente desde el modelo vivo:

- `RE Pedidos contexto`;
- `RE Pedidos en SLA contexto`;
- `RE Pedidos fuera SLA contexto`;
- `RE NS contexto`;
- `RE Promedio contexto DH`;
- `RE P90 contexto DH`.

La nueva tabla UI no puede alterar estos valores.

Validar además que permanecen visibles:

- `STGO ≤4 · REG ≤5 DH` para En SLA;
- `STGO >4 · REG >5 DH` para Fuera SLA;
- promesa cliente 5/7 DH.

Guardar:

`raw/flow_tooltip_regression.md`

---

## P6 — Evidencia final

Crear corrida:

```powershell
./Scripts/audit_local/bootstrap_local_audit.ps1 -RunName "l00_flow_tooltip_tableex"
```

Actualizar `Docs/AUDITORIA_LIVE/LOCAL_LATEST.json` y publicar evidencia en la misma rama.

`READY_FOR_CHATGPT.md` debe terminar exactamente con:

```text
FLOW_TABLEEX_PREFLIGHT=<GREEN|RED>
FLOW_MODEL_LOAD=<GREEN|RED>
FLOW_SVG_RENDER=<GREEN|RED>
FLOW_TOOLTIP_HOVER=<GREEN|RED>
FLOW_METRIC_REGRESSION=<GREEN|RED>
FLOW_TOOLTIP_CERTIFICATION=<GREEN|RED>
NEXT_STEP=<DONE|FIX_TABLEEX_TOOLTIP|FIX_MODEL|FIX_RENDER>
```

`FLOW_TOOLTIP_CERTIFICATION=GREEN` requiere obligatoriamente:

- preflight GREEN;
- modelo GREEN;
- SVG visible correctamente;
- hover real GREEN;
- regresión GREEN.

No declarar cierre por mera presencia de `visualTooltip` en JSON.
