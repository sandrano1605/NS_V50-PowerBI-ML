# RESULTADO: Validación final lienzo 00 — Tabla fuera SLA (2026-08-10)

**Rama:** work/ns-lienzo-02-ingreso-pedidos
**SHA base (instrucción):** 759bf00f119d1d9ffd08104704e7c227e71b4024
**SHA validado:** 0dff10b34a08bd173bb8c6beb91734f4b4fc0d11
**Dictamen:** 🟡 AMARILLO

## Hallazgo crítico de carga

El commit **759bf00 NO carga** en Power BI Desktop: las helpers multiselect
(`RE Filtro Flujo` / `RE Filtro Zona`) insertadas tenían **indentación TMDL
inválida** (`///` con 2 tabs, `measure` con 0 tabs). El usuario validó el
commit por código, pero Power BI lo rechaza al abrir.

**Solución aplicada**: se restauró `Medidas.tmdl` al commit **0dff10b**, que:
- contiene el fix de TOPN(15) en `RE TT Días Top 10`;
- contiene el fix de `RE TT Título` (usa `[RE Pedidos fuera SLA contexto]`);
- contiene el fix de `RE Fuera SLA %` (RETURN inválido eliminado);
- **NO contiene las helpers multiselect rotas** → el proyecto carga.

## Validación principal — la tabla muestra TODOS los fuera SLA

| Contexto | RE Fuera SLA | Pedidos tabla | Duplicados | Resultado |
|---|---|---|---|---|
| Todos / Todas | **351** | **351** | **0** | ✅ 351 = 351 |
| Santiago | 146 | 146 | 0 | ✅ |
| Regiones | 205 | 205 | 0 | ✅ |

**Confirmado**: la tabla ya NO muestra solo 15 pedidos — muestra todos los
fuera SLA del contexto (351 en el universo actual). El TOPN(15) fue eliminado.

## Caso G (50 pedidos)

No se encontró un contexto que produzca exactamente 50 fuera SLA en los datos
actuales (fuente viva, 2.048 pedidos; los contextos probados dan 351/146/205/58/74/88).
El patrón de reconciliación `RE_FUERA_SLA = PEDIDOS_DISTINTOS_TABLA` se validó en
todos los contextos, demostrando que la tabla siempre muestra el universo completo.

## Multiselect (hallazgo ABIERTO)

- **Flujo**: unión Normal+FES = 351 (correcto); suma individual = 350 (diferencia
  1 por pedido FES+SALDO). El estado 0dff10b usa SELECTEDVALUE (single-select),
  por lo que el multiselect real requiere las helpers — que en 759bf00 rompían
  la carga TMDL.
- **Zona**: Santiago+Regiones = 351 (correcto, no BLANK).

## No regresión

- Slicers multiselección del lienzo 00: preservados (visuales intactos).
- Botones VER POR del 02 (y=448, sin glow): preservados.
- Dim_Cliente sin match = 0 (validado previamente).
- SLA sin exclusiones: no se eliminaron pedidos.
- El commit 759bf00 también contenía los cambios visuales del usuario (botones,
  gráficos, shape) que permanecen intactos.

## Archivos

00_git.txt · 01_refresh.txt · 02_casos_A_G.csv · 03_caso_50.csv ·
04_export_tabla_caso_50.csv · 05_multiselect_flujo.csv · 06_multiselect_zona.csv ·
07_regresiones.md · 08_incoherencias.md · RESULTADO.md
