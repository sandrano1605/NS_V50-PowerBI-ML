/*
================================================================================
 QUERY DE MANIFIESTO FES (origen: modelo Power BI NS)
================================================================================
 Extraída del TMDL de Fact_Pedidos_Auditoria (lógica oficial de cierre FES).

 Regla de cierre:
   - FES / FES + SALDO -> cierre por ÚLTIMO MANIFIESTO válido
   - El manifiesto se obtiene desde el flujo VBFA y su relación con transporte/VTTP
   - Solo pedidos TRACKING = TRUE y cerrados entran al NS histórico

 Flujo de la query (de abajo hacia arriba):
   1. PedidosPosteriores  : pedido original (VBELV) -> pedido posterior (VBELN) via VBFA C->C
   2. EntregasPosteriores : pedido posterior -> entrega posterior (VBFA C->J)
   3. Manifiestos         : entrega posterior -> manifiesto (VTTP por VBELN)
   4. ResumenManifiestos  : primera y última fecha de manifiesto por pedido original

 PARA MEJORAR:
   - Incluir manifiestos MANUALES (cargados externamente, no via VBFA/VTTP)
   - Unir con tabla de manifiestos manuales (ej. MANT_MANIFIESTO_MANUAL) y usar
     COALESCE(ULTIMA_FECHA_MANIFIESTO, MANIFIESTO_MANUAL) como cierre
================================================================================
*/

-- ============================================================================
-- VERSION 1: SELECT de manifiesto FES (solo lectura, replicable)
-- Devuelve por pedido original: primera y última fecha de manifiesto.
-- ============================================================================
SET NOCOUNT ON;

DECLARE @FechaDesde DATE = '2026-07-01';
DECLARE @FechaHasta DATE = '2026-07-02';

;WITH PedidosPosteriores AS
(
    SELECT DISTINCT
        TRY_CONVERT(BIGINT, P1.VBELV) AS PEDIDO_ORIGINAL_NUM,
        CONVERT(VARCHAR(20), P1.VBELN) AS PEDIDO_POSTERIOR,
        COALESCE
        (
            TRY_CONVERT(DATE, CONVERT(VARCHAR(30), P1.ERDAT), 112),
            TRY_CONVERT(DATE, CONVERT(VARCHAR(30), P1.ERDAT), 105),
            TRY_CONVERT(DATE, CONVERT(VARCHAR(30), P1.ERDAT), 103),
            TRY_CONVERT(DATE, CONVERT(VARCHAR(30), P1.ERDAT))
        ) AS FECHA_PEDIDO_POSTERIOR
    FROM [DMF_VTA_PRD].[dbo].[VBFA_SAP] AS P1
    WHERE P1.VBTYP_V = 'C'
      AND P1.VBTYP_N = 'C'
      AND TRY_CONVERT(BIGINT, P1.VBELV) IS NOT NULL
),
ResumenPedidos AS
(
    SELECT
        PEDIDO_ORIGINAL_NUM,
        MIN(FECHA_PEDIDO_POSTERIOR) AS PRIMERA_FECHA_PEDIDO_POSTERIOR,
        MAX(FECHA_PEDIDO_POSTERIOR) AS ULTIMA_FECHA_PEDIDO_POSTERIOR
    FROM PedidosPosteriores
    GROUP BY PEDIDO_ORIGINAL_NUM
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
       AND P2.VBTYP_V = 'C'
       AND P2.VBTYP_N = 'J'
),
ResumenEntregas AS
(
    SELECT
        PEDIDO_ORIGINAL_NUM,
        MIN(FECHA_ENTREGA_POSTERIOR) AS PRIMERA_FECHA_ENTREGA_POSTERIOR,
        MAX(FECHA_ENTREGA_POSTERIOR) AS ULTIMA_FECHA_ENTREGA_POSTERIOR
    FROM EntregasPosteriores
    GROUP BY PEDIDO_ORIGINAL_NUM
),
Manifiestos AS
(
    SELECT DISTINCT
        EP.PEDIDO_ORIGINAL_NUM,
        EP.ENTREGA_POSTERIOR,
        COALESCE
        (
            TRY_CONVERT(DATE, CONVERT(VARCHAR(30), VTTP.ERDAT), 112),
            TRY_CONVERT(DATE, CONVERT(VARCHAR(30), VTTP.ERDAT), 105),
            TRY_CONVERT(DATE, CONVERT(VARCHAR(30), VTTP.ERDAT), 103),
            TRY_CONVERT(DATE, CONVERT(VARCHAR(30), VTTP.ERDAT))
        ) AS FECHA_MANIFIESTO
    FROM EntregasPosteriores AS EP
    INNER JOIN [DMF_VTA_PRD].[dbo].[VTTP_SAP] AS VTTP
        ON TRY_CONVERT(BIGINT, VTTP.VBELN) = TRY_CONVERT(BIGINT, EP.ENTREGA_POSTERIOR)
),
ResumenManifiestos AS
(
    SELECT
        PEDIDO_ORIGINAL_NUM,
        MIN(FECHA_MANIFIESTO) AS PRIMERA_FECHA_MANIFIESTO,
        MAX(FECHA_MANIFIESTO) AS ULTIMA_FECHA_MANIFIESTO
    FROM Manifiestos
    GROUP BY PEDIDO_ORIGINAL_NUM
)
SELECT
    RM.PEDIDO_ORIGINAL_NUM,
    RM.PRIMERA_FECHA_MANIFIESTO,
    RM.ULTIMA_FECHA_MANIFIESTO,
    DATEDIFF(DAY, RM.PRIMERA_FECHA_MANIFIESTO, RM.ULTIMA_FECHA_MANIFIESTO) AS DIAS_ENTRE_PRIMER_Y_ULTIMO
