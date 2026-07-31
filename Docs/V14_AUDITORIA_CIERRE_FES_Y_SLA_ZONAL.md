# V14 · Auditoría de cierre FES y SLA zonal

## Regla oficial de cierre

- Todos los análisis históricos consideran únicamente pedidos con cierre oficial (`ES_CERRADO = TRUE`) y días internos calculables.
- NORMAL / SALDO: cierre por último despacho válido.
- FES / FES + SALDO: cierre por último manifiesto.
- Fuente prioritaria FES: `ULTIMA_FECHA_MANIFIESTO` obtenida mediante VBFA → entrega posterior → VTTP.
- Respaldo: si VBFA/VTTP no devuelve manifiesto pero existe evento de transporte en tracking, se utiliza `TRP_U_FECHA_HORA`, o `TRP_P_FECHA_HORA` cuando no hay último evento.

## SLA vigente

| Zona | Administrativo | Operación | Interno | Última milla | Cliente |
|---|---:|---:|---:|---:|---:|
| Santiago | 1 DH | 3 DH | 4 DH | 1 DH | 5 DH |
| Regiones | 1 DH | 4 DH | 5 DH | 2 DH | 7 DH |

## Casos de control

### Pedido 4190139455

- Clasificación: FES.
- Zona: Regiones.
- Creación: 26-05-2026 16:16:10.
- Factura: 28-05-2026 15:56:36.
- TRP_P = TRP_U: 28-05-2026 16:05:00.
- El archivo de auditoría anterior tenía manifiesto vacío; V14 usa TRP_U como respaldo.
- Cierre esperado: 28-05-2026 16:05:00.
- Días internos esperados: 2 DH.
- SLA interno Regiones: 5 DH.
- Resultado esperado: cerrado en SLA, 3 DH de holgura.
- Factura → manifiesto: 0 DH.

### Pedido 1167577

- Clasificación: FES.
- Zona: Santiago.
- Creación: 30-06-2026 16:50:32.
- Factura y TRP: 01-07-2026 12:11:39.
- Manifiesto VBFA/VTTP: 02-07-2026 00:00:00.
- Se conserva la fecha VBFA/VTTP porque tiene prioridad sobre TRP.
- Cierre esperado: 02-07-2026.
- Días internos esperados: 2 DH.
- SLA interno Santiago: 4 DH.
- Resultado esperado: cerrado en SLA, 2 DH de holgura.
- Factura → manifiesto: 1 DH.
