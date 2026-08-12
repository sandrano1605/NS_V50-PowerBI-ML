# RESULTADO — Cierre INC-015

RUN_ID: 20260811_232642_post_fix_tracking_inc015_18f0baa
SHA: 18f0baa24089742dab35f00300506cb8ce10856f
Estado: COMPLETED

## INC-015 → CAUSA_VISTA_VBAP_SAP (confirmado)

Clasificación de los 810 pedidos sin match en VBAP:

| Estado | Cantidad | Diagnóstico |
|---|---|---|
| DENTRO_730_EN_VBAK | 782 | Existen en VBAK con fecha reciente. Deberían estar en VBAP_SAP. No están → CAUSA_VISTA_VBAP_SAP |
| AUSENTE_VBAK | 28 | Fuera de ventana 90-días VBAK |
| EXCLUIDO_AEDAT | 0 | Hipótesis AEDAT descartada |

Cobertura actual: 1.131/1.941 = 58,3%
Cobertura potencial: 1.913/1.941 = 98,6%

## Fixes validados (regresión)
- FIND-002A: RE TT Título sin SemanticError ✓
- INC-011: 0 cerrados sin DH ✓
- INC-007B: 0 FES cerrados sin manifiesto ✓
