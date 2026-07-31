# Diagnóstico FES y Saldo

## Regla de agrupación

- **FES total** = `FES` + `FES + SALDO`.
- **FES puro** = clasificación `FES`.
- **FES + Saldo** = pedido FES cuya primera y última factura están en fechas calendario distintas.
- **Saldo puro** sigue siendo un grupo principal separado y no se suma nuevamente dentro de FES.

La reconciliación obligatoria es:

```text
FES puro + FES + Saldo = FES total
Normal + FES total + Saldo puro = Total evaluado
```

## Indicadores incorporados

- Pedidos FES total, FES puro y FES + Saldo.
- Participación de FES + Saldo dentro de FES total.
- NS interno de cada subgrupo.
- Promedio y P90 de días internos.
- Brecha promedio de facturación en días hábiles.
- Diferencia de promedio entre FES + Saldo y FES puro.

## Interpretación

La brecha de facturación muestra tiempo asociado a completar la facturación. La comparación permite observar si FES + Saldo tarda más que FES puro, pero no demuestra por sí sola causalidad. La causa raíz debe confirmarse con el hito crítico y la Auditoría 360.
