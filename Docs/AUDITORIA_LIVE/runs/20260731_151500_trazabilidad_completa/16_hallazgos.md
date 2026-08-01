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

## 3. Contrato Python (tabla Resultado) - CONFIRMADO
- Resultado = Fact_Pedidos_Auditoria COMPLETO + Fact_Tracking + Dim_Cliente -> Python.Execute
- El script recibe el DataFrame `dataset` con TODAS las columnas de Fact_Pedidos_Auditoria
- 11 columnas REQUIRED (obligatorias, el script falla si faltan):
  PED_NUMERO_PEDIDO, PED_CODIGO_CLIENTE, PED_RESPONSABLE, PED_CANAL_CODIGO,
  PED_REGION, PED_CONDICION_EXPEDICION_CODIGO, PED_ESTADO_CREDITO,
  SERV_TIPO_SERVICIO, PED_VALOR_NETO, PED_FECHA_HORA, DH_ENTREGA_COMPLETA_100
- 158 nombres de columna referenciados dentro del bloque Python
- Usa `df.columns` para aplicar OPTIONAL_DEFAULTS: si una columna opcional falta, la rellena con default
- Usa acceso directo df["PED_NUMERO_PEDIDO"], df["FECHA_ACTUALIZACION"], etc.
- CONCLUSION: recortar una columna REQUIRED rompe el script; recortar una OPTIONAL cambia el dataset recibido.
  Ninguna columna de entrada a Python puede borrarse sin prueba A/B del contrato.

## 4. Procedimiento VBFA
- Script sql/AUDIT_STP_GET_VBFA_TRAMO_FILTRO.sql listo
- NO ejecutado: requiere acceso SQL Server 128.1.3.21/DMF_VTA_PRD
- Credenciales solo en Power BI Desktop (no disponibles para el LLM)
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
- Pendiente: ejecucion SP VBFA, prueba A/B, lectura de Table.Schema
