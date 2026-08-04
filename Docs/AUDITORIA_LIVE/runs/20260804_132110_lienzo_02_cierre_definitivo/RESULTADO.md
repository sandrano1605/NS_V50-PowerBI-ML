# RESULTADO: Cierre definitivo lienzo 02 — Ingreso de Pedidos (2026-08-04)

**Rama:** work/ns-lienzo-02-ingreso-pedidos
**SHA inicial (entrega ChatGPT):** b64b000fa229c148718bb5be36144c357c7f932f
**Dictamen:** 🟢 VERDE — reconciliado, preguntas respondidas con cifras

## Informe del error corregido (bloqueante, introducido en b64b000)

El proyecto **no abría** con: `Error del motor M: "Se esperaba el token ','"`.

### Causa raíz (2 problemas)
1. **`Fact_Tracking.tmdl`**: ChatGPT agregó el paso `ResultadoUnico = Table.Distinct(Resultado, {"PED_NUMERO_PEDIDO"})` después de `Resultado`, pero **no agregó la coma final** al paso `Resultado = Table.SelectColumns(...)`. En M, todo paso del `let` excepto el último lleva coma. El motor M falló al parsear.
2. **`Medidas.tmdl`**: el commit eliminó la declaración `column __Medida` pero la partición M sigue generándola (`#table(type table [__Medida = Int64.Type], {{1}})`) y la cultura `es-ES.tmdl` conserva referencias.

### Corrección aplicada (por LLM local, autorizado por usuario)
1. Agregada coma al final del paso `Resultado` en Fact_Tracking.tmdl.
2. Restaurada `column __Medida` (lineageTag a999e59e-...) en Medidas.tmdl.
3. Proyecto vuelve a abrir y refrescar sin errores.

## Control 1 · Tracking una fila por pedido

| Métrica | Valor |
|---|---|
| Filas Fact_Tracking | 1.948 |
| Pedidos distintos | 1.948 |
| **Duplicados** | **0** ✅ |

## Control 2 · Tracking vs Master (EXCEPT ambos sentidos)

| Refresh | Solo Tracking | Solo Master | Explicación |
|---|---|---|---|
| 1º refresh | 10 | 0 | 10 pedidos de hoy (04-08-2026, PENDIENTE FACTURA) aún sin cierre para master |
| 2º refresh | **0** | **0** | Master absorbió los pedidos nuevos — **reconciliado** ✅ |

Diferencia explicada por cambio de fuente durante el refresh (pedidos creados entre refrescos), NO es defecto.

## Q1 · Día líder

| Métrica | Día | Valor |
|---|---|---|
| Pedidos | **Lunes** | 553 |
| Líneas | **Jueves** | 5.665 |
| Unidades | **Miércoles** | 563.221 |

## Q2 · Cobertura horaria (cifras nuevas)

| Métrica | Valor | Fórmula |
|---|---|---|
| Total pedidos | 1.948 | — |
| Hasta 14:30 | 637 | — |
| Después de 14:30 | 519 | — |
| Sin hora válida | 792 | — |
| **Cobertura hora válida** | **59,3%** | (637+519)/1948 |
| **Después 14:30 sobre medibles** | **44,9%** | 519/(637+519) |
| **Sin hora válida sobre total** | **40,7%** | 792/1948 |

Coincide con lo esperado por ChatGPT (~59,5% / 44,9% / 40,5%).

## Q3 · Concentración al cierre (promedios diarios)

| Métrica | Valor |
|---|---|
| Pedidos cierre | 625 |
| Días con ingreso en cierre | 26 |
| **Promedio diario cierre** | **24,04** |
| Pedidos resto | 587 |
| Días con ingreso en resto | 27 |
| **Promedio diario resto** | **21,74** |
| **Delta promedios** | **+10,6%** |
| FES/Saldo en cierre | 155 (24,8%) |
| Día pico unidades | 29 (454.282 = 22,7%) |

## Botones y filtros

- 3 botones con display.hidden (esquema 2.1.0): cada uno muestra su gráfico y oculta los otros 2.
- Bookmarks sin filtros capturados; filtro global 43/45 eliminado.
- Persistencia de filtros: OK estructural (validación real en pantalla pendiente del usuario).

## Archivos de evidencia

00_git.txt · 01_refresh_1.txt · 02_refresh_2.txt · 03_tracking_vs_master.csv ·
04_q1_dia_semana.csv · 05_q2_cobertura_horaria.csv · 06_q3_promedios_diarios.csv ·
07_q3_flujo_y_pico_unidades.csv · 08_botones_prueba_real.csv · 09_filtros_persistencia.csv ·
10_calidad_visual.txt · 11_regresiones.txt · 12_incoherencias.csv · RESULTADO.md · manifest.json
