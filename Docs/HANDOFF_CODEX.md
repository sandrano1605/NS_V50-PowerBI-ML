# HANDOFF CODEX — Ciclo 1C: corrección definitiva de escala y Brier

## Rama y objetivo
Validar `work/chatgpt-powerbi` después del commit de este ciclo.

## Causa raíz confirmada
La normalización anterior calculaba una escala distinta por cada fila usando el orden de magnitud individual del score. Eso deformaba probabilidades menores a 10%: por ejemplo, un valor equivalente a 0,09 podía terminar interpretado como 0,90. El AUC no cambiaba porque preservaba parcialmente el orden, pero el Brier quedaba artificialmente bajo.

## Cambios
- `ML_Comparacion_Modelos` usa ahora una sola escala global para toda la columna `PROB_ML_ATRASO`.
- La escala se detecta a partir del máximo absoluto del conjunto completo.
- Python recibe `PROB_NORM` ya normalizada y no vuelve a reinterpretar cada fila.
- Brier se calcula directamente como `media((Y - P)^2)`.
- `ML_Auditoria_Target_Score` usa exactamente la misma escala global.
- `ML_Auditoria_Metricas` usa exactamente la misma escala global y debe reconciliar con `ML_Comparacion_Modelos`.
- No se modifica todavía el modelo predictivo de `Resultado`.

## Validación obligatoria
1. Abrir `NS.pbip` y ejecutar Actualizar todo.
2. Confirmar 34 tablas cargadas.
3. Confirmar que `ML_Comparacion_Modelos` entregue 10 filas.
4. Confirmar que `ML_Auditoria_Metricas` entregue una fila.
5. Entregar valores exactos:
   - N_Train.
   - Positivos_Train.
   - Tasa_Train.
   - N_Test.
   - Positivos_Test.
   - Tasa_Test.
   - Brier_Base_Directo.
   - Brier_Base_Formula.
   - Brier_Base_Reportado.
   - Diferencia_Brier_Base.
   - Brier_ML_Directo.
   - Brier_ML_Reportado.
   - Diferencia_Brier_ML.
   - Estado_Auditoria.
   - Detalle.
6. Consultar las 10 filas actualizadas de `ML_Comparacion_Modelos`.
7. Verificar en `Auditoria_HIST` que aparezca una única `ESCALA_GLOBAL`.
8. Confirmar que `Brier_Base_Directo = Brier_Base_Formula = Brier_Base_Reportado` dentro de `0.000001`.
9. Confirmar que `Brier_ML_Directo = Brier_ML_Reportado` dentro de `0.000001`.
10. Revisar `ML_Auditoria_Target_Score` y confirmar:
    - Probabilidad mínima y máxima dentro de 0 y 1.
    - BAJO menor que 0,10.
    - MEDIO desde 0,10 hasta menor que 0,20.
    - ALTO desde 0,20.
11. No reutilizar métricas de informes anteriores.
12. No modificar `Resultado`, visuales ni medidas DAX.
13. No hacer merge a main.

## Criterio de aprobación
- Sin errores TMDL, Power Query ni Python.Execute.
- 34 tablas cargadas.
- `ML_Auditoria_Metricas[Estado_Auditoria] = "OK"`.
- Diferencias de Brier menores o iguales a `0.000001`.
- Valores extraídos directamente desde las tablas recién actualizadas.
