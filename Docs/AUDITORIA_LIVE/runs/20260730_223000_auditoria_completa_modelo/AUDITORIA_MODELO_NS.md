# AUDITORÍA MODELO NS — Modelo en vivo v15

## Resultado general

**Estado: VERDE** (con 3 hallazgos medios de visualización a corregir)

- Fecha auditoría: 30-07-2026 22:54 (refresco 31-07-2026 02:49)
- Modelo: NS — `NS_V50_v15_Error_Python_ndarray_Corregido`
- Conexión: MCP Modeline en vivo (localhost:55483 → proceso PBIDesktop "NS")
- Universo evaluado: **1.616 pedidos cerrados** de 1.695 totales (79 abiertos excluidos del NS histórico)
- Clientes: 682

---

## Resumen ejecutivo

| Métrica | Lienzo 00 (RE) | Lienzo 01 (FA) | Diferencia |
|---|---|---|---|
| Pedidos | 1.616 | 1.616 | **0** ✅ |
| Fuera SLA | 360 | 360 | **0** ✅ |
| NS | 77,72% | 77,72% (1 - 22,28%) | **0** ✅ |

| Zona | Pedidos | Fuera SLA | NS | Consistencia |
|---|---|---|---|---|
| Santiago | 708 | 161 | 77,26% | ✅ |
| Regiones | 908 | 199 | 78,08% | ✅ |

| Flujo | Pedidos | % |
|---|---|---|
| NORMAL | 1.243 | 73,4% |
| FES | 448 | 26,4% |
| FES + SALDO | 3 | 0,2% |
| SALDO | 1 | 0,1% |

### Recurrencia (ventana 3M: 2026-05, 2026-06, 2026-07)

| Clasificación | Clientes | Consistencia medida vs recálculo |
|---|---|---|
| Recurrente 3M | 3 | ✅ coincide |
| Recurrente 2M | 27 | ✅ coincide (2M+ = 30 oficial) |
| Puntual 1M | 221 | ✅ |
| Sin incumplimiento | 430 | ✅ |
| **Total fuera SLA** | **251 clientes / 360 pedidos** | ✅ |

---

## Reglas de negocio verificadas

| Regla | Resultado |
|---|---|
| Universo: solo cerrados con DIAS_INTERNOS_DH | ✅ 1.616 de 1.695 (ES_CERRADO + días informado) |
| Cierre FES/FES+SALDO = último manifiesto | ✅ 451/451 verificados |
| Cierre NORMAL/SALDO = último despacho | ✅ 1.244/1.244 verificados |
| SLA interno Santiago = 4 DH | ✅ SLA_INTERNO_DH = 1 + 3 |
| SLA interno Regiones = 5 DH | ✅ SLA_INTERNO_DH = 1 + 4 |
| Promesa cliente Santiago = 5 DH | ✅ SLA_CLIENTE_DH = 4 + 1 |
| Promesa cliente Regiones = 7 DH | ✅ SLA_CLIENTE_DH = 5 + 2 |
| Cumplimiento usa CUMPLE_SLA_INTERNO (zonal) | ✅ v15 corregido — ya NO usa >5/<=5 fijo |
| No existen medidas con SLA fijo 5 | ✅ 0/276 medidas marcadas REVISAR |
| Días hábiles: excluye inicio, fines de semana y feriados | ✅ 0 diferencias en 1.695 recálculos |
| Recurrencia: 0..3 meses, sin meses en blanco | ✅ validado 681 clientes, 0 errores |

---

## Hallazgos críticos

**Ninguno.** El modelo v15 corrigió el error de SLA fijo (v14 usaba `DIAS_INTERNOS_DH <= 5`; v15 usa `CUMPLE_SLA_INTERNO = TRUE()`).

## Hallazgos medios

