# DICTAMEN — AUDITORÍA INTEGRAL MODELO Y LIENZOS

**SHA base:** 1866f3f39da0238398af112acb23a50b664d0cf1
**SHA corrección:** [pendiente commit]
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
| Cierre FES datos | 🟢 | 437 cerrados = 437 con manifiesto VBFA. 0 cierran por TRP solo. |
| Cierre FES regla | 🔴 | FECHA_MANIFIESTO permite TRP fallback (riesgo estructural,0 casos actuales) |
| Multiselect lienzo 00 RE | 🟢 | 14 medidas RE corregidas con helpers [RE Filtro Flujo]/[RE Filtro Zona] |
| Multiselect lienzo 00 distribución | 🟢 | RE Distribución Flujo SVG corregida con VALUES/ISFILTERED/CONTAINS |
| Reloj SLA | 🔴 | 946 pedidos diferidos por corte en Hitos vs Tracking sin corte |
| Denominador NS | 🟠 | U NS = 78.8% (1.962 denom) vs RE NS = 81.5% (1.898 denom) |
| Lienzo 01 multiselect | 🟠 | 9 medidas FA con SELECTEDVALUE |
| Lienzo 02 cobertura | 🟠 | VBAP coverage no cuantificada |
| SLA legacy | 🟢 | 5 DH hardcode solo en audit SQL y ML Python, no en visuales NS oficiales |
| Feriados | 🟠 | 50 nacionales. No contempla regionales |

---

## DICTAMEN: 🔴 ROJO

Existen **2 contradicciones materiales** que afectan números o interpretación:

### 1. Dos relojes SLA distintos (INC-006) — ROJO
- **Fact_Tracking**: reloj desde `PED_FECHA_HORA` (sin corte)
- **Fact_Hitos_Operacionales**: reloj desde `FECHA_INGRESO_SLA` con corte 14:00 L-J / 12:00 Viernes

**946 pedidos** están diferidos por corte en Fact_Hitos. Fact_Tracking los cuenta desde la hora de creación. Sin decisión de negocio formal, estos dos hechos entregan NS diferentes para el mismo pedido.

**Pendiente**: ejecutar comparativo de los 946 pedidos (DH actual vs DH con corte, NS impact).

### 2. Cierre FES permite TRP fallback (INC-007B) — ROJO
- **DATA**: 0 FES cierran sin manifiesto VBFA en datos actuales. VERDE.
- **REGLA**: `FECHA_MANIFIESTO` en Fact_Tracking.tmdl tiene fallback `TRP_U_FECHA_HORA` / `TRP_P_FECHA_HORA`. Si un FES llega sin manifiesto VBFA pero con TRP, el tracking lo cerraría sin manifiesto real. Fact_Hitos NO lo cerraría.

**Decisión requerida**: si FES debe cerrar exclusivamente con manifiesto VBFA/VTTP, eliminar el fallback TRP de FECHA_MANIFIESTO.

### 3. Dos denominadores para "NS interno" (INC-011) — AMARILLO
- **U NS observado interno** = 1.547 / 1.962 = **78.8%**
- **RE NS contexto** = 1.547 / 1.898 = **81.5%**

Los 64 cerrados sin DH válidos están en U pero no en RE. Ambos se llaman "NS interno" en distintos visuales.

---

## Correcciones aplicadas en este commit

### Multiselect RE (INC-005, INC-010) — CORREGIDO
14 medidas RE corregidas usando `[RE Filtro Flujo]` / `[RE Filtro Zona]` (helpers con VALUES/ISFILTERED/CONTAINS que ya funcionan en Pedidos contexto):

- RE Valor contexto
- RE Promedio contexto DH
- RE P90 contexto DH
- RE Pedidos hito con dato / cumplen
- RE Promedio hito DH / P90 hito DH
- RE Periodo contexto
- RE Tooltip seleccionado texto
- RE Pedido Seleccionado SVG
- RE FES Brecha facturación promedio DH

**RE Distribución Flujo SVG**: corregida con VALUES/ISFILTERED/CONTAINS para display condicional (no helpers, porque usa FlujoSel para decidir qué segmentos mostrar, no para filtrar filas).

### Proxy factura (INC-008) — CORREGIDO documentación
FECHA_DESPACHO se calcula para TODOS los flujos (no solo Normal/Saldo). Lo diferente es que FES usa FECHA_MANIFIESTO para FECHA_CIERRE.

### FES DATA/REGLA (INC-007) — CORREGIDO documentación
Separado INC-007A (datos: VERDE) de INC-007B (regla: ROJO).

---

## Pendientes antes de declarar VERDE

1. **Eliminar fallback TRP de FECHA_MANIFIESTO** si mantenemos la regla "FES solo cierra por manifiesto VBFA/VTTP".
2. **Comparativo 946 pedidos diferidos**: cuántos cambian DH, cuántos FUERA→EN SLA, cuántos EN→FUERA SLA, NS actual vs NS con corte.
3. **Corregir 9 medidas FA** del lienzo 01 con el mismo patrón helpers.
4. **Unificar denominadores U vs RE**: documentar NS oficial 81.5% sobre 1.898 evaluables.
5. **Cuantificar cobertura VBAP** lienzo 02: pedidos con/sin match líneas/unidades.

---

## Evidencia

- `00_git.txt` · `01_refresh.txt` · `02_universo_master.csv` · `03_integridad_relaciones.csv`
- `04_fes_cierre_manifesto_vs_trp.csv` · `05_sla_reloj_actual_vs_corte.csv`
- `06_proxy_factura_despacho.csv` · `07_sla_clasificacion.csv`
- `08_multiselect_lienzo00.csv` · `09_visuales_lienzo00.csv`
- `10_visuales_lienzo01.csv` · `11_visuales_lienzo02.csv`
- `12_cobertura_lineas_unidades.csv` · `13_medidas_u_vs_re.csv`
- `14_legacy_sla.csv` · `15_incoherencias.csv`
