# V13 · NS zonal y cierre oficial por flujo

## Regla oficial
- Santiago: 1 DH administrativo + 3 DH operación = 4 DH internos; +1 DH última milla = 5 DH cliente.
- Regiones: 1 DH administrativo + 4 DH operación = 5 DH internos; +2 DH última milla = 7 DH cliente.

## Cohorte del análisis histórico
Todos los flujos, únicamente pedidos cerrados y medibles (`Fact_Tracking[ES_CERRADO] = TRUE`). Esto corresponde al universo que el negocio denomina TRACKING analítico = TRUE.

## Cierre por flujo
- FES y FES + SALDO: último manifiesto obtenido desde VBFA/VTTP.
- NORMAL y SALDO: último despacho válido.
- La factura proxy de Santiago puede completar la salida física cuando no existe TRP, pero nunca cierra un pedido FES.

## Permanencia postfactura
- FES / FES + SALDO: factura válida → último manifiesto.
- NORMAL / SALDO: factura válida → último despacho.
- El bloque muestra solo cohorte cerrada; no mezcla antigüedad de pedidos abiertos.

## Bloque FES vs carga
Se calcula únicamente sobre la misma cohorte cerrada. La palabra “coincide” expresa asociación observada y no causalidad demostrada.
