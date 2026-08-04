# REQ-011 · Lienzo 02 — Análisis de ingreso de pedidos

## Objetivo

Rediseñar la página existente:

- ID: `df1cb253a6314642a469`
- Nombre actual: `02 Entrada y Cierre`
- Nombre final: `02 Ingreso de Pedidos`
- Tamaño: 1600 × 940

La página debe responder, en forma ejecutiva y operacional, cómo entra la carga que posteriormente debe procesar Logística.

## Decisión técnica

Usar únicamente visuales nativos de Power BI. No usar Python, SVG DAX ni visuales Image URL.

Razones:

- mayor velocidad de implementación;
- interacción completa con filtros y tooltips;
- menor riesgo de refresh y renderizado;
- evita volver a exponer código en hover;
- permite usar Analytics para líneas de promedio sin crear medidas adicionales.

## Fuente y cohorte

Usar como hecho principal `Fact_Tracking`, porque contiene una fila por pedido, `PED_FECHA`, `PED_FECHA_HORA`, `CLASIFICACION` y relaciones activas con `Dim_Fecha` y `Dim_Pedido`.

Para líneas y unidades usar `Lineas_y_unidades_por_pedidos`, relacionada mediante `Dim_Pedido` y, en las medidas, `TREATAS` sobre el conjunto de pedidos del contexto.

La página analiza todos los pedidos de la ventana seleccionada, abiertos y cerrados. No usar las medidas `FA Carga ...` como base porque están restringidas a la cohorte histórica cerrada y no responden la pregunta de ingreso.

## Calidad horaria — barrera obligatoria

Antes de construir el visual de corte 14:30, verificar la hora real de `PED_FECHA_HORA`.

Los pedidos integrados desde VBAK deben combinar:

- fecha: `VBAK_SAP.ERDAT`;
- hora: `VBAK_SAP.ERZET`.

No clasificar un registro `00:00:00` como “antes de 14:30” cuando la hora no está disponible. Debe quedar como `Sin hora válida`.

Crear en `Fact_Tracking`, desde Power Query, solamente estos atributos técnicos:

- `TRAMO_HORA_INGRESO`: `Hasta 14:30`, `Después de 14:30`, `Sin hora válida`;
- `ORDEN_TRAMO_HORA_INGRESO`: 1, 2, 3.

`TRAMO_HORA_INGRESO` debe ordenarse por `ORDEN_TRAMO_HORA_INGRESO`.

Regla:

```powerquery
if [PED_FECHA_HORA] = null then "Sin hora válida"
else if Time.From([PED_FECHA_HORA]) = #time(0,0,0) then "Sin hora válida"
else if Time.From([PED_FECHA_HORA]) <= #time(14,30,0) then "Hasta 14:30"
else "Después de 14:30"
```

Si la integración VBAK sigue dejando solamente la fecha, corregir `Fact_Pedidos_Auditoria` desde la interfaz de Power Query para combinar `ERDAT + ERZET`. No editar manualmente el TMDL para esa corrección.

## Medidas mínimas

Revisar primero si existen medidas equivalentes válidas para todos los pedidos. Si no existen, crear solamente estas tres medidas en la tabla `Medidas`, reutilizando el display folder existente:

`04. Análisis Fuera SLA\Carga y SLA`

No crear una nueva tabla de medidas ni un nuevo grupo de carpetas.

```DAX
IN Pedidos =
DISTINCTCOUNT(Fact_Tracking[PED_NUMERO_PEDIDO])
```

```DAX
IN Líneas =
VAR PedidosContexto = VALUES(Fact_Tracking[PED_NUMERO_PEDIDO])
RETURN
    CALCULATE(
        SUM(Lineas_y_unidades_por_pedidos[Lineas]),
        TREATAS(PedidosContexto, Lineas_y_unidades_por_pedidos[Pedido])
    )
```

```DAX
IN Unidades =
VAR PedidosContexto = VALUES(Fact_Tracking[PED_NUMERO_PEDIDO])
RETURN
    CALCULATE(
        SUM(Lineas_y_unidades_por_pedidos[Suma_Unidades]),
        TREATAS(PedidosContexto, Lineas_y_unidades_por_pedidos[Pedido])
    )
```

No crear medidas de promedio. Usar la línea de promedio del panel Analytics de cada gráfico.

## Preguntas de negocio

### 1. Día de la semana

**Pregunta:** ¿Qué día de la semana concentra más pedidos, líneas y unidades?

Visual recomendado: matriz nativa compacta.

