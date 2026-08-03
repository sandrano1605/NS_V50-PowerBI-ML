# RESULTADO: Validación cruce VBAK inline en modelo vivo — ERROR DE REFRESH

**Fecha:** 2026-08-03
**Rama:** work/ns-vbak-master-append (HEAD cfb8241)
**Kit validador:** VERDE (master_integration_present=true)
**Modelo:** NS.pbip (abierto, refresh completo ejecutado)

## Estado: ERROR DE REFRESH — DETENIDA (no se corrige)

Instrucción: "No corrijas hallazgos. Registra el error exacto si algo falla."

## Error exacto

Al ejecutar Actualizar todo en Power BI Desktop, TODAS las tablas del modelo
fallan con el mismo error de SQL:

```
Microsoft SQL: El nombre de columna 'VSBED' no es válido.
Microsoft SQL: El nombre de columna 'CMGST' no es válido.
Microsoft SQL: El nombre de columna 'ORT01' no es válido.
```

Tablas afectadas (todas): Fact_Pedidos_Auditoria, auditoria, Fact_Pedidos,
Fact_Tiempos_Hitos, Dim_Fecha, Dim_Canal, Dim_Responsable,
Dim_Condicion_Expedicion, Fact_Hitos_Operacionales, Fact_Tracking,
Dim_Pedido, Resultado.

## Causa raíz verificada en la base

Verificado contra DMF_VTA_PRD (INFORMATION_SCHEMA.COLUMNS):

| Columna requerida por el kit | Tabla | Estado real |
|---|---|---|
| VSBED | VBAK_SAP | NO EXISTE |
| CMGST | VBAK_SAP | NO EXISTE |
| ORT01 | KNA1_SAP | NO EXISTE |

VBAK_SAP tiene 29 columnas (VBELN, KUNNR, VTWEG, AUART, ERDAT, ERZET, BSTNK,
NETWR, WAERK, LIFSK presentes; VSBED y CMGST ausentes).
KNA1_SAP tiene 21 columnas (KUNNR, REGIO, NAME1 presentes; ORT01 ausente).

Estas columnas son usadas por el cruce inline en:
`NS.SemanticModel/definition/tables/Fact_Pedidos_Auditoria.tmdl`
y por `PowerQuery/VBAK_APPEND/02_VBAK_ATRIBUTOS_MAYORISTA.pq`.

## Acción tomada

- No se corrigió ningún hallazgo (prohibido por instrucción).
- El refresh quedó fallando en el modelo abierto.
- No se pudo validar ningún control (MASTER_TOTAL, filas VBAK, duplicados, etc.)
  porque el modelo no tiene datos cargados tras el error.

## Siguiente paso (decisión de ChatGPT)

Las columnas VSBED, CMGST y ORT01 deben mapearse a las columnas reales de la
base (o eliminarse del kit). En VBAK_SAP existen alternativas parciales:
- VSBED: no hay equivalente directo; candidato a omitir o usar otra columna.
- CMGST: no hay equivalente directo; candidato a omitir.
- ORT01 (ciudad en KNA1): KNA1_SAP no tiene columna de ciudad; usar otra fuente
  o dejar PED_CIUDAD en null.
