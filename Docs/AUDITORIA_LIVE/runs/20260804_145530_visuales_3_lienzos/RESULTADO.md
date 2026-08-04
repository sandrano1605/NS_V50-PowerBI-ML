# RESULTADO: Evidencia de visuales de los 3 lienzos + hallazgo SLA (2026-08-04)

**Rama:** work/ns-lienzo-02-ingreso-pedidos
**SHA:** 0c5ea56ea34c66a7ac39f8eb2d42d6d1790c5d00 (cambios de usuario: botones nav eliminados)

## 1. Cambios del usuario publicados

- Commit `0c5ea56`: eliminados botones de navegación (`nav_tracking_v34`,
  `nav_resumen_v34`, `nav_cuellos_v34`, `nav_detalle_v34`) en lienzos 00, 01 y 02;
  eliminado `footer_actualizacion` y `shape_d1e9fe2f962046` en la 02.
- 38 archivos cambiados, todos publicados y empujados.

## 2. Inventario de visuales (62 totales)

| Lienzo | Visuales |
|---|---|
| 00 Resumen Ejecutivo Mayorista | 25 |
| 01 Análisis Fuera SLA | 13 |
| 02 Ingreso de Pedidos | 24 |

Archivo: `01_inventario_visuales.csv` (con posiciones X/Y/W/H).

## 3. KPIs de los 3 lienzos

### Lienzo 00 — Resumen Ejecutivo
| KPI | Valor |
|---|---|
| Pedidos evaluables | 1.781 |
| Pedidos en SLA | 1.549 |
| Pedidos fuera SLA | 232 |
| NS | 87,0% |
| Valor contexto | 1.861.100.093 CLP |

### Lienzo 01 — Análisis Fuera SLA
| KPI | Valor |
|---|---|
| FA Pedidos | 1.781 |
| FA Fuera SLA | 232 (13,0%) |
| FA FES | 213 (12,0%) |

### Lienzo 02 — Ingreso de Pedidos
| KPI | Valor |
|---|---|
| IN Pedidos | 1.950 |
| IN Líneas | 21.171 |
| IN Unidades | 2.003.201 |
| Lectura ejecutiva | Q1/Q2/Q3 respondidas (ver abajo) |

## 4. Lectura ejecutiva del lienzo 02 (texto real del modelo)

```
Días líderes · Pedidos: Lunes (553) · Líneas: Jueves (5.665) · Unidades: Miércoles (563.221)
Hora válida: 59,3% · Después de 14:30 sobre medibles: 44,9% · Sin hora: 40,7%
Cierre vs resto (promedio diario): 24,0 vs 21,7 (+10,6%) · FES/Saldo: 24,8% · Día pico unidades: 29 (22,7%)
```

## 5. HALLAZGO: pedidos fuera de SLA en la tabla 1 del lienzo 01

**El usuario reportó 54 pedidos "fuera del SLA" en la tabla
"1. CLIENTES FUERA SLA · FRECUENCIA EN LOS ÚLTIMOS 3 MESES" y pidió revisarlos.**

### Investigación (evidencia)

- La medida base `RE Pedidos fuera SLA contexto = RE Pedidos contexto - RE Pedidos en SLA contexto`.
- `RE Pedidos contexto` filtra `ES_CERRADO=TRUE() && NOT ISBLANK(DIAS_INTERNOS_DH)` → cohorte cerrada oficial.
- Total de pedidos fuera de SLA en el universo: **109** (junio=59, julio=50).
- Composición: **95 NORMAL + 14 FES** (SALDO/FES+SALDO = 0).
- El usuario ve **54** en la tabla → es el subconjunto del **contexto del slicer de mes vigente**
  y de la agrupación por cliente con recurrencia visible (FA Meses Fuera SLA Cliente >= 1).

### ¿De dónde salen?

Son pedidos **reales cerrados fuera de SLA** — no son "fantasmas". Ejemplos verificados:

| Pedido | Cliente | Clasif | Días internos | SLA | Exceso | Estado |
|---|---|---|---|---|---|---|
| 1167123 | 981617 | NORMAL | 5 | 4 | 1 DH | CERRADO FUERA SLA |
| 1166855 | 550126 | NORMAL | 17 | 5 | 12 DH | CERRADO FUERA SLA |
| 1167033 | 590042 | FES | 22 | 5 | 17 DH | CERRADO FUERA SLA |

Cada uno tiene `CUMPLE_SLA_INTERNO=False`, `EXCESO_SLA_INTERNO_DH>=1`, `SEMAFORO=CERRADO FUERA SLA`.

### Conclusión

- Los 54 pedidos son **legítimos** (cerrados fuera de SLA), no datos erróneos.
- Aparecen en la tabla porque la medida `FA Pedidos Fuera SLA Cliente Visible`
  los agrupa por cliente con recurrencia.
- **NO se modificó el modelo** (protocolo: no corregir sin autorización).
- Si el negocio considera que deben excluirse del lienzo 01, la decisión y ajuste
  de medidas corresponde a ChatGPT (requiere cambio de DAX en `RE Pedidos contexto`
  o en `FA Pedidos Fuera SLA Cliente Visible`).

## 6. Archivos de evidencia

- 00_git.txt
- 01_inventario_visuales.csv (62 visuales con posiciones)
- 02_kpis_3_lienzos.csv
- 03_resumen_visuales.csv
- RESULTADO.md (este archivo)
- manifest.json
