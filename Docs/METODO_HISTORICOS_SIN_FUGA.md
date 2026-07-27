# Metodología — Variables históricas sin fuga temporal

## Objetivo
Construir señales históricas de cliente, vendedor y canal que puedan utilizarse como predictores sin incorporar resultados futuros del pedido evaluado.

## Unidad analítica
Una fila por `PED_NUMERO_PEDIDO`.

## Target histórico
`Y_ATRASO_SLA_5DH = 1` cuando el pedido válido y cerrado tiene `DH_TOTAL > 5`; en caso contrario, `0`.

Los pedidos pendientes o sin target válido no alimentan los históricos.

## Variables
- `HIST_CLIENTE_RIESGO`: tasa histórica suavizada del cliente.
- `HIST_VENDEDOR_RIESGO`: tasa histórica suavizada del vendedor.
- `HIST_CANAL_RIESGO`: tasa histórica suavizada del canal.
- `HIST_GLOBAL_RIESGO`: tasa histórica general disponible hasta ese momento.
- Los campos terminados en `_N` informan el soporte histórico utilizado.

## Suavizado
Se utiliza:

`(atrasos_entidad + K × tasa_global) / (pedidos_entidad + K)`

con `K = 10`.

Cuando no existe ningún antecedente global anterior, se utiliza un prior neutral de `0,15`. Este valor evita extremos artificiales en las primeras filas y no se deriva de pedidos futuros.

## Tratamiento temporal

### TRAIN
Los pedidos se ordenan por `PED_FECHA`. Para cada fila se consideran únicamente pedidos de entrenamiento válidos con fecha estrictamente anterior.

La implementación utiliza una unión temporal hacia atrás con `allow_exact_matches=False`. Por ello, pedidos con la misma fecha y hora no se usan entre sí.

### TEST
Las tasas se congelan usando exclusivamente el conjunto TRAIN completo. Ningún resultado del mes TEST alimenta a otro pedido TEST.

### PENDIENTE y EXCLUIDO
Se consideran únicamente pedidos cerrados válidos con fecha estrictamente anterior a la del pedido evaluado.

## Auditoría
`ML_Auditoria_Historicos` controla:
- unicidad por pedido;
- uso de fechas futuras;
- rango de probabilidades;
- cobertura de señales;
- pedidos sin fecha;
- congelamiento de TEST;
- estabilidad por cliente, vendedor y canal dentro de TEST.

## Restricción de integración
En el Ciclo 2A estas variables se construyen y auditan, pero todavía no modifican `Resultado` ni el score productivo. Solo podrán integrarse al modelo en el Ciclo 2B después de una validación local completa.