/*
================================================================================
 FLUJO PEDIDOS FES - QUERY COMPLETA
================================================================================
 Objetivo: identificar pedidos originales FES con manifiesto manual (WMS)
 cruzando la cadena VBFA y el manifiesto del WMS.

 Flujo (de arriba a abajo):
   PASO 1 - VBFA C->C : pedido original -> pedido posterior
   PASO 2 - VBFA C->J : pedido posterior -> entrega posterior
   PASO 3 - WMS       : entrega/pedido -> manifiesto manual (fecha min/max)
   PASO 4 - CRUCE     : VBFA entrega (normalizada BIGINT) = WMS entrega
                        O VBFA pedido original = WMS MAD_PEDIDO

 Normalizacion de ENTREGA:
   - VBFA entrega viene como VARCHAR con ceros a la izquierda: '0082389032'
   - WMS entrega viene como NUMERIC: 82389032
   - Se normaliza con CONVERT(BIGINT, ...) que elimina los 00 a la izquierda.
   - NUNCA usar REPLACE(entrega,'0','') porque elimina los 0 internos.

 Universo:
   - El VBFA C-J trae pedidos originales (mayormente FES) con entrega.
   - Puede haber pedidos NORMAL con transporte manual -> por eso la query
     trae TODO el universo y luego se cruza con la master para clasificar.

 Tablas origen:
   - DMF_VTA_PRD.dbo.VBFA_SAP  (flujo documental SAP)
   - PASO_WMS.dbo.MANIFIESTO_H / MANIFIESTO_D (manifiesto manual WMS)

 Conexiones:
   - DMF_VTA_PRD : usuario a_moya (lectura)
   - PASO_WMS    : usuario solo_lectura (lectura)
================================================================================
*/

-- ============================================================================
-- PASO 1: VBFA C->C - pedidos originales con pedido posterior
-- ============================================================================
IF OBJECT_ID('tempdb..#VBFA_CC') IS NOT NULL DROP TABLE #VBFA_CC;
SELECT DISTINCT
    TRY_CONVERT(BIGINT, P1.VBELV) AS PEDIDO_ORIGINAL,
    CONVERT(VARCHAR(20), P1.VBELN) AS PEDIDO_POSTERIOR
INTO #VBFA_CC
FROM [DMF_VTA_PRD].[dbo].[VBFA_SAP] AS P1
WHERE P1.VBTYP_V = 'C' AND P1.VBTYP_N = 'C'
  AND TRY_CONVERT(BIGINT, P1.VBELV) IS NOT NULL;

-- ============================================================================
-- PASO 2: VBFA C->J - pedido posterior -> entrega posterior (normalizada BIGINT)
-- ============================================================================
IF OBJECT_ID('tempdb..#VBFA_CJ') IS NOT NULL DROP TABLE #VBFA_CJ;
SELECT DISTINCT
    CC.PEDIDO_ORIGINAL,
    CONVERT(BIGINT, P2.VBELN) AS ENTREGA_NUM,
    CONVERT(VARCHAR(20), P2.VBELN) AS ENTREGA_RAW,
    COALESCE(
        TRY_CONVERT(DATE, CONVERT(VARCHAR(30), P2.ERDAT), 112),
        TRY_CONVERT(DATE, CONVERT(VARCHAR(30), P2.ERDAT), 105),
        TRY_CONVERT(DATE, CONVERT(VARCHAR(30), P2.ERDAT), 103),
        TRY_CONVERT(DATE, CONVERT(VARCHAR(30), P2.ERDAT))
    ) AS FECHA_ENTREGA
INTO #VBFA_CJ
FROM #VBFA_CC AS CC
INNER JOIN [DMF_VTA_PRD].[dbo].[VBFA_SAP] AS P2
    ON TRY_CONVERT(BIGINT, P2.VBELV) = TRY_CONVERT(BIGINT, CC.PEDIDO_POSTERIOR)
   AND P2.VBTYP_V = 'C' AND P2.VBTYP_N = 'J';

