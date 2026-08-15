# Design System — NS Mayorista

## 1. Paleta de colores

| Rol | Hex | Uso |
|---|---|---|
| Fondo principal | `#0B3558` | Tarjetas SVG ejecutivas |
| Azul institucional | `#1B365D` | Títulos, headers |
| Azul suave | `#BFD3E3` | Texto secundario sobre fondo oscuro |
| Blanco | `#FFFFFF` | Valores, fondo de tabla |
| Gris bordes | `#CED9E5` | Bordes de tarjetas |
| Gris fondo | `#E6ECF2` / `#EEF3F8` | Header de tabla |
| Texto | `#141414` / `#111111` | Texto normal |

### Semáforo (estado)

| Estado | Hex |
|---|---|
| Rojo (fuera SLA / crítico) | `#D3392C` |
| Amarillo (atención) | `#FFC827` |
| Verde (cumple) | `#2E8B57` |
| Neutro (sin dato) | `#84807D` |

## 2. Tipografía

- Familia: **Segoe UI** (Web-safe, presente en Power BI).
- Pesos: `400` normal, `600` semibold, `700` bold.
- Escala (en pt, usada en el reporte):

| Rol | Tamaño |
|---|---|
| Valor KPI grande | 27pt |
| Título tarjeta SVG | 15pt |
| Título visual | 8-10pt |
| Cuerpo tabla | 5.5-7pt |
| Etiqueta badge | 7-10.5pt |

## 3. Componentes SVG (medidas DAX)

Todos los SVG son **medidas DAX** que retornan un string
`"data:image/svg+xml,..."` con la cadena URL-encoded (`%3C` = `<`, `%23` = `#`).

### 3.1 Tarjeta KPI ejecutiva

```dax
measure '[TEMPLATE] Tarjeta KPI SVG' =
    VAR Acento   = "%23E8B10D"          -- color del acento lateral
    VAR Etiqueta = "TU ETIQUETA"        -- texto superior
    VAR Valor    = FORMAT([TU MEDIDA], "#,##0")
    RETURN
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='420' height='110' viewBox='0 0 420 110'%3E"
        & "%3Crect width='420' height='110' rx='16' fill='%230B3558'/%3E"
        & "%3Crect x='0' y='0' width='12' height='110' rx='6' fill='" & Acento & "'/%3E"
        & "%3Ccircle cx='58' cy='55' r='28' fill='" & Acento & "' opacity='.18'/%3E"
        & "%3Ccircle cx='58' cy='55' r='17' fill='" & Acento & "'/%3E"
        & "%3Ctext x='98' y='38' font-family='Segoe%20UI' font-size='13' font-weight='600' fill='%23BFD3E3'%3E" & Etiqueta & "%3C/text%3E"
        & "%3Ctext x='98' y='76' font-family='Segoe%20UI' font-size='27' font-weight='700' fill='%23FFFFFF'%3E" & Valor & "%3C/text%3E"
        & "%3C/svg%3E"
```

### 3.2 Semáforo (badge de estado)

```dax
measure '[TEMPLATE] Semáforo SVG' =
    VAR Color = SWITCH(TRUE(),
        CONTAINSSTRING([ESTADO], "FUERA"), "%23D3392C",
        CONTAINSSTRING([ESTADO], "ATENCI"), "%23FFC827",
        CONTAINSSTRING([ESTADO], "CUMPLE"), "%232E8B57",
        "%2384807D")
    VAR Etiqueta = [TU MEDIDA ESTADO]
    RETURN
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='36' viewBox='0 0 160 36'%3E"
        & "%3Crect x='1' y='1' width='158' height='34' rx='17' fill='" & Color & "' opacity='.13'/%3E"
        & "%3Ccircle cx='18' cy='18' r='7' fill='" & Color & "'/%3E"
        & "%3Ccircle cx='18' cy='18' r='2.5' fill='%23FFFFFF'/%3E"
        & "%3Ctext x='32' y='22' font-family='Segoe%20UI' font-size='10.5' font-weight='700' fill='" & Color & "'%3E" & Etiqueta & "%3C/text%3E"
        & "%3C/svg%3E"
```

### 3.3 Badge de estado (pill pequeño)

```dax
measure '[TEMPLATE] Badge estado SVG' =
    VAR Color = "%232E8B57"
    VAR Estado = "CUMPLE"
    RETURN
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='112' height='26' viewBox='0 0 112 26'%3E"
        & "%3Ctext x='26' y='17' font-family='Segoe%20UI' font-size='10' font-weight='700' fill='" & Color & "'%3E" & Estado & "%3C/text%3E%3C/svg%3E"
```

## 4. Cómo parametrizar (para otra implementación)

1. Reemplazar `Acento` con tu color de marca.
2. Reemplazar `Etiqueta` / `Estado` con tus textos.
3. Reemplazar `[TU MEDIDA]` con tus medidas reales.
4. Mantener la estructura `data:image/svg+xml` y el URL-encoding (`%3C`, `%3E`, `%23`, `%20`).

> Regla: los `%` en DAX se concatenan con `&`. Todo carácter especial va URL-encoded.
> Usar `fill='%23RRGGBB'` para colores (el `#` se codifica como `%23`).
