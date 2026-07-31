/*
AUDITORÍA DE TRAZABILIDAD
Procedimiento: STP_GET_VBFA_TRAMO_FILTRO
Llamada de referencia solicitada:
EXEC STP_GET_VBFA_TRAMO_FILTRO 'M-J', 'C', '01-07-2026', '02-07-2026';

Objetivos:
1. Obtener definición y esquema de salida del procedimiento.
2. Ejecutar exactamente la ventana solicitada.
3. Documentar granularidad, duplicados y claves.
4. Validar primera/última fecha por pedido original.
5. Comparar manifiesto versus transporte usado como respaldo.

IMPORTANTE:
- No se asume el significado de 'M-J' ni de 'C'. Debe demostrarse desde la definición del SP.
- No modificar el procedimiento.
- Ejecutar primero en lectura/QA cuando exista ese ambiente.
*/

SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @ProcName SYSNAME = N'dbo.STP_GET_VBFA_TRAMO_FILTRO';
DECLARE @FechaDesde DATE = CONVERT(DATE, '20260701', 112);
DECLARE @FechaHasta DATE = CONVERT(DATE, '20260702', 112);

/* ============================================================
   1. IDENTIDAD Y DEFINICIÓN DEL PROCEDIMIENTO
   ============================================================ */
SELECT
    DB_NAME() AS BASE_DATOS,
    OBJECT_SCHEMA_NAME(p.object_id) AS ESQUEMA,
    p.name AS PROCEDIMIENTO,
    p.create_date AS FECHA_CREACION,
    p.modify_date AS FECHA_MODIFICACION
FROM sys.procedures p
WHERE p.object_id = OBJECT_ID(@ProcName);

SELECT OBJECT_DEFINITION(OBJECT_ID(@ProcName)) AS DEFINICION_SQL;

SELECT
    prm.parameter_id,
    prm.name AS PARAMETRO,
    TYPE_NAME(prm.user_type_id) AS TIPO,
    prm.max_length,
    prm.precision,
    prm.scale,
    prm.is_output
FROM sys.parameters prm
WHERE prm.object_id = OBJECT_ID(@ProcName)
ORDER BY prm.parameter_id;

/* ============================================================
   2. CONTRATO DE SALIDA
   ============================================================ */
EXEC sys.sp_describe_first_result_set
    @tsql = N'EXEC dbo.STP_GET_VBFA_TRAMO_FILTRO ''M-J'', ''C'', ''01-07-2026'', ''02-07-2026'';',
    @params = NULL,
    @browse_information_mode = 1;

/* ============================================================
   3. RESULTADO REAL DE LA VENTANA SOLICITADA
   Exportar este result set como:
   Docs/AUDITORIA_LIVE/runs/<run>/vbfa_tramo_raw_20260701_20260702.csv
   ============================================================ */
EXEC dbo.STP_GET_VBFA_TRAMO_FILTRO
    'M-J',
    'C',
    '01-07-2026',
    '02-07-2026';

/* ============================================================
   4. PRUEBA DE CONTROL CON VENTANA MÁS AMPLIA
   Sirve para detectar efectos de borde de fecha.
   Exportar por separado.
   ============================================================ */
EXEC dbo.STP_GET_VBFA_TRAMO_FILTRO
    'M-J',
    'C',
    '30-06-2026',
    '03-07-2026';

/* ============================================================
   5. CONSULTAS QUE DEBEN EJECUTARSE DESPUÉS DE MATERIALIZAR
      EL RESULTADO EN UNA TABLA TEMPORAL #VBFA_TRAMO.

   Crear #VBFA_TRAMO con el esquema devuelto por
   sp_describe_first_result_set y ejecutar:

   INSERT INTO #VBFA_TRAMO
   EXEC dbo.STP_GET_VBFA_TRAMO_FILTRO
        'M-J', 'C', '01-07-2026', '02-07-2026';

   Reemplazar los nombres de columnas marcados <...> por los
   nombres reales informados por el contrato de salida.
   ============================================================ */

