let
    Origen =
        Sql.Database(
            "128.1.3.21",
            "DMF_VTA_PRD",
            [
                Query = "
SET NOCOUNT ON;

DECLARE @FechaHasta DATE = CAST(GETDATE() AS DATE);
DECLARE @FechaDesde DATE = DATEADD(MONTH, -3, @FechaHasta);

;WITH Base AS
(
    SELECT
        LTRIM(RTRIM(CONVERT(VARCHAR(20), V.VBELN))) AS PED_NUMERO_PEDIDO,
        NULLIF(LTRIM(RTRIM(CONVERT(VARCHAR(30), V.KUNNR))), '') AS PED_CODIGO_CLIENTE,
        RIGHT('00' + LTRIM(RTRIM(CONVERT(VARCHAR(10), V.VTWEG))), 2) AS PED_CANAL_CODIGO,
        NULLIF(LTRIM(RTRIM(CONVERT(VARCHAR(10), V.VSBED))), '') AS PED_CONDICION_EXPEDICION_CODIGO,
        NULLIF(LTRIM(RTRIM(CONVERT(VARCHAR(100), V.BSTNK))), '') AS PED_ORDEN_COMPRA_CLIENTE,
        TRY_CONVERT(DECIMAL(18,2), V.NETWR) AS PED_VALOR_NETO,
        NULLIF(LTRIM(RTRIM(CONVERT(VARCHAR(10), V.WAERK))), '') AS PED_MONEDA,
        NULLIF(LTRIM(RTRIM(CONVERT(VARCHAR(10), V.LIFSK))), '') AS PED_BLOQUEO_ENTREGA,
        NULLIF(LTRIM(RTRIM(CONVERT(VARCHAR(10), V.CMGST))), '') AS PED_ESTADO_CREDITO,
        NULLIF(LTRIM(RTRIM(CONVERT(VARCHAR(10), V.AUART))), '') AS VBAK_CLASE_PEDIDO,
        NULLIF(LTRIM(RTRIM(CONVERT(VARCHAR(100), K.ORT01))), '') AS PED_CIUDAD,
        NULLIF(LTRIM(RTRIM(CONVERT(VARCHAR(20), K.REGIO))), '') AS PED_REGION,
        COALESCE
        (
            TRY_CONVERT(DATE, CONVERT(VARCHAR(30), V.ERDAT), 112),
            TRY_CONVERT(DATE, CONVERT(VARCHAR(30), V.ERDAT), 103),
            TRY_CONVERT(DATE, CONVERT(VARCHAR(30), V.ERDAT), 105),
            TRY_CONVERT(DATE, CONVERT(VARCHAR(30), V.ERDAT))
        ) AS PED_FECHA,
        COALESCE
        (
            TRY_CONVERT(TIME(0), CONVERT(VARCHAR(30), V.ERZET)),
            TRY_CONVERT
            (
                TIME(0),
                STUFF
                (
                    STUFF
                    (
                        RIGHT
                        (
                            '000000' + REPLACE(LTRIM(RTRIM(CONVERT(VARCHAR(30), V.ERZET))), ':', ''),
                            6
                        ),
                        3,
                        0,
                        ':'
                    ),
                    6,
                    0,
                    ':'
                )
            )
        ) AS PED_HORA
    FROM dbo.VBAK_SAP AS V
    LEFT JOIN dbo.KNA1_SAP AS K
        ON TRY_CONVERT(BIGINT, K.KUNNR) = TRY_CONVERT(BIGINT, V.KUNNR)
    WHERE V.AUART IN ('ZEDI','ZMAY','ZMAN','ZPDA','ZVGF','ZREL','ZVGM','ZTAN','TAN')
      AND RIGHT('00' + LTRIM(RTRIM(CONVERT(VARCHAR(10), V.VTWEG))), 2)
          IN ('42','43','44','45','46','47')
),
Filtrada AS
(
    SELECT
        *,
        ROW_NUMBER() OVER
        (
            PARTITION BY TRY_CONVERT(BIGINT, PED_NUMERO_PEDIDO)
            ORDER BY PED_FECHA DESC, PED_NUMERO_PEDIDO
        ) AS RN
    FROM Base
    WHERE PED_FECHA BETWEEN @FechaDesde AND @FechaHasta
      AND TRY_CONVERT(BIGINT, PED_NUMERO_PEDIDO) IS NOT NULL
)
SELECT
    CONVERT(VARCHAR(20), TRY_CONVERT(BIGINT, PED_NUMERO_PEDIDO)) AS PED_NUMERO_PEDIDO,
    PED_CODIGO_CLIENTE,
    PED_CANAL_CODIGO,
    PED_CONDICION_EXPEDICION_CODIGO,
    PED_ORDEN_COMPRA_CLIENTE,
    PED_VALOR_NETO,
    PED_MONEDA,
    PED_BLOQUEO_ENTREGA,
    PED_ESTADO_CREDITO,
    VBAK_CLASE_PEDIDO,
    PED_CIUDAD,
    PED_REGION,
    CASE
        WHEN PED_FECHA IS NULL THEN NULL
        ELSE DATEADD
        (
            SECOND,
            CASE
                WHEN PED_HORA IS NULL THEN 0
                ELSE DATEDIFF(SECOND, CAST('00:00:00' AS TIME(0)), PED_HORA)
            END,
            CAST(PED_FECHA AS DATETIME2(0))
        )
    END AS PED_FECHA_HORA,
    CASE WHEN PED_HORA IS NULL THEN CONVERT(BIT, 0) ELSE CONVERT(BIT, 1) END AS HORA_PEDIDO_DISPONIBLE
FROM Filtrada
WHERE RN = 1
ORDER BY TRY_CONVERT(BIGINT, PED_NUMERO_PEDIDO);
"
            ]
        ),
    Tipos =
        Table.TransformColumnTypes(
            Origen,
            {
                {"PED_NUMERO_PEDIDO", type text},
                {"PED_CODIGO_CLIENTE", type text},
                {"PED_CANAL_CODIGO", type text},
                {"PED_CONDICION_EXPEDICION_CODIGO", type text},
                {"PED_ORDEN_COMPRA_CLIENTE", type text},
                {"PED_VALOR_NETO", type number},
                {"PED_MONEDA", type text},
                {"PED_BLOQUEO_ENTREGA", type text},
                {"PED_ESTADO_CREDITO", type text},
                {"VBAK_CLASE_PEDIDO", type text},
                {"PED_CIUDAD", type text},
                {"PED_REGION", type text},
                {"PED_FECHA_HORA", type datetime},
                {"HORA_PEDIDO_DISPONIBLE", type logical}
            }
        ),
    Normalizados =
        Table.TransformColumns(
            Tipos,
            {
                {"PED_NUMERO_PEDIDO", each if _ = null then null else Text.From(Int64.FromText(Text.Trim(_))), type nullable text},
                {"PED_CODIGO_CLIENTE", each if _ = null then null else Text.Trim(_), type nullable text},
                {"PED_CANAL_CODIGO", each if _ = null then null else Text.PadStart(Text.Trim(_), 2, "0"), type nullable text},
                {"PED_REGION", each if _ = null then null else Text.Trim(_), type nullable text}
            }
        ),
    Unicos = Table.Distinct(Normalizados, {"PED_NUMERO_PEDIDO"})
in
    Unicos
