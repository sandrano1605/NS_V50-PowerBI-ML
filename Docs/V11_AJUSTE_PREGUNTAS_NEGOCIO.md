# V11 · Ajuste del lienzo 01 según resultados reales

## Evidencia observada antes de la corrección

1. La tabla de recurrencia mostraba `Meses f.SLA = 4` aunque la ventana contiene tres meses.
   - Causa: `VALUES(Dim_Periodo_3M[AnioMes])` incorporaba la fila en blanco creada por fechas fuera de la dimensión 3M.
   - Además, la medida retiraba el filtro de fecha sin reaplicar el mes iterado.

2. La tabla de permanencia postfactura devolvía 691 combinaciones cliente-flujo, pero solo 10 tenían pedidos sobre 15 días.
   - Las 681 filas no críticas ocultaban el ranking.
   - El cálculo utilizaba días calendario y solo pedidos cerrados.

3. En vendedores, `Clientes 3M` y `Clientes 2M+` eran iguales.
   - Era un efecto directo del error de recurrencia.
   - El promedio DH incluía pedidos dentro del SLA, por lo que podía quedar bajo 5 DH aunque el bloque trataba incumplimientos.

4. La tabla temporal solo presentaba un total por mes.
   - No permitía comparar inicio, resto y cierre del mes.
   - Por lo tanto, no respondía si el deterioro provenía de FES o de la acumulación de pedidos, líneas y unidades.

## Correcciones V11

- Recurrencia limitada estrictamente a 0–3 meses válidos.
- El ranking de clientes muestra solo reincidentes en 2 o 3 meses.
- Se incorpora `Flujo` en rankings de cliente y vendedor.
- Promedio DH de recurrencia calculado solo sobre pedidos fuera SLA.
- Permanencia postfactura medida en días hábiles.
- Incluye pedidos cerrados y pedidos aún abiertos después de la factura.
- La tabla de CD muestra solo clientes con al menos un pedido sobre 15 DH.
- Se agrega cantidad de pedidos abiertos sobre 15 DH.
- La evolución temporal se descompone en:
  - Inicio · primeros 7 DH.
  - Resto del mes.
  - Cierre · últimos 7 DH.
- La comparación temporal muestra pedidos, FES, porcentaje FES, líneas, unidades, NS y promedio DH.
- Se incorpora filtro de zona manteniendo flujo y clasificación.
- Los CSV previos se archivan en `Docs/Resultados_Antes_V11` para evitar confusión con futuros resultados.

## Validaciones esperadas después de Actualizar todo

- `Meses f.SLA` debe quedar entre 2 y 3 en el ranking visible.
- `Clientes 3M` debe ser menor o igual que `Clientes 2M+`.
- `Prom. DH f.SLA` debe ser superior a 5 DH.
- La tabla de permanencia debe mostrar únicamente filas con `Pedidos >15 DH`.
- Cada mes debe desglosarse por inicio, resto y cierre cuando existan fechas en cada tramo.
