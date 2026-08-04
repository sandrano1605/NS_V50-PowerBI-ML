# Prueba final · Dim_Cliente y filas en blanco del lienzo 01

## Rol

El LLM local **solo prueba, reconcilia y publica evidencia**. No modifica el modelo ni los visuales.

## Rama y base mínima

```text
Rama: work/ns-lienzo-02-ingreso-pedidos
Commit funcional mínimo: 2d842e49de0d0e4a860dc3ec6dc0648429d7b60c
```

## Cambio que debe probarse

`Dim_Cliente` ahora parte de `Fact_Pedidos_Auditoria`, la misma master que alimenta `Fact_Tracking`, y se enriquece con:

- `KNA1_SAP` para el nombre del cliente;
- `CLIENTE_VENDEDOR` + `VENDEDOR` para el vendedor vigente;
- clave normalizada solo para los cruces de maestro;
- clave textual original para la relación con los hechos;
- `SIN VENDEDOR ASIGNADO` cuando no existe asignación;
- `SIN CLIENTE IDENTIFICADO` únicamente para códigos nulos o vacíos.

No se modificó la definición de SLA ni se excluyeron pedidos.

## Secuencia obligatoria

1. Recuperar la rama y comprobar que local y remoto apuntan al mismo SHA.
2. Abrir el PBIP en Power BI Desktop.
3. Ejecutar **Actualizar todo** dos veces.
4. Confirmar que no aparece Formula Firewall, error SQL, error M, clave duplicada ni relación inválida.
5. Consultar el modelo después del segundo refresh.
6. Abrir `01 Análisis Fuera SLA` y revisar las tablas 1 y 3.
7. Cerrar Power BI Desktop, reabrir y repetir los controles principales.

## Controles de integridad

Publicar cifras reales para:

```text
Filas Fact_Tracking
Pedidos distintos Fact_Tracking
Códigos distintos no vacíos Fact_Tracking
Filas Dim_Cliente
Códigos distintos Dim_Cliente
Duplicados de CLIENTE_CODIGO en Dim_Cliente
Pedidos sin match con Dim_Cliente
Códigos sin match con Dim_Cliente
Pedidos fuera SLA sin match
Clientes con CLIENTE_NOMBRE vacío
Clientes con VENDEDOR_NOMBRE vacío
Clientes etiquetados SIN VENDEDOR ASIGNADO
Clientes etiquetados SIN CLIENTE IDENTIFICADO
```

Condiciones de aprobación:

```text
Duplicados Dim_Cliente = 0
Pedidos sin match = 0
Códigos sin match = 0
Pedidos fuera SLA sin match = 0
CLIENTE_NOMBRE vacío = 0
VENDEDOR_NOMBRE vacío = 0
```

`SIN VENDEDOR ASIGNADO` puede ser mayor que cero; debe representar ausencia real de asignación y no una relación rota.

## Reconciliación de los 22 pedidos documentados

Usar la lista:

```text
Docs/AUDITORIA_LIVE/runs/20260804_162325_auditoria_dim_cliente/02_lista_pedidos_sin_match.csv
```

Para cada pedido registrar después del refresh:

```text
Pedido
Cliente_FACT
Cliente_DIM
CLIENTE_NOMBRE
VENDEDOR_NOMBRE
Estado_match
```

Los 22 deben tener `Estado_match = OK`. El nombre puede quedar como código cuando KNA1 no tenga descripción. El vendedor puede quedar `SIN VENDEDOR ASIGNADO` si no existe asignación vigente.

## Reconciliación 54 vs 22

No asumir que 54 es subconjunto de 22: matemáticamente no puede serlo bajo la misma cohorte.

Registrar para la fila en blanco original de la tabla 1:

```text
Filtros activos exactos
Rango de fechas efectivo
Cohorte de RE Pedidos contexto
Cantidad de pedidos distintos
Lista de PED_NUMERO_PEDIDO
```

Después del cambio:

```text
Fila cliente en blanco tabla 1 = inexistente
Fila vendedor en blanco tabla 3 = inexistente
```

Cuando existan clientes sin maestro o sin vendedor, deben aparecer respectivamente como código de cliente y `SIN VENDEDOR ASIGNADO`, nunca como blanco.

## Prueba visual

En la tabla 1 validar:

- ningún cliente vacío;
- ningún vendedor vacío;
- los pedidos que antes estaban agrupados en blanco ahora aparecen distribuidos por cliente;
- el total fuera SLA no cambia por esta corrección;
- cliente, vendedor, flujo, meses, recurrencia y pedidos fuera SLA son legibles.

En la tabla 3 validar:

- ningún vendedor vacío;
- `SIN VENDEDOR ASIGNADO` aparece solo cuando corresponde;
- los pedidos y líneas recurrentes se redistribuyen sin alterar el total oficial;
- no hay una fila en blanco de 54 pedidos.

## No regresión

Confirmar que no cambian, salvo nuevos pedidos creados entre refresh:

```text
Pedidos evaluables
Pedidos en SLA
Pedidos fuera SLA
NS
IN Pedidos
```

## Evidencia

Crear:

```text
Docs/AUDITORIA_LIVE/runs/<timestamp>_dim_cliente_cierre/
```

Archivos mínimos:

```text
00_git.txt
01_refresh_1.txt
02_refresh_2.txt
03_integridad_dim_cliente.csv
04_reconciliacion_22_pedidos.csv
05_reconciliacion_54_vs_22.csv
06_tabla_1_clientes.csv
07_tabla_3_vendedores.csv
08_kpis_antes_despues.csv
09_calidad_visual.txt
10_regresiones.txt
11_incoherencias.csv
RESULTADO.md
manifest.json
```

`11_incoherencias.csv` es obligatorio. Si no existen hallazgos, registrar `SIN_INCOHERENCIAS_DETECTADAS`.

## Dictamen

- **VERDE:** todos los controles obligatorios en cero y visuales sin filas en blanco.
- **AMARILLO:** match en cero, pero existen clientes reales sin vendedor y quedan correctamente etiquetados.
- **ROJO:** error de refresh, duplicados, cualquier pedido sin match, fila cliente/vendedor vacía o cambio injustificado del NS.

No realizar correcciones. Ante ROJO, documentar causa, evidencia y detenerse.
