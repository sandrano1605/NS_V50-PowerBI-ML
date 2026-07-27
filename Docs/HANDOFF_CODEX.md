# HANDOFF CODEX — Ciclo UX-1: mesa operativa de pedidos pendientes

## Objetivo
Validar las nuevas tablas de priorización y evolucionar el lienzo de Power BI hacia una mesa de control diaria de pedidos pendientes.

Este ciclo no modifica el modelo predictivo de `Resultado`. Utiliza el score existente, los históricos sin fuga y datos operacionales actuales para construir una prioridad transparente.

## Cambios semánticos
- Nueva tabla `Config_Criterios_Pendientes` con seis criterios visibles y su puntaje.
- Nueva tabla `ML_Pedidos_Pendientes_Priorizados`, una fila por pedido pendiente.
- Nuevas medidas:
  - `Pendientes Total`.
  - `Pendientes Críticos`.
  - `Pendientes Alta Prioridad`.
  - `Pendientes Intervenir Hoy`.
  - `Pendientes Fuera SLA`.
  - `Valor Pendiente`.
  - `Valor Crítico y Alto`.
  - `Riesgo ML Promedio Pendientes`.
  - `Días Actuales Promedio Pendientes`.
  - `Pendientes Sin Antecedentes`.

## Regla de prioridad
El score utiliza:
- SLA consumido: máximo 40 puntos.
- Riesgo ML: máximo 25 puntos.
- Permanencia en el hito: máximo 15 puntos.
- Valor del pedido: máximo 10 puntos.
- Riesgo histórico: máximo 10 puntos.
- Fin de mes: máximo 5 puntos.

El score se limita a 100.

Categorías:
- `CRÍTICA`: pedido vencido o score >= 70.
- `ALTA`: score >= 50.
- `MEDIA`: score >= 30.
- `BAJA`: score < 30.

La predicción de días es solo referencial porque la regresión todavía no supera al baseline. No participa en el score.

## Validación semántica obligatoria
1. Abrir `NS.pbip` y ejecutar Actualizar todo.
2. Confirmar:
   - TMDL sin errores.
   - Power Query sin errores.
   - Python.Execute sin errores.
   - 38 tablas cargadas.
   - 40 relaciones activas.
3. `Config_Criterios_Pendientes` debe tener exactamente 6 filas.
4. `ML_Pedidos_Pendientes_Priorizados` debe tener exactamente la misma cantidad de pedidos que `Resultado` con `ES_PENDIENTE = TRUE()`.
5. Confirmar una fila única por `PED_NUMERO_PEDIDO`.
6. Confirmar que `RANK_PRIORIDAD` vaya de 1 a N sin duplicados.
7. Confirmar que `PROB_ML_ATRASO_NORM`, `HIST_CLIENTE_RIESGO`, `HIST_VENDEDOR_RIESGO`, `HIST_CANAL_RIESGO` y `RIESGO_HISTORICO_MAX` estén entre 0 y 1.
8. Confirmar que `PRIORIDAD_OPERATIVA_SCORE` esté entre 0 y 100.
9. Recalcular manualmente al menos 10 pedidos y comprobar que el score sea la suma de:
   - `PUNTOS_SLA`.
   - `PUNTOS_RIESGO_ML`.
   - `PUNTOS_PERMANENCIA`.
   - `PUNTOS_VALOR`.
   - `PUNTOS_HISTORICO`.
   - `PUNTOS_FIN_MES`.
10. Confirmar que todo pedido con `DIAS_ACTUALES_DH > 5` quede `CRÍTICA` y `INTERVENIR HOY`.
11. Confirmar que `CRITERIOS_ACTIVOS`, `FOCO_INTERVENCION` y `ACCION_OPERATIVA` no estén vacíos.
12. Confirmar que `USO_DH_PREDICHO` indique que la regresión es referencial.

## Evolución del lienzo
Leer `Docs/LIENZO_PEDIDOS_PENDIENTES.md` y aplicar el diseño en Power BI Desktop.

Crear una nueva página o transformar la página ML actual con el nombre:

`05 Pedidos pendientes · Priorización`

La página debe incluir:
- Logo oficial ARTEL arriba a la derecha.
- Título y subtítulo definidos en la documentación.
- Cinco tarjetas principales.
- Segmentadores de prioridad, foco, hito, vendedor, región y canal.
- Tabla principal ordenada por `RANK_PRIORIDAD`.
- Panel o tabla de criterios.
- Barras por foco de intervención.
- Barras apiladas por hito y prioridad.
- Tooltip con desglose de puntos.

## Tabla principal
Usar exclusivamente `ML_Pedidos_Pendientes_Priorizados` y respetar el orden de columnas descrito en `Docs/LIENZO_PEDIDOS_PENDIENTES.md`.

Aplicar formato condicional:
- CRÍTICA: rojo.
- ALTA: naranja.
- MEDIA: amarillo.
- BAJA: verde.

## Restricciones
- No modificar `Resultado`.
- No reentrenar modelos.
- No cambiar relaciones existentes.
- No alterar otras páginas salvo navegación necesaria.
- No hacer merge a `main`.

## Entrega
Guardar:
- `validation/latest/RESULTADOS_UX_1.md`.
- `validation/latest/metricas_UX_1.json`.
- `validation/latest/errores_UX_1.txt`.
- Captura completa de la nueva página en `validation/latest/capturas/`.

El informe debe incluir:
- Filas de pedidos pendientes.
- Distribución por prioridad.
- Distribución por foco.
- Total y valor de pedidos críticos y altos.
- Diez primeros pedidos del ranking.
- Resultado de los controles de score.
- Estado de todos los visuales.

## Criterio de aprobación
- 38 tablas cargadas.
- Una fila por pedido pendiente.
- Cero scores fuera de rango.
- Cero campos operativos vacíos en pedidos pendientes.
- Página creada y funcional.
- Tabla ordenada correctamente.
- Filtros y formato condicional funcionando.
- Sin errores en Actualizar todo.
