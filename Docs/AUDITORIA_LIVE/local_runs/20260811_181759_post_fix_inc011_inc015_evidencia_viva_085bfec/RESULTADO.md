# RESULTADO AUDITORÍA LOCAL

RUN_ID: 20260811_181759_post_fix_inc011_inc015_evidencia_viva_085bfec
SHA auditado: 085bfec7531f57bd5894641e397a0ce99938680d
Timestamp: 2026-08-11 18:17:59
Estado: COMPLETED

## Objetivo

Completar los pendientes de la corrida `20260811_123620` (INC-011 e INC-015) que
quedaron sin resolver por falla del tool DAX, y revalidar FIND-002A en vivo.

## Hallazgos

### FIND-002A — ROJO confirmado (sin regresión en números)

- `RE TT Título` tiene estado `SemanticError` en el modelo vivo.
- Error: "No se puede determinar un valor único para la columna OrdenRango".
- Falló en las 12 combinaciones de flujo/zona evaluadas.
- Los valores numéricos (Pedidos, Valor, PromDH, P90DH, FueraSLA) son correctos
  y consistentes con el multiselect (Normal+FES=1932 ≠ Todos=1934).

### INC-011 — causa raíz identificada

- 55 cerrados sin `DIAS_INTERNOS_DH` (el corte previo contó 64; el universo
  cambió con el refresh, no comparar entre cortes).
- 100% (55/55) con `FECHA_CIERRE=FECHA_DESPACHO=2020-09-24 22:47:00` (fecha
  centinela) anterior a la creación → `FnDH` retorna null (Fin < Inicio).
- 55/55 sin factura ni manifiesto. Todos NORMAL.
- Lista completa en `raw/inc011_cerrados_sin_dh.md`.

### INC-015 — causa raíz identificada (hipótesis de ceros FALSO_POSITIVO)

- Cobertura exacta: 1.128/1.934 = 58,3%.
- NO hay ceros a la izquierda en ninguna tabla; match numérico no mejora;
  derivados 7↔10 = 0 → la hipótesis de padding se descarta.
- 806 sin match: 778 (96,5%) existen en `Pedidos_Normal_VBAK`.
- La causa es la fuente `VBAP_SAP` (filtro `AEDAT>=GETDATE()-730` o contenido
  de la vista), no el join por clave.

### INC-007B — fallback TRP: impacto actual 0

- 439 FES; 437 cerrados; 437 con manifiesto real (100%).
- 0 FES cerrados por TRP. 2 FES sin manifiesto ni TRP (1167574, 4190139472),
  ambos INCOMPLETO y no cerrados.
- El fallback existe en código (líneas 353-358 de Fact_Tracking.tmdl).

## Pruebas vivas

- 42 filas en `07_live_results.csv`.
- 12 combinaciones FIND-002A + universo + NS + FES + VBAP + regresión.

## Regresión

- 10/11 casos del `regression_cases.csv` coinciden.
- Discrepante: `4190139455` (histórico FES → actual NORMAL). Explicación:
  la regla FES exige pedido posterior C-C; el pedido tiene
  `REGLA_CLASIFICACION_FES='SIN PEDIDO POSTERIOR C-C'`. Implementación
  actual consistente; el CSV no se edita.

## Estado final

- Paquete de 15 archivos + raw/ generado.
- Validación: pendiente de ejecutar `validate_local_evidence.py`.
- Sin cambios funcionales: solo `Docs/AUDITORIA_LIVE/local_runs/<RUN_ID>/**`
  y `LOCAL_LATEST.json`.
- Working tree con cambios preexistentes en `NS.Report/**` declarados en el
  manifest y NO incluidos en el commit de evidencia.