FROM ResumenManifiestos AS RM
WHERE RM.ULTIMA_FECHA_MANIFIESTO BETWEEN @FechaDesde AND @FechaHasta
ORDER BY RM.ULTIMA_FECHA_MANIFIESTO DESC;

/*
================================================================================
 VERSION 2 (PLANTILLA PARA MEJORAR - manifiestos manuales)
================================================================================
 Para incluir manifiestos MANUALES, crear una tabla de apoyo, por ejemplo:

   CREATE TABLE dbo.MANIFIESTO_MANUAL (
       PEDIDO_NUMERO        VARCHAR(20)  NOT NULL,
       FECHA_MANIFIESTO     DATE         NOT NULL,
       OBSERVACION          VARCHAR(200) NULL,
       CARGADO_POR          VARCHAR(50)  NULL,
       FECHA_CARGA          DATETIME     DEFAULT GETDATE()
   );

 Y luego combinar en ResumenManifiestos:

   UNION ALL
   SELECT
       TRY_CONVERT(BIGINT, MM.PEDIDO_NUMERO) AS PEDIDO_ORIGINAL_NUM,
       MM.FECHA_MANIFIESTO AS FECHA_MANIFIESTO
   FROM dbo.MANIFIESTO_MANUAL AS MM
   WHERE MM.FECHA_MANIFIESTO BETWEEN @FechaDesde AND @FechaHasta;

 El ULTIMO_MANIFIESTO resultante incluira los manuales, ampliando el universo
 de cierre FES para pedidos sin manifiesto VBFA/VTTP.
================================================================================
*/

