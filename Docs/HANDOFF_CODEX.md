# HANDOFF CODEX — Ciclo 2A: históricos sin fuga temporal

## Rama y objetivo
Validar `work/chatgpt-powerbi` después del commit de este ciclo.

El objetivo es construir y auditar las variables históricas antes de incorporarlas al modelo predictivo principal. Este ciclo **no modifica `Resultado`, sus predicciones ni los visuales**.

## Cambios
- Se agrega `ML_Historicos_Sin_Fuga`, con una fila por pedido.
- Se calculan:
  - `HIST_CLIENTE_RIESGO` y `HIST_CLIENTE_N`.
  - `HIST_VENDEDOR_RIESGO` y `HIST_VENDEDOR_N`.
  - `HIST_CANAL_RIESGO` y `HIST_CANAL_N`.
  - `HIST_GLOBAL_RIESGO` y `HIST_GLOBAL_N`.
- Suavizado: `K = 10`.
- Prior neutral inicial: `0,15`, usado solamente cuando no existe historia anterior.
- Se agrega `ML_Auditoria_Historicos` con nueve controles automáticos.

## Regla temporal obligatoria
- **TRAIN:** expanding histórico con `shift` temporal estricto. Un pedido solo puede usar pedidos con `PED_FECHA` estrictamente anterior. Los pedidos con la misma fecha/hora no se usan entre ellos.
- **TEST:** mapa congelado construido únicamente con TRAIN. Los resultados reales del propio TEST no pueden alimentar sus variables.
- **PENDIENTE/EXCLUIDO:** solo pedidos cerrados válidos con fecha estrictamente anterior al pedido evaluado.
- `HIST_FECHA_MAX_USADA` debe ser menor que `PED_FECHA`.

## Validación obligatoria
1. Abrir `NS.pbip` y ejecutar **Actualizar todo**.
2. Confirmar:
   - TMDL sin errores.
   - Power Query sin errores.
   - Python.Execute sin errores.
   - **36 tablas cargadas**.
   - 40 relaciones activas.
3. Confirmar que `ML_Historicos_Sin_Fuga` tenga:
   - El mismo número de filas que `Resultado`.
   - Una fila única por `PED_NUMERO_PEDIDO`.
   - Cohortes TRAIN, TEST, PENDIENTE y EXCLUIDO reconciliadas con `Resultado`.
4. Entregar por cohorte:
   - Pedidos.
   - Riesgo promedio cliente, vendedor, canal y global.
   - Soporte promedio y mínimo por entidad.
   - Pedidos sin antecedentes.
   - Fecha mínima y máxima utilizada como historia.
   - Conteo por `HIST_METODO`.
5. Consultar `ML_Auditoria_Historicos` y entregar sus nueve filas completas:
   - CONTROL.
   - FILAS_EVALUADAS.
   - INCUMPLIMIENTOS.
   - ESTADO.
   - DETALLE.
6. Deben quedar en `OK` y con cero incumplimientos:
   - `UNICIDAD_PEDIDO`.
   - `SIN_FUGA_FECHA`.
   - `RANGO_0_1`.
   - `COBERTURA_RIESGOS`.
   - `TEST_SOLO_TRAIN`.
   - `TEST_CLIENTE_CONGELADO`.
   - `TEST_VENDEDOR_CONGELADO`.
   - `TEST_CANAL_CONGELADO`.
7. `FECHA_PEDIDO_FALTANTE` puede quedar `REVISAR` únicamente si existen pedidos sin fecha; informar los pedidos afectados. Nunca pueden incorporarse al entrenamiento.
8. Validar directamente:
   - Todas las probabilidades entre 0 y 1.
   - `HIST_FECHA_MAX_USADA < PED_FECHA` para toda fila con historia.
   - En TEST, un mismo cliente, vendedor o canal tiene un único riesgo histórico.
   - En TEST, `HIST_FECHA_MAX_USADA` corresponde al máximo cierre de TRAIN.
   - En las primeras filas de TRAIN sin historia, el prior es 0,15 y soporte 0.
9. Entregar diez ejemplos auditables:
   - Tres TRAIN tempranos.
   - Tres TRAIN con historia.
   - Dos TEST.
   - Dos PENDIENTES.
10. No modificar:
   - `Resultado`.
   - Visuales.
   - Medidas DAX.
   - Relaciones.
   - `main`.

## Criterio de aprobación
- Actualización completa sin errores.
- 36 tablas cargadas.
- Una fila por pedido.
- Cero uso de información futura.
- Cero riesgos fuera de rango o nulos.
- TEST completamente congelado con TRAIN.
- Todos los controles críticos en `OK`.

El ciclo se marca `BLOQUEADO` ante cualquier incumplimiento crítico. La integración de estos históricos al modelo se realizará recién en el Ciclo 2B.