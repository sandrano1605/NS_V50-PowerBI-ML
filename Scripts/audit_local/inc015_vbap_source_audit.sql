/*
INC-015 — Auditoría read-only de la fuente VBAP_SAP
Compatible con SQL Server 2012.

Objetivo:
1) Identificar qué es VBAP_SAP (VIEW / TABLE / SYNONYM).
2) Cuantificar el gap VBAK_SAP -> VBAP_SAP para pedidos recientes del universo.
3) Detectar si existe una fuente base VBAP y comparar cobertura.
4) No crear/modificar objetos persistentes.

Base esperada: DMF_VTA_PRD
*/

SET NOCOUNT ON;

PRINT '=== INC-015 / CONTEXTO ===';
SELECT
    DB_NAME() AS database_name,
    GETDATE() AS server_now,
    @@VERSION AS sql_server_version;

PRINT '=== OBJETOS VBAP / VBAP_SAP ===';
SELECT
    s.name AS schema_name,
    o.name AS object_name,
    o.type,
    o.type_desc,
    o.create_date,
    o.modify_date
FROM sys.objects AS o
INNER JOIN sys.schemas AS s
    ON s.schema_id = o.schema_id
WHERE o.name IN ('VBAP_SAP', 'VBAP')
ORDER BY o.name, s.name;

PRINT '=== SINONIMOS VBAP / VBAP_SAP ===';
SELECT
    SCHEMA_NAME(sn.schema_id) AS schema_name,
    sn.name AS synonym_name,
    sn.base_object_name
FROM sys.synonyms AS sn
WHERE sn.name IN ('VBAP_SAP', 'VBAP')
ORDER BY sn.name;

PRINT '=== DEFINICION DE VBAP_SAP (si es VIEW y hay permiso VIEW DEFINITION) ===';
SELECT
    s.name AS schema_name,
    v.name AS view_name,
    OBJECT_DEFINITION(v.object_id) AS view_definition
FROM sys.views AS v
INNER JOIN sys.schemas AS s
    ON s.schema_id = v.schema_id
WHERE v.name = 'VBAP_SAP';

PRINT '=== DEPENDENCIAS DE VBAP_SAP ===';
SELECT
    OBJECT_SCHEMA_NAME(d.referencing_id) AS referencing_schema,
    OBJECT_NAME(d.referencing_id) AS referencing_object,
    d.referenced_server_name,
    d.referenced_database_name,
    d.referenced_schema_name,
    d.referenced_entity_name
FROM sys.sql_expression_dependencies AS d
WHERE OBJECT_NAME(d.referencing_id) = 'VBAP_SAP'
ORDER BY d.referenced_database_name, d.referenced_schema_name, d.referenced_entity_name;

PRINT '=== COLUMNAS CLAVE VBAP_SAP ===';
SELECT
    c.column_id,
    c.name AS column_name,
    t.name AS data_type,
    c.max_length,
    c.is_nullable
FROM sys.columns AS c
INNER JOIN sys.types AS t
    ON t.user_type_id = c.user_type_id
WHERE c.object_id = OBJECT_ID('dbo.VBAP_SAP')
   OR c.object_id IN (
       SELECT o.object_id
       FROM sys.objects AS o
       WHERE o.name = 'VBAP_SAP'
   )
ORDER BY c.column_id;

/*
Universo de cabeceras reciente, alineado con los AUART usados por Pedidos_Normal_VBAK.
Se usa ERDAT > GETDATE()-90 porque ese es el filtro actual de esa tabla del modelo.
*/
IF OBJECT_ID('tempdb..#RecentHeaders') IS NOT NULL DROP TABLE #RecentHeaders;

SELECT
    CONVERT(varchar(20), K.VBELN) AS VBELN,
    MIN(K.ERDAT) AS ERDAT,
    MAX(K.AUART) AS AUART
INTO #RecentHeaders
FROM VBAK_SAP AS K
WHERE K.ERDAT > GETDATE() - 90
  AND K.AUART IN ('ZEDI','ZMAY','ZMAN','ZPDA','ZVGF','ZREL','ZVGM','ZTAN','TAN')
GROUP BY CONVERT(varchar(20), K.VBELN);

PRINT '=== COBERTURA RECENT HEADERS -> VBAP_SAP ===';
SELECT
    COUNT(*) AS headers_recent,
    SUM(CASE WHEN X.has_vbap_sap = 1 THEN 1 ELSE 0 END) AS headers_with_vbap_sap,
    SUM(CASE WHEN X.has_vbap_sap = 0 THEN 1 ELSE 0 END) AS headers_missing_vbap_sap,
    CAST(100.0 * SUM(CASE WHEN X.has_vbap_sap = 1 THEN 1 ELSE 0 END) / NULLIF(COUNT(*),0) AS decimal(6,2)) AS coverage_pct
FROM #RecentHeaders AS H
OUTER APPLY (
    SELECT TOP (1) 1 AS has_vbap_sap
    FROM VBAP_SAP AS V
    WHERE CONVERT(varchar(20), V.VBELN) = H.VBELN
) AS A
CROSS APPLY (
    SELECT CASE WHEN A.has_vbap_sap = 1 THEN 1 ELSE 0 END AS has_vbap_sap
) AS X;

