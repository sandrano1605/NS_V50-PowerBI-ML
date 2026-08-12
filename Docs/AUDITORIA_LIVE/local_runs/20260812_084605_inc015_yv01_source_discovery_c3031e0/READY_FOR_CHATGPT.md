# READY FOR CHATGPT — INC-015 YV01 Source Discovery

RUN_ID: 20260812_084605_inc015_yv01_source_discovery_c3031e0
Rama: work/ns-lienzo-02-ingreso-pedidos
SHA: c3031e04bbff51fc0e4298f83cc28cc55e10accd
SQL: DMF_VTA_PRD (A_MOYA), 33 bases visibles

## Resumen

Se ejecuto `inc015_yv01_source_discovery.sql` contra 128.1.3.21. Se escanearon 7 candidatos con firma de posiciones SAP (VBELN + POSNR/KWMENG/MATNR) en DMF_VTA_PRD y SAP_PRD. **Ninguno tiene cobertura YV01.** Dictamen: SIN_FUENTE_YV01_EN_DMF_VTA_PRD.

## Hallazgos RED confirmados
Ninguno.

## Hallazgos ORANGE confirmados
INC-015: SIN_FUENTE_YV01_EN_DMF_VTA_PRD. Cobertura 58.3% es maxima alcanzable sin fuente externa.

## Falsos positivos relevantes
- dbo.VISTA_PEDIDO: tiene VBELN+KWMENG pero solo cubre ZPDA/ZMAY/ZPPO/ZVGM (783 pedidos, 0 YV01).
- SAP_PRD: sin objetos VBAP, sin tablas con columna VBELN.

## Decisiones de negocio necesarias
Definir como obtener posiciones YV01: replicacion SAP a DMF, conexion directa RFC/BW, o fuente externa.

## Cambios recomendados para implementación remota
Replicar VBAP desde SAP con AUART=YV01 hacia DMF_VTA_PRD.
Solo despues de tener la fuente, modificar Lineas_y_unidades_por_pedidos.

## Evidencia principal
- raw/inc015_yv01_discovery_final.md — diagnostico completo con tablas
- raw/inc015_yv01_source_discovery.txt — salida SQL completa

## No resuelto
- Ubicacion fisica de las posiciones YV01 (no estan en DMF_VTA_PRD ni SAP_PRD en este servidor)
