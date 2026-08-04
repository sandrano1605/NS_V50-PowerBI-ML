# LLM local · Prueba, evidencia y diagnóstico del lienzo 02

## Rol estricto

ChatGPT implementa el modelo y el lienzo. El LLM local **no diseña, no corrige y no completa** la solución.

Su función en cada entrega es exclusivamente:

1. recuperar el SHA indicado por ChatGPT;
2. abrir el proyecto;
3. ejecutar refresh completo;
4. probar cada elemento y cada pregunta de negocio;
5. reconciliar resultados contra las fuentes del modelo;
6. generar evidencia reproducible;
7. detectar y diagnosticar cualquier incoherencia;
8. detenerse sin modificar el proyecto cuando encuentre una diferencia no explicada.

Una entrega sin evidencia no se considera validada.

## Recuperación

```powershell
git fetch origin
git switch work/ns-lienzo-02-ingreso-pedidos
git pull --ff-only origin work/ns-lienzo-02-ingreso-pedidos
git status --short
git rev-parse HEAD
```

Registrar el SHA local y remoto en `00_git_before.txt`. Ambos deben coincidir.

Leer completamente:

```text
Docs/AUDITORIA_LIVE/REQ011_LIENZO_02_INGRESO_PEDIDOS.md
Docs/AUDITORIA_LIVE/latest/lienzo_02_visual_matrix.csv
Docs/AUDITORIA_LIVE/PROTOCOLO_EVIDENCIA_CADA_ENTREGA.md
```

## Prohibiciones

El LLM local no puede:

- editar Power Query, TMDL, DAX, Python, relaciones o JSON del reporte;
- crear, eliminar o reemplazar visuales;
- cambiar filtros, títulos, tooltips o navegación;
- modificar páginas 00, 01, 01.1 o 02;
- cambiar reglas SLA, FES, SALDO, cierre o ventana temporal;
- crear medidas, columnas, tablas o parámetros;
- ocultar errores o reemplazar datos faltantes por valores inventados;
- guardar una normalización de Power BI como si fuera una corrección funcional;
- declarar VERDE basándose solamente en que el archivo abre.

Si una prueba falla, debe registrar el error exacto, el alcance, la causa probable y la evidencia. Después debe detenerse.

## Página bajo prueba

```text
ID: df1cb253a6314642a469
Nombre esperado: 02 Ingreso de Pedidos
Tamaño esperado: 1600 × 940
```

La página debe estar visible únicamente cuando todos los controles estén verdes.

## Filtros obligatorios

Comparar la franja de filtros con el lienzo 00. Deben mantener el mismo lenguaje visual, altura, alineación y comportamiento.

Validar como mínimo:

- mes/período mediante `Dim_Fecha[AnioMes]`;
- flujo mediante `Fact_Tracking[CLASIFICACION]` o el filtro reutilizado equivalente;
- zona;
- responsable;
- canal;
- momento del mes.

Para el filtro mensual:

1. seleccionar un mes;
2. confirmar que los cinco visuales cambian;
3. comparar `[IN Pedidos]` con el distinct count de pedidos del mismo mes;
4. confirmar que líneas y unidades responden al mismo conjunto de pedidos;
5. quitar el filtro y comprobar que vuelve el total de la ventana vigente;
6. comprobar interacción cruzada sin filtros bloqueados o desconectados.

## Pruebas de las preguntas de negocio

### Q1 · Día de la semana

Pregunta respondida:

> ¿Qué día de la semana concentra más pedidos, líneas y unidades?

Validar:

- orden lunes a domingo;
- siete categorías sin duplicados;
- pedidos, líneas y unidades visibles;
- suma de pedidos por día = total del contexto;
- suma de líneas por día = total de líneas del contexto;
- suma de unidades por día = total de unidades del contexto;
- identificar y registrar el día máximo de cada métrica;
- diagnosticar diferencias entre el día de mayor cantidad de pedidos y el de mayor carga física.

### Q2 · Disponibilidad para Logística a las 14:30

Pregunta respondida:

> ¿Qué proporción queda disponible hasta las 14:30, después de las 14:30 o sin hora válida, por día de la semana?

Validar:

- categorías exactas: `Hasta 14:30`, `Después de 14:30`, `Sin hora válida`;
- no clasificar `00:00:00` como hora válida;
- hasta + después + sin hora = total de pedidos por día;
- tooltip con pedidos, líneas y unidades;
- registrar porcentaje antes/después por día;
- identificar el día con mayor proporción posterior al corte;
- separar hallazgo operacional de problema de calidad horaria.

### Q3 · Tendencia por día del mes

Preguntas respondidas:

> ¿Los pedidos aumentan hacia el final del mes?
>
> ¿Las líneas aumentan hacia el final del mes?
>
> ¿Las unidades aumentan hacia el final del mes?
>
> ¿Qué flujo explica el crecimiento?

Validar en los tres gráficos:

