# Consultas vivas ejecutadas
RUN_ID: 20260811_115352_auditoria_integral_cbcff02
SHA: cbcff026432f6bd3e5d5bfb3072688ad95039077
Puerto: 56878

## Q1 - Baseline universo
EVALUATE ROW(Total, Abiertos, Cerrados, Cerrados_con_DH, Cerrados_sin_DH, RE_Pedidos, RE_EnSLA, RE_FueraSLA, RE_NS)
Resultado: 2048/86/1962/1898/64/1898/1547/351/0.815

## Q2 - Clasificación
EVALUATE SUMMARIZECOLUMNS(CLASIFICACION, Pedidos) = NORMAL 1459, FES 432, FES+SALDO 5, SALDO 2

## Q3 - Zona
EVALUATE SUMMARIZECOLUMNS(ZONA, Pedidos, EnSLA, FueraSLA) = Santiago 925/779/146, Regiones 973/768/205

## Q4 - INC-005 RE multiselect
Normal+FES: Pedidos=1896, Valor=2271756623, PromDH=3.5005, P90=8
Todos: Pedidos=1898, Valor=2274130561, PromDH=3.5021, P90=8
Santiago+Regiones: 1898=Todos

## Q5 - INC-006 diferidos
CALCULATE(DISTINCTCOUNT HITOS, DIFERIDO_POR_CORTE=TRUE) = 946

## Q6 - INC-007 FES
FES cerrados=437, con manifiesto=437, abiertos=2

## Q7 - INC-009 FA multiselect
Normal+FES: FA_Ped=1896, FA_Lin=22801, FA_Unid=2420479
Todos: FA_Ped=1898, FA_Lin=22869, FA_Unid=2421491

## Q8 - INC-011 U vs RE
U cerrados=1962, RE evaluables=1898, diferencia=64 (cerrados sin DH)

## Q9 - INC-015 VBAP
Evaluables=1898, con_match=1107, sin_match=791, cobertura=58.3%

## Q10 - Regresión
11 pedidos consultados, ver 08_regression_cases_results.csv

## Q11 - INC-013 feriados
Dim_Feriados_Chile = 50 feriados nacionales

## Q12 - Errores nuevos
No RETURN huérfano. 1 SELECTEDVALUE(Flujo) restante en RE TT Título (display only).
