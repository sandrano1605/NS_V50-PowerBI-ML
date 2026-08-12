# INC-015 — YV01 Source Discovery (resultado final)

## Ejecución
- Script: `inc015_yv01_source_discovery.sql`
- Servidor: 128.1.3.21 · Base: DMF_VTA_PRD · Usuario: A_MOYA
- Fecha: 2026-08-12 08:46

## Bases de datos accesibles en el servidor
33 bases (DMF_VTA_PRD, SAP_PRD, SAP_QAS, B2B_PRD, INF_PRD, etc.)

## Candidatos con firma VBELN + POSNR/KWMENG/MATNR (en DMF_VTA_PRD)

| Objeto | Tipo | POSNR | KWMENG | MATNR | Muestra YV01 | Hits | Cobertura |
|---|---|---|---|---|---|---|---|
| VBAP_SAP | USER_TABLE | ✓ | ✓ | ✓ | 200 | 0 | 0% |
| VISTA_PEDIDO | VIEW | ✓ | ✓ | ✓ | 200 | 0 | 0% |
| VBRP_SAP | USER_TABLE | ✓ | ✗ | ✓ | 200 | 0 | 0% |
| VBRP_SAP_2 | USER_TABLE | ✓ | ✗ | ✓ | 200 | 0 | 0% |
| LIPS_SAP | USER_TABLE | ✓ | ✗ | ✓ | 200 | 0 | 0% |
| VBBE_SAP | USER_TABLE | ✓ | ✗ | ✓ | 200 | 0 | 0% |
| VBPA2_SAP | USER_TABLE | ✓ | ✗ | ✗ | 200 | 0 | 0% |

## VISTA_PEDIDO — análisis complementario

- 19.882 filas, 783 pedidos distintos
- AUART cubiertos: ZPDA(305), ZMAY(290), ZPPO(143), ZVGM(45)
- 0 pedidos YV01
- Definición VIEW inaccesible (falta permiso VIEW DEFINITION para A_MOYA)
- Solapa parcialmente con VBAP_SAP pero **no resuelve YV01**

## SAP_PRD

- Sin objetos VBAP
- Sin tablas con columna VBELN
- `dbo.VBAP` no existe

## Dictamen final

**`SIN_FUENTE_YV01_EN_DMF_VTA_PRD`**

Ninguna tabla, vista o sinónimo en DMF_VTA_PRD, SAP_PRD ni en las 33 bases accesibles del servidor contiene posiciones de pedidos YV01. YV01 es el AUART principal del universo Mayorista (349.215 headers, 95,4% del total).

## Opciones para resolver INC-015

1. **Réplica SAP → DMF**: crear una tabla `YV01_POSICIONES` replicando `VBAP` desde SAP con filtro AUART='YV01'
2. **Conexión directa SAP**: usar RFC/BW para consultar VBAP en SAP sin pasar por DMF_VTA_PRD
3. **Fuente externa**: identificar si hay un data lake, data warehouse o sistema intermedio con las posiciones YV01

## Recomendación

No modificar `Lineas_y_unidades_por_pedidos` hasta tener una fuente de posiciones YV01. La cobertura 58,3% es el máximo alcanzable con las fuentes actuales.
