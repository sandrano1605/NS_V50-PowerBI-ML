# Lienzo 01 — Auditoría de coherencia funcional (visual 3 VENDEDORES)

## Objetivo

Auditar la coherencia del visual `3. VENDEDORES · IMPACTO DE CLIENTES REINCIDENTES
SEGÚN FLUJO` y la propagación del filtro de vendedor por todo el modelo.

## 1. Mapeo de relaciones (hallazgo estructural)

### Dos conceptos de "vendedor" desconectados

| Concepto | Campo | Tabla | Relación |
|---|---|---|---|
| Vendedor ACTUAL | `VENDEDOR_NOMBRE` | `Dim_Cliente` (maestro) | Fact_*[PED_CODIGO_CLIENTE] → Dim_Cliente[CLIENTE_CODIGO] |
| Responsable del pedido | `PED_RESPONSABLE` (código) | `Fact_*` | Fact_*[PED_RESPONSABLE] → Dim_Responsable[RESPONSABLE_CODIGO] |

- `Dim_Responsable` tiene **solo 1 columna** (`RESPONSABLE_CODIGO`), sin nombre.
- No hay puente entre `Dim_Cliente[VENDEDOR_NOMBRE]` y `Dim_Responsable[RESPONSABLE_CODIGO]`.
- El visual 3 usa `Dim_Cliente[VENDEDOR_NOMBRE]` → filtra por **cliente asignado actualmente**,
  NO por el responsable histórico del pedido.

### Relaciones por tabla de hechos (todas consistentes)

| Hecho | Dim_Cliente | Dim_Responsable | Dim_Canal | Dim_Fecha | Dim_Pedido |
|---|---|---|---|---|---|
| Fact_Tracking | ✓ (PED_CODIGO_CLIENTE) | ✓ (PED_RESPONSABLE) | ✓ | ✓ | ✓ |
| Fact_Hitos_Operacionales | ✓ | ✓ | ✓ | ✓ | ✓ |
| Fact_Pedidos | ✓ | ✓ | ✓ | ✓ | ✓ |
| Fact_Tiempos_Hitos | ✓ | ✓ | ✓ | ✓ | ✓ |

→ La propagación del filtro por CLIENTE es consistente en las 4 tablas de hechos.

## 2. Definición real de "reincidente"

La medida `FA Meses Fuera SLA Cliente` cuenta **meses (de 3) con ≥1 pedido fuera SLA**:

```dax
FA Meses Fuera SLA Cliente =
SUMX( FILTER(ALL(Dim_Periodo_3M[AnioMes]), NOT ISBLANK(...)),
      CALCULATE([RE Pedidos fuera SLA contexto], REMOVEFILTERS(Dim_Fecha), TREATAS({Mes}, Dim_Fecha[AnioMes])) )
```

Clasificación (`FA Recurrencia Cliente`):
- >= 3 → Recurrente 3M
- = 2 → Recurrente 2M
- = 1 → Puntual 1M

### Respuesta a las 5 definiciones planteadas

| Definición | ¿Es la del modelo? |
|---|---|
| A — COUNT(PEDIDO) > 1 | ❌ No |
| B — COUNT(DISTINCT PEDIDO) > 1 | ❌ No |
| C — cliente + flujo | ❌ No (ignora flujo) |
| D — cliente + últimos 3 meses | ✅ **SÍ** |
| E — cliente + todo histórico | ❌ No (solo 3M) |

**Conclusión**: "reincidente" = cliente con **meses distintos de incumplimiento en la
ventana de 3 meses**, NO cliente con múltiples pedidos. Esto es clave para interpretar
el visual: un cliente con 10 pedidos fuera SLA todos en el mismo mes = "Puntual 1M",
no "reincidente".

## 3. Baseline y Carlos Garrido (modelo vivo)

### Sin filtro

| Métrica | Valor |
|---|---|
| Pedidos | 2.097 |
| Clientes | 745 |
| Reincidentes 2M+ | 22 |
| Fuera SLA | 372 |
| NS | 80,8% |

### Carlos Garrido

| Métrica | Valor |
|---|---|
| Clientes | 25 |
| Pedidos (Fact_Tracking) | 78 |
| Pedidos (Fact_Hitos_Operacionales) | 78 |
| Fuera SLA | 24 |
| Reincidentes 2M+ | 3 |
| NS | 68,4% |

### Coherencia verificada

- `Fact_Tracking` y `Fact_Hitos_Operacionales` devuelven el MISMO número (78) para
  Carlos → la propagación del filtro por cliente es consistente. ✅
- No hay "25 vs 27" en el modelo vivo actual: el número es 78 en ambas tablas.
  (La discrepancia 25/27 referida corresponde a otro momento/refresh.)

## 4. Punto de coherencia semántica pendiente

El visual 3 usa `Dim_Cliente[VENDEDOR_NOMBRE]` (vendedor actual del maestro).
Los pedidos de esos clientes tienen `PED_RESPONSABLE` = códigos distintos (V610/V650/V550),
porque el vendedor asignado cambió con el tiempo.

**Implicación**: si el negocio quiere "impacto del vendedor que atendió el pedido",
debe usar `Dim_Responsable[RESPONSABLE_CODIGO]`. Si quiere "impacto del vendedor que
hoy tiene al cliente", debe usar `Dim_Cliente[VENDEDOR_NOMBRE]`. Son cosas distintas.

## 5. Dictamen

- ✅ Propagación de filtro por cliente: consistente en las 4 tablas de hechos.
- ✅ Definición de reincidencia: documentada (meses de incumplimiento en 3M).
- ⚠️ Semántica "Vendedor": ambigua (actual vs histórico) — decisión de negocio.
- ⚠️ "Reincidente" puede confundir con "múltiples pedidos" — considerar renombrar o aclarar en tooltip.
