# Consultas DAX ejecutadas (REQ-002)

## 1. Ventana temporal (nuevas medidas)

```dax
EVALUATE ROW(
    "FechaMin", [RE Fecha mínima contexto],
    "FechaMax", [RE Fecha máxima contexto],
    "Ventana", [RE Ventana análisis texto],
    "EstadoMes", [RE Estado último mes]
)
```
Resultado: 30-04-2026 | 14-07-2026 | Período analizado: 30-04-2026 al 14-07-2026 · 4 meses · Último mes parcial | Último mes parcial

## 2. Coherencia lienzos 00 vs 01

```dax
EVALUATE ROW(
    "Pedidos00", [RE Pedidos contexto],
    "FueraSLA00", [RE Pedidos fuera SLA contexto],
    "NS00", [RE NS contexto],
    "Pedidos01", [FA Pedidos],
    "FueraSLA01", [FA Fuera SLA]
)
```
Resultado: 1616 | 360 | 77,72% | 1616 | 360 (diferencia 0)

## 3. Recurrencia clientes fuera SLA

```dax
DEFINE
    VAR vTabla =
        SUMMARIZE(Fact_Tracking, Dim_Cliente[CLIENTE_CODIGO],
            "Meses f.SLA", [FA Meses Fuera SLA Cliente Visible],
            "Recurrencia", [FA Recurrencia Cliente Visible])
    VAR vFiltrada = FILTER(vTabla, NOT ISBLANK([Meses f.SLA]))
EVALUATE
{
    ROW("TotalClientes", COUNTROWS(vFiltrada)),
    ROW("Recurrentes3M", COUNTROWS(FILTER(vFiltrada, [Meses f.SLA] = 3))),
    ROW("Recurrentes2M", COUNTROWS(FILTER(vFiltrada, [Meses f.SLA] = 2))),
    ROW("Puntual1M", COUNTROWS(FILTER(vFiltrada, [Meses f.SLA] = 1)))
}
```
Resultado: 251 | 3 | 27 | 221

## 4. Pedidos clave regresión

```dax
EVALUATE FILTER(SELECTCOLUMNS(Fact_Tracking,
    "Pedido", Fact_Tracking[PED_NUMERO_PEDIDO],
    "Flujo", Fact_Tracking[CLASIFICACION],
    "Zona", Fact_Tracking[ZONA],
    "Cierre", Fact_Tracking[FECHA_CIERRE],
    "Dias", Fact_Tracking[DIAS_INTERNOS_DH],
    "SLA", Fact_Tracking[SLA_INTERNO_DH],
    "Cumple", Fact_Tracking[CUMPLE_SLA_INTERNO]),
    [Pedido] IN {"4190139455", "1167577"})
```
Resultado: ambos FES cerrados por manifiesto, cumplen SLA.
