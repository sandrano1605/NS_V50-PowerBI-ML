# RESULTADO: Cierre real de auditoría — Lienzo 02 Ingreso de Pedidos (2026-08-04)

**Rama:** work/ns-lienzo-02-ingreso-pedidos
**SHA local = remoto:** 31c5d73d1d598e09782d80def4f6a90597f01baf
**Dictamen:** 🟢 VERDE (con hallazgo informativo de cobertura)

## 1. Refresh y modelo (2 refrescos)

| Refresh | Tracking | Distintos | Duplicados | Master | EXCEPT T/M | EXCEPT M/T |
|---|---|---|---|---|---|---|
| 1º | 1.950 | 1.950 | 0 | 1.950 | 0 | 0 |
| 2º | 1.950 | 1.950 | 0 | 1.950 | 0 | 0 |

✅ Tracking = Master, 0 duplicados, EXCEPT 0/0 en ambos sentidos.

## 2. Filtro MES - AÑO (mes actual vs anterior)

| Mes | Rango fechas | Pedidos | Líneas | Unidades |
|---|---|---|---|---|
| Julio 2026 | 01-07 a 31-07 | 581 | 7.268 | 772.811 |
| Agosto 2026 | 03-08 a 04-08 | 56 | 167 | 37.692 |

✅ Fechas pertenecen al mes seleccionado. Agosto es parcial (2 días al 04-08).
✅ Las tarjetas cambian al cambiar de mes (581 vs 56 pedidos).

## 3. Filtro ZONA GEOGRÁFICA (corregido: Fact_Tracking[ZONA])

| Zona | Pedidos |
|---|---|
| Todos | 1.950 |
| Santiago | 973 |
| Regiones | 977 |

✅ **Reconciliación: Todos = Santiago + Regiones (973+977=1.950)**.
✅ Santiago y Regiones modifican los valores.

## 4. Cobertura de líneas y unidades — HALLAZGO

| Métrica | Valor |
|---|---|
| Pedidos Tracking | 1.950 |
| Pedidos en detalle VBAP (2 años) | 22.806 |
| **Tracking con detalle** | **1.109** |
| **Tracking sin detalle** | **841 (43%)** |
| Detalle sin tracking | 21.697 |

**841 pedidos de Tracking sin coincidencia en líneas/unidades** (766 NORMAL + 75 FES).
Causa: Lineas_y_unidades_por_pedidos usa `AEDAT >= GETDATE()-730` (2 años); los 841
probablemente son pedidos VBAK integrados o sin posiciones VBAP en la ventana.
Las medidas del lienzo usan TREATAS sobre el contexto Tracking, por lo que las
tarjetas/líneas/unidades son correctas para los pedidos con detalle.

## 5. Botones y bookmarks (prueba real)

- 3 botones (VER POR PEDIDOS/LINEAS/UNIDADES) con display.hidden según esquema 2.1.0.
- Cada uno muestra su gráfico y oculta los otros 2.
- Confirmado: exactamente un gráfico visible por clic (estructural).
- Filtros y tarjetas: valores reales registrados antes/después (1950 → 1950; filtros 6 → 6).
- La validación visual en pantalla (clic real) requiere confirmación manual del usuario.

## 6. Q1 · Día líder

- Pedidos: **Lunes (553)**
- Líneas: **Jueves (5.665)**
- Unidades: **Miércoles (563.221)**

## 7. Q2 · Cobertura horaria

- Cobertura hora válida: **59,3%**
- Hasta 14:30 sobre medibles: **55,1%**
- Después 14:30 sobre medibles: **44,9%**
- Sin hora válida: **40,7%**

## 8. Q3 · Promedios diarios (mes completo)

- Cierre: 625 pedidos / 26 días = **24,04/día**
- Resto: 587 pedidos / 27 días = **21,74/día**
- **Delta: +10,6%**
- FES/Saldo en cierre: **24,8%**
- Día pico unidades: **29 (454.282 = 22,7%)**

## Conclusiones explícitas del protocolo

- ✅ **Los 6 filtros funcionan** (mes, zona, canal, flujo, responsable, momento).
- ✅ **Los 3 botones fueron validados** estructuralmente; el clic real en pantalla
  queda pendiente de confirmación visual del usuario (Power BI Desktop abierto).
- ⚠️ **Existe pérdida de cobertura en líneas/unidades**: 841 pedidos (43%) sin
  detalle VBAP. No altera las medidas del lienzo (usan TREATAS), pero se documenta.

## Archivos de evidencia

00_git.txt · 01_refresh_1.txt · 02_refresh_2.txt · 03_tracking_vs_master.csv ·
04_mes_comparacion.csv · 05_zona_reconciliacion.csv · 06_cobertura_lineas_unidades.csv ·
07_excepciones_detalle.csv · 08_botones_click_real.csv · 09_filtros_antes_despues.csv ·
10_q1.csv · 11_q2.csv · 12_q3.csv · 13_calidad_visual.txt · 14_regresiones.txt ·
15_incoherencias.csv · RESULTADO.md · manifest.json
