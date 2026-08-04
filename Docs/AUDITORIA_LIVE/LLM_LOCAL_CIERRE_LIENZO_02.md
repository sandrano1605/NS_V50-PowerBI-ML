# LLM local · Cierre definitivo lienzo 02

## Rol

La solución ya está corregida. No modificar DAX, Power Query, TMDL, JSON, medidas, visuales, bookmarks ni botones.

Ejecutar únicamente: recuperar rama, refrescar, probar, reconciliar, diagnosticar y publicar evidencia.

## Controles obligatorios

### Modelo

1. `Fact_Tracking` debe tener una fila por `PED_NUMERO_PEDIDO`.
2. Informar filas, pedidos distintos y duplicados de `Fact_Tracking`.
3. Comparar pedidos de `Fact_Tracking` contra `Fact_Pedidos_Auditoria` con `EXCEPT` en ambos sentidos.
4. Si existe diferencia, listar los pedidos y determinar si corresponde a cambio de la fuente durante el refresh. Repetir un segundo refresh antes de clasificarlo como defecto.
5. No declarar VERDE mientras exista una diferencia no explicada.

### Q1

Reconciliar día líder y valor para pedidos, líneas y unidades.

### Q2

Publicar cuatro cifras:

- cobertura de hora válida = `(Hasta 14:30 + Después 14:30) / Total`;
- porcentaje hasta 14:30 sobre pedidos con hora válida;
- porcentaje después de 14:30 sobre pedidos con hora válida;
- porcentaje sin hora válida sobre el total.

La lectura ejecutiva y la consulta independiente deben coincidir.

### Q3

No comparar totales de períodos con distinta cantidad de días.

Publicar:

- cantidad de días con ingreso en cierre;
- pedidos de cierre;
- promedio diario de cierre;
- cantidad de días con ingreso en resto;
- pedidos del resto;
- promedio diario del resto;
- delta entre promedios diarios;
- participación FES/Saldo en cierre;
- día pico de unidades y participación sobre las unidades del período.

### Botones y filtros

La prueba debe ser real en Power BI Desktop, no solo estructural:

1. Seleccionar mes, canal distinto de 43/45, flujo, zona, responsable y momento del mes.
2. Pulsar los tres botones.
3. Confirmar exactamente un gráfico visible por clic.
4. Confirmar que ningún filtro cambia.
5. Cambiar mes y canal, repetir.
6. Cerrar, reabrir y repetir.

## Evidencia

Crear:

```text
Docs/AUDITORIA_LIVE/runs/<timestamp>_lienzo_02_cierre_definitivo/
```

Archivos mínimos:

```text
00_git.txt
01_refresh_1.txt
02_refresh_2.txt
03_tracking_vs_master.csv
04_q1_dia_semana.csv
05_q2_cobertura_horaria.csv
06_q3_promedios_diarios.csv
07_q3_flujo_y_pico_unidades.csv
08_botones_prueba_real.csv
09_filtros_persistencia.csv
10_calidad_visual.txt
11_regresiones.txt
12_incoherencias.csv
RESULTADO.md
manifest.json
```

`RESULTADO.md` debe responder Q1, Q2 y Q3 con cifras y explicar cualquier diferencia entre Tracking y master.

Commit permitido:

```text
audit(lienzo-02): validar cierre definitivo
```

Versionar solamente la carpeta de evidencia.
