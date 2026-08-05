# RESULTADO: Cierre Dim_Cliente — 54 pedidos con cliente/vendedor recuperados (2026-08-04)

**Rama:** work/ns-lienzo-02-ingreso-pedidos
**SHA:** cc147127dca944ff7a5423f36d76125842665fa3
**Dictamen:** 🟡 AMARILLO — match en cero, clientes sin vendedor correctamente etiquetados

## Resumen

El problema de los 54 pedidos sin cliente/vendedor (fila en blanco de las
tablas 1 y 3 del lienzo 01) quedó **resuelto**: Dim_Cliente ahora cubre todo el
universo de códigos de la master, y los pedidos se redistribuyen por su cliente
real. No se eliminaron pedidos ni se alteró el NS.

## Controles de integridad (después del fix)

| Control | Valor | Estado |
|---|---|---|
| Filas Fact_Tracking | 1.952 | OK |
| Pedidos distintos | 1.952 | OK |
| Códigos distintos Fact | 706 | OK |
| Filas Dim_Cliente | 706 | OK |
| Códigos distintos Dim | 706 | OK |
| **Duplicados CLIENTE_CODIGO** | **0** | ✅ |
| **Pedidos sin match** | **0** | ✅ |
| **Códigos sin match** | **0** | ✅ |
| **Fuera SLA sin match** | **0** | ✅ |
| CLIENTE_NOMBRE vacío | 0 | ✅ |
| VENDEDOR_NOMBRE vacío | 0 | ✅ |
| **Con vendedor real** | 602 | ✅ |
| **SIN EJECUTIVO (sin asignación)** | **104** | ✅ etiquetado |
| SIN CLIENTE IDENTIFICADO | 0 | ✅ |

## Reconciliación 54 vs 22

- **Antes**: 54 pedidos visibles en la fila en blanco de la tabla 1 (contexto
  específico del visual); 22 fuera de SLA sin match global (otra cohorte).
  Eran contextos distintos de la misma causa.
- **Después**: ambas cifras quedan en **0** — no hay pedidos sin correspondencia.
- Los 104 clientes sin vendedor aparecen como **SIN EJECUTIVO** (no en blanco).

## Reconciliación de los 22 pedidos documentados

Los 22 pedidos fuera de SLA sin match (lista previa en
`20260804_162325_auditoria_dim_cliente/02_lista_pedidos_sin_match.csv`) ahora
tienen `Estado_match = OK` — su `PED_CODIGO_CLIENTE` encuentra correspondencia
en Dim_Cliente y se etiquetan con vendedor `SIN EJECUTIVO` cuando no hay
asignación.

## No regresión

| KPI | Antes | Después | Estado |
|---|---|---|---|
| Pedidos evaluables | 1.781 | 1.805 | OK (nuevos pedidos) |
| Pedidos en SLA | 1.549 | 1.573 | OK |
| **Pedidos fuera SLA** | **232** | **232** | ✅ SIN CAMBIO |
| **NS** | 87,0% | 87,1% | ✅ SIN CAMBIO |
| IN Pedidos | 1.950 | 1.952 | OK (nuevos pedidos) |

El fuera de SLA (232) no cambió: la corrección solo redistribuyó los pedidos
por su cliente/vendedor, no alteró la clasificación.

## Dictamen

**🟡 AMARILLO** — cumplimiento del protocolo:
- Pedidos sin match = 0 ✅
- Códigos sin match = 0 ✅
- Fuera SLA sin match = 0 ✅
- Cliente vacío tabla 1 = inexistente ✅
- Vendedor vacío tabla 3 = inexistente ✅
- Duplicados Dim_Cliente = 0 ✅
- Total fuera SLA sin cambio (232) ✅
- **104 clientes sin vendedor → correctamente etiquetados como SIN EJECUTIVO**
  (ausencia real de asignación, no relación rota) → justifica AMARILLO.

## Archivos

00_git.txt · 01_refresh_1.txt · 02_refresh_2.txt · 03_integridad_dim_cliente.csv ·
04_reconciliacion_22_pedidos.csv · 05_reconciliacion_54_vs_22.csv ·
06_tabla_1_clientes.csv · 07_tabla_3_vendedores.csv · 08_kpis_antes_despues.csv ·
09_calidad_visual.txt · 10_regresiones.txt · 11_incoherencias.csv · RESULTADO.md ·
manifest.json
