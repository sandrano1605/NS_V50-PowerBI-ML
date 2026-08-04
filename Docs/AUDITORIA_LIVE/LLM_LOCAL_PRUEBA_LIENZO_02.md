# LLM local · Prueba canónica del lienzo 02

## Rol

El lienzo y el modelo ya fueron implementados por ChatGPT.

El LLM local solo debe:

- recuperar la rama;
- abrir el PBIP;
- ejecutar refresh completo;
- probar cada visual, filtro y pregunta de negocio;
- reconciliar las métricas;
- diagnosticar incoherencias;
- publicar únicamente evidencia.

No debe modificar Power Query, TMDL, DAX, Python, relaciones, JSON ni visuales.

## Rama

```text
work/ns-lienzo-02-ingreso-pedidos
```

Recuperar siempre el HEAD remoto vigente:

```powershell
git fetch origin
git switch work/ns-lienzo-02-ingreso-pedidos
git pull --ff-only origin work/ns-lienzo-02-ingreso-pedidos
git status --short
git rev-parse HEAD
git rev-parse origin/work/ns-lienzo-02-ingreso-pedidos
```

SHA local y remoto deben coincidir.

## Documentos obligatorios

Leer completamente:

```text
Docs/AUDITORIA_LIVE/REQ011_LIENZO_02_INGRESO_PEDIDOS.md
Docs/AUDITORIA_LIVE/LLM_LOCAL_IMPLEMENTA_LIENZO_02.md
Docs/AUDITORIA_LIVE/PROTOCOLO_EVIDENCIA_CADA_ENTREGA.md
Docs/AUDITORIA_LIVE/latest/lienzo_02_build_validation.json
```

El nombre histórico `LLM_LOCAL_IMPLEMENTA...` se conserva por trazabilidad, pero su contenido vigente limita al LLM a pruebas y diagnóstico.

## Página esperada

```text
ID: df1cb253a6314642a469
Nombre: 02 Ingreso de Pedidos
Tamaño: 1600 × 940
Estado: visible
```

## Filtros esperados

La franja debe mantener el estilo del lienzo 00.

Campos exactos:

```text
MES - AÑO       = Dim_Periodo_3M[Etiqueta]
FLUJO           = Fact_Tracking[CLASIFICACION]
ZONA            = Fact_Tracking[ZONA]
RESPONSABLE     = Dim_Responsable[RESPONSABLE_CODIGO]
CANAL           = Dim_Canal[CANAL]
MOMENTO DEL MES = Dim_Fecha[Momento_Mes]
```

El filtro mensual es una copia del slicer sincronizado del lienzo 00 y debe responder igual.

## Visuales esperados

```text
1. Matriz: día de semana × pedidos, líneas y unidades.
2. Columnas 100% apiladas: hasta 14:30, después de 14:30 y sin hora válida.
3. Combo: pedidos por día del mes + promedio.
4. Combo: líneas por día del mes + promedio.
5. Combo: unidades por día del mes + promedio.
```

Los tres gráficos mensuales deben apilar las barras por clasificación de flujo.

## Preguntas que deben quedar respondidas

### Q1

¿Qué día de la semana concentra más pedidos, líneas y unidades?

### Q2

¿Qué proporción queda disponible para Logística hasta las 14:30, después de las 14:30 o sin hora válida, por día de semana?

### Q3

¿La carga crece al final del mes para pedidos, líneas y unidades, y qué flujo explica el crecimiento?

No basta con que el visual tenga datos. `RESULTADO.md` debe responder cada pregunta con cifras y diagnóstico.

## Barreras obligatorias

- refresh completo sin errores;
- seis filtros funcionales;
- filtro mensual cambia todos los visuales;
- siete días ordenados lunes a domingo;
- tramos horarios reconcilian con el total;
- `00:00:00` queda en `Sin hora válida`;
- día del mes ordenado 1–31;
- barras por flujo reconcilian con el total;
- línea promedio visible en los tres gráficos;
- líneas y unidades reconcilian con la tabla de detalle;
- páginas 00, 01 y 01.1 sin regresiones;
- ningún visual Python, SVG DAX o Image URL;
- sin superposiciones, textos cortados o campos rotos.

## Evidencia

Crear una carpeta nueva:

```text
Docs/AUDITORIA_LIVE/runs/<timestamp>_lienzo_02_ingreso/
```

Debe contener todos los archivos exigidos por:

```text
Docs/AUDITORIA_LIVE/LLM_LOCAL_IMPLEMENTA_LIENZO_02.md
Docs/AUDITORIA_LIVE/PROTOCOLO_EVIDENCIA_CADA_ENTREGA.md
```

El archivo `15_incoherencias.csv` es obligatorio, incluso si no se detectan problemas.

## Diagnóstico

Toda incoherencia debe indicar:

- esperado;
- real;
- diferencia absoluta y porcentual;
- filtros activos;
- tabla, medida o visual afectado;
- causa raíz demostrada o hipótesis;
- evidencia faltante;
- impacto;
- acción requerida de ChatGPT.

No corregir. Detenerse y entregar evidencia.

## Publicación permitida

Solo versionar:

```text
Docs/AUDITORIA_LIVE/runs/<timestamp>_lienzo_02_ingreso/
```

Commit permitido:

```text
audit(lienzo-02): probar y diagnosticar ingreso de pedidos
```

Dictamen final obligatorio: `VERDE`, `AMARILLO` o `ROJO`.