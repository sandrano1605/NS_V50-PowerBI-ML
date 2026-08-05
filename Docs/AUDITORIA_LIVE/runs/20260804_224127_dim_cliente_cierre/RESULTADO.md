# RESULTADO: Cierre Dim_Cliente — ROJO (modelo colgado) (2026-08-04)

**Rama:** work/ns-lienzo-02-ingreso-pedidos
**SHA:** 0ab7efb82bdba82b07611291576f4d4947793e4f
**Dictamen:** 🔴 ROJO — el modelo NO carga tras el commit 2d842e4

## Contexto

Se intentó cerrar el problema de los 54 pedidos sin cliente/vendedor (fila en
blanco de las tablas 1 y 3 del lienzo 01). ChatGPT publicó el commit 2d842e4
"fix(dim-cliente): construir dimensión desde universo oficial de pedidos".

## Síntoma

- Power BI Desktop abrió el proyecto, pero el refresh se **cuelga indefinidamente**.
- Después de ~35 minutos, ninguna consulta DAX responde (Fact_Tracking, Dim_Cliente, etc.).
- msmdsrv usa 1GB+ de memoria y CPU activa sin completar.

## Causa raíz

El commit 2d842e4 cambió el origen M de `Dim_Cliente`:

| Versión | Origen M | Estado |
|---|---|---|
| Antes (1426e00) | `Sql.Database(...)` → ZART_TRACK_DATA_SAP | Funcionaba |
| Después (2d842e4) | `Fact_Pedidos_Auditoria` (tabla del modelo) | **Cuelga** |

El M nuevo (Dim_Cliente.tmdl línea 61) hace:
```m
BasePedidos = Table.SelectColumns(Fact_Pedidos_Auditoria, {...})
```

**Problema**: Dim_Cliente es una **dimensión con relaciones activas** hacia los
hechos (Fact_Tracking, Fact_Pedidos, etc.). Al hacer que su M dependa de
`Fact_Pedidos_Auditoria` (tabla importada), y simultáneamente los hechos
dependen de Dim_Cliente por las relaciones, se genera un **ciclo de dependencia
de evaluación** que Power BI Desktop no resuelve → refresh infinito.

Nota: otras tablas (auditoria, Fact_Tiempos_Hitos, etc.) también referencian
la master en su M y funcionan, pero son tablas de hechos/auxiliares SIN
relaciones activas hacia Dim_Cliente que cierren el ciclo.

## Impacto

- El proyecto NO puede actualizarse → no se puede validar el cierre de los 54.
- Estado previo de los 54 (fila en blanco) sigue vigente pero sin poder verificarlo.

## Corrección requerida (ChatGPT)

1. Revertir Dim_Cliente a una fuente que no cree el ciclo:
   - Opción A: mantener `Sql.Database(...)` a ZART_TRACK_DATA_SAP pero **ampliar
     la ventana** para cubrir más códigos.
   - Opción B: construir Dim_Cliente desde SQL que lea el universo de clientes
     de la master vía query directa (sin referenciar la tabla del modelo en M).
   - Opción C: usar `Table.Buffer`/referencia a una expresión Power Query (no a
     la tabla importada del modelo).
2. Evitar que el M de una dimensión referencie una tabla importada con la que
   tiene relaciones activas.

## Archivos

- 00_git.txt
- RESULTADO.md
- manifest.json