PRINT '=== GAP POR AUART ===';
SELECT
    H.AUART,
    COUNT(*) AS headers_recent,
    SUM(CASE WHEN A.has_vbap_sap = 1 THEN 1 ELSE 0 END) AS with_vbap_sap,
    SUM(CASE WHEN A.has_vbap_sap IS NULL THEN 1 ELSE 0 END) AS missing_vbap_sap,
    CAST(100.0 * SUM(CASE WHEN A.has_vbap_sap = 1 THEN 1 ELSE 0 END) / NULLIF(COUNT(*),0) AS decimal(6,2)) AS coverage_pct
FROM #RecentHeaders AS H
OUTER APPLY (
    SELECT TOP (1) 1 AS has_vbap_sap
    FROM VBAP_SAP AS V
    WHERE CONVERT(varchar(20), V.VBELN) = H.VBELN
) AS A
GROUP BY H.AUART
ORDER BY missing_vbap_sap DESC, H.AUART;

PRINT '=== GAP POR MES ERDAT ===';
SELECT
    CONVERT(char(7), H.ERDAT, 120) AS erdat_month,
    COUNT(*) AS headers_recent,
    SUM(CASE WHEN A.has_vbap_sap = 1 THEN 1 ELSE 0 END) AS with_vbap_sap,
    SUM(CASE WHEN A.has_vbap_sap IS NULL THEN 1 ELSE 0 END) AS missing_vbap_sap,
    CAST(100.0 * SUM(CASE WHEN A.has_vbap_sap = 1 THEN 1 ELSE 0 END) / NULLIF(COUNT(*),0) AS decimal(6,2)) AS coverage_pct
FROM #RecentHeaders AS H
OUTER APPLY (
    SELECT TOP (1) 1 AS has_vbap_sap
    FROM VBAP_SAP AS V
    WHERE CONVERT(varchar(20), V.VBELN) = H.VBELN
) AS A
GROUP BY CONVERT(char(7), H.ERDAT, 120)
ORDER BY erdat_month;

PRINT '=== MUESTRA 100 PEDIDOS RECIENTES AUSENTES EN VBAP_SAP ===';
SELECT TOP (100)
    H.VBELN,
    H.AUART,
    H.ERDAT
FROM #RecentHeaders AS H
WHERE NOT EXISTS (
    SELECT 1
    FROM VBAP_SAP AS V
    WHERE CONVERT(varchar(20), V.VBELN) = H.VBELN
)
ORDER BY H.ERDAT DESC, H.VBELN;

PRINT '=== AEDAT PARA PEDIDOS QUE SI EXISTEN EN VBAP_SAP ===';
SELECT
    COUNT(DISTINCT H.VBELN) AS headers_with_vbap_sap,
    COUNT(DISTINCT CASE WHEN V.AEDAT >= GETDATE() - 730 THEN H.VBELN END) AS headers_inside_730,
    COUNT(DISTINCT CASE WHEN V.AEDAT < GETDATE() - 730 OR V.AEDAT IS NULL THEN H.VBELN END) AS headers_with_old_or_null_aedat
FROM #RecentHeaders AS H
INNER JOIN VBAP_SAP AS V
    ON CONVERT(varchar(20), V.VBELN) = H.VBELN;

/*
Si existe una tabla o vista accesible llamada dbo.VBAP, comparar cobertura.
Esto no asume que exista: el bloque se ejecuta solo si OBJECT_ID resuelve.
*/
IF OBJECT_ID('dbo.VBAP') IS NOT NULL
BEGIN
    PRINT '=== COMPARACION CONTRA dbo.VBAP ===';

    EXEC (
    'SELECT
        COUNT(*) AS headers_recent,
        SUM(CASE WHEN EXISTS (SELECT 1 FROM dbo.VBAP AS B WHERE CONVERT(varchar(20), B.VBELN) = H.VBELN) THEN 1 ELSE 0 END) AS headers_with_base_vbap,
        SUM(CASE WHEN NOT EXISTS (SELECT 1 FROM dbo.VBAP AS B WHERE CONVERT(varchar(20), B.VBELN) = H.VBELN) THEN 1 ELSE 0 END) AS headers_missing_base_vbap,
        CAST(100.0 * SUM(CASE WHEN EXISTS (SELECT 1 FROM dbo.VBAP AS B WHERE CONVERT(varchar(20), B.VBELN) = H.VBELN) THEN 1 ELSE 0 END) / NULLIF(COUNT(*),0) AS decimal(6,2)) AS base_coverage_pct
     FROM #RecentHeaders AS H;'
    );

    EXEC (
    'SELECT TOP (100)
        H.VBELN,
        H.AUART,
        H.ERDAT,
        CASE WHEN EXISTS (SELECT 1 FROM dbo.VBAP AS B WHERE CONVERT(varchar(20), B.VBELN) = H.VBELN) THEN 1 ELSE 0 END AS exists_base_vbap,
        CASE WHEN EXISTS (SELECT 1 FROM dbo.VBAP_SAP AS V WHERE CONVERT(varchar(20), V.VBELN) = H.VBELN) THEN 1 ELSE 0 END AS exists_vbap_sap
     FROM #RecentHeaders AS H
     WHERE NOT EXISTS (SELECT 1 FROM dbo.VBAP_SAP AS V WHERE CONVERT(varchar(20), V.VBELN) = H.VBELN)
     ORDER BY H.ERDAT DESC, H.VBELN;'
    );
END
ELSE
BEGIN
    PRINT 'dbo.VBAP no existe o no es visible para este usuario. Revisar OBJETOS/SINONIMOS/DEPENDENCIAS anteriores.';
END;

PRINT '=== FIN INC-015 SOURCE AUDIT ===';
