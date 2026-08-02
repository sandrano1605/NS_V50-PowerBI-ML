/*
================================================================================
 DISEÑO PROPUESTO: 3 TABLAS PARA EL MODELO NS (mejora universo de cierre FES)
================================================================================
 Objetivo: separar el origen FES en 3 tablas consultables que se cruzan por
 pedido/entrega, y permitir ampliar el cierre con manifiestos manuales del WMS.

 Tablas propuestas:
   1. MASTER            -> Fact_Pedidos_Auditoria (la principal actual, sin cambios)
   2. DIM_VBFA_FES      -> logica VBFA: pedido original -> pedido posterior -> entrega
                           (C->C y C->J) con fechas min/max (mismo concepto que VTTP)
   3. DIM_WMS_MANIFIESTO -> manifiesto manual del WMS (entrega, fecha min/max, folio)

 Cruce propuesto (validado con datos reales):
   - DIM_VBFA_FES.ENTREGA_POSTERIOR  =  DIM_WMS_MANIFIESTO.MAD_ENTREGA
   - DIM_VBFA_FES.PEDIDO_ORIGINAL    =  MASTER.PED_NUMERO_PEDIDO
   - Resultado: fecha de cierre FES = COALESCE(ULTIMO_MANIFIESTO_VTTP,
                                               ULTIMO_MANIFIESTO_WMS_MANUAL)

 Validacion exitosa (2026-08-02):
   - Pedido 1167577: VBFA C->J entrega 0082389032 -> WMS entrega 82389032 -> manifiesto 02-07
     COINCIDE con el cierre actual del modelo.
   - IMPORTANTE: la entrega debe normalizarse como BIGINT (elimina ceros a la
     izquierda). VBFA entrega '0082389032' y WMS entrega '82389032' son la MISMA
     entrega. Usar CONVERT(BIGINT, ...) en el cruce.

 CONTEO VALIDADO (2026-08-02):
   - WMS tiene 41 pedidos unicos con manifiesto manual en ultimos 90 dias
   - De ellos, SOLO 1 (1167577) cruza con VBFA C->J por ENTREGA
   - La mayoria de manifiestos WMS son de pedidos que NO pasan por el flujo
     VBFA C->C / C->J (canales directos o entregas sin pedido posterior)
   - ESTRATEGIA DE CRUCE DUAL:
       a) Por ENTREGA: DIM_VBFA_FES.ENTREGA_NUM = DIM_WMS.ENTREGA_NUM (1 coincidencia hoy)
       b) Por PEDIDO:  DIM_WMS.PEDIDO_WMS = MASTER.PED_NUMERO_PEDIDO (41 candidatos,
          cruzar dentro del modelo Power BI para ver cuantos son FES cerrados)
   - La master (Fact_Pedidos_Auditoria) NO es tabla fisica SQL; es tabla calculada
     del modelo. El cruce por pedido debe hacerse en Power BI.
================================================================================
*/

-- ============================================================================
-- TABLA 1: DIM_VBFA_FES (logica VBFA completa)
-- Pedido original -> pedido posterior (C->C) -> entrega posterior (C->J)
-- Fechas min/max de entrega (mismo concepto que VTTP)
-- ============================================================================
IF OBJECT_ID('tempdb..#Dim_VBFA_FES') IS NOT NULL DROP TABLE #Dim_VBFA_FES;

