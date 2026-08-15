# Patrones DAX reutilizables — NS Mayorista

Patrones de arquitectura de medidas extraídos del modelo NS. Son el "know-how"
más caro de reproducir: permiten un reporte ejecutivo mantenible.

## Patrón 1 — Medida "Base" + variante "Visible"

**Problema:** querés mostrar solo filas que cumplen una condición, pero mantener
la medida base intacta para otros cálculos.

**Solución:** la medida base calcula; la "Visible" la envuelve con un `IF`.

```dax
// Base: meses fuera SLA por cliente (sin filtro)
measure 'FA Meses Fuera SLA Cliente' =
    SUMX(
        FILTER(ALL(Dim_Periodo_3M[AnioMes]), NOT ISBLANK(Dim_Periodo_3M[AnioMes])),
        VAR Mes = Dim_Periodo_3M[AnioMes]
        VAR Fuera = CALCULATE([TU MEDIDA FUERA], REMOVEFILTERS(Dim_Fecha), TREATAS({Mes}, Dim_Fecha[AnioMes]))
        RETURN IF(Fuera > 0, 1, 0)
    )

// Visible: solo filas con >= 1 mes
measure 'FA Meses Fuera SLA Cliente Visible' =
    IF([FA Meses Fuera SLA Cliente] >= 1, [FA Meses Fuera SLA Cliente])
```

**Beneficio:** el visual usa la `Visible` (filtra filas), los KPIs usan la base
(no altera totales).

## Patrón 2 — Jerarquía ejecutiva desconectada

**Problema:** querés un visual que se expanda por niveles (Total → Flujo →
Macroproceso → Subproceso) sin duplicar visuales.

**Solución:** una tabla desconectada con la jerarquía + una medida que "adivina"
el nivel según `ISINSCOPE`.

```dax
// Tabla desconectada Dim_Vista_Ejecutiva
// columnas: Grupo, Flujo, Macroproceso, Subproceso, METRICA_CODIGO, ORDEN_*

// Medida que resuelve el código de métrica según el nivel visible
measure '[RE Código nivel]' =
    VAR Macro = SELECTEDVALUE(Dim_Vista_Ejecutiva[Macroproceso])
    RETURN
        SWITCH(TRUE(),
            ISINSCOPE(Dim_Vista_Ejecutiva[Subproceso]), SELECTEDVALUE(Dim_Vista_Ejecutiva[METRICA_CODIGO]),
            ISINSCOPE(Dim_Vista_Ejecutiva[Macroproceso]) && CONTAINSSTRING(Macro, "Administrativo"), "ADMIN_TOTAL",
            ISINSCOPE(Dim_Vista_Ejecutiva[Macroproceso]) && CONTAINSSTRING(Macro, "Operaciones"), "OPERACIONES_TOTAL",
            "TOTAL")
```

**Beneficio:** un único visual se expande por toda la jerarquía. Muy usado en
matrices ejecutivas.

## Patrón 3 — Tablas de configuración editables

**Problema:** el negocio cambia metas (SLA, promesa) sin tocar código DAX.

**Solución:** tabla de parámetros hardcodeada en TMDL, consumida vía `LOOKUPVALUE`
o `RELATED`.

```dax
// Consumo
VAR SLA = LOOKUPVALUE(Config_SLA_Hitos[SLA_DH], Config_SLA_Hitos[METRICA_CODIGO], [CODIGO_ACTUAL])
RETURN IF([DIAS_HABILES] <= SLA, "CUMPLE", "FUERA")
```

Ver `tablas-config/` para las plantillas TMDL.

## Patrón 4 — Filtro zonal sobre medida (SLA por zona)

```dax
measure 'SLA zonal' =
    IF([METRICA] = "OPERACIONES_TOTAL",
        IF([ZONA] = "Santiago", 3, 4),
        [SLA_DEFAULT])
```

**Beneficio:** una sola medida aplica SLA distinto por zona sin duplicar.

## Nota general

- `TREATAS` + tabla desconectada = filtro manual sin relación física.
- `REMOVEFILTERS` = abrir el universo para el denominador (usar con cuidado y documentar).
- `KEEPFILTERS` = mantener el filtro externo dentro de `FILTER`/`CALCULATE`.
- `ISINSCOPE` = detectar si una columna está en el eje de la matriz.