1. ~~Visual `fa_clientes_recurrentes` NO muestra todos los clientes fuera SLA.~~ **CORREGIDO (P1, 2026-07-31)**
   - Las 5 medidas "Visible" usaban `IF([FA Meses Fuera SLA Cliente] >= 2, ...)` y excluían 221 clientes "Puntual 1M".
   - **Aplicado**: cambio a `>= 1` en:
     - `FA Meses Fuera SLA Cliente Visible`
     - `FA Recurrencia Cliente Visible`
     - `FA Pedidos Fuera SLA Cliente Visible`
     - `FA % Fuera SLA Cliente Visible`
     - `FA DH Fuera SLA Cliente Visible`
   - **Universo resultante verificado en vivo**: 251 clientes (3 Recurrente 3M + 27 Recurrente 2M + 221 Puntual 1M).

2. ~~Ordenamiento por Prom. DH~~ **CORREGIDO (P2, 2026-07-31)**
   - Sort del visual `fa_clientes_recurrentes` actualizado: `FA Meses Fuera SLA Cliente Visible` DESC → `FA Pedidos Fuera SLA Cliente Visible` DESC → `FA DH Fuera SLA Cliente Visible` DESC.
   - Verificado en vivo: primer bloque = 3 clientes Recurrente 3M (PRISA 7 pedidos, EVENTAIL 4, PLAZA EGAÑA 3).

3. ~~Título desactualizado~~ **CORREGIDO (P3, 2026-07-31)**
   - Nuevo título: "1. CLIENTES FUERA SLA · FRECUENCIA EN LOS ÚLTIMOS 3 MESES".

4. **Pedidos abiertos en tracking pero excluidos del NS**: 79 pedidos abiertos (4,7%) no entran al histórico — correcto según regla, pero el tracking operativo (lienzo 03) los muestra. No es error.

## Hallazgos menores

- La columna `TRACKING` del plan de auditoría no existe en el modelo; el filtro equivalente es `ES_CERRADO = TRUE AND NOT ISBLANK(DIAS_INTERNOS_DH)`.
- `Dim_Responsable` tiene 1 sola columna (RESPONSABLE_CODIGO), sin nombre — los visuales usan `Dim_Cliente.VENDEDOR_NOMBRE` para mostrar el vendedor.
- Línea de unidades: tabla `Lineas_y_unidades_por_pedidos` (22.835 filas) con 1 fila/pedido; cobertura vs tracking verificada.

---

## Auditoría de pedidos clave

| Pedido | Flujo | Zona | Cerrado | Creación | Factura | Despacho | Manifiesto | Cierre | DH | SLA | Cumple |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 4190139455 | FES | Regiones | ✅ | 26-05 16:16 | 28-05 15:56 | 28-05 16:05 | 28-05 | 28-05 (manifiesto) | 2 | 5 | ✅ |
| 1167577 | FES | Santiago | ✅ | 30-06 16:50 | 01-07 12:11 | 01-07 12:11 | 02-07 | 02-07 (manifiesto) | 2 | 4 | ✅ |

Ambos cierran con **manifiesto** (regla FES correcta). El recálculo independiente coincide con el modelo.

## Medidas incorrectas

Ninguna detectada. Las 276 medidas fueron revisadas por SLA fijo 5; 0 marcadas. La medida de recurrencia `FA Meses Fuera SLA Cliente` está corregida para ignorar el filtro de mes del canvas (usa `ALL(Dim_Periodo_3M)` + `REMOVEFILTERS(Dim_Fecha)` + `TREATAS`).

## Fechas de cierre incorrectas

Ninguna. 1.695/1.695 pedidos con `FECHA_CIERRE` coincidente con la fuente esperada (FES→manifiesto, otros→despacho).

## Diferencias entre modelo y recálculo

| Archivo | Diferencia |
|---|---|
| 03 cohorte | 1.695 filas (universo completo) |
| 04 fechas | 0 diferencias en cierre |
| 05 días hábiles | 0 diferencias en 1.695 recálculos (convención excluye día inicial) |
| 07 recurrencia | 0 inconsistencias en clasificación |

## Problemas de relaciones

