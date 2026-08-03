let
    Origen =
        Sql.Database(
            "128.1.3.21",
            "DMF_VTA_PRD",
            [
                Query = "
SET NOCOUNT ON;

WITH Requeridas AS
(
    SELECT 'VBAK_SAP' AS TABLA, 'VBELN' AS COLUMNA UNION ALL
    SELECT 'VBAK_SAP', 'KUNNR' UNION ALL
    SELECT 'VBAK_SAP', 'VTWEG' UNION ALL
    SELECT 'VBAK_SAP', 'AUART' UNION ALL
    SELECT 'VBAK_SAP', 'ERDAT' UNION ALL
    SELECT 'VBAK_SAP', 'ERZET' UNION ALL
    SELECT 'VBAK_SAP', 'VSBED' UNION ALL
    SELECT 'VBAK_SAP', 'BSTNK' UNION ALL
    SELECT 'VBAK_SAP', 'NETWR' UNION ALL
    SELECT 'VBAK_SAP', 'WAERK' UNION ALL
    SELECT 'VBAK_SAP', 'LIFSK' UNION ALL
    SELECT 'VBAK_SAP', 'CMGST' UNION ALL
    SELECT 'KNA1_SAP', 'KUNNR' UNION ALL
    SELECT 'KNA1_SAP', 'ORT01' UNION ALL
    SELECT 'KNA1_SAP', 'REGIO'
)
SELECT
    R.TABLA,
    R.COLUMNA,
    CASE WHEN C.column_id IS NULL THEN 'FALTA' ELSE 'OK' END AS ESTADO,
    T.name AS TIPO_SQL,
    C.max_length AS LARGO
FROM Requeridas AS R
LEFT JOIN sys.tables AS TB
    ON TB.name = R.TABLA
LEFT JOIN sys.schemas AS S
    ON S.schema_id = TB.schema_id
   AND S.name = 'dbo'
LEFT JOIN sys.columns AS C
    ON C.object_id = TB.object_id
   AND C.name = R.COLUMNA
LEFT JOIN sys.types AS T
    ON T.user_type_id = C.user_type_id
ORDER BY R.TABLA, R.COLUMNA;
"
            ]
        ),
    Tipos =
        Table.TransformColumnTypes(
            Origen,
            {
                {"TABLA", type text},
                {"COLUMNA", type text},
                {"ESTADO", type text},
                {"TIPO_SQL", type text},
                {"LARGO", Int64.Type}
            }
        )
in
    Tipos
