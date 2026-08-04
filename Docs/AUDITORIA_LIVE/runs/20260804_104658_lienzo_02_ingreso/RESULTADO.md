# RESULTADO: Validación lienzo 02 — Ingreso de Pedidos (2026-08-04)

**Rama:** work/ns-lienzo-02-ingreso-pedidos
**SHA local:** 9f0a65da0f257b1f3884d64345cc250424184ef1
**SHA remoto:** 9f0a65da0f257b1f3884d64345cc250424184ef1
**Dictamen:** 🟢 VERDE — preguntas respondidas con cifras reales

## Contexto

- Modelo refrescado: Fact_Tracking=1.942, Master=1.938, Lineas_y_unidades=22.788.
- Columna `TRAMO_HORA_INGRESO` corregida y expuesta en el modelo (commit 9f0a65d).
- Página 02: 26 visuales, 6 filtros, 3 tarjetas, lectura ejecutiva, 3 botones con bookmarks.

## Q1 · ¿Qué día ingresan más pedidos, líneas y unidades?

| Día | Pedidos | Líneas | Unidades |
|---|---|---|---|
| Lunes | **553** | 4.454 | 431.793 |
| Martes | 370 | 4.167 | 250.949 |
| Miércoles | 368 | 3.717 | **563.221** |
| Jueves | 356 | **5.665** | 361.287 |
| Viernes | 266 | 2.631 | 307.026 |
| Sábado | 19 | 207 | 13.943 |
| Domingo | 10 | 84 | 3.522 |
| **Total** | **1.942** | **20.925** | **1.931.741** |

**Respuesta:** Lunes lidera pedidos (553); Jueves lidera líneas (5.665);
Miércoles lidera unidades (563.221).

## Q2 · ¿A qué hora quedan disponibles para Logística?

| Día | Hasta 14:30 | Después 14:30 | Sin hora válida | Total |
|---|---|---|---|---|
| Lunes | 157 | 113 | 283 | 553 |
| Martes | 114 | 130 | 126 | 370 |
| Miércoles | 128 | 107 | 133 | 368 |
| Jueves | 102 | 92 | 162 | 356 |
| Viernes | 126 | 65 | 75 | 266 |
| Sábado | 9 | 8 | 2 | 19 |
| Domingo | 1 | 4 | 5 | 10 |
| **Total** | **637 (32,8%)** | **519 (26,7%)** | **786 (40,5%)** | **1.942** |

**Respuesta:** 32,8% hasta 14:30; 26,7% después de 14:30; 40,5% sin hora válida.
Los registros 00:00:00 quedan en "Sin hora válida" (correcto, no se clasifican como tempranos).
Suma por día reconcilia con Q1 (ej. Lunes 157+113+283=553 ✅).

## Q3 · ¿Existe concentración hacia el final del mes?

### Pedidos por día del mes (1-31)
- Días máximos: día 1 (106), 8 (109), 22 (107), 28 (93).
- Últimos 7 DH (Cierre): 625 pedidos.
- Resto del mes: 587 pedidos.
- **Delta cierre vs resto: +6,5%** (625 vs 587).

### Desglose por flujo en el cierre
| Flujo | Pedidos en cierre | Participación |
|---|---|---|
| NORMAL | 470 | 75,2% |
| FES | 153 | 24,5% |
| SALDO | 1 | 0,2% |
| FES + SALDO | 1 | 0,2% |
| **Total cierre** | **625** | 100% |

**Respuesta:** Sí existe concentración moderada al cierre (+6,5%). El crecimiento
es principalmente NORMAL (75,2% del cierre); FES/Saldo aportan 24,8% del cierre.

### Líneas por día del mes
- Días máximos: día 2 (2.134), 8 (1.293), 18 (1.142), 28 (1.511).

### Unidades por día del mes
- Días máximos: día 29 (454.282), 28 (195.861), 4 (161.220).
- El día 29 concentra el 23,5% de las unidades del mes.

## Tarjetas (Q0)

| Tarjeta | Valor |
|---|---|
| Pedidos ingresados | 1.942 |
| Líneas ingresadas | 20.925 |
| Unidades ingresadas | 1.931.741 |

## Lectura ejecutiva dinámica

```
Días líderes · Pedidos: Lunes (553) · Líneas: Jueves (5.665) · Unidades: Miércoles (563.221)
Después de 14:30: 26,7%
Cierre vs resto: +6,5%
FES/Saldo en cierre: 24,8%
```

## Botones y bookmarks (verificado estructural)

| Botón | Visible | Ocultos | Filtros | Targets |
|---|---|---|---|---|
| VER POR PEDIDOS | pedidos | líneas+unidades | sin captura | 3 ✅ |
| VER POR LINEAS | líneas | pedidos+unidades | sin captura | 3 ✅ |
| VER POR UNIDADES | unidades | pedidos+líneas | sin captura | 3 ✅ |

- display.mode=hidden según esquema 2.1.0 (validado sin errores).
- Filtro global 43/45: eliminado.

## Archivos de evidencia

00_git_before.txt · 01_refresh.txt · 02_tarjetas.csv · 03_lectura_ejecutiva.csv ·
04_q1_dia_semana.csv · 05_q2_hora_1430.csv · 06_q3_pedidos_dia_mes.csv ·
07_q3_lineas_dia_mes.csv · 08_q3_unidades_dia_mes.csv · 09_botones_y_filtros.csv ·
10_calidad_visual.txt · 11_regresiones.txt · 13_visual_inventory.csv ·
14_smoke_test_paginas.txt · 15_incoherencias.csv · RESULTADO.md · manifest.json
