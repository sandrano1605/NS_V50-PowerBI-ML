/*
INC-015 — Descubrimiento read-only de fuente de posiciones YV01
Compatible con SQL Server 2012.

Objetivo:
1) Encontrar tablas/vistas en DMF_VTA_PRD con firma de posiciones SAP:
   VBELN + al menos una de POSNR / KWMENG / MATNR.
2) Probar cobertura contra una muestra reciente YV01.
3) Para candidatos con hits, medir cobertura contra todo YV01 reciente.
4) No crear/modificar objetos persistentes. Solo usa tablas temporales.
*/

SET NOCOUNT ON;

PRINT '=== INC-015 / YV01 SOURCE DISCOVERY / CONTEXTO ===';
SELECT DB_NAME() AS database_name, GETDATE() AS server_now, @@VERSION AS sql_server_version;

PRINT '=== BASES VISIBLES EN EL SERVIDOR ===';
SELECT name, state_desc, compatibility_level
FROM sys.databases
ORDER BY name;

PRINT '=== OBJETOS CON NOMBRE RELACIONADO A VBAP / YV01 / POSICION ===';
SELECT
    s.name AS schema_name,
    o.name AS object_name,
    o.type_desc
FROM sys.objects AS o
INNER JOIN sys.schemas AS s ON s.schema_id = o.schema_id
WHERE o.type IN ('U','V')
  AND (
        o.name LIKE '%VBAP%'
     OR o.name LIKE '%YV01%'
     OR o.name LIKE '%POSIC%'
     OR o.name LIKE '%PEDIDO%DET%'
     OR o.name LIKE '%DET%PEDIDO%'
  )
ORDER BY o.type_desc, s.name, o.name;

IF OBJECT_ID('tempdb..#Candidates') IS NOT NULL DROP TABLE #Candidates;
CREATE TABLE #Candidates (
    schema_name sysname NOT NULL,
    object_name sysname NOT NULL,
    object_type nvarchar(60) NOT NULL,
    has_posnr bit NOT NULL,
    has_kwmeng bit NOT NULL,
    has_matnr bit NOT NULL,
    PRIMARY KEY (schema_name, object_name)
);

INSERT INTO #Candidates (schema_name, object_name, object_type, has_posnr, has_kwmeng, has_matnr)
SELECT
    s.name,
    o.name,
    o.type_desc,
    CASE WHEN EXISTS (SELECT 1 FROM sys.columns c WHERE c.object_id=o.object_id AND c.name='POSNR') THEN 1 ELSE 0 END,
    CASE WHEN EXISTS (SELECT 1 FROM sys.columns c WHERE c.object_id=o.object_id AND c.name='KWMENG') THEN 1 ELSE 0 END,
    CASE WHEN EXISTS (SELECT 1 FROM sys.columns c WHERE c.object_id=o.object_id AND c.name='MATNR') THEN 1 ELSE 0 END
FROM sys.objects AS o
INNER JOIN sys.schemas AS s ON s.schema_id=o.schema_id
WHERE o.type IN ('U','V')
  AND EXISTS (SELECT 1 FROM sys.columns c WHERE c.object_id=o.object_id AND c.name='VBELN')
  AND (
       EXISTS (SELECT 1 FROM sys.columns c WHERE c.object_id=o.object_id AND c.name='POSNR')
    OR EXISTS (SELECT 1 FROM sys.columns c WHERE c.object_id=o.object_id AND c.name='KWMENG')
    OR EXISTS (SELECT 1 FROM sys.columns c WHERE c.object_id=o.object_id AND c.name='MATNR')
  );

PRINT '=== CANDIDATOS POR FIRMA DE COLUMNAS ===';
SELECT *
FROM #Candidates
ORDER BY object_type, schema_name, object_name;

IF OBJECT_ID('tempdb..#YV01Recent') IS NOT NULL DROP TABLE #YV01Recent;
SELECT
    CONVERT(varchar(20), K.VBELN) AS VBELN,
    MIN(K.ERDAT) AS ERDAT
