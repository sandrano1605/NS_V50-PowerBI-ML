# READY FOR CHATGPT — Lienzo 01 coherencia filtros (Carlos Garrido)

RUN_ID: 20260813_123309_l01_coherencia_carlos_garrido_f044e2e
Rama: work/ns-lienzo-01-analisis-fuera-sla
SHA: f044e2e8965a477340d96f6a3352d9b8a24ff9d2

L01_COHERENCIA = L01_COHERENCIA_RED

## Resumen

Al hacer clic en la fila de Carlos Garrido de la tabla 3
(fa_vendedores_reincidentes), la selección NO filtra solo Carlos:
filtra Carlos + Flujo (NORMAL o FES), porque la tabla cruza dos dimensiones
(VENDEDOR_NOMBRE + CLASIFICACION).

## Respuestas a las 10 preguntas

1. Clic en Carlos = selección conjunta Vendedor + Flujo.
2. Filtra Carlos + flujo (NO solo Carlos).
3. Tabla 1 (clientes): se reduce al flujo seleccionado.
4. Tabla 4 (FES vs Carga): %FES salta a 100% (Carlos+FES) o 0/blank (Carlos+NORMAL).
5. critical_table: queda filtrada por flujo heredado.
6. 0 de 81 pedidos de clientes de Carlos tienen PED_RESPONSABLE "Carlos Garrido"
   (son V610/V650/V550).
7. "Vendedor" es semánticamente ambiguo: actual (Dim_Cliente) vs histórico (PED_RESPONSABLE).
8. Mantener: interacción de tabla 3 sobre tabla 1 (clientes) si es intencional.
9. Deshabilitar/reemplazar: interacción de tabla 3 sobre tabla 4 y critical_table.
10. NO es DAX: basta corregir interacción/UX (o un slicer de vendedor separado).

## Hallazgos RED confirmados
L01-001: selección de fila arrastra flujo y distorsiona tabla 4.

## Hallazgos ORANGE confirmados
L01-002: vendedor actual difiere 100% de PED_RESPONSABLE.

## Falsos positivos relevantes
Ninguno. Las medidas DAX responden correctamente al contexto.

## Decisiones de negocio necesarias
1. ¿"Filtrar por Carlos" = Carlos completo o Carlos en el flujo de la fila?
2. ¿Semántica "Vendedor" = actual o histórico?

## Cambios recomendados para implementación remota
Deshabilitar interacción tabla3->tabla4, o cambiar la tabla 3 para filtrar solo vendedor.

## Evidencia principal
- raw/l01_diagnostico.md — diagnóstico completo
- 07_live_results.csv — 10 pruebas

## No resuelto
Decisión final de negocio sobre el significado de clic en vendedor.
