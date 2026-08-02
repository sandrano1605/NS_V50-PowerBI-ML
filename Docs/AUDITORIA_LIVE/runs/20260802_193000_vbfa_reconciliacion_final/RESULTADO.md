# RESULTADO - Reconciliacion VBFA (queries directas SELECT)

## Estado: AMARILLO (VBFA probado con queries directas; SP no ejecutable por permiso)

## Hallazgo principal
- El SP dbo.STP_GET_VBFA_TRAMO_FILTRO NO es visible para el usuario SQL de auditoria
  -> no se ejecuto el SP. Se probaron las queries SELECT directas contra VBFA_SAP y VTTP_SAP.

## Logica del SP descubierta por queries (no por memoria)
- 'M-J' NO es un literal: representa el rango VBTYP_V IN ('M','J')
- 'C' = tipo de documento posterior = PEDIDO (VBTYP_N='C')
- Tramo valido: VBTYP_V IN ('M','J') AND VBTYP_N='C'
- Ventana 01-07 a 02-07 (TRY_CONVERT 105): 8.001 filas / 607 pedidos / 355 doc post
- Borde 30-06 a 03-07: 9.663 filas / 755 pedidos / 429 doc post

## Reconciliacion
- VBFA_SAP: VBELV (pedido original), VBELN (documento posterior), ERDAT/ERZET (fecha/hora)
- VTTP_SAP: VBELN, TKNUM (manifiesto/transporte), ERDAT, PKSTA
- Los codigos VBTYP_V en VBFA: M, J, C, H, T, K, O (tipos de documento anterior)
- Los codigos VBTYP_N: R, J, M, Q, X, C, 8, O, H, T, N, S (tipos posterior)

## Limites
- No se pudo leer la definicion completa del SP (permiso de metadata)
- La interpretacion de M-J como rango es una hipotesis confirmada por datos (25316 filas vs 0 literal)
- Se requiere validacion de negocio sobre que documentos M y J representan
- ERDAT es varchar dd-MM-yyyy; se usa TRY_CONVERT estilo 105
