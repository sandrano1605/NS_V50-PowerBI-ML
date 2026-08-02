# RESULTADO - Reconciliacion VBFA (queries SELECT directas)

## Estado: AMARILLO

## Ejecucion
- NO se ejecuto el SP (permiso EXECUTE denegado / SP no visible para a_moya)
- Se probaron queries SELECT directas contra dbo.VBFA_SAP y dbo.VTTP_SAP (solo lectura, sin modificar BD)
- Conexion: SQL auth a_moya -> 128.1.3.21/DMF_VTA_PRD OK

## Hallazgos

### 1. Logica del SP descubierta por datos
- 'M-J' NO es literal: es el rango VBTYP_V IN ('M','J')
- 'C' = tipo documento posterior = PEDIDO (VBTYP_N='C')
- Codigos VBTYP_V en VBFA: M, J, C, H, T, K, O (tipos anteriores)
- Codigos VBTYP_N: R, J, M, Q, X, C, 8, O, H, T, N, S (tipos posteriores)

### 2. Granularidad del tramo M->C
- TOTAL = 25.316 filas
- PEDIDOS_ORIGINALES (VBELV distintos) = 1.872
- DOCUMENTOS_POSTERIORES (VBELN distintos) = 990
- Nota: hay filas repetidas (1.706 grupos duplicados, ej. 28 repeticiones por pedido)
  -> VBFA tiene duplicados a la granularidad VBELV+VBELN+ERDAT+ERZET

### 3. Ventanas
- Borde 30-06 a 03-07: 9.663 filas / 755 pedidos / 429 doc post
- Solicitada 01-07 a 02-07: 0 filas (no hay eventos en ese rango exacto; datos hasta 31-07-2026)

### 4. Pedidos clave
- 4190139455 y 1167577 NO aparecen en el tramo VBFA M->C (no tienen eventos VBFA con esos IDs)
- Su cierre fue por manifiesto (modelo OK). VBFA no los referencia directamente.

### 5. VTTP_SAP (manifiesto/transporte)
- Esquema: VBELN, TKNUM, ERDAT, ERZET, PKSTA
- 50 filas de muestra exportadas

## Limitaciones
- Definicion completa del SP no disponible (sin permiso de metadata)
- La interpretacion de M-J como rango es hipotesis confirmada por datos (25316 vs 0 literal)
- Se requiere validacion de negocio sobre el significado de documentos M y J
- ERDAT_DATE tiene datos con valores que SQL Server no puede convertir en ciertas expresiones
  (se uso TRY_CONVERT(date, ERDAT, 105) como workaround)

## Dictamen
| Area | Estado |
|---|---|
| Auditor estatico | VERDE |
| Modelo vivo | VERDE |
| Pedidos clave | VERDE |
| Contrato Python | AMARILLO (5 categorias) |
| VBFA (queries) | AMARILLO - logica probada, SP no ejecutable |
| Recorte columnas | BLOQUEADO |
| Columnas autorizadas | 0 |