Ninguna relación ambigua detectada. 35 relaciones, todas unidireccionales, 1 activa por par. Fact_Tracking → Dim_Pedido, Lineas → Dim_Pedido verificadas sin duplicación.

## Problemas de visuales

1. ~~`fa_clientes_recurrentes` excluía Puntual 1M~~ **CORREGIDO (P1)**: ahora muestra 251 clientes.
2. ~~`fa_clientes_recurrentes` ordenaba por Prom. DH~~ **CORREGIDO (P2)**: ahora ordena por recurrencia (3M→2M→1M) y luego pedidos y DH.
3. ~~Título~~ **CORREGIDO (P3)**: "1. CLIENTES FUERA SLA · FRECUENCIA EN LOS ÚLTIMOS 3 MESES".
4. Los demás visuales FA (`fa_permanencia_cd`, `fa_vendedores_reincidentes`, `fa_fes_carga_tiempo`) usan cohorte cerrada con medidas correctas.

## Problemas de Power Query/Python

- **El error `ndarray` de Python fue corregido en v15** (nombre del proyecto lo indica). No se detectó `Python.Execute` en las 27 particiones M (fuente SQL directa).
- `Fact_Pedidos_Auditoria` usa SQL con ventana móvil de 3 meses (`DATEADD(MONTH, -3, GETDATE())`).
- `Fact_Tracking` deriva de `Fact_Pedidos_Auditoria` con lógica M (ZONA, CLASIFICACION, cierres, DH con feriados).

## Recomendaciones priorizadas

1. **✅ APLICADO (P1)** — Mostrar todos los clientes fuera SLA: `>= 2` → `>= 1` en las 5 medidas "Visible" de recurrencia. Verificado: 251 clientes.
2. **✅ APLICADO (P2)** — Ordenar por recurrencia: sort 3M→2M→1M, luego pedidos y DH. Verificado: 3 Recurrente 3M primero.
3. **✅ APLICADO (P3)** — Título actualizado: "1. CLIENTES FUERA SLA · FRECUENCIA EN LOS ÚLTIMOS 3 MESES".
4. **OPCIONAL (mejora visual)** — Formato condicional en columna Recurrencia (3M rojo, 2M amarillo, 1M gris) y filtro rápido "Todos | 3M | 2M | 1M". Requiere acción manual en Power BI Desktop.

---

## Evidencia generada

| Archivo | Filas | Descripción |
|---|---|---|
| 00_inventario_modelo.csv | 892 | Tablas, columnas, medidas, particiones |
| 01_relaciones_modelo.csv | 35 | Relaciones del modelo |
| 02_medidas_sla.csv | 276 | Auditoría SLA fijo 5 (0 errores) |
| 03_cohorte_tracking.csv | 1.695 | Universo completo por pedido |
| 04_auditoria_fechas.csv | 1.695 | Cierres vs fuente esperada (0 diff) |
| 05_auditoria_dias_habiles.csv | 1.695 | DH modelo vs recálculo (0 diff) |
| 06_auditoria_pedidos_clave.csv | 39 | 4190139455, 1167577 + muestras |
| 07_clientes_recurrentes.csv | 681 | Recurrencia 3M/2M/1M por cliente |
| 08_permanencia_postfactura.csv | 1.695 | Factura → cierre oficial |
| 08b_resumen_permanencia_cliente.csv | 5 | Resumen por cliente >15 DH |
| 09_vendedores_recurrentes.csv | 13 | Vendedores con clientes recurrentes |
| 10_fes_vs_carga.csv | 4 | FES vs carga por mes |
| 11_comparacion_lienzos.csv | 22 | Lienzo 00 vs 01 (0 diferencias) |
| 12_cobertura_lineas_unidades.csv | 1.695 | Cobertura líneas/unidades |
| 13_objetos_lienzos.csv | 74 | Visuales de 3 páginas |
| 14_consultas_powerquery.csv | 27 | Particiones M (sin Python) |
| AUDITORIA_MODELO_NS.md | — | Este informe |
