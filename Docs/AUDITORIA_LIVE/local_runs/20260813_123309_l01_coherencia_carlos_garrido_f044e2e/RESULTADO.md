# RESULTADO — Lienzo 01 coherencia filtros (Carlos Garrido)

RUN_ID: 20260813_123309_l01_coherencia_carlos_garrido_f044e2e
Estado: COMPLETED
Dictamen: L01_COHERENCIA_RED

## H1 (vendedor actual vs histórico)
Carlos Garrido: 25 clientes, 81 pedidos. PED_RESPONSABLE = V610(72)/V650(6)/V550(3).
0 pedidos con PED_RESPONSABLE "Carlos Garrido" -> discrepancia 100%.

## H2 (selección fila = vendedor + flujo)
Tabla 3 cruza VENDEDOR_NOMBRE + CLASIFICACION. Clic = Carlos + flujo.

## H3 (tabla 4 distorsionada)
Carlos SOLO: %FES=48% | Carlos+NORMAL: blank | Carlos+FES: 100%.
La tabla 4 deja de comparar FES vs carga al heredar flujo.

## Conclusión
Problema de interacción/UX, no de DAX.
