# Consultas vivas ejecutadas - validación post-fix

RUN_ID: 20260811_225907_post_fix_validacion_viva_00756db
SHA: 00756dbe763335879daf14ec466dcc7514361023
Modelo: localhost:58610 (Power BI Desktop, base 512b1fa5), refresh 2026-08-11 22:21

## Q1 — FIND-002A: 12 combinaciones RE TT Título
Evaluar [RE TT Título], [RE Pedidos contexto], [RE Pedidos fuera SLA contexto] con TREATAS sobre Dim_Vista_Ejecutiva[Flujo] y Dim_Rango_Entrega[Zona].
Resultado: 12/12 sin SemanticError. Títulos renderizan correctamente (flujo/zona concatenados, Universo cerrado sin filtro).

## Q2 — INC-011: cerrados sin DH post-fix
`COUNTROWS(FILTER(Fact_Tracking, ES_CERRADO=TRUE && ISBLANK(DIAS_INTERNOS_DH)))` = 0.
Muestra de 10 ex-centinela: todos ES_CERRADO=FALSE, FECHA_DESPACHO=null, Estado=PENDIENTE FACTURA.

## Q3 — INC-007B: FES manifiesto
FES cerrados 437/437 con FECHA_MANIFIESTO no nula. 0 sin manifiesto. 0 pendiente manifiesto.

## Q4 — INC-015: cobertura VBAP
1131/1941 = 58.3% (sin cambio). Hipótesis ceros descartada en corrida previa.

## Q5 — Baseline
Total 2097, cerrados 1941, evaluables 1941, en SLA 1580, fuera SLA 361, NS 81.4%, PromDH 3.49, P90 8.

## Q6 — Regresión
11 casos de regression_cases.csv. 10/11 OK. 4190139455 sigue NORMAL (regla pedido posterior C-C no cumple).
