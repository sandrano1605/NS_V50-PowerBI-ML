# REQ-002 · Preguntas de negocio, ventana temporal y comportamiento SVG

## Proyecto

- **Repositorio:** `sandrano1605/NS_V50-PowerBI-ML`
- **Rama de trabajo:** `work/ns-live-audit`
- **Proyecto PBIP:** `NS.pbip`
- **Modelo semántico:** `NS.SemanticModel`
- **Reporte:** `NS.Report`
- **Lienzos prioritarios:**
  - `00 Resumen Ejecutivo Mayorista`
  - `01 Análisis Fuera SLA`
  - `01.1 Auditoría por Pedido`

---

# 1. Objetivo

Asegurar que cada visual relevante del reporte:

1. Declare claramente la **pregunta de negocio que responde**.
2. Muestre el **período real de datos considerado**, indicando fecha mínima y fecha máxima.
3. No exponga código SVG, `data:image/svg+xml`, XML, HTML o texto técnico al pasar el mouse.
4. Mantenga la coherencia entre título, pregunta, filtros, medidas y resultado.
5. Quede auditado contra el modelo Power BI en vivo mediante MCP.

Este requerimiento es funcional, visual y documental. No debe resolverse únicamente cambiando títulos.

---

# 2. Alcance

## 2.1 Lienzo 00 · Resumen Ejecutivo Mayorista

Auditar y ajustar todos los visuales de negocio:

- Tarjetas KPI.
- NS general.
- Pedidos evaluados.
- Pedidos fuera SLA.
- Valor en/fuera SLA.
- Evolución temporal.
- Distribución Santiago/Regiones.
- Flujos NORMAL, FES, SALDO y FES + SALDO.
- Hitos o procesos críticos.
- Top clientes.
- Top vendedores.
- SVG de estado, semáforos, flujo o navegación.
- Tooltips del lienzo.

## 2.2 Lienzo 01 · Análisis Fuera SLA

Auditar y ajustar:

1. Clientes fuera SLA y recurrencia.
2. Permanencia postfactura.
3. Vendedores con clientes recurrentes.
4. FES versus carga.
5. Pedidos críticos.
6. Botones, SVG y tooltips.

## 2.3 Lienzo 01.1 · Auditoría por Pedido

Auditar y ajustar:

- Identificación del pedido.
- Flujo.
- Zona.
- Fecha de creación.
- Factura.
- Despacho.
- Manifiesto.
- Fecha de cierre.
- Días hábiles.
- SLA aplicado.
- Estado de cumplimiento.
- SVG de estados e hitos.
- Tooltips.

---

# 3. Regla obligatoria: pregunta de negocio por visual

Cada visual de negocio debe tener:

- **Título breve**, orientado al indicador.
- **Pregunta de negocio explícita**, visible debajo del título o en un bloque de texto inmediatamente asociado.
- **Ventana temporal visible**, con fecha mínima y fecha máxima.
- **Unidad y cohorte**, cuando corresponda.

No usar preguntas genéricas como:

- “¿Qué está pasando?”
- “¿Cómo estamos?”
- “Análisis de clientes”

La pregunta debe coincidir exactamente con la medida y el contexto del visual.

---

# 4. Preguntas de negocio requeridas

## 4.1 Lienzo 00 · Resumen Ejecutivo Mayorista

### KPI · Nivel de servicio

**Título sugerido**

`NIVEL DE SERVICIO INTERNO`

**Pregunta de negocio**

`¿Qué porcentaje de pedidos cerrados y evaluables cumplió el SLA interno correspondiente a su zona?`

**Aclaración**

- Santiago: 4 DH.
- Regiones: 5 DH.
- Solo pedidos cerrados y evaluables.

### KPI · Pedidos evaluados

`¿Cuántos pedidos cerrados cuentan con información suficiente para evaluar su cumplimiento de SLA?`

### KPI · Pedidos fuera SLA

`¿Cuántos pedidos cerrados superaron el SLA interno correspondiente a Santiago o Regiones?`

### KPI · Valor afectado

`¿Qué valor neto está asociado a pedidos que incumplieron el SLA interno?`

### Evolución mensual

`¿Cómo ha evolucionado el nivel de servicio durante el período analizado y en qué meses se observa deterioro?`

### Santiago versus Regiones

`¿Qué zona presenta mayor incumplimiento considerando su SLA interno específico?`

### Distribución por flujo

`¿Qué flujo operativo concentra más pedidos fuera SLA: NORMAL, FES, SALDO o FES + SALDO?`

### Procesos o hitos críticos

