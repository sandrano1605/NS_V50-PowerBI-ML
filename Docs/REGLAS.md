# Reglas de negocio vigentes

## Universo
- Ventana móvil de 90 días por fecha de creación.
- Canales mayoristas 42–47.
- Una sola cartera para los cuatro lienzos: pedidos abiertos y cerrados.
- Clasificaciones exclusivas: NORMAL, FES, SALDO y FES + SALDO.

## Saldo
- Existe Saldo cuando la fecha calendario de la última factura es posterior a la primera.
- Varias facturas el mismo día no generan Saldo.
- En el resumen: FES incluye FES + Saldo; la fila Saldos puros excluye FES + Saldo para evitar doble conteo.

## Cierre operativo
- Normal y Saldo: último despacho válido.
- FES y FES + Saldo: último manifiesto válido.
- Regla Santiago: si falta despacho/manifiesto y la factura base fue emitida hasta las 16:00, se usa esa factura como cierre operativo del mismo día.
- En Saldo la factura base es la última factura; en los demás segmentos es la primera.
- Regiones requieren salida registrada; no se completa con factura.

## SLA
- Administrativo total: 1 DH.
- Operaciones total: 4 DH.
- Interno total: 5 DH.
- Compromiso: 90% dentro de 5 DH.
- Crédito → Ingreso a Logística es un control del macroproceso administrativo y mantiene SLA 1 DH. El SLA 4 DH comienza en Ingreso a Logística y termina en salida oficial.
- Regiones agregan 2 DH estimados de transporte solamente para promesa; no existe POD ni medición de última milla.

## Indicadores
- NS: cerrados en ≤5 DH / cerrados evaluables.
- Promedio: media de días hábiles internos.
- P90: días dentro de los cuales finaliza el 90% de los pedidos.
- La cobertura del hito se muestra separada; el NS de hito usa la cohorte común para penalizar faltantes.


## Desglose interno de FES

El grupo principal FES no duplica pedidos y se descompone para diagnóstico en:

- FES puro.
- FES + Saldo.

Se deben comparar pedidos, participación, NS, promedio, P90 y brecha de facturación. La brecha se expresa en días hábiles y se interpreta como asociación temporal, no como causalidad demostrada.
