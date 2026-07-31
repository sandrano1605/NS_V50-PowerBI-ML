# Consultas DAX ejecutadas (run 20260731_033000)

## Validacion de acceso y datos

```dax
EVALUATE ROW(
    "FechaAuditoria", NOW(),
    "PedidosTracking", CALCULATE(DISTINCTCOUNT(Fact_Tracking[PED_NUMERO_PEDIDO]), Fact_Tracking[ES_CERRADO] = TRUE(), NOT ISBLANK(Fact_Tracking[DIAS_INTERNOS_DH])),
    "PedidosTotales", COUNTROWS(Fact_Tracking),
    "Clientes", COUNTROWS(Dim_Cliente)
)
```

Resultado: 30-07-2026 22:54:13 | 1.616 | 1.695 | 682

## Validacion de recurrencia con medidas corregidas

```dax
DEFINE
    VAR vTabla =
        SUMMARIZE(
            Fact_Tracking,
            Dim_Cliente[CLIENTE_CODIGO],
            Dim_Cliente[CLIENTE_NOMBRE],
            "Meses f.SLA", [FA Meses Fuera SLA Cliente Visible],
            "Recurrencia", [FA Recurrencia Cliente Visible],
            "Pedidos f.SLA", [FA Pedidos Fuera SLA Cliente Visible],
            "% f.SLA", [FA % Fuera SLA Cliente Visible],
            "Prom. DH f.SLA", [FA DH Fuera SLA Cliente Visible]
        )
    VAR vFiltrada = FILTER(vTabla, NOT ISBLANK([Meses f.SLA]))
EVALUATE
{
    ROW("TotalClientesVisibles", COUNTROWS(vFiltrada)),
    ROW("Recurrentes3M", COUNTROWS(FILTER(vFiltrada, [Meses f.SLA] = 3))),
    ROW("Recurrentes2M", COUNTROWS(FILTER(vFiltrada, [Meses f.SLA] = 2))),
    ROW("Puntual1M", COUNTROWS(FILTER(vFiltrada, [Meses f.SLA] = 1)))
}
```

Resultado: 251 | 3 | 27 | 221 ✅

## Validacion de lienzos 00 y 01

```dax
EVALUATE ROW(
    "PedidosLienzo00", [RE Pedidos contexto],
    "FueraSLA00", [RE Pedidos fuera SLA contexto],
    "NS00", [RE NS contexto],
    "FAPedidos", [FA Pedidos],
    "FAFueraSLA", [FA Fuera SLA],
    "FAPorcentaje", [FA % Fuera SLA]
)
```

Resultado: 1.616 | 360 | 77,72% | 1.616 | 360 | 22,28% ✅

## Top del ranking (primer bloque = Recurrente 3M)

```dax
DEFINE
    VAR vTabla =
        SUMMARIZE(
            Fact_Tracking,
            Dim_Cliente[CLIENTE_NOMBRE],
            "Meses f.SLA", [FA Meses Fuera SLA Cliente Visible],
            "Recurrencia", [FA Recurrencia Cliente Visible],
            "Pedidos f.SLA", [FA Pedidos Fuera SLA Cliente Visible],
            "% f.SLA", [FA % Fuera SLA Cliente Visible],
            "Prom. DH f.SLA", [FA DH Fuera SLA Cliente Visible]
        )
    VAR vFiltrada = FILTER(vTabla, NOT ISBLANK([Meses f.SLA]))
    VAR vOrdenada = ADDCOLUMNS(vFiltrada, "Orden", RANKX(vFiltrada, [Meses f.SLA] * 10000 + [Pedidos f.SLA] * 100 + [Prom. DH f.SLA], , DESC))
EVALUATE
FILTER(vOrdenada, [Orden] <= 8)
```

Resultado top: PRISA 3M/7 pedidos, EVENTAIL 3M/4, PLAZA EGAÑA 3M/3, luego 2M ✅

## Pedidos clave de regresion

```dax
EVALUATE
FILTER(
    SELECTCOLUMNS(
        Fact_Tracking,
        "Pedido", Fact_Tracking[PED_NUMERO_PEDIDO],
        "Flujo", Fact_Tracking[CLASIFICACION],
        "Zona", Fact_Tracking[ZONA],
        "Cierre", Fact_Tracking[FECHA_CIERRE],
        "Dias", Fact_Tracking[DIAS_INTERNOS_DH],
        "SLAInterno", Fact_Tracking[SLA_INTERNO_DH],
        "Cumple", Fact_Tracking[CUMPLE_SLA_INTERNO]
    ),
    [Pedido] IN {"4190139455", "1167577"}
)
```

Resultado: ambos FES cerrados por manifiesto, cumple TRUE ✅
