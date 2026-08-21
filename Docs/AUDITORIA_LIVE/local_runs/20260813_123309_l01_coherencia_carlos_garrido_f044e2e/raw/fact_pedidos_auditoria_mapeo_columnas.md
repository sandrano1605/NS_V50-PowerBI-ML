# Mapeo columna-a-columna — Fact_Pedidos_Auditoria (181 columnas)

## Conclusión ejecutiva

De las **181 columnas**, el modelo realmente necesita **~68**. Las ~113 restantes
son prescindibles: ~90 son de auditoría (AUD_*), ~20 son DH_* intermedios o campos
de cabecera que nadie consume.

La tabla es la **fuente pivote** de 6 tablas hijas. El mapeo exacto:

## Consumidores y columnas que necesitan

### Fact_Tracking (25 columnas)
PED_NUMERO_PEDIDO, PED_CODIGO_CLIENTE, PED_RESPONSABLE, PED_CANAL_CODIGO,
PED_CONDICION_EXPEDICION_CODIGO, PED_VALOR_NETO, PED_CIUDAD, PED_REGION,
ES_FES, ES_SALDO, PED_FECHA_HORA, CRD_P_FECHA_HORA, ENT_P_FECHA_HORA,
PIC_P_FECHA_HORA, PAC_P_FECHA_HORA, FAC_P_FECHA_HORA_REAL, FAC_U_FECHA_HORA,
TRP_P_FECHA_HORA, TRP_U_FECHA_HORA, PRIMERA_FECHA_PEDIDO_POSTERIOR,
ULTIMA_FECHA_PEDIDO_POSTERIOR, PRIMERA_FECHA_ENTREGA_POSTERIOR,
ULTIMA_FECHA_ENTREGA_POSTERIOR, PRIMERA_FECHA_MANIFIESTO, ULTIMA_FECHA_MANIFIESTO

### Fact_Hitos_Operacionales (32 columnas adicionales vs Fact_Tracking)
Añade: PDA_P_FECHA_HORA, COM_P_FECHA_HORA, COM_U_FECHA_HORA, ENT_U_FECHA_HORA,
PIC_U_FECHA_HORA, PAC_U_FECHA_HORA, AUD_ESTADO_GENERAL

### Fact_Pedidos (54 columnas — la más amplia en cabecera)
PED_CENTRO, PED_CONDICION_EXPEDICION, PED_ORDEN_COMPRA_CLIENTE, PED_CANAL,
PED_MONEDA, PED_BLOQUEO_ENTREGA, PED_ESTADO_CREDITO, SERV_TIPO_SERVICIO,
SERV_TIPO_SERVICIO_PLANIFICADO, OTIF_ESTADO_PEDIDO, PED_TEXTO_ESTADO,
SEGMENTO_ANALISIS, INCLUIR_SLA_NORMAL, DH_CREDITO_COBRANZAS, DH_OPERACION_INTERNA,
DH_CREDITO_A_PRIMERA_ENTREGA, DH_PRIMERA_ENTREGA_A_PRIMER_PICKING,
DH_PRIMER_PICKING_A_PRIMERA_FACTURA, DH_DESPACHO, DH_LEAD_NORMAL,
ESTADO_SLA_NORMAL, PROCESO_DOMINANTE_NORMAL, MES_CREACION, DIA_MES_CREACION,
TRAMO_MES_CALENDARIO, ES_ULTIMOS_7_DIAS_HABILES_MES, AUD_PCT_COBERTURA_HITOS,
AUD_TOTAL_CRITICAS, AUD_TOTAL_ADVERTENCIAS, AUD_TOTAL_INCONGRUENCIAS,
AUD_REQUIERE_REVISION, AUD_ESTADO_FLUJO_NORMAL, AUD_ESTADO_FLUJO_FES,
AUD_ESTADO_FLUJO_SALDO, AUD_ESTADO_GENERAL, AUD_PRINCIPAL_INCONGRUENCIA

### Fact_Tiempos_Hitos (todas las DH_* — 39 columnas)
Todas las DH_* (FES y NORMAL), más DH_COMERCIAL_PDA_SAC, DH_DESPACHO_A_CEDIBLE,
DH_CREACION_A_CEDIBLE, y las DH_ENT/PIC/PAC/FAC primera-última.

### Dim_Cliente (3 columnas)
PED_CODIGO_CLIENTE, PED_CIUDAD, PED_REGION

### Medidas DAX (8 columnas)
PED_NUMERO_PEDIDO, ES_FES, ULTIMA_FECHA_MANIFIESTO, FAC_P_FECHA_HORA_REAL,
FAC_U_FECHA_HORA, TRP_P_FECHA_HORA, TRP_U_FECHA_HORA, MES_CREACION

### Resultado (vía Fact_Tracking y Dim_Cliente — indirecto, no directo)

## Unión (conjunto mínimo) ≈ 68 columnas

Consolidando todas las anteriores sin duplicados, el modelo necesita ~68 columnas.
Se agrupan en 5 bloques:

1. **Identificación y cabecera** (~15): PED_*, CLIENTE, RESPONSABLE, CANAL, CIUDAD, REGION, CONDICION, VALOR, MONEDA, SEGMENTO.
2. **Banderas de flujo** (2): ES_FES, ES_SALDO.
3. **Hitos/fechas efectivas** (~15): PDA/COM/CRD/ENT/PIC/PAC/FAC/TRP (P y U), manifiestos y pedidos/entregas posteriores.
4. **Métricas DH_*** (~20): las que alimentan Fact_Tiempos_Hitos y Fact_Pedidos.
5. **Auditoría mínima** (~8): AUD_ESTADO_GENERAL, AUD_TOTAL_CRITICAS/ADVERTENCIAS/INCONGRUENCIAS, AUD_PCT_COBERTURA_HITOS, AUD_ESTADO_FLUJO_*.

## Columnas eliminables (~113)

### Auditoría granular AUD_* que nadie consume (~90)
AUD_TIENE_*, AUD_INC_*, AUD_HORA_00_*, AUD_FES_*, AUD_NO_FES_*, AUD_SALDO_*,
AUD_OBS_*, AUD_ALERTAS_*, AUD_CRITICAS_*, AUD_ADVERTENCIAS_*, AUD_FALTANTES_*,
AUD_CANTIDAD_*, AUD_HITOS_* (las que no estén en Fact_Pedidos).

### Columnas de cálculo intermedio no consumidas (~20)
HRS_COMERCIAL_PDA_SAC, DIAS_EQ_COMERCIAL_9_5H, FES_FECHA_CIERRE_OPERATIVO_100,
FAC_FECHA_OPERATIVA_AJUSTADA, PARAM_FECHA_DESDE/HASTA, FECHA_CARGA_MASTER,
REGLA_CLASIFICACION_FES/SALDO, CED_CANTIDAD_COPIAS, TSTTO_*, CED_*, GER_*.

## Advertencia crítica

Antes de eliminar, verificar que:
1. `Fact_Tiempos_Hitos` no se use en el reporte activo (es la tabla larga de hitos).
2. Las columnas AUD_* no alimenten la tabla `auditoria` (lienzo de auditoría 360).
3. Ningún visual referencie columnas directamente (no solo medidas).

## Recomendación de ejecución

1. **P0**: filtrar VBFA_SAP por fecha (mayor impacto de rendimiento, sin tocar columnas).
2. **P1**: eliminar las ~113 columnas no usadas del SELECT final de Fact_Pedidos_Auditoria.
3. **P2**: normalizar joins con TRY_CONVERT(BIGINT).
