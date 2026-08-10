# DICTAMEN AUDITORÍA FINAL DE NEGOCIO

**SHA:** 87a954857c7a32f3108ae027c2afeb56ee43f84f
**Fecha:** 2026-08-10 15:58:53
**Modelo:** Power BI Desktop local, refresh actual (Tracking = 2.048)

---

## Resultado por punto

| # | Punto | Resultado | Estado |
|---|-------|-----------|--------|
| 1 | Universo | RE Pedidos contexto = 1.898 = cerrados con DH válidos (1.898 + 64 sin DH = 1.962 cerrados; 86 abiertos; total 2.048) | ✅ |
| 2 | SLA | TRUE=1.547 · FALSE=351 · BLANK=0 · SLA_DH_BLANK=0 · 1.547+351=1.898 | ✅ |
| 3 | SLA por zona | Santiago: interno=4, cliente=5, operación=3 · Regiones: interno=5, cliente=7, operación=4 — verificado contra columnas SLA_INTERNO_DH / SLA_CLIENTE_DH / SLA_OPERACION_DH reales | ✅ |
| 4 | Clasificación | NORMAL=1.459 · FES=432 · FES+SALDO=5 · SALDO=2 · BLANK=0 · otras=0 · suma=1.898 | ✅ |
| 5 | Fuera SLA | RE fuera=351 · tabla=351 · duplicados=0 · 351/351 cumplen cerrado+DH+FALSE | ✅ |
| 6 | Zona (351) | Santiago=146 · Regiones=205 · blank=0 · otras=0 · 146+205=351 | ✅ |
| 7 | Multiselect flujo | Normal=132=132 · FES=218=218 · Saldo=1=1 · N+F=350=350 · N+S=133=133 · F+S=219=219 · Todos=351=351 | ✅ |
| 7 | Multiselect zona | Santiago=146=146 · Regiones=205=205 · S+R=351=351 | ✅ |
| 8 | Narrativa | Single-select OK. **HALLAZGO**: Normal+FES muestra "Universo cerrado" | ⚠️ |
| 9 | Cambio BD | Timestamp 2026-08-10 15:58:53 · 351 actual NO comparable con 232 histórico | ✅ |

## Hallazgo único (no bloqueante para reconciliación)

**INC-004 — Título no representa el filtro real con multiselect.**
`RE TT Título` usa `SELECTEDVALUE(Dim_Vista_Ejecutiva[Flujo])` para construir el contexto del texto.
Con selección múltiple (Normal+FES = 350 pedidos), SELECTEDVALUE devuelve BLANK y el título cae en
"Universo cerrado", que no describe el filtro real. Se reporta sin corregir, según instrucción.

**Impacto:** cosmético (título), sin efecto en los valores numéricos ni en la reconciliación.

---

## DICTAMEN: 🟢 VERDE

Universo, SLA, clasificación, zona y tabla **reconcilian a nivel de PED_NUMERO_PEDIDO**:
- 1.898 = 1.547 + 351 (universo ↔ SLA)
- 1.898 = 1.459 + 432 + 5 + 2 (universo ↔ clasificación)
- 351 = 146 + 205 (fuera SLA ↔ zona)
- 351 = 351 tabla, 0 duplicados (fuera SLA ↔ tabla)
- Todas las combinaciones multiselect: tarjeta = tabla

**Condición del dictamen cumplida en su totalidad.** El hallazgo INC-004 es narrativa/cosmético
y se documenta como mejora pendiente, no como falla de reconciliación.

**Pendiente recomendado (no urgente):** corregir RE TT Título para construir el contexto con
CONCATENATEX de los flujos seleccionados cuando haya multiselect.