- Filas: `Dim_Fecha[Dia_Semana]`.
- Columnas/valores: `[IN Pedidos]`, `[IN Líneas]`, `[IN Unidades]`.
- Orden: `Dim_Fecha[Dia_Semana_Numero]`.
- Formato: barras de datos y escala de intensidad por cada medida.
- Totales visibles.

La matriz evita comparar tres escalas incompatibles en un mismo eje.

### 2. Disponibilidad para Logística

**Pregunta:** ¿Qué proporción de pedidos queda disponible hasta las 14:30 y después de las 14:30, por día de la semana?

Visual recomendado: columnas 100% apiladas.

- Eje: `Dim_Fecha[Dia_Semana]`.
- Leyenda: `Fact_Tracking[TRAMO_HORA_INGRESO]`.
- Valor principal: `[IN Pedidos]`.
- Tooltip: `[IN Pedidos]`, `[IN Líneas]`, `[IN Unidades]`.
- Mostrar las tres categorías, incluida `Sin hora válida`.

No ocultar `Sin hora válida`; es un indicador de calidad del origen.

### 3. Concentración dentro del mes

**Pregunta:** ¿La carga aumenta al final del mes y qué flujo explica ese crecimiento?

Crear tres gráficos nativos separados, alineados y con el mismo ancho:

1. Pedidos por día del mes.
2. Líneas por día del mes.
3. Unidades por día del mes.

Configuración común:

- Eje X: `Dim_Fecha[Dia_Mes]`, orden ascendente 1–31.
- Leyenda: `Fact_Tracking[CLASIFICACION]`.
- Valores: medida correspondiente.
- Línea de promedio: Analytics → Average line.
- Tooltip: fecha/mes, `Dim_Fecha[Momento_Mes]`, pedidos, líneas, unidades y clasificación.
- Título/subtítulo: indicar que el gráfico acumula el período filtrado.

El apilado por `NORMAL`, `FES`, `FES + SALDO` y `SALDO` permite observar si el crecimiento de cierre está impulsado por FES.

Agregar un segmentador compacto de `Dim_Fecha[Momento_Mes]` con:

- Inicio · primeros 7 DH;
- Resto del mes;
- Cierre · últimos 7 DH.

Esto marca el cierre usando la definición real de días hábiles, sin asumir que siempre comienza el día 22.

## Diseño del lienzo

Mantener el lenguaje visual de las páginas 00 y 01.

### Encabezado

- Título: `02 Ingreso de Pedidos`.
- Subtítulo: `Cuándo entra la carga y en qué momento queda disponible para Logística`.
- Navegación consistente con páginas 00 y 01.

### Distribución sugerida

- Franja superior: título, período, flujo, zona y momento del mes.
- Bloque superior izquierdo: matriz por día de semana.
- Bloque superior derecho: corte 14:30 por día de semana.
- Franja inferior: tres gráficos de tendencia, Pedidos / Líneas / Unidades.

No usar fondos recargados ni más de una leyenda por gráfico.

## Filtros

Reutilizar los filtros existentes cuando estén disponibles:

- período;
- flujo/clasificación;
- zona;
- responsable;
- canal.

El período inicial debe corresponder a la ventana móvil vigente del modelo; no fijar manualmente fechas históricas.

## Validaciones obligatorias

1. `[IN Pedidos]` total = `DISTINCTCOUNT(Fact_Tracking[PED_NUMERO_PEDIDO])`.
2. La suma por día de semana debe reconciliar con el total general.
3. La suma de `Hasta 14:30 + Después de 14:30 + Sin hora válida` debe reconciliar con el total por día.
4. La suma por día del mes debe reconciliar con el total general.
5. La suma de flujos en cada día debe coincidir con el total de la barra.
6. Líneas y unidades deben reconciliar contra `Lineas_y_unidades_por_pedidos` para los pedidos del contexto.
7. Pedidos sin cobertura de líneas/unidades deben documentarse; no convertir nulos en datos inventados.
8. Las filas `VBAK SIN ZART` con hora no disponible deben quedar en `Sin hora válida`.
9. No debe quedar ningún visual Python, SVG DAX o Image URL en esta página.
10. El proyecto debe abrir, actualizar y guardar sin JSON o TMDL roto.
11. Smoke test de páginas 00, 01, 01.1 y 02.

## Condición de publicación

La página permanece `HiddenInViewMode` durante la construcción. Solo se muestra en vista normal después de:

- refresh completo verde;
- reconciliación de métricas verde;
- validación visual de alineación, títulos y tooltips;
- confirmación de que no existe hover técnico.
