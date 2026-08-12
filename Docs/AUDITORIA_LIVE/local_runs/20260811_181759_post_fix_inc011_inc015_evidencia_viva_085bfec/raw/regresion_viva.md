# Regresión en vivo — casos del regression_cases.csv (SHA 085bfec)

Pedido,Caso,Flujo_Real,Zona_Real,Cierre_Real,DH_Real,SLA_Real,Cumple_Real,Esperado_Historico,COINCIDE
4190139455,Clave oficial FES,NORMAL,Regiones,28-05-2026 16:05,2,5,True,FES/Regiones/28-05-2026/5/True,NO_FLUJO
1167577,Clave oficial FES,FES,Santiago,02-07-2026 00:00,2,4,True,FES/Santiago/02-07-2026/4/True,SI
1167307,Santiago exactamente 4 DH,NORMAL,Santiago,30-06-2026 11:42,4,4,True,NORMAL/Santiago/30-06-2026/4/True,SI
1168045,Santiago 5 DH,NORMAL,Santiago,13-07-2026 09:56,5,4,False,NORMAL/Santiago/13-07-2026/4/False,SI
1167339,Regiones exactamente 5 DH,NORMAL,Regiones,02-07-2026 11:38,5,5,True,NORMAL/Regiones/02-07-2026/5/True,SI
4190139759,Regiones 6 DH,NORMAL,Regiones,26-06-2026 09:24,6,5,False,NORMAL/Regiones/26-06-2026/5/False,SI
1167926,FES cerrado,FES,Santiago,08-07-2026 00:00,5,4,False,FES/Santiago/08-07-2026/4/False,SI
4190139760,Pedido con multiples facturas,SALDO,Regiones,30-06-2026 11:32,7,5,False,SALDO/Regiones/30-06-2026/5/False,SI
1166696,FES + SALDO cerrado,FES + SALDO,Santiago,05-06-2026 00:00,6,4,False,FES + SALDO/Santiago/05-06-2026/4/False,SI
1167581,Factura y manifiesto mismo dia,FES,Santiago,10-07-2026 00:00,8,4,False,FES/Santiago/10-07-2026/4/False,SI
1167658,Pedido con multiples despachos,FES,Regiones,20-07-2026 00:00,12,5,False,FES/Regiones/20-07-2026/5/False,SI

## Detalle del caso discrepante: 4190139455

- Esperado histórico: FES / Regiones / 28-05-2026 / SLA 5 / CUMPLE True / FUENTE MANIFIESTO
- Real vivo: NORMAL / Regiones / 28-05-2026 16:05 / DH 2 / SLA 5 / CUMPLE True / FUENTE DESPACHO
- Tabla origen (Fact_Pedidos_Auditoria): ES_FES=False, ES_SALDO=False,
  REGLA_CLASIFICACION_FES='SIN PEDIDO POSTERIOR C-C',
  REGLA_CLASIFICACION_SALDO='FACTURACION EN UNA MISMA FECHA'
- Sin manifiesto (PRIMERA/ULTIMA null), canal 43.

Conclusión: el CSV histórico marcaba este pedido como FES, pero la
implementación actual lo clasifica NORMAL porque no cumple la regla FES
(pedido posterior C-C). El CSV es hipótesis histórica; la clasificación actual
es consistente con la regla documentada. No se edita el CSV (prohibido).
