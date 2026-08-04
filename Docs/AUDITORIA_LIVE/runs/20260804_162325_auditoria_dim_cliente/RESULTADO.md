# RESULTADO: Auditoría Dim_Cliente — pedidos sin correspondencia (2026-08-04)

**Rama:** work/ns-lienzo-02-ingreso-pedidos
**SHA:** 2fcd81dd67dfa7af80c7870bfb1df26c95ebcba9
**Dictamen:** 🔴 ROJO (dimensión) — problema de correspondencia CONFIRMADO, requiere corrección de Dim_Cliente

## Confirmación de la hipótesis de ChatGPT

El problema **NO es visual** (ancho/formato) ni de exclusión de pedidos.
Es un **problema de dimensión**: los pedidos sin match en `Dim_Cliente` caen en
la fila en blanco automática y se muestran como "cliente vacío / vendedor vacío".

## Evidencia del modelo vivo (2026-08-04)

| Métrica | Valor |
|---|---|
| Pedidos totales Tracking | 1.950 |
| **Pedidos sin match en Dim_Cliente** | **635 (32,6%)** |
| Pedidos con match | 1.315 |
| Códigos únicos en Fact_Tracking | 706 |
| Códigos únicos en Dim_Cliente | **355** |
| **Códigos sin cobertura** | **351 (49,7%)** |
| Fuera de SLA totales | 109 |
| Fuera de SLA sin match (relación rota) | 22 |
| Fuera de SLA con match | 87 |

## Causa raíz

`Dim_Cliente` se construye desde `ZART_TRACK_DATA_SAP` (fuente parcial, últimos
2 meses) y conserva el código textual original. `Fact_Tracking` hereda códigos
desde la master de auditoría, que cubre un universo mayor (3 meses + VBAK).
Resultado: **solo 355 de 706 códigos (50,3%) tienen cobertura** en la dimensión.

## Nota sobre el conteo 54 vs 22

- Los **22** son los fuera de SLA sin match en todo el universo (junio=18, julio=4).
- El usuario observa **54** en la fila en blanco de la tabla `fa_clientes_recurrentes`
  → corresponde al **contexto del slicer de la página 01** (mes vigente + agrupación
  por cliente/vendedor/flujo con totales desactivados). Es un subconjunto del visual,
  no un universo distinto.
- Ambos confirman el mismo problema: pedidos sin correspondencia en Dim_Cliente.

## Los 22 pedidos fuera de SLA sin match (lista en 02_lista_pedidos_sin_match.csv)

Pedidos NORMAL cerrados con exceso de SLA (ej. 4190139957→460137 exceso 2DH,
4190139950→411459 exceso 11DH). Todos tienen `PED_CODIGO_CLIENTE` presente pero
ausente de Dim_Cliente.

## Corrección recomendada (corresponde a ChatGPT, no al LLM)

1. Construir `Dim_Cliente` desde el **universo de pedidos**:
   `DISTINCT Fact_Tracking[PED_CODIGO_CLIENTE]` y enriquecer con KNA1 y CLIENTE_VENDEDOR.
2. Normalizar claves (ceros iniciales, espacios, numérico vs texto).
3. Mantener como mínimo el código cuando no exista nombre (COALESCE ya lo hace).
4. Etiquetar vendedor sin asignación como "SIN VENDEDOR ASIGNADO".
5. Control de integridad: pedidos con cliente sin correspondencia = 0.

## Archivos

- 00_git.txt
- 01_metricas_dim_cliente.csv
- 02_lista_pedidos_sin_match.csv (22 fuera de SLA sin match)
- RESULTADO.md
