# NS V50 · Modelo de Machine Learning auditado

## Propósito

- **Regresión logística:** estima la probabilidad de que un pedido incumpla el SLA interno de 5 días hábiles.
- **Regresión lineal regularizada:** estima los días hábiles totales del ciclo.
- Entrena con pedidos de **flujo completo**, calidad válida y sin críticas de auditoría.
- Predice los pedidos pendientes identificados por `Fact_Tracking[ES_CERRADO]`.

## Control de fuga temporal

El score inicial no usa FES, Saldo, factura, despacho ni tiempos finales de proceso. Estas variables quedan como diagnóstico histórico, no como predictores iniciales.

## Evidencia previa con data(2).xlsx

- 1.636 pedidos únicos.
- 1.540 pedidos completos y válidos para el entrenamiento final.
- Validación temporal: mayo entrena y junio prueba.
- AUC logística: 74,53%.
- MAE regresión de días: 1,49 DH.
- RMSE: 2,51 DH.
- R²: 35,79%.

La actualización corporativa recalculará las cifras con el universo vivo de SQL y `Fact_Tracking`.
