# HANDOFF CODEX — Ciclo 1: target y score

## Rama y objetivo
Validar `work/chatgpt-powerbi` después del commit de este ciclo.

## Cambios
- `ML_Comparacion_Modelos` ya no reentrena un modelo paralelo sobre `DH_LEAD_NORMAL`.
- La comparación utiliza las predicciones existentes en `Resultado` y el target oficial `DH_TOTAL > 5`.
- El baseline usa prevalencia de train para clasificación y mediana de train para regresión.
- Se normalizan valores de probabilidad escalados antes de calcular métricas.
- Se agrega `ML_Auditoria_Target_Score` con reconciliación por cohorte y categoría.

## Validación obligatoria
1. Abrir `NS.pbip` y ejecutar Actualizar todo.
2. Confirmar 33 tablas cargadas.
3. Confirmar que `ML_Comparacion_Modelos` entregue 10 filas o una fila de auditoría explícita.
4. Confirmar que `ML_Auditoria_Target_Score` tenga filas para TRAIN, TEST, PENDIENTE y/o EXCLUIDO.
5. Validar que las probabilidades normalizadas estén entre 0 y 1.
6. Validar que ALTO tenga mínimo >= 0.20, MEDIO entre 0.10 y <0.20, BAJO <0.10.
7. Reconciliar positivos train/test con `DH_TOTAL > 5`.
8. Informar AUC, Brier, MAE, RMSE y R² para ML y baseline.
9. No hacer merge a main.

## Criterio de aprobación
- Sin errores TMDL ni Python.Execute.
- Sin split vacío.
- Target y cohortes reconciliados.
- Score dentro de rango.
- Categorías ordenadas y coherentes.
