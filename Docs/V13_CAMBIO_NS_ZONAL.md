# V13 · Cambio oficial de Nivel de Servicio por zona

## Regla oficial

- Santiago: 1 DH administración + 3 DH operación = 4 DH internos; +1 DH última milla = 5 DH cliente.
- Regiones: 1 DH administración + 4 DH operación = 5 DH internos; +2 DH última milla = 7 DH cliente.

## Cierre por flujo

- FES y FES + SALDO: último manifiesto VBFA/VTTP.
- NORMAL y SALDO: último despacho válido.

## Cambios

- Fact_Tracking incorpora SLA_OPERACION_DH, SLA_INTERNO_DH, ULTIMA_MILLA_DH, SLA_CLIENTE_DH, CUMPLE_SLA_INTERNO y EXCESO_SLA_INTERNO_DH.
- Todas las medidas de cumplimiento usan la meta por pedido y zona; se eliminan comparaciones fijas contra 5 DH.
- Config_Promesa_Entrega se ajusta a objetivos exactos 5/7 DH cliente.
- Dim_Rango_Entrega cambia Santiago a 0–2, 3–4 y >4; Regiones mantiene 0–2, 3–5 y >5.
- FES cierra exclusivamente con manifiesto; el bloque postfactura usa factura → manifiesto para FES.
- Textos, títulos y SVG se actualizan con promesa e SLA zonales.