-- ============================================================================
-- PASO 3: MANIFIESTO WMS - entrega/pedido -> fecha min/max del manifiesto manual
-- ============================================================================
IF OBJECT_ID('tempdb..#WMS_MANIFIESTO') IS NOT NULL DROP TABLE #WMS_MANIFIESTO;
SELECT
    CONVERT(BIGINT, MAD_ENTREGA) AS ENTREGA_NUM,
    CONVERT(BIGINT, MAD_PEDIDO)  AS PEDIDO_WMS,
    MIN(MAD_FECHA_EMISION) AS MANIFIESTO_WMS_MIN,
    MAX(MAD_FECHA_EMISION) AS MANIFIESTO_WMS_MAX,
    COUNT(*) AS CANTIDAD_DETALLE
INTO #WMS_MANIFIESTO
FROM [PASO_WMS].[dbo].[MANIFIESTO_D]
WHERE MAD_ENTREGA IS NOT NULL AND MAD_PEDIDO > 1000
  AND YEAR(MAD_FECHA_EMISION) BETWEEN 2000 AND 2100
  AND ISNULL(MAD_ELIMINADO, 0) = 0
GROUP BY CONVERT(BIGINT, MAD_ENTREGA), CONVERT(BIGINT, MAD_PEDIDO);

-- ============================================================================
-- PASO 4: CRUCE FINAL - VBFA C-J con WMS (por ENTREGA y por PEDIDO)
-- Resultado: todo el universo FES con entrega + manifiesto manual si existe
-- ============================================================================
SELECT
    V.PEDIDO_ORIGINAL,
    V.ENTREGA_NUM,
    V.ENTREGA_RAW,
    V.FECHA_ENTREGA,
    -- Manifiesto por ENTREGA
    W1.MANIFIESTO_WMS_MIN AS MANIF_WMS_ENTREGA_MIN,
    W1.MANIFIESTO_WMS_MAX AS MANIF_WMS_ENTREGA_MAX,
    -- Manifiesto por PEDIDO
    W2.MANIFIESTO_WMS_MIN AS MANIF_WMS_PEDIDO_MIN,
    W2.MANIFIESTO_WMS_MAX AS MANIF_WMS_PEDIDO_MAX,
    -- Cierre FES ampliado: manifiesto WMS (entrega o pedido) si existe
    COALESCE(W1.MANIFIESTO_WMS_MAX, W2.MANIFIESTO_WMS_MAX, V.FECHA_ENTREGA) AS FECHA_CIERRE_FES_AMPLIADO,
    CASE
        WHEN W1.ENTREGA_NUM IS NOT NULL THEN 'WMS_POR_ENTREGA'
        WHEN W2.PEDIDO_WMS IS NOT NULL THEN 'WMS_POR_PEDIDO'
        ELSE 'VBFA_SIN_MANIFIESTO_WMS'
    END AS FUENTE_MANIFIESTO
FROM #VBFA_CJ AS V
LEFT JOIN #WMS_MANIFIESTO AS W1
    ON V.ENTREGA_NUM = W1.ENTREGA_NUM
LEFT JOIN #WMS_MANIFIESTO AS W2
    ON V.PEDIDO_ORIGINAL = W2.PEDIDO_WMS
ORDER BY V.PEDIDO_ORIGINAL;

/*
================================================================================
 VERIFICACION DE COBERTURA (validado 2026-08-02)
================================================================================
 - VBFA C-C: 990 pedidos originales con posterior
 - VBFA C-J: 992 pares pedido->entrega
 - WMS manifiesto: 1.943 registros / 1.398 pedidos / 1.894 entregas
 - Cruce por ENTREGA: 1 (pedido 1167577, manifiesto 2026-07-02)
 - Cruce por PEDIDO : 1 (mismo 1167577)
 - CONCLUSION: el universo WMS es casi disjunto del VBFA C-J. La mayoria
   de manifiestos WMS corresponden a pedidos que no pasan por VBFA C->C/C->J
   (canales directos CDQ, pedidos sin posterior, etc.)

 PROXIMO PASO (en Power BI):
   - Cargar #WMS_MANIFIESTO como tabla Dim_WMS_Manifiesto
   - Cruzar por PEDIDO_WMS con la master (Fact_Pedidos_Auditoria) por
     PED_NUMERO_PEDIDO -> identificar cuales son FES y cerrarlos con manifiesto
================================================================================
*/
