# RESULTADO AUDITORÍA LOCAL — VALIDACIÓN POST-FIX

RUN_ID: 20260811_225907_post_fix_validacion_viva_00756db
SHA auditado: 00756dbe763335879daf14ec466dcc7514361023
Timestamp: 2026-08-11 22:59:07
Estado: COMPLETED

## Objetivo

Validar los tres fixes aplicados (FIND-002A, INC-011, INC-007B) en modelo vivo post-refresh.

## Resultados

### FIND-002A → GREEN
- `RE TT Título` usa `CONCATENATEX(..., Dim_Rango_Entrega[Rango], ASC)` (Rango como sort-by, no OrdenRango).
- Estado: Ready (sin SemanticError). DataType: String.
- **12/12 combinaciones renderizan correctamente**, incluyendo:
  - "Universo cerrado" (sin filtro)
  - "1. Flujo Normal + 2. FES (incluye FES + Saldo)" (multiselect)
  - "1. Flujo Normal + 2. FES (incluye FES + Saldo) · Santiago" (flujo+zona)

### INC-011 → GREEN
- **0 cerrados con DIAS_INTERNOS_DH = BLANK** (anterior: 55).
- Los 55 pedidos con fecha centinela `2020-09-24 22:47` ahora tienen:
  - `FECHA_DESPACHO = null` (TRP < PED_FECHA_HORA → null)
  - `ES_CERRADO = FALSE` (sin cierre oficial)
  - Estado: `PENDIENTE FACTURA` (no tienen factura asignada)
- Denominador RE ahora es 100% válido: 1.941 evaluables, todos con DH calculable.

### INC-007B → GREEN
- Fallback TRP eliminado de `FECHA_MANIFIESTO`. Solo VBFA/VTTP.
- 439 FES totales, 437 cerrados, **437/437 con manifiesto real**.
- **0 FES cerrados sin manifiesto**. 0 pendientes de manifiesto.

### INC-015 → ORANGE / pendiente AEDAT
- Cobertura: 1.131/1.941 = 58,3% (sin cambio respecto a la corrida previa).
- Hipótesis de ceros a la izquierda descartada en dos corridas independientes.
- Pendiente: consulta VBAP_SAP sin `AEDAT>=GETDATE()-730`.

## Baseline vivo post-refresh

| Métrica | Valor |
|---|---|
| Total Fact_Tracking | 2.097 |
| Cerrados (ES_CERRADO=TRUE) | 1.941 |
| Evaluables RE | 1.941 |
| En SLA | 1.580 |
| Fuera SLA | 361 |
| RE NS | 81,40% |
| PromDH | 3,49 |
| P90 DH | 8 |

## Regresión

10/11 casos del `regression_cases.csv` OK. Solo `4190139455` difiere (histórico FES → actual NORMAL), explicado por regla de pedido posterior C-C.

## Cambios vs corrida previa

| Métrica | Antes | Ahora | Explicación |
|---|---|---|---|
| Cerrados sin DH | 55 | 0 | Fix INC-011 |
| Evaluables RE | 1.934 | 1.941 | Fix + refresh |
| FES fallback TRP | Código | Eliminado | Fix INC-007B |
| RE TT Título | SemanticError | Ready (12/12) | Fix FIND-002A |
