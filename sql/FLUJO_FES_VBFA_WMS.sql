/*
================================================================================
 FLUJO PEDIDOS FES - QUERY COMPLETA
================================================================================
 Objetivo: identificar pedidos originales FES con manifiesto manual (WMS)
 cruzando la cadena VBFA y el manifiesto del WMS.

 NOTA IMPORTANTE: la query NO tiene filtro de FES. El VBFA C->J trae TODO el
 universo de pedidos con entrega posterior, sin importar su clasificacion.
 Esto es a proposito: puede haber pedidos NORMAL/SALDO con transporte manual
 cargado en el WMS, y pedidos FES sin transporte. El filtro de clasificacion
 se aplica DESPUES al cruzar con la master (Fact_Pedidos_Auditoria) por
 PED_NUMERO_PEDIDO.

 Flujo (de arriba a abajo):
   PASO 0 - VBFA C->J : pedido original -> entrega posterior (TODO EL UNIVERSO)
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
-- PASO 0: VBFA C->J - TODO EL UNIVERSO pedido original -> entrega posterior
-- SIN filtro de FES. Esta es la primera consulta del flujo.
-- ============================================================================
SELECT DISTINCT
    TRY_CONVERT(BIGINT, P1.VBELV) AS PEDIDO_ORIGINAL,
    CONVERT(BIGINT, P2.VBELN)     AS ENTREGA_NUM,
    CONVERT(VARCHAR(20), P2.VBELN) AS ENTREGA_RAW,
    COALESCE(
        TRY_CONVERT(DATE, CONVERT(VARCHAR(30), P2.ERDAT), 112),
        TRY_CONVERT(DATE, CONVERT(VARCHAR(30), P2.ERDAT), 105),
        TRY_CONVERT(DATE, CONVERT(VARCHAR(30), P2.ERDAT), 103),
        TRY_CONVERT(DATE, CONVERT(VARCHAR(30), P2.ERDAT))
    ) AS FECHA_ENTREGA
FROM [DMF_VTA_PRD].[dbo].[VBFA_SAP] AS P1
INNER JOIN [DMF_VTA_PRD].[dbo].[VBFA_SAP] AS P2
    ON TRY_CONVERT(BIGINT, P2.VBELV) = TRY_CONVERT(BIGINT, P1.VBELN)
   AND P2.VBTYP_V = 'C' AND P2.VBTYP_N = 'J'
WHERE TRY_CONVERT(BIGINT, P1.VBELV) IS NOT NULL;
-- NOTA: P1 sin filtro VBTYP_V/VBTYP_N -> trae todos los originales con entrega
--       (FES, NORMAL, SALDO, FES+SALDO - todo el universo con C->J)

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
-- PASO 3: MANIFIESTO WMS - TODOS los registros con campos validos
-- AUDITORIA 2026-08-02: el filtro MAD_PEDIDO > 1000 era INCORRECTO
-- (87% de MANIFIESTO_D tiene MAD_PEDIDO NULL/0/1; reducia 17.542 a 1.943 filas).
-- Ahora se trae todo registro con MAD_PEDIDO, MAD_ENTREGA o MAD_NRO_SAP valido.
-- ============================================================================
IF OBJECT_ID('tempdb..#WMS_MANIFIESTO') IS NOT NULL DROP TABLE #WMS_MANIFIESTO;
SELECT
    CONVERT(BIGINT, MAD_PEDIDO)  AS PEDIDO_WMS,
    CONVERT(BIGINT, MAD_ENTREGA) AS ENTREGA_WMS,
    CONVERT(BIGINT, MAD_NRO_SAP) AS NRO_SAP_WMS,
    MIN(MAD_FECHA_EMISION) AS MANIFIESTO_WMS_MIN,
    MAX(MAD_FECHA_EMISION) AS MANIFIESTO_WMS_MAX,
    COUNT(*) AS CANTIDAD_DETALLE
INTO #WMS_MANIFIESTO
FROM [PASO_WMS].[dbo].[MANIFIESTO_D]
WHERE (MAD_PEDIDO IS NOT NULL AND MAD_PEDIDO NOT IN (0,1))
   OR (MAD_ENTREGA IS NOT NULL AND MAD_ENTREGA NOT IN (0,1))
   OR (MAD_NRO_SAP IS NOT NULL AND MAD_NRO_SAP NOT IN (0,1))
GROUP BY CONVERT(BIGINT, MAD_PEDIDO), CONVERT(BIGINT, MAD_ENTREGA), CONVERT(BIGINT, MAD_NRO_SAP);

-- ============================================================================
-- PASO 4: CRUCE FINAL - VBFA C-J con WMS por TRES claves
--   W1: VBFA.ENTREGA_NUM = WMS.ENTREGA_WMS
--   W2: VBFA.PEDIDO_ORIGINAL = WMS.PEDIDO_WMS
--   W3: VBFA.ENTREGA_NUM = WMS.NRO_SAP_WMS (o PEDIDO_ORIGINAL = NRO_SAP_WMS)
-- AUDITORIA 2026-08-02: la union de las 3 claves elevo la vinculacion de 3 a 65.
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
    -- Manifiesto por NRO_SAP
    W3.MANIFIESTO_WMS_MIN AS MANIF_WMS_NRO_MIN,
    W3.MANIFIESTO_WMS_MAX AS MANIF_WMS_NRO_MAX,
    -- Cierre FES ampliado: manifiesto WMS (entrega, pedido o NRO_SAP) si existe
    COALESCE(W1.MANIFIESTO_WMS_MAX, W2.MANIFIESTO_WMS_MAX, W3.MANIFIESTO_WMS_MAX, V.FECHA_ENTREGA) AS FECHA_CIERRE_FES_AMPLIADO,
    CASE
        WHEN W1.ENTREGA_WMS IS NOT NULL THEN 'WMS_POR_ENTREGA'
        WHEN W2.PEDIDO_WMS IS NOT NULL THEN 'WMS_POR_PEDIDO'
        WHEN W3.NRO_SAP_WMS IS NOT NULL THEN 'WMS_POR_NRO_SAP'
        ELSE 'VBFA_SIN_MANIFIESTO_WMS'
    END AS FUENTE_MANIFIESTO
FROM #VBFA_CJ AS V
LEFT JOIN #WMS_MANIFIESTO AS W1
    ON V.ENTREGA_NUM = W1.ENTREGA_WMS
LEFT JOIN #WMS_MANIFIESTO AS W2
    ON V.PEDIDO_ORIGINAL = W2.PEDIDO_WMS
LEFT JOIN #WMS_MANIFIESTO AS W3
    ON (V.ENTREGA_NUM = W3.NRO_SAP_WMS OR V.PEDIDO_ORIGINAL = W3.NRO_SAP_WMS)
ORDER BY V.PEDIDO_ORIGINAL;

/*
================================================================================
 VERIFICACION DE COBERTURA (auditoria 2026-08-02)
================================================================================
 - VBFA C-C: 553 pedidos originales con posterior
 - VBFA C-J (PASO 0, sin filtro FES): 3.066 pares / 2.512 pedidos / 1.037 entregas
 - VBFA entregas J totales: 376.982 | pedidos C totales: 1.564.143
 - WMS MANIFIESTO_D total: 17.542 filas (el filtro MAD_PEDIDO>1000 era incorrecto)
 - WMS entregas validas: 7.838 | pedidos validos: 1.409 | NRO_SAP unicos: 8.749
 - Cruce por ENTREGA: 5 | por PEDIDO: 13 | por NRO_SAP: 52
 - UNION de documentos vinculados: 65 (vs 3 con el filtro erroneo)
 - CONCLUSION: el WMS es mayoritariamente operacion de transporte interno sin
   entrega SAP (solo 66 pedidos en rango NS 116xxxx/117xxxx). Para ampliar el
   universo de cierre FES el cruce relevante es MAD_PEDIDO/MAD_NRO_SAP contra
   la master en Power BI (tabla calculada), no solo VBFA C->J.
 - Referencia completa: Docs/AUDITORIA_VINCULACION_VBFA_WMS.md

 PROXIMO PASO (en Power BI):
   - Cargar #WMS_MANIFIESTO como tabla Dim_WMS_Manifiesto (3 claves)
   - Cruzar por PEDIDO_WMS / NRO_SAP_WMS con la master (Fact_Pedidos_Auditoria)
     por PED_NUMERO_PEDIDO -> identificar cuales son FES y cerrarlos con manifiesto
================================================================================
*/