INTO #YV01Recent
FROM VBAK_SAP AS K
WHERE K.ERDAT > GETDATE() - 90
  AND K.AUART = 'YV01'
GROUP BY CONVERT(varchar(20), K.VBELN);

PRINT '=== UNIVERSO YV01 RECIENTE ===';
SELECT COUNT(*) AS yv01_recent_headers, MIN(ERDAT) AS min_erdat, MAX(ERDAT) AS max_erdat
FROM #YV01Recent;

IF OBJECT_ID('tempdb..#YV01Sample') IS NOT NULL DROP TABLE #YV01Sample;
SELECT TOP (200) VBELN, ERDAT
INTO #YV01Sample
FROM #YV01Recent
ORDER BY ERDAT DESC, VBELN;

IF OBJECT_ID('tempdb..#Probe') IS NOT NULL DROP TABLE #Probe;
CREATE TABLE #Probe (
    schema_name sysname NOT NULL,
    object_name sysname NOT NULL,
    object_type nvarchar(60) NOT NULL,
    sample_headers int NULL,
    matched_sample_headers int NULL,
    matched_rows bigint NULL,
    error_message nvarchar(4000) NULL
);

DECLARE @schema sysname, @object sysname, @otype nvarchar(60), @sql nvarchar(max);
DECLARE cur_candidates CURSOR LOCAL FAST_FORWARD FOR
SELECT schema_name, object_name, object_type
FROM #Candidates
WHERE NOT (schema_name='dbo' AND object_name IN ('VBAK_SAP','VBAP_SAP'))
ORDER BY schema_name, object_name;

