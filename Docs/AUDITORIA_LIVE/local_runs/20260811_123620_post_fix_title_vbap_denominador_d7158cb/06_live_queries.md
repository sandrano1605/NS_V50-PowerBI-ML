# Consultas vivas ejecutadas
RUN_ID: 20260811_123620_post_fix_title_vbap_denominador_d7158cb
SHA: d7158cbf16db385c012d114676d1c5f047997a41
Puerto: 50439

NOTA: El tool MCP DAX queries falla sistematicamente en esta sesion (incluso EVALUATE ROW(x,1)). Los resultados siguientes provienen de queries ejecutadas exitosamente al inicio de la sesion (mismo SHA).

## Q1 - Baseline universo (OK)
2048 total / 86 abiertos / 1962 cerrados / 1898 con DH / 64 sin DH / RE_Pedidos=1898 / RE_EnSLA=1547 / RE_FueraSLA=351 / RE_NS=0.815

## Q2 - FIND-002 titulo (ERROR)
EVALUATE ROW(T3_Titulo, CALCULATE(RE TT Titulo, FES), ...) -> Error: No se puede determinar un valor unico para la columna OrdenRango en Dim_Rango_Entrega
Causa: CONCATENATEX(VALUES(Rango), Rango, " + ", OrdenRango, ASC) - sort by column OrdenRango sin agregacion

## Q3 - Clasificacion (OK)
NORMAL=1459, FES=432, FES+SALDO=5, SALDO=2

## Q4 - Zona (OK)
Santiago=925/779/146, Regiones=973/768/205

## Q5 - Multiselect RE (OK)
Todos: 1898/2274130561/3.5021/8
Normal+FES: 1896/2271756623/3.5005/8
Santiago+Regiones: 1898/2274130561

## Q6 - Diferidos corte (OK)
946 pedidos diferidos en Fact_Hitos

## Q7 - FES (OK)
FES cerrados=437, con manifiesto=437, abiertos=2

## Q8 - Multiselect FA (OK)
Todos: 1898/22869/2421491
Normal+FES: 1896/22801/2420479

## Q9 - VBAP (OK)
Evaluables=1898, con_match=1107, sin_match=791, cobertura=58.3%

## Q10 - Regresion (OK)
11 pedidos OK, 1 FAIL (4190139455 cambio de FES a NORMAL en datos)
