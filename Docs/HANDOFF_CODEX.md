# HANDOFF CODEX — Ciclo UX-2: cola diaria realmente operativa

## Motivo
UX-1 validó correctamente las tablas, pero no construyó el lienzo en el PBIP y los 37 pedidos quedaron en una única categoría crítica. El commit de validación solo agregó archivos bajo `validation/`; no modificó `NS.Report`.

UX-2 separa:
- gravedad absoluta del pedido;
- orden relativo de intervención diaria.

## Nuevas tablas
- `Config_Niveles_Intervencion`: reglas de severidad absoluta.
- `ML_Pedidos_Pendientes_Intervencion`: score, exceso SLA, severidad y motivo principal.
- `Config_Tramos_Intervencion_Diaria`: Top 5, siguientes 5, siguientes 10 y resto.
- `ML_Cola_Intervencion_Diaria`: fuente definitiva del lienzo operativo.

## Regla diaria
La cola se ordena por:
1. score de intervención descendente;
2. exceso SLA descendente;
3. días en el hito descendente;
4. valor del pedido descendente;
5. número de pedido.

Después se asignan tramos:
- Rank 1–5: `P1 · INTERVENIR`.
- Rank 6–10: `P2 · REVISAR`.
- Rank 11–20: `P3 · PLAN 24H`.
- Rank 21 en adelante: `P4 · MONITOREAR`.

La severidad absoluta se conserva por separado en `PRIORIDAD_ABSOLUTA`, `SEVERIDAD_SLA` y `ESTADO_SLA_OPERATIVO`.

## Validación semántica
1. Abrir `NS.pbip` y ejecutar Actualizar todo.
2. Confirmar:
   - TMDL sin errores;
   - Power Query sin errores;
   - Python.Execute sin errores;
   - 42 tablas cargadas;
   - 40 relaciones activas.
3. `ML_Cola_Intervencion_Diaria` debe tener la misma cantidad de filas que `Resultado[ES_PENDIENTE]=TRUE()`.
4. Una fila por `PED_NUMERO_PEDIDO`.
5. `RANK_DIARIO` continuo de 1 a N, sin duplicados.
6. Para N=37 la distribución esperada es exactamente:
   - P1 = 5;
   - P2 = 5;
   - P3 = 10;
   - P4 = 17.
7. Para otro N usar:
   - P1 = mínimo entre 5 y N;
   - P2 = máximo entre mínimo(N,10)-5 y 0;
   - P3 = máximo entre mínimo(N,20)-10 y 0;
   - P4 = máximo entre N-20 y 0.
8. `SCORE_INTERVENCION` debe estar entre 0 y 100.
9. `EXCESO_SLA_DH` debe ser igual a `max(DIAS_ACTUALES_DH-5,0)`.
10. No deben existir valores vacíos en nivel, plazo, foco, motivo ni acción.
11. Recalcular manualmente los primeros 10 pedidos.

## Construcción obligatoria del reporte
Leer `Docs/LIENZO_COLA_INTERVENCION_V2.md`.

Crear o reemplazar la página:

`05 Cola diaria · Intervención`

Usar `ML_Cola_Intervencion_Diaria` como fuente principal.

### Evidencia obligatoria
No marcar APROBADO salvo que se cumplan todos estos puntos:

1. El commit final debe modificar archivos reales bajo:
   - `NS.Report/definition/pages/`;
   - al menos un `page.json`;
   - al menos un archivo `visual.json`.
2. Ejecutar y guardar:
   - `git diff --name-only <SHA_DESARROLLO>..HEAD`.
3. El listado debe mostrar al menos un archivo de `NS.Report/definition/pages/`.
4. Guardar una captura real y no vacía:
   - `validation/latest/capturas/cola_intervencion_v2.png`.
5. La captura debe mostrar:
   - logo ARTEL;
   - cinco tarjetas;
   - segmentadores;
   - tabla con pedidos reales;
   - barras por foco y severidad.
6. El Top 10 del informe debe contener los diez números de pedido reales. No se aceptan guiones, valores ficticios ni filas vacías.
7. Validar que al seleccionar una fila o filtro cambien las tarjetas y gráficos relacionados.

## Diseño
- Logo: `Assets/logo_artel.svg`.
- Fuente principal: `ML_Cola_Intervencion_Diaria`.
- Colores y orden según `Docs/LIENZO_COLA_INTERVENCION_V2.md`.
- Mostrar simultáneamente:
  - `NIVEL_COLA` como turno diario;
  - `PRIORIDAD_ABSOLUTA` como gravedad.

## Restricciones
- No modificar `Resultado`.
- No reentrenar modelos.
- No cambiar relaciones existentes.
- No hacer merge a `main`.
- No afirmar que la página fue creada si no existen cambios en `NS.Report`.

## Entrega
Crear:
- `validation/latest/RESULTADOS_UX_2.md`.
- `validation/latest/metricas_UX_2.json`.
- `validation/latest/errores_UX_2.txt`.
- `validation/latest/capturas/cola_intervencion_v2.png`.
- `validation/latest/diff_reporte_UX_2.txt`.

El informe debe incluir:
- SHA validado;
- tablas y relaciones;
- total de pendientes;
- distribución P1/P2/P3/P4;
- distribución de severidad absoluta;
- distribución por foco;
- valor Top 10;
- primeros 10 pedidos con todos sus campos operativos;
- recálculo manual del score;
- archivos reales del reporte modificados;
- estado de cada visual;
- errores;
- veredicto.

## Criterio de aprobación
- 42 tablas cargadas.
- Cola discriminante y reconciliada.
- Página PBIP realmente modificada.
- Captura real disponible.
- Top 10 completo.
- Filtros funcionando.
- Sin errores de actualización.

Cualquier ausencia de cambios en `NS.Report`, captura o Top 10 real obliga a marcar `BLOQUEADO`.
