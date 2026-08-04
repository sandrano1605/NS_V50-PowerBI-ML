# Decisión · 54 pedidos fuera de SLA del lienzo 01

Fecha: 2026-08-04
Rama: `work/ns-lienzo-02-ingreso-pedidos`
Base auditada: `0803fc8d2a5ca772c447c7c4debbf26555c8825e`

## Decisión

**No excluir los 54 pedidos del indicador oficial ni modificar DAX.**

La cohorte oficial considera pedidos que cumplen simultáneamente:

- `ES_CERRADO = TRUE()`;
- `DIAS_INTERNOS_DH` no vacío;
- `CUMPLE_SLA_INTERNO = FALSE()` para fuera de SLA.

Excluir pedidos que cumplen esas condiciones mejoraría artificialmente el nivel de servicio y ocultaría incumplimientos reales. Una exclusión futura solo puede aplicarse mediante una regla de negocio explícita, documentada y auditable; nunca por el hecho de que un pedido aparezca en la tabla de clientes.

## Qué representa la tabla 1

El visual `fa_clientes_recurrentes` agrupa por:

- cliente;
- vendedor;
- flujo;
- meses fuera de SLA;
- recurrencia;
- pedidos fuera de SLA;
- porcentaje fuera de SLA;
- promedio de días fuera de SLA.

La medida visible es:

```DAX
FA Pedidos Fuera SLA Cliente Visible =
IF(
    [FA Meses Fuera SLA Cliente] >= 1,
    [FA Fuera SLA]
)
```

La condición `>= 1` controla la visibilidad del cliente; no transforma ni elimina pedidos. La recurrencia se clasifica como puntual 1M, recurrente 2M o recurrente 3M.

## Aclaración de las cifras

Las cifras **232, 109 y 54 no deben tratarse como el mismo universo** sin conservar el contexto de filtros:

- **232**: pedidos fuera de SLA del contexto KPI del lienzo 00/01 informado en la evidencia.
- **109**: conteo documentado únicamente para junio y julio (`59 + 50`). No incluye necesariamente todos los meses o fechas presentes en el contexto de 232.
- **54**: valor observado en la tabla agrupada por cliente/vendedor/flujo o en su contexto visible. La evidencia publicada contiene tres ejemplos, pero no un listado de 54 pedidos que demuestre una equivalencia directa con 109 o 232.

Por lo tanto, la frase “los 54 son el subconjunto del mes vigente” debe considerarse una hipótesis hasta que se publique el detalle de los 54 pedidos y el contexto exacto de la fila o selección.

## Evidencia mínima para una reconciliación exhaustiva

Cuando se necesite identificar exactamente los 54, exportar:

```text
PED_NUMERO_PEDIDO
PED_CODIGO_CLIENTE
CLIENTE_NOMBRE
VENDEDOR_NOMBRE
CLASIFICACION
PED_FECHA
DIAS_INTERNOS_DH
SLA_INTERNO_DH
EXCESO_SLA_INTERNO_DH
CUMPLE_SLA_INTERNO
SEMAFORO
MES / filtros activos
```

Y reconciliar:

```text
Total fuera SLA KPI = suma por mes del mismo contexto
Total visible de la tabla = suma de pedidos distintos, no suma ingenua de filas si existe más de una agrupación
54 = lista de 54 PED_NUMERO_PEDIDO distintos bajo el contexto observado
```

## Validación de los cambios visuales

El commit `0c5ea56` elimina los botones de navegación solicitados. No modifica las medidas DAX ni las consultas del modelo semántico. Los tres botones funcionales del lienzo 02 para alternar pedidos, líneas y unidades permanecen.

El commit contiene además normalización de archivos del reporte realizada por Power BI Desktop (posiciones, identificadores, bookmarks y cultura). Debe tratarse como ruido de serialización salvo que una prueba visual detecte regresión.

## Dictamen

| Control | Estado |
|---|---|
| Pedidos fuera SLA reales | Aceptado |
| Exclusión de los 54 | Rechazada |
| Cambio DAX | No requerido |
| Botones de navegación eliminados | Aceptado |
| 232 vs 109 | Contextos distintos; no reconciliados en la evidencia actual |
| Identificación exhaustiva de los 54 | Pendiente solo si se requiere trazabilidad pedido a pedido |

**Decisión final: mantener los pedidos y conservar el indicador oficial sin exclusiones.**
