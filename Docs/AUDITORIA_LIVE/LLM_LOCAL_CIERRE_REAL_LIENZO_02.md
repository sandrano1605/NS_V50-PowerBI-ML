# LLM local · Cierre real de auditoría del lienzo 02

## Rol

El lienzo ya está implementado y corregido. No modificar DAX, Power Query, TMDL, relaciones, JSON, bookmarks, botones ni visuales.

Ejecutar únicamente: recuperar rama, abrir Power BI Desktop, refrescar, probar, reconciliar y publicar evidencia.

## Rama

```text
work/ns-lienzo-02-ingreso-pedidos
```

Confirmar que SHA local y remoto coincidan antes de abrir `NS.pbip`.

## 1. Refresh y modelo

1. Ejecutar dos refresh consecutivos.
2. Confirmar:
   - `Fact_Tracking` filas = pedidos distintos;
   - duplicados por pedido = 0;
   - EXCEPT Tracking vs Master = 0 en ambos sentidos después del segundo refresh.
3. Registrar cualquier diferencia causada por pedidos creados durante el refresh.

## 2. Filtro MES - AÑO

Probar al menos dos períodos disponibles, incluido el mes actual y el anterior.

Para cada mes registrar:

- etiqueta seleccionada;
- fecha mínima y máxima de `Fact_Tracking[PED_FECHA]`;
- pedidos;
- líneas;
- unidades;
- día líder en las tres métricas;
- cobertura horaria;
- promedio diario de cierre y resto.

Condiciones de aprobación:

- todas las fechas deben pertenecer al mes seleccionado;
- las tarjetas y los cinco visuales deben cambiar cuando cambian los datos del mes;
- no se acepta que el slicer muestre un mes y las tarjetas mantengan el universo completo;
- la suma de pedidos de los períodos debe reconciliar con el universo de la ventana, considerando el mes actual parcial.

## 3. Filtro ZONA GEOGRÁFICA

El slicer corregido usa `Fact_Tracking[ZONA]`.

Probar:

- Todos;
- Santiago;
- Regiones.

Registrar pedidos, líneas y unidades en cada selección.

Condiciones de aprobación:

- Santiago y Regiones deben modificar los valores;
- Pedidos Todos = Pedidos Santiago + Pedidos Regiones;
- Líneas y unidades deben reconciliar de la misma forma, salvo pedidos sin detalle, los que deben listarse;
- la selección debe afectar matriz, gráfico horario, gráficos mensuales, tarjetas y lectura ejecutiva.

## 4. Cobertura de líneas y unidades

Publicar:

- pedidos distintos en `Fact_Tracking`;
- pedidos distintos en `Lineas_y_unidades_por_pedidos`;
- pedidos de Tracking sin coincidencia en detalle;
- pedidos de detalle sin coincidencia en Tracking;
- pedidos repetidos en la tabla resumen de líneas/unidades;
- pedidos con `Lineas` nulo;
- pedidos con `Suma_Unidades` nulo.

Listar las claves de cualquier excepción. No declarar VERDE con diferencias no explicadas.

## 5. Botones y bookmarks · prueba real

Con filtros activos de mes, zona, canal, flujo, responsable y momento del mes:

1. Registrar los seis filtros y las tres tarjetas.
2. Pulsar `VER POR PEDIDOS`.
3. Confirmar exactamente un gráfico visible.
4. Pulsar `VER POR LINEAS` y repetir.
5. Pulsar `VER POR UNIDADES` y repetir.
6. Confirmar que ningún filtro ni tarjeta cambió por el clic.
7. Cambiar de mes y zona y repetir.
8. Cerrar Power BI Desktop, reabrir y repetir.

La evidencia debe registrar valores reales antes y después, no `SIN_CAMBIO` genérico ni solo `OK_estructural`.

## 6. Q1, Q2 y Q3

Reconciliar nuevamente:

### Q1

- día líder en pedidos;
- día líder en líneas;
- día líder en unidades.

### Q2

- cobertura de hora válida;
- porcentaje hasta 14:30 sobre casos medibles;
- porcentaje después de 14:30 sobre casos medibles;
- porcentaje sin hora válida.

### Q3

- pedidos y días con ingreso en cierre;
- promedio diario de cierre;
- pedidos y días con ingreso en resto;
- promedio diario del resto;
- delta entre promedios;
- participación FES/Saldo;
- día pico de unidades y su participación.

La lectura ejecutiva indica explícitamente que Q3 compara el mes completo, incluso cuando se usa el filtro `Momento del mes` para explorar los gráficos.

## 7. Calidad visual

Comprobar en pantalla:

- etiquetas legibles;
- narrativa sin corte;
- títulos completos;
- leyenda visible;
- línea promedio distinguible;
- un solo gráfico mensual visible;
- sin superposiciones;
- filtro Zona con opciones Santiago y Regiones;
- páginas 00, 01 y 01.1 sin regresiones.

## Evidencia obligatoria

Crear:

```text
Docs/AUDITORIA_LIVE/runs/<timestamp>_lienzo_02_cierre_real/
```

Archivos mínimos:

```text
00_git.txt
01_refresh_1.txt
02_refresh_2.txt
03_tracking_vs_master.csv
04_mes_comparacion.csv
05_zona_reconciliacion.csv
06_cobertura_lineas_unidades.csv
07_excepciones_detalle.csv
08_botones_click_real.csv
09_filtros_antes_despues.csv
10_q1.csv
11_q2.csv
12_q3.csv
13_calidad_visual.txt
14_regresiones.txt
15_incoherencias.csv
RESULTADO.md
manifest.json
```

`RESULTADO.md` debe concluir explícitamente si los seis filtros funcionan, si los tres botones fueron pulsados realmente y si existe alguna pérdida de cobertura en líneas/unidades.

Commit permitido:

```text
audit(lienzo-02): cerrar auditoria funcional completa
```

Versionar solamente la carpeta de evidencia.
