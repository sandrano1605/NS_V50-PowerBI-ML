# READY FOR CHATGPT — Root cause INC-015 (filtro AEDAT)

RUN_ID: 20260812_111242_in02_hora_vbak_postfix_8d022cf
SHA: 8d022cf1f322e4fb4f5867084170de0e40836424
Power BI: puerto 63977

## Resumen

Se identificó la causa raíz definitiva de la baja cobertura de líneas/unidades (58,3%):
el filtro `AEDAT >= GETDATE() - 730` en la query M de `Lineas_y_unidades_por_pedidos`.

VBAP_SAP tiene 8,8M pedidos con posiciones, pero solo 22.799 tienen AEDAT reciente.
Al quitar el filtro, la cobertura sube de 58,3% a 99,9% (2.053/2.055).

## Hallazgo principal: INC-015 = CAUSA_FILTRO_AEDAT (RED)

Evidencia (comparación coherente, sin TOP ni filtros distorsionantes):
- VBAP_SAP SIN filtro AEDAT: 8.858.283 pedidos
- VBAP_SAP CON AEDAT>=730d: 22.799 (0,26%)
- ZART_TRACK 3M: 2.055 pedidos
- En VBAP sin filtro (clave exacta): 2.053 (99,9%)
- 7 dígitos: 1.045/1.047 (99,8%) | 10 dígitos: 1.008/1.008 (100%)

AEDAT es la fecha de actualización de la posición, NO la fecha del pedido.
La mayoría de posiciones tienen AEDAT >730d aunque el pedido siga vigente.

## Hallazgos RED confirmados
INC-015-ROOTCAUSE: filtro AEDAT elimina 99,74% de posiciones.
IN02-002: bug parser ERZET (ya corregido en efbfda7).

## Hallazgos ORANGE confirmados
Ninguno pendiente.

## Falsos positivos relevantes
- "SIN_FUENTE_YV01" (corrida previa): FALSO_POSITIVO para 43/45. YV01 no existe
  en canales 43/45; el universo real es ZPDA/ZPPO/ZMAY/YPA que SÍ están en VBAP.
- Prefijo 1221: falso positivo de LIKE. 1221168066 es pedido distinto (YV01, 2023).

## Decisiones de negocio necesarias
Ninguna. El fix es quitar un filtro incorrecto.

## Cambios recomendados para implementación remota
En Lineas_y_unidades_por_pedidos.tmdl: quitar WHERE VBAP.AEDAT >= GETDATE() - 730.
Cobertura resultante: 99,9%.

## Evidencia principal
- raw/inc015_aedat_rootcause.md — diagnóstico completo con números
- raw/in02_bug_hora_vbak.md — bug parser ERZET (corregido)

## No resuelto
- 2 pedidos (1168066, 1168568) sin posiciones en VBAP por clave — calidad de dato.
