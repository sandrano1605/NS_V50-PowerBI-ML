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
