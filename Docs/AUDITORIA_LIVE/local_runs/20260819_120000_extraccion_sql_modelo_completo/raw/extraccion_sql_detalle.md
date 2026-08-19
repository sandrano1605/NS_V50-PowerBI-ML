# Detalle de consultas SQL directas — Auditoría de Extracción

## 1. Fact_Pedidos_Auditoria — SQL Principal (Master)

**Tabla modelo:** `Fact_Pedidos_Auditoria`
**Servidor:** `128.1.3.21`
**Base de datos:** `DMF_VTA_PRD`
**Tipo:** `Sql.Database` con `Query` embebido (stored procedure-like)

### SQL actual (completo)

La consulta ejecuta:
1. Creación de tabla temporal `#PedidosFES_AUD_V3` con clasificación FES
2. Consulta principal sobre `ZART_TRACK_DATA_SAP` con UNPIVOT de ~20 columnas de hitos
3. Cálculo de 25+ columnas DH
4. Clasificación FES/SALDO/NORMAL
5. Métricas de auditoría

### Tablas SAP referenciadas

| Tabla SAP | Uso | Filas estimadas | Filtro actual |
|-----------|-----|-----------------|---------------|
| `ZART_TRACK_DATA_SAP` | Fuente principal de pedidos | ~2M (3M) | `ZERDAT_PED >= DATEADD(MONTH,-3)` |
| `VBFA_SAP` (C→C) | Pedidos FES (pedido posterior) | ~6.3M SIN filtro | `VBTYP_V='C' AND VBTYP_N='C'` |
| `VBFA_SAP` (C→J) | Entregas posteriores FES | ~6.3M SIN filtro | `VBTYP_V='C' AND VBTYP_N='J'` |
| `VTTP_SAP` | Manifiestos FES | ~500K | JOIN con entregas |
| `VBAK_SAP` | Pedidos VBAK (append) | ~2M (3M) | `AUART IN (...); ERDAT >= -3M` |
| `KNA1_SAP` | Nombres de clientes | ~100K | LEFT JOIN |

### Filtros de canal

**Canal 43/45:** Se aplican DESPUÉS de la carga en M, no en SQL.
```
#"Filas filtradas" = Table.SelectRows(Origen, each [PED_CANAL_CODIGO] = "43" or [PED_CANAL_CODIGO] = "45")
```
Esto significa que SQL retorna TODOS los canales y luego M filtra. **Candidato a pushdown SQL.**

### Problemas identificados

1. **VBFA sin ventana temporal:** Las consultas C→C y C→J sobre VBFA_SAP escanean ~6.3M filas SIN filtro de fecha. Ya prevalidado que ventana 3M reduce a ~976K con 0 pedidos perdidos.
2. **SELECT con columnas innecesarias:** La master retorna 181 columnas; ~68 son consumidas.
3. **Filtros de canal en M:** Los filtros 43/45 se aplican en Power Query, no en SQL.
4. **TRY_CONVERT en joins:** `TRY_CONVERT(BIGINT, P1.VBELV)` en los CTEs de FES impide uso de índices.
5. **ORDER BY innecesario:** No hay ORDER BY explícito en la consulta principal.

### Propuesta de reducción

| Cambio | Capa | Impacto |
|--------|------|---------|
| Agregar ventana 3M a VBFA C→C y C→J | SQL_WHERE | ~6.3M → ~976K filas |
| Filtrar canales 43/45 en SQL | SQL_WHERE | ~20-30% reducción |
| Reducir columnas SELECT de 181 a ~68 | SQL_SELECT | ~63% menos datos transferidos |
| Mover filtros M a SQL | SQL_WHERE | Menor transferencia |

---

## 2. Fact_Pedidos_Auditoria — SQL VBAK Append

**Tabla modelo:** `Fact_Pedidos_Auditoria` (segunda query M)
**Servidor:** `128.1.3.21`
**Base de datos:** `DMF_VTA_PRD`
**Tipo:** `Sql.Database` con `Query` embebido

### SQL actual

```sql
SELECT
    CONVERT(VARCHAR(20), V.VBELN) AS PED_NUMERO_PEDIDO,
    LTRIM(RTRIM(CONVERT(VARCHAR(30), V.KUNNR))) AS PED_CODIGO_CLIENTE,
    RIGHT('00' + LTRIM(RTRIM(CONVERT(VARCHAR(10), V.VTWEG))), 2) AS PED_CANAL_CODIGO,
    ...
FROM dbo.VBAK_SAP AS V
LEFT JOIN dbo.KNA1_SAP AS K
    ON TRY_CONVERT(BIGINT, K.KUNNR) = TRY_CONVERT(BIGINT, V.KUNNR)
WHERE V.AUART IN ('ZEDI','ZMAY','ZMAN','ZPDA','ZVGF','ZREL','ZVGM','ZTAN','TAN')
  AND COALESCE(...) >= DATEADD(MONTH, -3, CAST(GETDATE() AS DATE))
```

### Problemas identificados

