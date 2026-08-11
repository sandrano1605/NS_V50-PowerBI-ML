# DICTAMEN — AUDITORÍA INTEGRAL MODELO Y LIENZOS

**SHA base auditoría:** 1866f3f39da0238398af112acb23a50b664d0cf1  
**Última validación viva FA:** abc5de3382b774046787e90b07dbdc2f50b0896e  
**Fecha de reevaluación INC-006:** 2026-08-11

---

## Estado por capa

| Capa | Estado | Resultado |
|---|---|---|
| Universo actual | 🟢 | 2.048 total; 1.898 cerrados evaluables |
| NS principal | 🟢 | 1.547 en SLA + 351 fuera = 1.898 |
| Clasificación | 🟢 | 1.459 NORMAL + 432 FES + 5 FES+SALDO + 2 SALDO = 1.898 |
| SLA zonal | 🟢 | Santiago 4/3/5 · Regiones 5/4/7 |
| Tabla fuera SLA | 🟢 | 351 = 351, 0 duplicados |
| Cliente/Dimensiones | 🟢 | sin match = 0, región blank = 0, región inválida = 0 |
| Cierre FES datos | 🟢 | 437 cerrados = 437 con manifiesto VBFA; 0 cierran solo por TRP en datos actuales |
| Cierre FES regla | 🔴 | `Fact_Tracking.FECHA_MANIFIESTO` aún permite fallback TRP; riesgo estructural futuro |
| Multiselect RE | 🟢 | 14 medidas validadas en vivo; Normal+FES y combinaciones de zona correctas |
| Multiselect FA | 🟢 | 14 medidas validadas en vivo; 10 combinaciones de multiselect correctas |
| Corte SLA / INC-006 | 🟢 | 946 diferidos existen, pero el corte solo afecta preparación/promesa; impacto sobre NS interno = 0 |
| Denominador NS | 🟠 | U NS = 78,8% (1.962) vs RE NS = 81,5% (1.898) |
| Lienzo 02 cobertura | 🟠 | cobertura VBAP aún no cuantificada |
| SLA legacy | 🟢 | 5 DH hardcode solo en auditoría SQL/ML, no en visuales NS oficiales |
| Feriados | 🟠 | nacionales implementados; regionales no |

---

## DICTAMEN ACTUAL: 🔴 ROJO

Queda **un bloqueo rojo estructural**:

### INC-007B — FES permite fallback TRP en `FECHA_MANIFIESTO`

- **Datos actuales:** 0 FES cierran sin manifiesto VBFA real.
- **Regla actual:** `Fact_Tracking` permite usar `TRP_U_FECHA_HORA` / `TRP_P_FECHA_HORA` cuando no existe manifiesto VBFA/VTTP.
- **Riesgo:** un FES futuro podría quedar cerrado operacionalmente sin manifiesto real.
- **Decisión requerida:** si la regla oficial es “FES cierra exclusivamente por manifiesto VBFA/VTTP”, eliminar el fallback TRP de `FECHA_MANIFIESTO`.

---

## INC-006 — REEVALUADO Y CERRADO 🟢

La auditoría original interpretó que existían dos relojes distintos para el NS porque `Fact_Hitos_Operacionales` contiene `FECHA_INGRESO_SLA` y marca **946 pedidos** como `DIFERIDO_POR_CORTE`.

La revisión del código demuestra que esa interpretación era un falso positivo:

- `Fact_Tracking` calcula `DIAS_INTERNOS_DH` desde `PED_FECHA_HORA` hasta `FECHA_CIERRE` y compara contra `SLA_INTERNO_DH`.
- `Fact_Hitos_Operacionales` calcula `DIAS_HABILES` desde `FECHA_INICIO` hasta `FECHA_FIN`.
- En los KPI integrales `MAYORISTA_CIERRE_TOTAL` y `FES_CIERRE_TOTAL`, `FECHA_INICIO = PED_FECHA_HORA`.
- `FECHA_INGRESO_SLA` se utiliza en `PREPARACION_SLA_DH`, `FECHA_PROMETIDA_MIN`, `FECHA_PROMETIDA_MAX` y `CUMPLE_PREPARACION`, no en el cálculo del NS interno integral.

**Conclusión:** los 946 diferidos son reales para la lógica de preparación/promesa, pero **no modifican el NS interno por efecto del corte**. Impacto atribuible al corte sobre NS interno: **0**.

---

## INC-009 — MULTISELECT FA CERRADO 🟢

Validación viva Power BI Desktop sobre 14 medidas FA y 10 combinaciones:

- Normal+FES Líneas = 22.801 = 14.778 + 8.023; distinto de Todos 22.869.
- Normal+FES Unidades = 2.420.479 = 997.671 + 1.422.808; distinto de Todos 2.421.491.
- Normal+FES Pedidos = 1.896 = 1.459 + 437; distinto de Todos 1.898.
- Santiago+Regiones = 1.898 pedidos = Todos.

Durante la prueba se corrigió además `FA Carga Pedidos Creados`, que tenía un `RETURN CALCULATE(...)` huérfano.

---

## Pendientes antes de declarar VERDE integral

1. **🔴 INC-007B — FES / TRP fallback:** decidir y, si corresponde, eliminar el fallback TRP de `FECHA_MANIFIESTO`.
2. **🟠 INC-011 — denominadores U vs RE:** definir/documentar cuál es el NS oficial y por qué el denominador es 1.898 o 1.962.
3. **🟠 INC-015 — cobertura VBAP lienzo 02:** cuantificar pedidos con/sin match en líneas y unidades.
4. **🟠 INC-013 — feriados regionales:** confirmar si el negocio requiere incorporarlos al calendario SLA.

---

## Evidencia

- `05_sla_reloj_actual_vs_corte.csv` — reevaluación estructural INC-006.
- `08_multiselect_lienzo00.csv` — validación viva RE.
- `10_multiselect_lienzo01_fa_fix.csv` — validación viva FA.
- `13_medidas_u_vs_re.csv` — diferencia denominadores U vs RE.
- `15_incoherencias.csv` — estado consolidado de INCs.