`¿En qué etapa del proceso se concentra el mayor exceso de días hábiles y cuántos pedidos afecta?`

### Clientes prioritarios

`¿Qué clientes concentran más pedidos fuera SLA, mayor recurrencia o mayor impacto económico?`

### Vendedores prioritarios

`¿Qué vendedores administran clientes con mayor recurrencia de incumplimiento y qué volumen representan?`

## 4.2 Lienzo 01 · Análisis Fuera SLA

### Visual 1 · Clientes fuera SLA

**Título**

`1. CLIENTES FUERA SLA · FRECUENCIA EN LOS ÚLTIMOS 3 MESES`

**Pregunta de negocio**

`¿Qué clientes estuvieron fuera SLA durante los últimos tres meses, con qué frecuencia repitieron el incumplimiento y cuáles requieren priorización?`

**Orden**

1. Meses fuera SLA, descendente.
2. Pedidos fuera SLA, descendente.
3. Promedio DH fuera SLA, descendente.

### Visual 2 · Permanencia postfactura

**Título**

`2. FACTURA → CIERRE OFICIAL >15 DH`

**Pregunta de negocio**

`¿Qué clientes presentan pedidos cerrados con más de 15 días hábiles entre la factura y el cierre oficial del flujo?`

**Regla de cierre**

- FES/FES + SALDO: factura → último manifiesto.
- NORMAL/SALDO: factura → último despacho válido.

### Visual 3 · Vendedores y recurrencia

`¿Qué vendedores concentran clientes recurrentes fuera SLA y qué nivel de incumplimiento generan esos clientes?`

Las métricas del vendedor deben considerar exclusivamente clientes recurrentes cuando el título indique “clientes recurrentes”.

### Visual 4 · FES versus carga

`¿El deterioro del nivel de servicio coincide con una mayor concentración de pedidos, líneas, unidades o participación FES al inicio o cierre del mes?`

Debe separar:

- Inicio.
- Resto.
- Cierre.

No usar causalidad directa sin prueba estadística. Usar: coincide, se asocia, presenta una señal, patrón observado.

### Visual 5 · Pedidos críticos

`¿Qué pedidos presentan el mayor exceso sobre su SLA y en qué hito o causa operacional se concentra el atraso?`

## 4.3 Lienzo 01.1 · Auditoría por Pedido

**Pregunta principal**

`¿Cómo se construye el resultado de SLA de este pedido y qué fechas, flujo, zona y regla de cierre determinan su estado?`

Preguntas secundarias:

- `¿Cuál fue la fecha real de creación?`
- `¿Cuál fue la factura inicial o final utilizada?`
- `¿Cuál es el cierre oficial según el flujo?`
- `¿Cuántos días hábiles fueron calculados?`
- `¿Qué SLA zonal se aplicó?`
- `¿Cumple o excede el SLA?`
- `¿Cuál es la fuente de la fecha de cierre?`

---

# 5. Ventana temporal obligatoria

Cada lienzo debe mostrar una leyenda visible con:

- Fecha mínima del contexto.
- Fecha máxima del contexto.
- Cantidad de meses incluidos.
- Estado del último mes: completo o parcial.

## 5.1 Medidas DAX requeridas

Crear o reutilizar medidas equivalentes a:

```DAX
RE Fecha mínima contexto =
MINX(
    ALLSELECTED(Fact_Tracking),
    Fact_Tracking[FECHA_CREACION]
)
```

```DAX
RE Fecha máxima contexto =
MAXX(
    ALLSELECTED(Fact_Tracking),
    Fact_Tracking[FECHA_CREACION]
)
```

```DAX
RE Ventana análisis texto =
VAR FechaMin = [RE Fecha mínima contexto]
VAR FechaMax = [RE Fecha máxima contexto]
VAR Meses =
    DATEDIFF(
        DATE(YEAR(FechaMin), MONTH(FechaMin), 1),
        DATE(YEAR(FechaMax), MONTH(FechaMax), 1),
        MONTH
    ) + 1
RETURN
IF(
    ISBLANK(FechaMin) || ISBLANK(FechaMax),
    "Sin datos en el contexto seleccionado",
    "Período analizado: "
        & FORMAT(FechaMin, "dd-MM-yyyy")
        & " al "
        & FORMAT(FechaMax, "dd-MM-yyyy")
        & " · "
        & FORMAT(Meses, "0")
        & " meses"
)
```

Adaptar nombres reales de tabla y columna.

## 5.2 Regla de contexto

La fecha mínima y máxima debe respetar:

- filtros de fecha;
- zona;
- flujo;
- cliente;
- vendedor;
- canal;
- selección del usuario.