1. **SELECT * implícito:** Trae muchas columnas que luego son descartadas por M.
2. **TRY_CONVERT en join KNA1:** Impide uso de índices sobre KUNNR.
3. **Filtro de canal NO está en SQL:** Se filtra después en M.

### Propuesta

- Filtrar canales 43/45 en SQL.
- Reducir columnas SELECT.
- Considerar CONVERT en vez de TRY_CONVERT si los datos son consistentes.

---

## 3. Pedidos_Normal_VBAK

**Tabla modelo:** `Pedidos_Normal_VBAK`
**Servidor:** `128.1.3.21`
**Base de datos:** `DMF_VTA_PRD`
**Tipo:** `Sql.Database` con `Query`

### SQL actual

```sql
SELECT *
FROM VBAK_SAP
WHERE VBAK_SAP.AUART IN ('ZEDI','ZMAY','ZMAN','ZPDA','ZVGF','ZREL','ZVGM','ZTAN','TAN')
  AND VBAK_SAP.ERDAT > GETDATE()-90
```

### Problemas identificados

1. **`SELECT *` SELECT COMPLETO:** Trae TODAS las columnas de VBAK_SAP (~100+ columnas). Solo usa VBELN, ERDAT.
2. **Sin filtro de canal:** No filtra 43/45 en SQL.
3. **Sin ventana 3M consistente:** Usa 90 días hardcoded, no DATEADD(MONTH,-3).
4. **Post-procesamiento M extenso:** Joins con 5 tablas derivadas en M que podrían resolverse en SQL.
5. **Sin semi-join a ZART:** Podría limitarse a pedidos reales.

### Propuesta

- `SELECT VBELN, ERDAT` solamente (o las ~7 columnas que realmente usa).
- Filtros 43/45 en SQL.
- Consistenciar ventana temporal.
- Mover joins a tablas derivadas a SQL si son costosos.

---

## 4. Dim_Cliente — Lookup SQL

**Tabla modelo:** `Dim_Cliente`
**Servidor:** `128.1.3.21`
**Base de datos:** `DMF_VTA_PRD`
**Tipo:** `Sql.Database` con `Query`

### SQL actual

```sql
-- Lookup completo: KNA1_SAP + CLIENTE_VENDEDOR + VENDEDOR
-- Sin filtro de universo
SELECT
    COALESCE(M.CLIENTE_CLAVE_NORMALIZADA, V.CLIENTE_CLAVE_NORMALIZADA),
    M.CLIENTE_NOMBRE,
    V.VENDEDOR_NOMBRE
FROM MaestroCliente AS M
FULL OUTER JOIN VendedorActual AS V
    ON V.CLIENTE_CLAVE_NORMALIZADA = M.CLIENTE_CLAVE_NORMALIZADA
WHERE COALESCE(...) IS NOT NULL
```

### Problemas identificados

1. **Maestro completo:** KNA1_SAP (~100K clientes) + CLIENTE_VENDEDOR + VENDEDOR. No filtra por universo 3M.
2. **FULL OUTER JOIN innecesario:** Podría ser LEFT JOIN desde el universo de pedidos.
3. **TRY_CONVERT en joins:** `TRY_CONVERT(BIGINT, K.KUNNR)` impide índices.
4. **Sin filtro de canal:** No restringe a clientes de canales 43/45.

### Propuesta

- Filtrar KNA1_SAP a clientes presentes en ZART_TRACK_DATA_SAP 3M.
- Filtrar CLIENTE_VENDEDOR a esos mismos clientes.
- Considerar LEFT JOIN en vez de FULL OUTER.

---

## 5. Dim_Cliente — Base de Fact_Pedidos_Auditoria

**Origen:** Primera parte de Dim_Cliente extrae `PED_CODIGO_CLIENTE`, `PED_CIUDAD`, `PED_REGION` de `Fact_Pedidos_Auditoria`.

### Evaluación

Esta parte es DERIVADA (no SQL directa). Es eficiente porque hereda el universo ya filtrado de la master. **Sin optimización requerida.**

---

## 6. Lineas_y_unidades_por_pedidos (ya optimizada)

**Tabla modelo:** `Lineas_y_unidades_por_pedidos`
**Estado:** GREEN — ya optimizada con semi-join a ZART 3M.

### Patrón aplicado

```sql
WHERE <CLAVE_PEDIDO> IN (
    SELECT DISTINCT CONVERT(BIGINT, ZVBELN_PED)
    FROM ZART_TRACK_DATA_SAP
    WHERE ZERDAT_PED >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE))
)
```

**Referencia:** `Docs/AUDITORIA_LIVE/local_runs/20260818_155007_fact_pedidos_auditoria_optimizacion_preflight_946fb29/`

---

## 7. Bloque_comercial — API Externa

**Tabla modelo:** `Bloque_comercial`
**Tipo:** `Web.Contents` → API REST `apis.nacional.cl`

### Evaluación

- No es SQL directa pero es candidata a optimización.
- Descarga TODOS los pedidos sin filtro.
- Credenciales embebidas en el código M.
- Podría filtrarse por universo de pedidos activos.

**Prioridad:** P2 (después de cerrar las optimizaciones SQL principales).
