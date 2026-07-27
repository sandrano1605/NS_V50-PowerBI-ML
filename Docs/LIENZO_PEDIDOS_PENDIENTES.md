# Lienzo operativo — Pedidos pendientes priorizados

## Propósito
Transformar la página ML en una mesa de control diaria: identificar qué pedido intervenir, por qué, en qué proceso y con qué acción.

## Encabezado
- Logo oficial ARTEL en la esquina superior derecha.
- Título: **Pedidos pendientes · priorización operativa**.
- Subtítulo: **SLA actual + riesgo ML + permanencia + valor + patrones históricos**.
- Nota metodológica pequeña: **La predicción de días es referencial y no participa en la prioridad hasta superar el baseline.**

## Fila de indicadores
1. `Pendientes Total`.
2. `Pendientes Intervenir Hoy`.
3. `Pendientes Críticos`.
4. `Pendientes Fuera SLA`.
5. `Valor Crítico y Alto`.

## Segmentadores
- `PRIORIDAD_OPERATIVA`.
- `FOCO_INTERVENCION`.
- `HITO_ACTUAL`.
- `VENDEDOR`.
- `PED_REGION`.
- `PED_CANAL`.

## Tabla principal
Orden predeterminado: `RANK_PRIORIDAD` ascendente.

Columnas visibles, en este orden:
1. `RANK_PRIORIDAD` — encabezado `#`.
2. `PRIORIDAD_OPERATIVA` — encabezado `Prioridad`.
3. `ESTADO_ACCION` — encabezado `Qué hacer`.
4. `PED_NUMERO_PEDIDO` — encabezado `Pedido`.
5. `CLIENTE` — encabezado `Cliente`.
6. `HITO_ACTUAL` — encabezado `Hito actual`.
7. `DIAS_ACTUALES_DH` — encabezado `DH actuales`.
8. `DIAS_EN_ESTADO_DH` — encabezado `DH en hito`.
9. `PROB_ML_ATRASO_NORM` — encabezado `Riesgo ML`.
10. `RIESGO_HISTORICO_MAX` — encabezado `Riesgo histórico`.
11. `VALOR_NETO` — encabezado `Valor`.
12. `CRITERIOS_ACTIVOS` — encabezado `Por qué prioriza`.
13. `FOCO_INTERVENCION` — encabezado `Dónde actuar`.
14. `ACCION_OPERATIVA` — encabezado `Acción recomendada`.

## Formato condicional
- `CRÍTICA`: fondo rojo oscuro, texto blanco.
- `ALTA`: fondo naranja, texto blanco.
- `MEDIA`: fondo amarillo suave, texto oscuro.
- `BAJA`: fondo verde suave, texto oscuro.
- Barra de datos para `PRIORIDAD_OPERATIVA_SCORE`.
- Icono rojo cuando `DIAS_ACTUALES_DH > 5`.
- Icono ámbar cuando `DIAS_EN_ESTADO_DH >= 2`.
- Formato porcentaje para probabilidades.
- Formato CLP sin decimales para valor.

## Tooltip de criterios
Mostrar:
- `PUNTOS_SLA`.
- `PUNTOS_RIESGO_ML`.
- `PUNTOS_PERMANENCIA`.
- `PUNTOS_VALOR`.
- `PUNTOS_HISTORICO`.
- `PUNTOS_FIN_MES`.
- `PRIORIDAD_OPERATIVA_SCORE`.
- `FACTOR_PRINCIPAL`.
- `FACTOR_HISTORICO`.
- `HIST_SOPORTE_MIN`.

## Tabla de criterios
Usar `Config_Criterios_Pendientes` con:
- `CRITERIO`.
- `REGLA`.
- `PUNTOS_MAX`.
- `LECTURA_OPERATIVA`.
- `ACCION_ESPERADA`.

Esta tabla debe quedar en un panel lateral o en una página tooltip/metodología; no debe competir con la cola operacional.

## Visuales secundarios
- Barras: pedidos por `FOCO_INTERVENCION`, ordenados por cantidad.
- Barras apiladas: pedidos por `HITO_ACTUAL` y `PRIORIDAD_OPERATIVA`.
- Tarjeta pequeña: `Riesgo ML Promedio Pendientes`.

## Regla de uso
La tabla es una herramienta de priorización asistida. El score no reemplaza la revisión operacional y no debe utilizar la predicción de días para decisiones automáticas mientras la regresión no supere al baseline.