No usar `ALL()` si elimina filtros que el usuario espera conservar.

## 5.3 Último mes parcial

Agregar una medida:

```DAX
RE Estado último mes =
VAR FechaMax = [RE Fecha máxima contexto]
VAR FinMes = EOMONTH(FechaMax, 0)
RETURN
IF(
    ISBLANK(FechaMax),
    BLANK(),
    IF(
        FechaMax < FinMes,
        "Último mes parcial",
        "Último mes completo"
    )
)
```

Leyenda esperada:

`Período analizado: 01-05-2026 al 28-07-2026 · 3 meses · Último mes parcial`

## 5.4 Ubicación

En cada lienzo:

- Debajo del título general.
- Sin superponer filtros o navegación.
- Tamaño legible.
- No ocultarlo dentro de tooltip.
- No usar fecha fija escrita manualmente.

---

# 6. Eliminación del código SVG al pasar el mouse

## 6.1 Problema

Al posicionar el mouse sobre ciertos elementos SVG, Power BI muestra:

- código SVG;
- `data:image/svg+xml`;
- XML;
- texto de la medida;
- URI completa;
- contenido técnico.

Esto no debe ocurrir.

## 6.2 Auditoría requerida

Identificar todos los objetos que usan:

- medidas SVG;
- columnas con categoría `Image URL`;
- `data:image/svg+xml`;
- `data:image/svg+xml;utf8`;
- `data:image/svg+xml;base64`;
- HTML o XML generado por DAX;
- SVG usado en tabla, matriz, tarjeta, botón o imagen.

Crear:

`Docs/AUDITORIA_LIVE/latest/svg_inventory.csv`

Columnas:

```text
PAGINA
VISUAL
TIPO_VISUAL
MEDIDA_SVG
DATA_CATEGORY
TOOLTIP_ACTIVO
CAMPO_EN_TOOLTIP
MUESTRA_CODIGO_AL_HOVER
ACCION_REQUERIDA
ESTADO
```

## 6.3 Corrección obligatoria

Para SVG decorativos o de estado:

1. Establecer la medida o columna como `Data category = Image URL`.
2. Desactivar tooltip del visual cuando no aporte información.
3. Eliminar la medida SVG de cualquier bucket de tooltip.
4. No usar la medida SVG como título dinámico.
5. No usar la medida SVG como texto alternativo.
6. No dejar el código SVG como campo oculto del visual.
7. No permitir tooltip automático basado en el campo Image URL.
8. Si se necesita tooltip, usar una medida de texto separada.

Ejemplo:

```DAX
RE Tooltip Estado =
"Pedido: " & SELECTEDVALUE(Fact_Tracking[PED_NUMERO_PEDIDO])
& UNICHAR(10)
& "Estado: " & [RE Estado Texto]
& UNICHAR(10)
& "Días: " & FORMAT([RE Días], "0.0")
```

No usar `RE Estado SVG` como contenido del tooltip.

## 6.4 Visuales de tabla o matriz

Cuando el SVG esté dentro de una tabla o matriz:

- Mantener el SVG únicamente como imagen.
- Usar una página tooltip dedicada o medidas de texto.
- Revisar `visualTooltip`.
- Revisar campos implícitos agregados al tooltip.
- Desactivar tooltip automático si sigue mostrando la URI.
- Verificar manualmente cada columna con SVG.

## 6.5 SVG en botones o navegación

Para SVG de botones:

- Preferir imagen integrada o recurso del reporte.
- Desactivar tooltip técnico.
- Usar tooltip descriptivo breve: `Ir al resumen`, `Abrir auditoría del pedido`, `Restablecer filtros`.
- Nunca mostrar el código o la URI.

## 6.6 Criterio de aceptación

Al pasar el mouse por cualquier SVG:

- No aparece código.
- No aparece `data:image`.
- No aparece XML.
- No aparece la expresión DAX.
- Solo aparece un tooltip de negocio, o no aparece tooltip.

---

# 7. Coherencia entre título, pregunta y medida

Crear:

`Docs/AUDITORIA_LIVE/latest/business_questions_matrix.csv`

Columnas:

```text
PAGINA
VISUAL
TITULO
PREGUNTA_NEGOCIO
MEDIDAS
COHORTE
FECHA_MIN
FECHA_MAX
FILTROS
RESPONDE_PREGUNTA
OBSERVACION
ESTADO
```

Estados: `OK`, `REVISAR`, `ERROR`.

Marcar `ERROR` si:

