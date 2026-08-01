# Hallazgos

## 1. Auditor estatico
- Estado: AMARILLO
- 29 tablas, 1218 edges, 0 referencias rotas
- 4 tablas con consumidor dinamico: Dim_Cliente, Fact_Pedidos_Auditoria, Fact_Tracking, Resultado

## 2. Clasificacion columnas Fact_Pedidos_Auditoria
- 181/181 clasificadas
- 87 CONSERVAR_REFERENCIADA
- 94 NO_BORRAR_SIN_PRUEBA_CONTRATO (NO autorizadas a borrar)
- 0 interseccion, 0 duplicados (87+94=181)

## 3. Contrato Python (tabla Resultado) - CORREGIDO con 5 categorias
- Resultado = Fact_Pedidos_Auditoria COMPLETO + Fact_Tracking + Dim_Cliente -> Python.Execute
- El script recibe el DataFrame `dataset` con TODAS las columnas de Fact_Pedidos_Auditoria
- CORRECCION: ya no se afirma '158 columnas de entrada'. Se clasificaron 100 identificadores unicos:

### Clasificacion final (5 categorias)
| Categoria | Cantidad | Regla |
|---|---|---|
| INPUT_REQUIRED | 11 | Columnas cuya ausencia genera error |
| INPUT_OPTIONAL | 28 | Comprobadas via df.columns/get/OPTIONAL_DEFAULTS |
| DERIVED_INTERNAL | 32 | Creadas dentro del Python (CAT_*, HIST_*, etc.) |
| OUTPUT_COLUMN | 19 | Devueltas por el dataframe final |
| LITERAL_OR_ENUM | 10 | Textos ALTO/BAJO/CRITICO/etc. |

### INPUT_REQUIRED (11) - demostradas desde el script:
PED_NUMERO_PEDIDO, PED_CODIGO_CLIENTE, PED_RESPONSABLE, PED_CANAL_CODIGO,
PED_REGION, PED_CONDICION_EXPEDICION_CODIGO, PED_ESTADO_CREDITO,
SERV_TIPO_SERVICIO, PED_VALOR_NETO, PED_FECHA_HORA, DH_ENTREGA_COMPLETA_100

### INPUT_OPTIONAL (28) - leidas o con default:
PED_CANAL, PED_CONDICION_EXPEDICION, SERV_TIPO_SERVICIO_PLANIFICADO, PED_CIUDAD,
ES_FES, ES_SALDO, SEGMENTO_ANALISIS, ES_ULTIMOS_7_DIAS_HABILES_MES, AUD_TOTAL_CRITICAS,
AUD_ESTADO_GENERAL, AUD_PRINCIPAL_INCONGRUENCIA, DH_CREDITO_COBRANZAS, DH_OPERACION_INTERNA,
DH_CREDITO_A_PRIMERA_ENTREGA, DH_PRIMERA_ENTREGA_A_PRIMER_PICKING, DH_PRIMER_PICKING_A_PRIMERA_FACTURA,
DH_PRIMER_PACKING_A_PRIMERA_FACTURA, DH_DESPACHO, ES_CERRADO, ESTADO_ACTUAL, HITO_ACTUAL,
DIAS_INTERNOS_DH, DIAS_EN_ESTADO_DH, DIAS_RESTANTES_DH, SLA_INTERNO_DH, FECHA_ACTUALIZACION,
CLIENTE_NOMBRE, VENDEDOR_NOMBRE

### OUTPUT_COLUMN (19): salida del dataframe final
### DERIVED_INTERNAL (32): variables y features creadas dentro (CAT_*, HIST_*, VALOR_*)
### LITERAL_OR_ENUM (10): ALTO/BAJO/ATRASADO/CRITICO/CUMPLE/NORMAL/SALDO/etc.

- CONCLUSION: recortar una INPUT_REQUIRED rompe el script; recortar una INPUT_OPTIONAL cambia
  el dataset recibido (se rellena con default). Ninguna columna de entrada a Python puede
  borrarse sin prueba A/B del contrato.

## 4. Procedimiento VBFA
- Script sql/AUDIT_STP_GET_VBFA_TRAMO_FILTRO.sql listo
- Ejecucion via Power Query con carga desactivada sobre copia temporal del PBIP (en progreso)
- Requiere autorizacion de Power BI Desktop a 128.1.3.21/DMF_VTA_PRD
- La definicion del SP debe demostrar el significado de 'M-J' y 'C'

## 5. Snapshot actual (2026-07-31)
- Pedidos evaluables: 1907
- Fuera SLA: 394
- NS: 79,34%
- Clientes fuera SLA: 265
- Recurrencia: 4 / 36 / 225
- NOTA: difiere del historico 1616/360/77,72%/251 por ventana movil GETDATE()

## 6. Pedidos clave
- 4190139455: FES, Regiones, cierre 28-05-2026 (manifiesto), 2 DH, SLA 5, cumple TRUE
- 1167577: FES, Santiago, cierre 02-07-2026 (manifiesto), 2 DH, SLA 4, cumple TRUE
- Ambos OK, cierran por manifiesto (regla FES correcta)

## 7. Estado
- AMARILLO CONTROLADO
- Recorte de columnas: NO autorizado (0 columnas aprobadas)
- Contrato Python REQUIRED: VERDE preliminar
- Contrato Python completo: AMARILLO (pendiente confirmacion manual de DERIVED/OUTPUT)
- Procedimiento VBFA: PENDIENTE
- Pendiente: ejecucion SP VBFA, prueba A/B, lectura de Table.Schema
