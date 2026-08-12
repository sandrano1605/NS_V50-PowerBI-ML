# Consultas vivas ejecutadas

RUN_ID: 20260811_181759_post_fix_inc011_inc015_evidencia_viva_085bfec
SHA auditado: 085bfec7531f57bd5894641e397a0ce99938680d
Modelo vivo: localhost:58835 (Power BI Desktop, base 56a5226e-f60b-4fc8-b6ef-199e71440797)
Método: powerbi-modeling_dax_query_operations (MCP funcional en esta sesión)

## Q1 — FIND-002A: estado de la medida RE TT Título

Obtener definición de medida `RE TT Título`:
- Resultado: state=SemanticError, errorMessage="A single value for column 'OrdenRango' in table 'Dim_Rango_Entrega' cannot be determined"
- Confirmado: el fix cdeda8bb sigue roto.

## Q2 — FIND-002A: 12 combinaciones (título + métricas)

Para cada caso se evaluó `RE TT Título`, `RE Pedidos contexto`, `RE Valor contexto`,
`RE Promedio contexto DH`, `RE P90 contexto DH`, `RE Pedidos fuera SLA contexto`.

Conjunto de filtros aplicado con TREATAS sobre Dim_Vista_Ejecutiva[Flujo] y
Dim_Rango_Entrega[Zona]:

1. Sin filtro
2. {1. Flujo Normal}
3. {2. FES (incluye FES + Saldo)}
4. {3. Saldos puros}
5. {1. Flujo Normal, 2. FES (incluye FES + Saldo)}
6. {1. Flujo Normal, 3. Saldos puros}
7. {2. FES (incluye FES + Saldo), 3. Saldos puros}
8. {Santiago}
9. {Regiones}
10. {Santiago, Regiones}
11. {1. Flujo Normal, 2. FES (incluye FES + Saldo)} + {Santiago}
12. {1. Flujo Normal, 2. FES (incluye FES + Saldo)} + {Santiago, Regiones}

Resultado: en los 12 casos el título falla con el error de OrdenRango; las métricas
numéricas devuelven valores consistentes. Ver raw/find002_titulo_12_combinaciones.csv.

## Q3 — INC-011: cerrados sin DH

```dax
EVALUATE
ROW(
  "CerradosSinDH", COUNTROWS(FILTER('Fact_Tracking', [ES_CERRADO] = TRUE() && ISBLANK([DIAS_INTERNOS_DH]))),
  "ConCierreSentinel", COUNTROWS(FILTER('Fact_Tracking', [ES_CERRADO] = TRUE() && ISBLANK([DIAS_INTERNOS_DH]) && [FECHA_CIERRE] = DATE(2020,9,24) + TIME(22,47,0))),
  "CierreAntesCreacion", COUNTROWS(FILTER('Fact_Tracking', [ES_CERRADO] = TRUE() && ISBLANK([DIAS_INTERNOS_DH]) && [FECHA_CIERRE] < [PED_FECHA_HORA])),
  "ConDespacho", ...,
  "ConManifiesto", ...,
  "ConFactura", ...
)
```
- Resultado: 55 / 55 / 55 / 55 / 0 / 0.
- Lista completa exportada a raw/inc011_cerrados_sin_dh.md.

## Q4 — INC-015: match exacto y normalizado VBAP

```dax
VAR Evaluables = FILTER(ADDCOLUMNS('Fact_Tracking', "Pedido", [PED_NUMERO_PEDIDO], ...),
   [EsCerrado]=TRUE() && NOT ISBLANK([DH]) && [RE Filtro Flujo] && [RE Filtro Zona])
ROW("Evaluables", COUNTROWS(Evaluables), "ConMatchExacto", COUNTROWS(FILTER(Evaluables, [Pedido] IN VALUES('Lineas_y_unidades_por_pedidos'[Pedido]))))
```
- Resultado: 1934 evaluables / 1128 match exacto (58,3%).
- Match por valor numérico (FORMAT(VALUE(...),"0")): 1128 (sin mejora).
- Conteos de ceros a la izquierda: 0 en ambas tablas.
- Derivados 10→7 y 7→10: 0.
- Sin match en VBAK: 778/806.
- Detalle en raw/inc015_cobertura_vbap.md.

## Q5 — INC-007B: FES manifiesto real vs TRP

```dax
VAR FES = FILTER('Fact_Pedidos_Auditoria', [ES_FES] = TRUE())
ROW("FES_total", COUNTROWS(FES),
     "FES_conManifiestoReal", COUNTROWS(FILTER(FES, NOT ISBLANK([ULTIMA_FECHA_MANIFIESTO]) || NOT ISBLANK([PRIMERA_FECHA_MANIFIESTO]))),
     "FES_sinManifiesto_conTRP", COUNTROWS(FILTER(FES, ISBLANK(ULT) && ISBLANK(PRIM) && (TRP_U o TRP_P no nula))),
     "FES_sinManifiesto_sinTRP", ...,
     "FES_cerrados", ...)
```
- Resultado: 439 / 437 / 0 / 2 / 437.
- Detalle en raw/inc007b_fes_trp.md.

## Q6 — Regresión casos CSV

- Consulta de los 11 pedidos de regression_cases.csv con flujo, zona, cierre, DH, SLA, cumple.
- Resultado en raw/regresion_viva.md.
- Caso discrepante: 4190139455 (histórico FES, actual NORMAL — regla de pedido posterior C-C no cumple).

## Q7 — Periodo activo

- Dim_Periodo_3M: 0=2026-08 (vigente), 1=2026-07, 2=2026-06.
- Dim_Fecha: 2026-01-01 a 2026-12-31.