- el título promete recurrencia y muestra solo promedio;
- el visual usa una cohorte diferente;
- fecha mínima/máxima no respeta filtros;
- muestra abiertos en análisis histórico;
- usa cierre incorrecto;
- usa SLA fijo;
- el SVG expone código;
- pregunta y medida no coinciden.

---

# 8. Validación mediante MCP del modelo vivo

No validar únicamente archivos PBIP.

Debe:

1. Abrir el PBIP correcto.
2. Ejecutar `Actualizar todo`.
3. Conectar MCP al modelo vivo.
4. Leer medidas reales.
5. Ejecutar consultas DAX.
6. Exportar resultados por visual.
7. Verificar filtros de página y visual.
8. Comparar fechas mínima y máxima.
9. Confirmar que las preguntas coinciden con los datos.
10. Verificar el comportamiento SVG manualmente y documentarlo.

---

# 9. Evidencia del run

Crear:

`Docs/AUDITORIA_LIVE/runs/YYYYMMDD_HHMMSS_req002_preguntas_fechas_svg/`

Archivos mínimos:

```text
00_resumen.md
01_inventario_visuales.csv
02_business_questions_matrix.csv
03_medidas_fecha.csv
04_resultados_fecha_contexto.csv
05_svg_inventory.csv
06_svg_before_after.csv
07_objetos_modificados.csv
08_consultas_dax.md
09_resultados_modelo_vivo.csv
10_validacion_visual.json
11_casos_regresion.csv
12_git_before.txt
13_git_after.txt
RESULTADO.md
```

Copiar a `latest/`:

```text
business_questions_matrix.csv
svg_inventory.csv
ventana_temporal.csv
RESULTADO.md
manifest.json
```

---

# 10. Casos de regresión

Mantener y ejecutar:

- `4190139455`
- `1167577`

Validar para ambos:

- flujo;
- zona;
- creación;
- factura;
- despacho;
- manifiesto;
- cierre;
- días;
- SLA;
- cumplimiento.

Además validar:

- un FES abierto;
- un NORMAL cerrado;
- un SALDO cerrado;
- Santiago exactamente 4 DH;
- Regiones exactamente 5 DH;
- último mes parcial.

No modificar lógica de cierre ni SLA durante este requerimiento.

---

# 11. Restricciones

No hacer en este requerimiento:

- cambiar SLA;
- cambiar cierre FES;
- cambiar universo histórico;
- cambiar relaciones;
- cambiar Power Query;
- cambiar Python;
- cambiar medidas de recurrencia ya aprobadas;
- rediseñar completamente los lienzos;
- mezclar otras mejoras funcionales.

Si se detecta un problema adicional, documentarlo como hallazgo separado.

---

# 12. Commits

## Commit funcional

```text
feat(report): agregar preguntas de negocio y ventana temporal por lienzo
```

## Commit SVG

```text
fix(svg): eliminar codigo tecnico de tooltips y hover
```

## Commit de auditoría

```text
audit(report): registrar evidencia de preguntas fechas y svg
```

No combinar los tres si los cambios pueden separarse.

---

# 13. Criterios de aceptación final

El requerimiento queda VERDE solo si:

- Todos los visuales relevantes tienen pregunta de negocio.
- Cada lienzo muestra fecha mínima y máxima dinámica.
- Se indica si el último mes es parcial.
- Las fechas responden a filtros.
- Ningún SVG muestra código al pasar el mouse.
- Título, pregunta y medida son coherentes.
- Los resultados del lienzo 00 y 01 siguen coincidiendo.
- Se mantienen:
  - 1.616 pedidos evaluables;
  - 360 fuera SLA;
  - NS 77,72%;
  - 251 clientes fuera SLA;
  - cierre FES por manifiesto;
  - SLA 4 DH Santiago y 5 DH Regiones.
- Los pedidos `4190139455` y `1167577` mantienen resultados correctos.
- Power BI completa `Actualizar todo` sin errores.
- JSON y TMDL son válidos.
- La evidencia queda publicada en GitHub.

---

# 14. Entrega esperada del LLM

```text
REPOSITORIO:
sandrano1605/NS_V50-PowerBI-ML

RAMA:
work/ns-live-audit

COMMITS:
<commit funcional>
<commit svg>
<commit auditoría>

REFRESH:
OK|ERROR

ESTADO:
VERDE|AMARILLO|ROJO

LIENZOS AUDITADOS:
...

VISUALES CON PREGUNTA:
...

VENTANA TEMPORAL:
Fecha mínima:
Fecha máxima:
Último mes:

SVG CORREGIDOS:
...

EVIDENCIA:
Docs/AUDITORIA_LIVE/runs/<run_id>/

LIMITACIONES:
...
```