;WITH PedidosPosteriores AS
(
    SELECT DISTINCT
        TRY_CONVERT(BIGINT, P1.VBELV) AS PEDIDO_ORIGINAL_NUM,
        CONVERT(VARCHAR(20), P1.VBELN) AS PEDIDO_POSTERIOR
    FROM [DMF_VTA_PRD].[dbo].[VBFA_SAP] AS P1
    WHERE P1.VBTYP_V = 'C' AND P1.VBTYP_N = 'C'
      AND TRY_CONVERT(BIGINT, P1.VBELV) IS NOT NULL
),
EntregasPosteriores AS
(
    SELECT DISTINCT
        PP.PEDIDO_ORIGINAL_NUM,
        PP.PEDIDO_POSTERIOR,
        CONVERT(VARCHAR(20), P2.VBELN) AS ENTREGA_POSTERIOR,
        COALESCE
        (
            TRY_CONVERT(DATE, CONVERT(VARCHAR(30), P2.ERDAT), 112),
            TRY_CONVERT(DATE, CONVERT(VARCHAR(30), P2.ERDAT), 105),
            TRY_CONVERT(DATE, CONVERT(VARCHAR(30), P2.ERDAT), 103),
            TRY_CONVERT(DATE, CONVERT(VARCHAR(30), P2.ERDAT))
        ) AS FECHA_ENTREGA_POSTERIOR
    FROM PedidosPosteriores AS PP
    INNER JOIN [DMF_VTA_PRD].[dbo].[VBFA_SAP] AS P2
        ON TRY_CONVERT(BIGINT, P2.VBELV) = TRY_CONVERT(BIGINT, PP.PEDIDO_POSTERIOR)
       AND P2.VBTYP_V = 'C' AND P2.VBTYP_N = 'J'
)
SELECT
    PEDIDO_ORIGINAL_NUM,
    PEDIDO_POSTERIOR,
    CONVERT(BIGINT, ENTREGA_POSTERIOR) AS ENTREGA_NUM,
    MIN(FECHA_ENTREGA_POSTERIOR) AS FECHA_ENTREGA_MIN,
    MAX(FECHA_ENTREGA_POSTERIOR) AS FECHA_ENTREGA_MAX
INTO #Dim_VBFA_FES
FROM EntregasPosteriores
GROUP BY PEDIDO_ORIGINAL_NUM, PEDIDO_POSTERIOR, CONVERT(BIGINT, ENTREGA_POSTERIOR);

-- Verificacion
SELECT COUNT(*) AS FILAS_VBFA, COUNT(DISTINCT PEDIDO_ORIGINAL_NUM) AS PEDIDOS_ORIG FROM #Dim_VBFA_FES;

-- ============================================================================
-- TABLA 2: DIM_WMS_MANIFIESTO (manifiesto manual del WMS)
-- 3 columnas clave: entrega (BIGINT normalizado), fecha min, fecha max
-- ============================================================================
IF OBJECT_ID('tempdb..#Dim_WMS_Manifiesto') IS NOT NULL DROP TABLE #Dim_WMS_Manifiesto;

SELECT
    CONVERT(BIGINT, MAD_ENTREGA)      AS ENTREGA_NUM,
    CONVERT(BIGINT, MAD_PEDIDO)       AS PEDIDO_WMS,
    MIN(MAD_FECHA_EMISION)            AS FECHA_MANIFIESTO_MIN,
    MAX(MAD_FECHA_EMISION)            AS FECHA_MANIFIESTO_MAX,
    COUNT(*)                          AS CANTIDAD_MANIFIESTOS
INTO #Dim_WMS_Manifiesto
FROM [PASO_WMS].[dbo].[MANIFIESTO_D]
WHERE MAD_ENTREGA IS NOT NULL
  AND MAD_PEDIDO > 1000000
  AND YEAR(MAD_FECHA_EMISION) BETWEEN 2000 AND 2100
  AND MAD_FECHA_EMISION > GETDATE()-90
  AND ISNULL(MAD_ELIMINADO, 0) = 0
GROUP BY CONVERT(BIGINT, MAD_ENTREGA), CONVERT(BIGINT, MAD_PEDIDO);

-- Verificacion
SELECT COUNT(*) AS FILAS_WMS, COUNT(DISTINCT ENTREGA) AS ENTREGAS FROM #Dim_WMS_Manifiesto;

