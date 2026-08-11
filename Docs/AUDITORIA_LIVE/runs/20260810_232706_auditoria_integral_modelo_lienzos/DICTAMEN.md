# DICTAMEN — AUDITORÍA INTEGRAL MODELO Y LIENZOS

**SHA:** 1866f3f39da0238398af112acb23a50b664d0cf1
**Fecha:** 2026-08-10 23:26:42
**Modelo:** Power BI Desktop local, puerto 57525

---

## Capa	Estado	Resultado

| Capa | Estado | Resultado |
|------|--------|-----------|
| Universo actual | 🟢 | 2.048 total; 1.898 cerrados evaluables |
| NS principal | 🟢 | 1.547 en SLA + 351 fuera = 1.898 |
| Clasificación | 🟢 | 1.459 NORMAL + 432 FES + 5 FES+SALDO + 2 SALDO = 1.898 |
| SLA zonal | 🟢 | Santiago 4/3/5 · Regiones 5/4/7 (verificado contra columnas reales) |
| Tabla fuera SLA | 🟢 | 351 = 351, 0 duplicados |
| Cliente/Dimensiones | 🟢 | sin match = 0, region blank = 0, region inválido = 0 |
| Cierre FES | 🟢 | 437 cerrados = 437 con manifiesto VBFA. 0 cierran por TRP solo. INC-007 no se materializa. |
| Multiselect lienzo 00 | 🔴 | 14 medidas RE usan SELECTEDVALUE. Valor/PromDH/P90 devuelven universo completo con multiselect |
| Reloj SLA | 🔴 | 946 pedidos diferidos por corte en Hitos vs Tracking sin corte |
| Denominador NS | 🟠 | U NS = 78.8% (1.962 denom) vs RE NS = 81.5% (1.898 denom) |
| Lienzo 01 multiselect | 🟠 | 9 medidas FA con SELECTEDVALUE |
| Lienzo 02 | 🟢 | Corte 14:30 es análisis carga logística, no corte SLA |
| SLA legacy | 🟢 | 5 DH hardcode solo en audit SQL y ML Python, no en visuales NS oficiales |
| Feriados | 🟠 | 50 nacionales. No contempla regionales |

---

## DICTAMEN: 🔴 ROJO

Existen **3 contradicciones materiales** que afectan números o interpretación:

### 1. Multiselect incompleto (INC-005, INC-010)
**14 medidas RE** todavía usan `SELECTEDVALUE(Dim_Vista_Ejecutiva[Flujo])`:
- RE Valor contexto
- RE Promedio contexto DH
- RE P90 contexto DH
- RE Pedidos hito con dato / cumplen
- RE Promedio hito DH / P90 hito DH
- RE Periodo contexto
- RE Distribución Flujo SVG
- RE Tooltip seleccionado texto
- RE Pedido Seleccionado SVG
- RE Evolución 3M SVG

**Consecuencia probada**: con selección Normal+FES (1.896 pedidos), los filtros de Pedidos y Fuera SLA funcionan correctamente, pero **Valor = 2.274M (universo completo), PromDH = 3.5 (universo completo), P90 = 8 (universo completo)**. Los visuales muestran datos mezclados.

**9 medidas FA** del lienzo 01 tienen el mismo problema.

### 2. Dos relojes SLA distintos (INC-006)
- **Fact_Tracking**: reloj desde `PED_FECHA_HORA` (sin corte)
- **Fact_Hitos_Operacionales**: reloj desde `FECHA_INGRESO_SLA` con corte 14:00 L-J / 12:00 Viernes

**946 pedidos** están diferidos por corte en Fact_Hitos. Fact_Tracking los cuenta desde la hora de creación. Sin decisión de negocio formal, estos dos hechos entregan NS diferentes para el mismo pedido.

### 3. Dos denominadores para "NS interno" (INC-011)
- **U NS observado interno** = 1.547 / 1.962 = **78.8%**
- **RE NS contexto** = 1.547 / 1.898 = **81.5%**

Los 64 cerrados sin DH válidos están en U pero no en RE. Ambos se llaman "NS interno" en distintos visuales.

---

## Hallazgos NO bloqueantes

| ID | Hallazgo | Estado |
|----|----------|--------|
| INC-007 | FES cierra sin manifiesto: **0 pedidos**. FECHA_MANIFIESTO no usa TRP fallback. | 🟢 |
| INC-008 | Proxy factura→despacho Santiago: diferencia estructural menor (ventana temporal). | 🟠 |
| INC-009 | Lienzo 01 FA medidas con SELECTEDVALUE (9 medidas). | 🟠 |
| INC-012 | SLA legacy 5 DH hardcode: solo en audit SQL y ML Python, no en visuales NS oficiales. | 🟢 |
| INC-013 | Feriados regionales no implementados. | 🟠 |
| INC-014 | Corte 14:30 lienzo 02: correcto como análisis de carga, no corte SLA. | 🟢 |

---

## Pendientes antes de declarar VERDE

1. **Corregir 14 medidas RE + 9 medidas FA** para usar helpers multiselect (mismo fix MAX() que se aplicó a Pedidos contexto).
2. **Decisión de negocio**: ¿NS se mide desde PED_FECHA_HORA o desde FECHA_INGRESO_SLA con corte?
3. **Unificar denominadores U vs RE**: documentar explícitamente cuál es el NS oficial y en qué universo.

---

## Evidencia

- `00_git.txt` · `01_refresh.txt` · `02_universo_master.csv` · `03_integridad_relaciones.csv`
- `04_fes_cierre_manifesto_vs_trp.csv` · `05_sla_reloj_actual_vs_corte.csv`
- `06_proxy_factura_despacho.csv` · `07_sla_clasificacion.csv`
- `08_multiselect_lienzo00.csv` · `09_visuales_lienzo00.csv`
- `10_visuales_lienzo01.csv` · `11_visuales_lienzo02.csv`
- `12_cobertura_lineas_unidades.csv` · `13_medidas_u_vs_re.csv`
- `14_legacy_sla.csv` · `15_incoherencias.csv`