- eje 1–31 ordenado;
- misma selección mensual y filtros;
- barras apiladas por `NORMAL`, `FES`, `FES + SALDO`, `SALDO` cuando existan;
- línea de promedio visible;
- suma por día = total del contexto;
- suma de flujos = total de cada barra;
- filtro `Momento_Mes` responde correctamente;
- últimos siete días hábiles se identifican con `Dim_Fecha[Momento_Mes]`, no con un día calendario fijo;
- registrar promedio de inicio, resto y cierre;
- diagnosticar si el cierre supera el resto del mes;
- identificar cuánto del aumento corresponde a FES/SALDO y cuánto a flujo normal.

## Diagnóstico obligatorio de incoherencias

Ante cualquier diferencia, el informe debe responder:

1. **Qué debería ocurrir.**
2. **Qué ocurrió realmente.**
3. **Cuál es la diferencia absoluta y porcentual.**
4. **En qué tabla, medida, filtro o visual aparece.**
5. **Qué filtros estaban activos.**
6. **Si la diferencia es de datos, modelo, relación, medida, visual o calidad de origen.**
7. **Cuál es la causa raíz demostrada o la hipótesis más probable.**
8. **Qué evidencia falta para demostrarla.**
9. **Qué elementos quedan afectados.**
10. **Qué debe corregir ChatGPT.**

No usar expresiones vagas como “parece correcto”, “probablemente funciona” o “se ve bien”.

## Estados

- **VERDE:** prueba ejecutada, reconciliada y con evidencia; diferencia igual a cero o explicada formalmente.
- **AMARILLO:** funciona, pero existe una limitación de calidad, cobertura o interpretación que no altera la reconciliación principal.
- **ROJO:** error de refresh, referencia rota, visual vacío inesperado, total que no reconcilia, filtro desconectado, pregunta no respondida o diferencia sin explicación.

La entrega general solo puede ser VERDE si todas las pruebas obligatorias están verdes. Un ROJO bloquea publicación. Un AMARILLO debe quedar explícitamente aceptado por ChatGPT.

## Evidencia obligatoria por entrega

Crear una carpeta nueva en cada ejecución:

```text
Docs/AUDITORIA_LIVE/runs/<timestamp>_lienzo_02_ingreso/
├── 00_git_before.txt
├── 01_refresh.txt
├── 02_inventario_filtros.csv
├── 03_calidad_hora.csv
├── 04_medidas_y_campos.csv
├── 05_reconciliacion_dia_semana.csv
├── 06_reconciliacion_hora_1430.csv
├── 07_reconciliacion_pedidos_dia_mes.csv
├── 08_reconciliacion_lineas_dia_mes.csv
├── 09_reconciliacion_unidades_dia_mes.csv
├── 10_analisis_inicio_resto_cierre.csv
├── 11_descomposicion_flujo.csv
├── 12_cobertura_lineas_unidades.csv
├── 13_visual_inventory.csv
├── 14_smoke_test_paginas.txt
├── 15_incoherencias.csv
├── RESULTADO.md
└── manifest.json
```

`15_incoherencias.csv` debe existir incluso cuando no haya problemas. En ese caso debe contener una fila con estado `SIN_INCOHERENCIAS_DETECTADAS` y el alcance probado.

## Estructura de RESULTADO.md

Debe incluir:

1. SHA local y remoto.
2. Estado del refresh.
3. Resultado de cada pregunta de negocio.
4. Totales y reconciliaciones.
5. Hallazgos operacionales.
6. Hallazgos de calidad de datos.
7. Incoherencias detectadas y causa raíz.
8. Pruebas visuales y filtros.
9. Regresiones en páginas 00, 01 y 01.1.
10. Dictamen final VERDE/AMARILLO/ROJO.
11. Lista exacta de archivos modificados por Power BI Desktop.

## Smoke test visual

Comprobar:

- página 02 visible solo cuando corresponde;
- título y subtítulo correctos;
- filtros alineados como en página 00;
- ninguna superposición o corte de texto;
- títulos completos y legibles;
- tooltips correctos;
- línea promedio presente en los tres gráficos;
- leyendas consistentes;
- no existe hover técnico, SVG DAX, Image URL ni visual Python;
- páginas 00, 01 y 01.1 sin regresión.

## Publicación de evidencia

El LLM local solo puede versionar archivos dentro de:

```text
Docs/AUDITORIA_LIVE/runs/<timestamp>_lienzo_02_ingreso/
```

Antes del commit debe restaurar cualquier normalización no solicitada:

```powershell
git restore NS.Report NS.SemanticModel
```

Solo se omite la restauración cuando ChatGPT indique expresamente que una normalización concreta forma parte de la entrega.

Commit permitido:

```text
audit(lienzo-02): probar y diagnosticar ingreso de pedidos
```

No corregir los hallazgos. Entregar la evidencia a ChatGPT para la siguiente iteración.