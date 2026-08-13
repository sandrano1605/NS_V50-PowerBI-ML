# READY FOR CHATGPT — Cierre INC-015 + IN02

RUN_ID: 20260813_094039_inc015_in02_postfix_94133e0
Rama: work/ns-lienzo-02-ingreso-pedidos
SHA: 94133e023205698d89e34458b32e10abdc48598a

INC015_STATUS=INC015_AEDAT_GREEN
IN02_STATUS=IN02_ERZET_PARSER_GREEN

## Resumen

Ambos fixes validados en modelo vivo post-refresh:

1. INC-015 (líneas/unidades): semi-join ZART 3M logra 99,9% de cobertura
   (2.075 filas, 2 residuales conocidos 1168066/1168568). Tiempo SQL 0,98s.
2. IN02 (hora 14:30): parser ERZET recupera 153 pedidos. Sin hora válida
   43/45 bajó de 184 → 1 (solo 1168066 sin VBAK).

## Hallazgos RED confirmados
Ninguno. Ambos dictámenes GREEN.

## Hallazgos ORANGE confirmados
Ninguno pendiente.

## Falsos positivos relevantes
- Los "Sin hora válida" restantes en el modelo son de canales 46/47/42
  (fuera del alcance del fallback 43/45) — no son regresión.

## Decisiones de negocio necesarias
Ninguna. El lienzo 02 (canales 43/45) queda técnicamente consistente.

## Cambios recomendados para implementación remota
Ninguno pendiente. Los fixes ya están aplicados (efbfda7, 41c0f2b, 2205859).

## Evidencia principal
- RESULTADO.md — dictamen conjunto con números
- 2.075 filas, cobertura 99,9%, Sin hora 184→1

## No resuelto
- 2 pedidos (1168066, 1168568) sin posiciones VBAP — calidad de dato aislada.
- 1 pedido 43/45 (1168066) sin VBAK.ERZET — sin hora recuperable.
