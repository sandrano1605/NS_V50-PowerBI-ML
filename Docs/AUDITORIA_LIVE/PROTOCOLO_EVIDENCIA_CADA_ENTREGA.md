# Protocolo obligatorio de evidencia por entrega

Este protocolo aplica a todas las entregas ejecutadas por el LLM local.

## Principio

El LLM local no valida por inspección superficial. Debe probar, reconciliar, diagnosticar y publicar evidencia en cada entrega.

Una entrega se considera incompleta cuando falta cualquiera de estos elementos:

- SHA local y remoto;
- refresh real;
- pruebas de negocio;
- reconciliación de métricas;
- inventario de archivos modificados;
- diagnóstico de incoherencias;
- estado final VERDE, AMARILLO o ROJO;
- evidencia versionada.

## Ciclo obligatorio

1. Recuperar el SHA indicado.
2. Confirmar repo limpio.
3. Abrir el proyecto.
4. Ejecutar refresh completo.
5. Probar cada componente de la entrega.
6. Reconciliar cada total contra su fuente.
7. Probar filtros e interacciones.
8. Ejecutar smoke test visual.
9. Comparar páginas o funciones no modificadas para detectar regresiones.
10. Diagnosticar toda diferencia.
11. Crear carpeta de evidencia con timestamp.
12. Restaurar normalizaciones no solicitadas.
13. Versionar solo evidencia.
14. Entregar a ChatGPT el SHA de evidencia y el dictamen.

## Diagnóstico mínimo

Cada incoherencia debe registrar:

- identificador;
- fecha y hora;
- componente;
- resultado esperado;
- resultado real;
- diferencia absoluta;
- diferencia porcentual;
- filtros activos;
- tablas/medidas/visuales afectados;
- evidencia reproducible;
- causa raíz demostrada o hipótesis;
- nivel de confianza;
- acción requerida de ChatGPT;
- estado `ABIERTO`, `EXPLICADO` o `BLOQUEANTE`.

## Clasificación

### VERDE

- prueba ejecutada;
- resultado reconciliado;
- evidencia disponible;
- sin diferencias no explicadas;
- sin regresiones.

### AMARILLO

- función principal correcta;
- limitación documentada de cobertura, calidad o interpretación;
- no altera el total principal;
- requiere aceptación de ChatGPT.

### ROJO

- refresh falla;
- visual o consulta rota;
- pregunta de negocio sin respuesta;
- filtros no funcionan;
- total no reconcilia;
- diferencia no explicada;
- regresión detectada;
- evidencia insuficiente.

## Reglas de detención

El LLM local debe detenerse y no corregir cuando:

- existe un ROJO;
- un total no reconcilia;
- una relación parece incorrecta;
- una medida cambia el universo sin explicación;
- Power BI normaliza archivos fuera del alcance;
- una corrección requeriría modificar modelo, reporte o reglas de negocio.

Debe informar el error exacto y esperar la corrección de ChatGPT.

## Evidencia mínima común

Toda carpeta de ejecución debe contener:

```text
00_git_before.txt
01_refresh.txt
02_pruebas.csv
03_reconciliacion.csv
04_filtros_interacciones.csv
05_smoke_test.txt
06_incoherencias.csv
07_archivos_modificados.txt
RESULTADO.md
manifest.json
```

Los proyectos específicos pueden exigir archivos adicionales.

## Regla de publicación

El LLM local no puede publicar cambios funcionales. Solo puede publicar evidencia dentro de `Docs/AUDITORIA_LIVE/runs/`.

Antes del commit debe revisar:

```powershell
git status --short
git diff --name-only
```

Cualquier cambio fuera de la carpeta de evidencia debe restaurarse, salvo autorización expresa de ChatGPT.

## Resultado esperado de cada mensaje del LLM

El resumen final debe indicar:

```text
RAMA
SHA LOCAL
SHA REMOTO
REFRESH
PRUEBAS EJECUTADAS
PREGUNTAS RESPONDIDAS
RECONCILIACIONES
INCOHERENCIAS
REGRESIONES
ARCHIVOS DE EVIDENCIA
COMMIT DE EVIDENCIA
DICTAMEN FINAL
```

No se aceptan conclusiones sin datos, archivos o consultas reproducibles.