/*
-- 5.1 Volumen y granularidad
SELECT
    COUNT(*) AS FILAS,
    COUNT(DISTINCT <PEDIDO_ORIGINAL>) AS PEDIDOS_ORIGINALES,
    COUNT(DISTINCT <DOCUMENTO_POSTERIOR>) AS DOCUMENTOS_POSTERIORES
FROM #VBFA_TRAMO;

-- 5.2 Duplicados exactos a la granularidad declarada
SELECT
    <PEDIDO_ORIGINAL>,
    <DOCUMENTO_POSTERIOR>,
    <TIPO_DOCUMENTO_ANTERIOR>,
    <TIPO_DOCUMENTO_POSTERIOR>,
    <FECHA_EVENTO>,
    COUNT(*) AS REPETICIONES
FROM #VBFA_TRAMO
GROUP BY
    <PEDIDO_ORIGINAL>,
    <DOCUMENTO_POSTERIOR>,
    <TIPO_DOCUMENTO_ANTERIOR>,
    <TIPO_DOCUMENTO_POSTERIOR>,
    <FECHA_EVENTO>
HAVING COUNT(*) > 1;

-- 5.3 Primera y última fecha por pedido original
SELECT
    <PEDIDO_ORIGINAL> AS PED_NUMERO_PEDIDO,
    MIN(<FECHA_EVENTO>) AS PRIMERA_FECHA_TRAMO,
    MAX(<FECHA_EVENTO>) AS ULTIMA_FECHA_TRAMO,
    COUNT(*) AS CANTIDAD_EVENTOS
FROM #VBFA_TRAMO
GROUP BY <PEDIDO_ORIGINAL>;

-- 5.4 Casos con primera fecha posterior a última fecha
WITH R AS
(
    SELECT
        <PEDIDO_ORIGINAL> AS PED_NUMERO_PEDIDO,
        MIN(<FECHA_EVENTO>) AS PRIMERA_FECHA,
        MAX(<FECHA_EVENTO>) AS ULTIMA_FECHA
    FROM #VBFA_TRAMO
    GROUP BY <PEDIDO_ORIGINAL>
)
SELECT *
FROM R
WHERE PRIMERA_FECHA > ULTIMA_FECHA;

-- 5.5 Comparación manifiesto/transporte
-- Ejecutar solo después de confirmar desde la definición del SP qué
-- columnas y códigos representan manifiesto y transporte.
SELECT
    <PEDIDO_ORIGINAL> AS PED_NUMERO_PEDIDO,
    MAX(CASE WHEN <ES_MANIFIESTO> = 1 THEN <FECHA_EVENTO> END) AS ULTIMO_MANIFIESTO,
    MAX(CASE WHEN <ES_TRANSPORTE> = 1 THEN <FECHA_EVENTO> END) AS ULTIMO_TRANSPORTE
FROM #VBFA_TRAMO
GROUP BY <PEDIDO_ORIGINAL>;
*/

/* ============================================================
   6. REGLAS DE RECONCILIACIÓN CON EL MODELO
   ============================================================

A. Para FES/FES + SALDO:
   FECHA_CIERRE_ESPERADA = ULTIMA_FECHA_MANIFIESTO.

B. Respaldo transporte:
   ULTIMA_FECHA_TRANSPORTE solo puede usarse cuando:
   - no existe manifiesto informado;
   - la definición del SP y la trazabilidad SAP demuestran que ese
     transporte corresponde al cierre oficial;
   - no es fecha de sincronización, creación técnica o evento intermedio.

C. Comparar por PED_NUMERO_PEDIDO:
   - PRIMERA_FECHA_PEDIDO_POSTERIOR
   - ULTIMA_FECHA_PEDIDO_POSTERIOR
   - PRIMERA_FECHA_ENTREGA_POSTERIOR
   - ULTIMA_FECHA_ENTREGA_POSTERIOR
   - PRIMERA_FECHA_MANIFIESTO
   - ULTIMA_FECHA_MANIFIESTO
   - FECHA_CIERRE
   - FUENTE_CIERRE

D. Casos obligatorios:
   - 4190139455
   - 1167577

E. La comparación debe usar el mismo refresh, misma ventana y misma
   zona horaria. No comparar métricas actuales con snapshots antiguos.
*/
