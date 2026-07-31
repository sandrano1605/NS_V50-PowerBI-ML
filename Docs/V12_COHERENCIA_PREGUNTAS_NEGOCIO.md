# V12 · Auditoría de coherencia de preguntas de negocio

## 1. Clientes reincidentes fuera SLA

Se mantiene la regla de recurrencia de 2 o 3 meses dentro de la ventana fija de los últimos 3 meses.
El promedio DH se calcula únicamente sobre pedidos fuera SLA.

## 2. Factura → despacho >15 DH

Corrección de negocio:

- Antes: `DIAS_POSTFACTURA_DH` medía factura → cierre.
- En FES Regiones, el cierre depende del manifiesto; por eso se inflaban los días aunque el pedido ya hubiese salido del CD.
- Ahora: `DIAS_POSTFACTURA_DH` mide `FACTURA_CIERRE_BASE` → `FECHA_DESPACHO`.
- Si todavía no existe despacho, se calcula hasta la fecha/hora de actualización.
- La espera de manifiesto FES queda separada en `DIAS_ESPERA_MANIFIESTO_DH` y no entra en la señal de permanencia física del CD.
- Promedio y P90 se calculan solamente sobre pedidos con más de 15 DH.
- `Sin desp. >15` cuenta solo facturas que aún no tienen despacho físico.

## 3. Vendedores con clientes reincidentes

Corrección de coherencia:

- Antes, si un vendedor tenía al menos un cliente recurrente, los pedidos, porcentaje, días y líneas incluían todos sus clientes.
- Ahora, esas métricas se restringen exclusivamente a los clientes recurrentes 2M+ del vendedor y flujo.

## 4. FES o carga

Corrección metodológica:

- La carga se mide con todos los pedidos creados, sin exigir cierre.
- El SLA se evalúa sobre la cohorte cerrada y medible.
- Se agrega `Madurez`, que indica qué porcentaje de la carga ya puede evaluarse.
- Se agregan líneas y unidades por pedido para medir complejidad.
- Se agrega `% carga` dentro de cada mes.
- Se agrega `Δ NS vs resto` como comparación dentro del mismo mes.
- La columna `Lectura` evita concluir sobre periodos con baja madurez.

## Validaciones estructurales

- JSON válido.
- Referencias de visuales a columnas y medidas válidas.
- Sin lineageTag duplicados.
- Visuales principales dentro del lienzo y sin superposición.
