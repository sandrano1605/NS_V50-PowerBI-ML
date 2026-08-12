# RESULTADO — Root cause INC-015 (filtro AEDAT)

RUN_ID: 20260812_111242_in02_hora_vbak_postfix_8d022cf
Estado: COMPLETED

## INC-015 = CAUSA_FILTRO_AEDAT (definitivo)

El filtro AEDAT >= GETDATE()-730 elimina 99,74% de posiciones de VBAP_SAP.
Quitar el filtro sube la cobertura de líneas/unidades de 58,3% a 99,9%.

Cobertura real (clave exacta, sin filtro AEDAT):
- ZART 3M: 2.055 pedidos
- En VBAP: 2.053 (99,9%)
- 7 dígitos: 99,8% | 10 dígitos: 100%

## IN02-002 (bug parser ERZET)
Corregido en efbfda7 (TRY_CONVERT(TIME(0), ERZET) directo).

## Próximo paso
Quitar WHERE AEDAT >= GETDATE()-730 en Lineas_y_unidades_por_pedidos.tmdl y refrescar.