-- ============================================================================
-- TABLA 3: CRUCE FINAL POR PEDIDO
-- Master + VBFA (entrega) + WMS (manifiesto manual) -> fecha de cierre FES ampliada
-- ESTRATEGIA A: cruce por ENTREGA (VBFA C->J entrega = WMS entrega)
-- ============================================================================
SELECT
    V.PEDIDO_ORIGINAL_NUM     AS PEDIDO,
    V.ENTREGA_NUM             AS ENTREGA,
    V.FECHA_ENTREGA_MIN,
    V.FECHA_ENTREGA_MAX,
    W.FECHA_MANIFIESTO_MIN    AS MANIFIESTO_WMS_MIN,
    W.FECHA_MANIFIESTO_MAX    AS MANIFIESTO_WMS_MAX,
    W.CANTIDAD_MANIFIESTOS,
    -- Cierre FES ampliado: manifiesto WMS manual si existe, si no la entrega
    COALESCE(W.FECHA_MANIFIESTO_MAX, V.FECHA_ENTREGA_MAX) AS FECHA_CIERRE_FES_AMPLIADO,
    CASE WHEN W.ENTREGA_NUM IS NOT NULL THEN 'WMS_MANUAL' ELSE 'VBFA_SIN_WMS' END AS FUENTE_MANIFIESTO
FROM #Dim_VBFA_FES AS V
LEFT JOIN #Dim_WMS_Manifiesto AS W
    ON V.ENTREGA_NUM = W.ENTREGA_NUM;

-- ============================================================================
-- TABLA 3B: ESTRATEGIA B - cruce por PEDIDO directo
-- WMS tiene 41 pedidos con manifiesto; cruzar por MAD_PEDIDO con la master
-- en Power BI (la master no es tabla fisica SQL). Este cruce amplia mas
-- el universo: cualquier pedido FES con manifiesto WMS manual.
-- ============================================================================
SELECT
    CONVERT(BIGINT, MAD_PEDIDO)     AS PEDIDO_WMS,
    MIN(MAD_FECHA_EMISION)          AS MANIFIESTO_WMS_MIN,
    MAX(MAD_FECHA_EMISION)          AS MANIFIESTO_WMS_MAX,
    COUNT(DISTINCT MAD_ENTREGA)     AS CANTIDAD_ENTREGAS,
    COUNT(*)                        AS CANTIDAD_DETALLE
FROM [PASO_WMS].[dbo].[MANIFIESTO_D]
WHERE MAD_PEDIDO IS NOT NULL AND MAD_PEDIDO > 1000
  AND YEAR(MAD_FECHA_EMISION) BETWEEN 2000 AND 2100
  AND MAD_FECHA_EMISION > GETDATE()-90
  AND ISNULL(MAD_ELIMINADO, 0) = 0
GROUP BY CONVERT(BIGINT, MAD_PEDIDO)
ORDER BY MANIFIESTO_WMS_MAX DESC;

/*
================================================================================
 COMO INTEGRAR EN EL MODELO POWER BI
================================================================================
 1. Crear las 3 tablas como consultas Power Query (o tablas calculadas):
    - Fact_Pedidos_Auditoria (master, ya existe)
    - Dim_VBFA_FES          (nueva, desde DMF_VTA_PRD)
    - Dim_WMS_Manifiesto    (nueva, desde PASO_WMS con solo_lectura)

 2. Relaciones:
    - Dim_VBFA_FES[PEDIDO_ORIGINAL_NUM] -> Fact_Pedidos_Auditoria[PED_NUMERO_PEDIDO] (1:N)
    - Dim_WMS_Manifiesto[ENTREGA]       -> Dim_VBFA_FES[ENTREGA_POSTERIOR] (1:N)

 3. En la master (Fact_Pedidos_Auditoria), reemplazar la columna de cierre FES:
    - Nueva logica: FES cierra con COALESCE(ULTIMO_MANIFIESTO_VTTP,
                                           MANIFIESTO_WMS_MANUAL,
                                           ULTIMA_FECHA_TRANSPORTE)
    - Solo cuando el flujo sea FES / FES + SALDO y el pedido este cerrado

 4. Agregar columnas necesarias a las otras tablas del modelo:
    - Fact_Tracking: MANIFIESTO_WMS_MIN, MANIFIESTO_WMS_MAX, FUENTE_MANIFIESTO
    - Fact_Hitos_Operacionales: FECHA_CIERRE_FES_AMPLIADO
================================================================================
*/
