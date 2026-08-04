# LLM local · Prueba final del lienzo 02 profesional

## Rol

El lienzo ya está implementado. No modificar DAX, Power Query, TMDL, JSON, bookmarks, botones, medidas ni visuales.

El trabajo local es abrir, refrescar, probar, reconciliar y publicar evidencia. Ante una incoherencia, detenerse y diagnosticarla.

## Rama

```text
work/ns-lienzo-02-ingreso-pedidos
```

Recuperar el HEAD remoto vigente y confirmar SHA local = remoto.

## Componentes obligatorios

### Tarjetas

- Pedidos ingresados.
- Líneas ingresadas.
- Unidades ingresadas.

Deben mostrar el valor grande, legible y responder a los seis filtros.

### Lectura ejecutiva dinámica

Debe responder en una sola línea:

- día líder en pedidos y su valor;
- día líder en líneas y su valor;
- día líder en unidades y su valor;
- porcentaje de pedidos después de las 14:30;
- variación del promedio diario del cierre respecto del resto del mes;
- participación FES/Saldo dentro del cierre.

Reconciliar cada valor contra consultas independientes del modelo.

### Q1 · Día de la semana

La matriz debe mostrar lunes a domingo y tres valores: pedidos, líneas y unidades.

Validar que los días máximos coincidan con `IN Lectura Ejecutiva`.

### Q2 · Disponibilidad para Logística

El gráfico 100% apilado debe mostrar por día:

- Hasta 14:30.
- Después de 14:30.
- Sin hora válida.

Las etiquetas deben ser visibles. Cada día debe sumar 100%. El porcentaje general posterior a las 14:30 debe coincidir con la lectura ejecutiva.

### Q3 · Tendencia dentro del mes

Los botones deben alternar entre:

- pedidos;
- líneas;
- unidades.

Cada gráfico debe ocupar todo el ancho disponible, incluir:

- día del mes 1–31;
- barras apiladas por flujo;
- valores visibles mediante etiquetas;
- línea de promedio;
- título correcto.

La lectura ejecutiva debe reconciliar el delta cierre vs resto y el peso FES/Saldo del cierre.

## Prueba de botones y filtros

1. Seleccionar mes, canal distinto de 43/45, flujo, zona, responsable y momento del mes.
2. Registrar los seis filtros.
3. Pulsar `VER POR PEDIDOS`, `VER POR LINEAS`, `VER POR UNIDADES`.
4. En cada clic confirmar exactamente un gráfico visible.
5. Confirmar que ningún filtro cambia.
6. Repetir con otro mes y otro canal.
7. Cerrar y reabrir Power BI Desktop.
8. Repetir la prueba y confirmar persistencia.

## Calidad visual profesional

Comprobar:

- tarjetas alineadas y con valores legibles;
- lectura ejecutiva sin texto cortado;
- títulos completos;
- gráfico mensual a ancho completo;
- etiquetas visibles pero sin saturación grave;
- leyenda legible;
- línea promedio distinguible;
- botones con texto normal y hover correctos;
- tooltips `Mostrar tendencia de...` correctos;
- ausencia de superposición involuntaria;
- ausencia de visuales rotos;
- páginas 00, 01 y 01.1 sin regresiones.

Si las etiquetas se superponen al punto de impedir la lectura, registrar `AMARILLO` con captura y detalle; no corregir.

## Evidencia obligatoria

Crear:

```text
Docs/AUDITORIA_LIVE/runs/<timestamp>_lienzo_02_profesional/
```

Archivos mínimos:

```text
00_git_before.txt
01_refresh.txt
02_tarjetas.csv
03_lectura_ejecutiva.csv
04_q1_dia_semana.csv
05_q2_hora_1430.csv
06_q3_pedidos_dia_mes.csv
07_q3_lineas_dia_mes.csv
08_q3_unidades_dia_mes.csv
09_botones_y_filtros.csv
10_calidad_visual.txt
11_regresiones.txt
12_incoherencias.csv
RESULTADO.md
manifest.json
```

`RESULTADO.md` debe responder explícitamente Q1, Q2 y Q3 con valores, no solo indicar que los gráficos cargaron.

Commit permitido:

```text
audit(lienzo-02): validar preguntas y acabado profesional
```

Solo versionar la carpeta de evidencia.