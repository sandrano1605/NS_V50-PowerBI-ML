# Lienzo V2 — Cola diaria de intervención

## Problema corregido
En UX-1 los 37 pedidos pendientes quedaron en categoría crítica porque todos superaban el SLA de 5 DH. Eso describe correctamente el estado, pero no ayuda a decidir el orden diario.

UX-2 separa dos lecturas:

1. **Severidad absoluta:** estado SLA, exceso de días, score y prioridad absoluta.
2. **Prioridad relativa diaria:** orden 1 a N y tramos Top 5, siguientes 5, siguientes 10 y resto.

## Fuente principal
Usar exclusivamente `ML_Cola_Intervencion_Diaria` para la tabla operacional.

## Encabezado
- Página: `05 Cola diaria · Intervención`.
- Logo ARTEL: `Assets/logo_artel.svg` arriba a la derecha.
- Título: **Pedidos pendientes · cola diaria de intervención**.
- Subtítulo: **Qué trabajar primero, dónde actuar y cuál es la causa principal**.
- Nota pequeña: **Todos pueden estar fuera de SLA; la cola relativa define el orden de trabajo del día.**

## Tarjetas
1. `Cola Diaria Total`.
2. `Cola Intervenir Hoy`.
3. `Cola Revisar Hoy`.
4. `Valor Top 10`.
5. `Exceso SLA Promedio` desde `ML_Pedidos_Pendientes_Intervencion`.

## Segmentadores
- `NIVEL_COLA`.
- `PRIORIDAD_ABSOLUTA`.
- `SEVERIDAD_SLA`.
- `FOCO_INTERVENCION`.
- `HITO_ACTUAL`.
- `VENDEDOR`.
- `PED_REGION`.
- `PED_CANAL`.

## Tabla principal
Orden: `RANK_DIARIO` ascendente.

Columnas visibles:
1. `RANK_DIARIO` — `#`.
2. `NIVEL_COLA` — `Cola diaria`.
3. `PLAZO_ACCION` — `Plazo`.
4. `PRIORIDAD_ABSOLUTA` — `Severidad`.
5. `PED_NUMERO_PEDIDO` — `Pedido`.
6. `CLIENTE` — `Cliente`.
7. `HITO_ACTUAL` — `Hito actual`.
8. `FOCO_INTERVENCION` — `Dónde actuar`.
9. `DIAS_ACTUALES_DH` — `DH actuales`.
10. `EXCESO_SLA_DH` — `Exceso SLA`.
11. `DIAS_EN_ESTADO_DH` — `DH en hito`.
12. `SCORE_INTERVENCION` — `Score`.
13. `PROB_ML_ATRASO_NORM` — `Riesgo ML`.
14. `RIESGO_HISTORICO_MAX` — `Riesgo histórico`.
15. `VALOR_NETO` — `Valor`.
16. `MOTIVO_PRINCIPAL_INTERVENCION` — `Motivo principal`.
17. `ACCION_DIARIA` — `Acción`.

## Formato
- `P1 · INTERVENIR`: rojo oscuro, texto blanco.
- `P2 · REVISAR`: naranja, texto blanco.
- `P3 · PLAN 24H`: amarillo, texto oscuro.
- `P4 · MONITOREAR`: verde suave, texto oscuro.
- Barra de datos para `SCORE_INTERVENCION`.
- Iconos por `SEVERIDAD_SLA`.
- `VALOR_NETO` como CLP sin decimales.
- Riesgos como porcentaje.

## Visuales secundarios
- Barras por `FOCO_INTERVENCION`, orden descendente.
- Barras por `SEVERIDAD_SLA` para mostrar el estado absoluto.
- Matriz pequeña con `Config_Criterios_Pendientes`.
- Matriz pequeña con `Config_Tramos_Intervencion_Diaria`.

## Tooltip
Mostrar:
- `PUNTOS_EXCESO_SLA`.
- `PUNTOS_RIESGO_ML`.
- `PUNTOS_PERMANENCIA`.
- `PUNTOS_VALOR`.
- `PUNTOS_HISTORICO`.
- `PUNTOS_FIN_MES`.
- `SCORE_INTERVENCION`.
- `CRITERIOS_ACTIVOS`.
- `HIST_SOPORTE_MIN`.

## Regla de interpretación
- `PRIORIDAD_ABSOLUTA` explica la gravedad.
- `NIVEL_COLA` define el turno diario.
- El Top 5 debe trabajarse primero, aunque existan más pedidos con gravedad crítica.
- La predicción de días continúa como referencial y no ordena la cola.
