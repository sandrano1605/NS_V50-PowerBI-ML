# HANDOFF CODEX — Ciclo 1B: reconciliación matemática de Brier

## Rama y objetivo
Validar `work/chatgpt-powerbi` después del commit de este ciclo.

## Motivo
La validación del Ciclo 1 informó aproximadamente 14,3% de positivos en train y 14,6% en test, pero un Brier baseline de 0,0137. Para una predicción constante igual a la prevalencia de train, ese Brier no reconcilia matemáticamente y debería estar alrededor de 0,125.

## Cambios
- Se agrega `ML_Auditoria_Metricas`.
- La tabla calcula directamente desde `Resultado`:
  - N train y test.
  - Positivos y prevalencia train/test.
  - Brier base directo fila a fila.
  - Brier base mediante fórmula cerrada.
  - Brier base informado por `ML_Comparacion_Modelos`.
  - Brier ML directo e informado.
  - Diferencias y estado de auditoría.
- La tolerancia de reconciliación es `0.000001`.
- No se modifica todavía el modelo predictivo de `Resultado`.

## Validación obligatoria
1. Abrir `NS.pbip` y ejecutar Actualizar todo.
2. Confirmar 34 tablas cargadas.
3. Confirmar que `ML_Auditoria_Metricas` entregue exactamente una fila.
4. Entregar los valores exactos, sin aproximaciones:
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
5. Consultar también las 10 filas exactas de `ML_Comparacion_Modelos`; no reutilizar métricas copiadas de informes anteriores.
6. Confirmar que `Brier_Base_Directo = Brier_Base_Formula` dentro de la tolerancia.
7. Confirmar que los valores reportados coincidan con los directos.
8. Si `Estado_Auditoria` no es `OK`, marcar el ciclo como BLOQUEADO y adjuntar los valores exactos.
9. No modificar `Resultado`, visuales ni medidas DAX.
10. No hacer merge a main.

## Criterio de aprobación
- Sin errores TMDL ni Power Query.
- 34 tablas cargadas.
- `ML_Auditoria_Metricas[Estado_Auditoria] = "OK"`.
- Diferencias de Brier menores o iguales a `0.000001`.
- Valores extraídos directamente desde las tablas actualizadas.
