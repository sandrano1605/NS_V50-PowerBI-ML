# IN02 — Hora de Ingreso Canales 43 y 45 (diagnóstico SQL)

## Ejecución
- SQL: `in02_hora_ingreso_audit.sql` contra DMF_VTA_PRD (A_MOYA)
- Ventana: 2026-05-12 a 2026-08-12 (3 meses)
- Power BI modelo vivo: puerto 64215

## Cobertura ZART (fuente primaria)

| Canal | Total pedidos | Hora válida | Sin hora válida | Cobertura |
|---|---|---|---|---|
| 43 | 1.232 | 1.111 | 121 | 90,18% |
| 45 | 301 | 268 | 33 | 89,04% |

## Causa de "Sin hora válida" en ZART

**100% de los casos: `ZART_HORA_000000`** — ZERZET_PED tiene el valor `000000` (medianoche), no NULL ni formato inválido. Power BI interpreta `H=#time(0,0,0)` como "Sin hora válida" (código M: `if H=null or H=#time(0,0,0) then "Sin hora valida"`).

## Recuperabilidad desde VBAK

| Canal | Sin hora ZART | Recuperable VBAK | % |
|---|---|---|---|
| 43 | 121 | **120** | **99,17%** |
| 45 | 33 | **33** | **100,00%** |
| Total | 154 | **153** | **99,35%** |

- 153 pedidos tienen `VBAK.ERZET` con hora válida (ej: 16:03:02, 09:05:28)
- 1 pedido (1168066, canal 43) no tiene entrada en VBAK → `SIN_VBAK`

## AUART de los recuperables

- ZMAY: ~80 pedidos (canal 43 + 45)
- ZPDA: ~73 pedidos (canal 43 + 45)

## Pedidos adicionales en VBAK sin ZART

20 pedidos del canal 43 tienen hora válida en VBAK pero no están en ZART (o su ZART tiene hora válida pero el modelo los clasifica mal). Requieren análisis adicional.

## Comparación con Power BI

Power BI reporta 197 pedidos "Sin hora válida" en canales 43/45. El SQL encuentra 154 en ZART con `000000`. La diferencia (43) incluye:
- 20 pedidos VBAK con hora (canal 43)
- Otros pedidos fuera de ventana de 3 meses o no en ZART

## Recomendación

El fix es viable y de bajo riesgo: cuando `ZERZET_PED = '000000'`, buscar `VBAK.ERZET` como fallback. Esto recuperaría 153 de 154 casos (99,35%).

**Código M propuesto (NO implementado):**
```
HoraRaw = if [ZERZET_PED] = "000000" or [ZERZET_PED] = null
    then VBAK[ERZET]  // fallback a cabecera SAP
    else [ZERZET_PED]
```
