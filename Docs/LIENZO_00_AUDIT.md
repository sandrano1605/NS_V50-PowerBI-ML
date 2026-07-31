# Auditoría del lienzo 00 — Resumen Ejecutivo Mayorista

## Cohorte oficial

Todos los indicadores del lienzo usan pedidos cerrados y evaluables de la misma cartera Mayorista (canales 42–47), incluyendo Normal, FES, Saldo y FES + Saldo.

- Pedidos evaluados: 1.823
- En SLA (0–5 DH): 1.486
- Fuera de SLA (>5 DH): 337
- NS interno: 81,5%
- Promedio: 3,9 DH
- P90: 8,0 DH

## Reconciliaciones

- Normal 1.251 + FES/FES+Saldo 571 + Saldo puro 1 = 1.823.
- Santiago 797 + Regiones 1.026 = 1.823.
- 0–2 DH 770 + 3–5 DH 716 + >5 DH 337 = 1.823.
- En SLA 1.486 + fuera 337 = 1.823.

## Reglas verificadas

1. NS total y por flujo: cierre operativo en 5 DH o menos.
2. Administrativo: macro SLA 1 DH.
3. Operaciones: macro SLA 4 DH.
4. Los SLA de subprocesos son controles no aditivos.
5. Regiones agregan 2 DH estimados de tránsito solo para promesa; no cambian el NS interno.
6. Saldo: última factura en fecha calendario posterior a la primera.
7. FES + Saldo se cuenta dentro de FES para evitar doble conteo; Saldo puro permanece separado.
8. Santiago sin salida registrada: factura hasta las 16:00 puede cerrar el mismo día solo después de cumplirse el corte.
9. Regiones sin salida registrada permanecen pendientes.
10. Fechas inválidas o cierre anterior a creación no entran en la cohorte evaluable.

## Casos de borde

- Cero pedidos: porcentajes quedan en blanco mediante DIVIDE, nunca infinitos.
- Factura Santiago a las 16:00: aplica después del corte.
- Factura Santiago a las 16:01: no aplica.
- Factura del día a las 15:00 con refresco 15:30: permanece abierta.
- Factura del día a las 15:00 con refresco 16:00 o posterior: aplica.
- Saldo con varias facturas: usa la última factura como base de cierre.
- Pedido duplicado accidental: valor neto se suma una sola vez por número de pedido.
- Hito sin dato: baja la cobertura y no crea cumplimiento artificial.
- Selección de zona/rango: flujo, matriz de hitos, promedio y P90 conservan el mismo subconjunto.
- Tooltip: hito crítico excluye macros agregados y muestra el subproceso real con mayor exceso.