/*
================================================================================
 VERSION 3 - MANIFIESTO MANUAL REAL (PASO_WMS 128.1.3.60) VALIDADA
================================================================================
 Fuente externa de manifiestos manuales:
   Servidor : 128.1.3.60
   Base     : PASO_WMS
   Usuario  : solo_lectura (solo SELECT)
   Tablas   : dbo.MANIFIESTO_H (cabecera) / dbo.MANIFIESTO_D (detalle)
   Relacion : MANIFIESTO_D.MAD_ID_H = MANIFIESTO_H.MAH_FOLIO

 Columna clave para cruzar con el modelo:
   MANIFIESTO_D.MAD_PEDIDO  -> numero de pedido original (igual a PED_NUMERO_PEDIDO)
   MANIFIESTO_D.MAD_FECHA_EMISION -> fecha del manifiesto
   MANIFIESTO_D.MAD_NRO_SAP -> numero SAP asociado
   MANIFIESTO_D.MAD_STAT    -> estado (S=salida / cerrado)
   MANIFIESTO_H.MAH_FOLIO   -> folio del manifiesto
   MANIFIESTO_H.MAH_MANIFIESTO_SAP -> manifiesto SAP (si existe)

 Consulta validada (785 filas en GETDATE()-90):
   SELECT *
   FROM [dbo].[MANIFIESTO_H]
   INNER JOIN [MANIFIESTO_D] ON MAD_ID_H = MAH_FOLIO
   WHERE MAD_FECHA_EMISION > GETDATE()-90;

 Ejemplo de conexion Power Query (solo_lectura):
   = Sql.Database("128.1.3.60", "PASO_WMS", [Query="
       SELECT *
       FROM [dbo].[MANIFIESTO_H]
       INNER JOIN [MANIFIESTO_D] ON MAD_ID_H = MAH_FOLIO
       WHERE MAD_FECHA_EMISION > GETDATE()-90
   "])

 NOTA IMPORTANTE - anomalias detectadas en datos:
   1. MAD_FECHA_EMISION contiene fechas fuera de rango (años 2223, 2424, 2028)
      -> filtrar con YEAR(MAD_FECHA_EMISION) BETWEEN 2000 AND 2100 o CAST valido
   2. MAD_PEDIDO tiene NULL en registros recientes (mayo 2026)
      -> excluir NULL al cruzar
   3. MAD_STAT: True/False (logico) y 'S' (string) segun fila -> normalizar
   4. MAD_ELIMINADO = False en muestras -> filtrar si aplica

 ANALISIS VALIDADO (2026-08-02):
   - MAD_FECHA_EMISION = fecha de emision real del manifiesto (datetime)
   - MAD_FECHA         = fecha operativa de registro (datetime, mas precisa)
   - MAD_INGRESO       = varchar 'S'/'M' (estado de ingreso, NO es fecha)
   - MAD_STAT          = bit (True/False) estado del detalle
   - MAD_PEDIDO        = 37 pedidos reales (> 1.000.000) en ultimos 90 dias;
                         570 NULL y 170 con valor 1 (basura) -> filtrar MAD_PEDIDO > 1000000
   - Anomalia: MAD_FECHA_EMISION con anos 2223/2424/2028 = fechas de expiracion
     o carga mal registrada -> usar MAD_FECHA o filtrar YEAR entre 2000 y 2100
================================================================================
*/

-- ============================================================================
-- QUERY RECOMENDADA: manifiestos manuales del WMS limpios para cruzar con el modelo
-- Filtra basura: MAD_PEDIDO > 1000000, fechas validas, sin eliminados
-- ============================================================================
SELECT
    MAD_PEDIDO            AS PEDIDO_MODELO,
    MAD_NRO_SAP           AS NRO_SAP,
    MAD_ENTREGA           AS ENTREGA_SAP,
    MAD_FECHA_EMISION     AS FECHA_MANIFIESTO_WMS,
    MAD_FECHA             AS FECHA_REGISTRO_WMS,
    MAH_FOLIO             AS FOLIO_MANIFIESTO,
    MAH_MANIFIESTO_SAP    AS MANIFIESTO_SAP,
    MAH_TRANSPORTE        AS TRANSPORTE,
    MAH_PATENTE           AS PATENTE,
    MAD_CLIENTE_NOMBRE    AS CLIENTE,
    MAD_STAT              AS ESTADO,
    MAD_ELIMINADO         AS ELIMINADO
FROM [PASO_WMS].[dbo].[MANIFIESTO_H]
INNER JOIN [PASO_WMS].[dbo].[MANIFIESTO_D] ON MAD_ID_H = MAH_FOLIO
WHERE MAD_FECHA_EMISION > GETDATE()-90
  AND MAD_PEDIDO > 1000000
  AND MAD_PEDIDO IS NOT NULL
  AND YEAR(MAD_FECHA_EMISION) BETWEEN 2000 AND 2100
  AND ISNULL(MAD_ELIMINADO, 0) = 0
ORDER BY MAD_FECHA_EMISION DESC;