OPEN cur_candidates;
FETCH NEXT FROM cur_candidates INTO @schema, @object, @otype;
WHILE @@FETCH_STATUS = 0
BEGIN
    SET @sql = N'
    BEGIN TRY
        INSERT INTO #Probe(schema_name,object_name,object_type,sample_headers,matched_sample_headers,matched_rows,error_message)
        SELECT
            N''' + REPLACE(@schema,'''','''''') + N''',
            N''' + REPLACE(@object,'''','''''') + N''',
            N''' + REPLACE(@otype,'''','''''') + N''',
            (SELECT COUNT(*) FROM #YV01Sample),
            COUNT(DISTINCT S.VBELN),
            COUNT_BIG(*),
            NULL
        FROM #YV01Sample AS S
        INNER JOIN ' + QUOTENAME(@schema) + N'.' + QUOTENAME(@object) + N' AS T
            ON CONVERT(varchar(20), T.VBELN) = S.VBELN;
    END TRY
    BEGIN CATCH
        INSERT INTO #Probe(schema_name,object_name,object_type,sample_headers,matched_sample_headers,matched_rows,error_message)
        VALUES(
            N''' + REPLACE(@schema,'''','''''') + N''',
            N''' + REPLACE(@object,'''','''''') + N''',
            N''' + REPLACE(@otype,'''','''''') + N''',
            (SELECT COUNT(*) FROM #YV01Sample),
            NULL,
            NULL,
            ERROR_MESSAGE()
        );
    END CATCH;';
    EXEC sp_executesql @sql;

    FETCH NEXT FROM cur_candidates INTO @schema, @object, @otype;
END
CLOSE cur_candidates;
DEALLOCATE cur_candidates;

PRINT '=== PROBE MUESTRA YV01 (200 HEADERS) ===';
SELECT
    P.schema_name,
    P.object_name,
    P.object_type,
    C.has_posnr,
    C.has_kwmeng,
    C.has_matnr,
    P.sample_headers,
    P.matched_sample_headers,
    P.matched_rows,
    CASE WHEN P.sample_headers > 0 AND P.matched_sample_headers IS NOT NULL
         THEN CAST(100.0 * P.matched_sample_headers / P.sample_headers AS decimal(6,2)) END AS sample_coverage_pct,
    P.error_message
FROM #Probe AS P
INNER JOIN #Candidates AS C
    ON C.schema_name=P.schema_name AND C.object_name=P.object_name
ORDER BY ISNULL(P.matched_sample_headers,-1) DESC, P.schema_name, P.object_name;

IF OBJECT_ID('tempdb..#FullProbe') IS NOT NULL DROP TABLE #FullProbe;
CREATE TABLE #FullProbe (
    schema_name sysname NOT NULL,
    object_name sysname NOT NULL,
    yv01_recent_headers int NULL,
    matched_yv01_headers int NULL,
    matched_rows bigint NULL,
    error_message nvarchar(4000) NULL
);

DECLARE cur_hits CURSOR LOCAL FAST_FORWARD FOR
SELECT schema_name, object_name, object_type
FROM #Probe
WHERE matched_sample_headers > 0
ORDER BY matched_sample_headers DESC, schema_name, object_name;

OPEN cur_hits;
FETCH NEXT FROM cur_hits INTO @schema, @object, @otype;
WHILE @@FETCH_STATUS = 0
BEGIN
    SET @sql = N'
    BEGIN TRY
        INSERT INTO #FullProbe(schema_name,object_name,yv01_recent_headers,matched_yv01_headers,matched_rows,error_message)
        SELECT
            N''' + REPLACE(@schema,'''','''''') + N''',
            N''' + REPLACE(@object,'''','''''') + N''',
            (SELECT COUNT(*) FROM #YV01Recent),
            COUNT(DISTINCT H.VBELN),
            COUNT_BIG(*),
            NULL
        FROM #YV01Recent AS H
        INNER JOIN ' + QUOTENAME(@schema) + N'.' + QUOTENAME(@object) + N' AS T
            ON CONVERT(varchar(20), T.VBELN) = H.VBELN;
    END TRY
    BEGIN CATCH
        INSERT INTO #FullProbe(schema_name,object_name,yv01_recent_headers,matched_yv01_headers,matched_rows,error_message)
        VALUES(
            N''' + REPLACE(@schema,'''','''''') + N''',
            N''' + REPLACE(@object,'''','''''') + N''',
            (SELECT COUNT(*) FROM #YV01Recent),
            NULL,
            NULL,
            ERROR_MESSAGE()
        );
    END CATCH;';
    EXEC sp_executesql @sql;

    FETCH NEXT FROM cur_hits INTO @schema, @object, @otype;
END
CLOSE cur_hits;
DEALLOCATE cur_hits;

PRINT '=== COBERTURA COMPLETA PARA CANDIDATOS CON HITS ===';
SELECT
    F.schema_name,
    F.object_name,
    C.object_type,
    C.has_posnr,
    C.has_kwmeng,
    C.has_matnr,
    F.yv01_recent_headers,
    F.matched_yv01_headers,
    F.matched_rows,
    CASE WHEN F.yv01_recent_headers > 0 AND F.matched_yv01_headers IS NOT NULL
         THEN CAST(100.0 * F.matched_yv01_headers / F.yv01_recent_headers AS decimal(6,2)) END AS full_coverage_pct,
    F.error_message
FROM #FullProbe AS F
INNER JOIN #Candidates AS C
    ON C.schema_name=F.schema_name AND C.object_name=F.object_name
ORDER BY ISNULL(F.matched_yv01_headers,-1) DESC, F.schema_name, F.object_name;

PRINT '=== CRITERIO ===';
PRINT 'Si existe candidato con cobertura YV01 material y columnas POSNR/KWMENG: candidato para Lineas_y_unidades_por_pedidos.';
PRINT 'Si solo tiene VBELN+POSNR/MATNR pero no KWMENG: puede servir para Lineas, pero no para Unidades sin otra columna de cantidad.';
PRINT 'Si ningún candidato tiene hits: DMF_VTA_PRD no expone posiciones YV01 y se requiere nueva replica/vista desde SAP/BW.';

PRINT '=== FIN INC-015 YV01 SOURCE DISCOVERY ===';
