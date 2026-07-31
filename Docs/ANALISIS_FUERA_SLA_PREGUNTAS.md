# 🔍 Análisis Fuera SLA — Preguntas de Negocio

## 🎯 Objetivo

Responder preguntas críticas sobre los pedidos **Fuera de SLA** (sobre el SLA interno zonal (Santiago >4 DH; Regiones >5 DH))
para identificar patrones, causas raíz y oportunidades de mejora.

---

## ❓ Preguntas de Negocio

### 1. ¿Hay clientes recurrentes fuera de SLA?
- ¿Los mismos clientes aparecen mes a mes en la tabla de críticos?
- ¿Por flujo: FES, NORMAL, SALDO?
- ¿Hay clientes "crónicos" que siempre están fuera de SLA?
- Visual needed: Tabla de clientes con frecuencia de aparición fuera SLA

### 2. ¿Por qué FES demora más en cerrar?
- FES (Factura Especial) = se factura "en verde" (pre-factura) y la operación va después
- ¿Cuánto tiempo pasa entre factura y manifiesto?
- ¿Todos los FES fuera de SLA son por demora en manifiesto?
- Hito dominante: "FES: Entrega posterior → Manifiesto"
- Hipótesis: el ciclo FES es naturalmente más largo por espera de pedido posterior y manifiesto

### 3. ¿Entran más pedidos a fin de mes?
- Distribución de pedidos por semana/día del mes
- ¿Hay un peak en los últimos 5 días hábiles?
- ¿Ese peak es principalmente FES?
- Visual needed: Distribución temporal de creación de pedidos

### 4. ¿Esos clientes se repiten?
- Clientela FES vs NORMAL vs SALDO
- ¿Los mismos clientes piden FES todos los meses?
- Concentración de pedidos FES por cliente

### 5. ¿Qué vendedor tiene más clientes fuera de SLA?
- Ranking de vendedores por cantidad de pedidos fuera de SLA
- Ranking por % de sus pedidos que quedan fuera de SLA
- Visual needed: Tabla vendedor vs pedidos fuera SLA

---

## 🧪 TESIS PRINCIPAL

### "Me están metiendo todo a fin de mes para llegar a los presupuestos, y eso me deja una ola a principios del mes siguiente que merma mi SLA"

**Contexto:**
- FES permite facturar "en verde" (pre-facturar) y hacer la operación después
- Se usa para ingresar ventas en verde a final de mes
- Esto permite cumplir cuotas/presupuestos mensuales
- Pero genera una **ola de pedidos a principios del mes siguiente**
- Esa ola merma el SLA de los pedidos normales de principio de mes

**Qué validar:**
1. Volumen de pedidos FES vs NORMAL por quincena
2. ¿Los pedidos FES se concentran en los últimos 10 días del mes?
3. ¿Los pedidos NORMAL de principios de mes se ven afectados por el backlog FES?
4. Correlación entre % FES del mes anterior y SLA del mes actual
5. Comparar DH de pedidos NORMAL en semanas con alta vs baja carga FES

**Evidencia disponible:**
- Julio 2026: 40 pedidos FES, 38 cerrados, 2 pendientes de manifiesto
- De los 15 fuera SLA: 10 son FES, 5 son NORMAL
- FES fuera SLA: promedian ~13 DH vs SLA interno zonal de 4/5 DH
- Los FES tienen hitos extra: Pedido posterior → Entrega posterior → Manifiesto

---

## ✅ Acciones Propuestas

1. **Identificar clientes FES recurrentes** — ¿quién y cada cuánto?
2. **Medir el ciclo FES completo** — desde creación a manifiesto, en DH
3. **Monitorear la "ola de fin de mes"** — tendencia diaria de creación de pedidos
4. **Evaluar si el backlog FES impacta SLA de pedidos normales**
5. **Revisar política de corte** — ¿los pedidos después del día 20 deberían contabilizarse en el mes siguiente?
6. **Agregar alerta** cuando % FES supere umbral (ej: >30% del mes)

---

## 📊 Métricas Clave a Construir

| Métrica | Descripción |
|---|---|
| Pedidos FES fin de mes | Pedidos FES creados en últimos 10 días del mes |
| % FES del total | Proporción de pedidos FES vs total |
| DH promedio FES vs NORMAL | Comparativa mensual |
| Clientes FES recurrentes | Clientes con FES en 2+ meses consecutivos |
| Vendedor con más fuera SLA | Ranking de vendedores |
| SLA post-FES | NS de pedidos NORMAL en primera quincena cuando mes anterior tuvo alto FES |

---

*Documento generado el 29-07-2026. Próxima revisión: después de construir las visualizaciones.*