# Extracción completa de pedidos FES de julio 2026

Objetivo: obtener todos los pedidos clasificados como `FES` o `FES + SALDO` cuya fecha de creación `Fact_Tracking[PED_FECHA]` esté entre 2026-07-01 y 2026-07-31, incluyendo cerrados y no cerrados.

## Resultado obligatorio

Publicar:

- total FES julio;
- cerrados;
- no cerrados;
- FES exactos;
- FES + SALDO;
- listado completo pedido a pedido.

## Campos del listado

- PED_NUMERO_PEDIDO
- PED_CODIGO_CLIENTE
- CLIENTE_NOMBRE
- VENDEDOR_NOMBRE
- CLASIFICACION
- PED_FECHA
- PED_FECHA_HORA
- ES_CERRADO
- ESTADO_ACTUAL
- FECHA_PRIMERA_FACTURA
- FECHA_ULTIMA_FACTURA
- FECHA_DESPACHO
- FECHA_MANIFIESTO
- FECHA_CIERRE
- PENDIENTE_FACTURA
- PENDIENTE_DESPACHO
- PENDIENTE_MANIFIESTO_FES
- DIAS_INTERNOS_DH
- SLA_INTERNO_DH
- CUMPLE_SLA_INTERNO
- EXCESO_SLA_INTERNO_DH

## Filtro exacto

```text
PED_FECHA >= 2026-07-01
PED_FECHA < 2026-08-01
CLASIFICACION IN {FES, FES + SALDO}
```

No usar `RE Pedidos contexto`, porque esa medida excluye pedidos abiertos. Consultar directamente `Fact_Tracking`.

## Archivos de salida

Crear:

```text
Docs/AUDITORIA_LIVE/runs/<timestamp>_fes_julio_2026/
```

con:

```text
00_git.txt
01_resumen_fes_julio.csv
02_listado_completo_fes_julio.csv
03_cerrados.csv
04_no_cerrados.csv
05_reconciliacion_visual_cerrados.csv
RESULTADO.md
manifest.json
```

La reconciliación visual debe comprobar que la suma cerrada del lienzo 01 para julio coincide con inicio + resto + cierre. En la captura actual esa suma es 1 + 19 + 48 = 68, pero debe validarse contra el modelo vivo.

No modificar el modelo ni los visuales.