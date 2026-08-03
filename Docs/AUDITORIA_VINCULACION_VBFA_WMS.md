# Auditoría de vinculación VBFA ↔ WMS (2026-08-02)

## Objetivo
Determinar por qué la vinculación entre el universo VBFA C→J y el manifiesto WMS
era tan baja (3 pedidos) y corregir la estrategia de cruce.

## Hallazgo 1: El filtro `MAD_PEDIDO > 1000` era incorrecto
- MANIFIESTO_D tiene **17.542 filas** reales (no 1.943 como mostraba la query anterior).
- 15.197 filas (87%) tienen `MAD_PEDIDO` NULL/0/1.
- El filtro descartaba registros válidos y reducía el universo a 1.943.

## Hallazgo 2: WMS no usa entregas SAP para la mayoría
- 7.838 entregas WMS válidas (distintas).
- Solo **1.590** están en rango de entrega SAP (80.000.000-99.999.999).
- **5.569** son números internos WMS (40.385, 40.409, ...) que no existen en SAP.
- De las 1.590 en rango SAP, solo **5** son entregas J en VBFA.

## Hallazgo 3: `MAH_MANIFIESTO_SAP` no sirve como clave
- Cabecera MANIFIESTO_H: 701 filas con `'0'`, 247 con `'-'`, el resto folios internos
  (104596, 15455, ...). No contiene pedidos ni entregas SAP utilizables.

## Hallazgo 4: `MAD_NRO_SAP` SÍ contiene números SAP reales
- Campo no considerado en la estrategia original.
- Aporta 52 documentos únicos adicionales a la vinculación.

## Estrategia corregida (3 claves de cruce)
1. `MAD_PEDIDO` (válido, < 1.000.000.000) → contra pedidos C de VBFA (VBELN/VBELV con VBTYP_V='C').
2. `MAD_ENTREGA` (en rango SAP) → contra entregas J de VBFA (VBTYP_N='J').
3. `MAD_NRO_SAP` → contra pedidos C o entregas J de VBFA.

## Resultado de la vinculación (comparación)

| Clave | Antes (filtro erróneo) | Corregido |
|---|---|---|
| MAD_PEDIDO vs pedidos C | 3 | **13 pedidos** |
| MAD_ENTREGA vs entregas J | 1 | **5 entregas** |
| MAD_NRO_SAP vs SAP | 4 | **52 documentos** |
| **UNIÓN única** | **3** | **65 documentos** |

Pedidos vinculados (13): 1157530, 1157710, 1158295, 1158305, 1159050, 1159103,
1159142, 1160052, 1166394, 1166421, 1167110, 1167125, 1167577.

## Distribución WMS 2024-2026 por tipo de ingreso
| Año | Manual (S) | Masivo (M) |
|---|---|---|
| 2024 | 1.385 | 1.343 |
| 2025 | 4.565 | 3.585 |
| 2026 | 4.209 | 691 |

Total manual (S): 10.159 registros — son los manifiestos manuales objetivo.

## Conclusión operativa
- La vinculación se multiplicó por ~21 (3 → 65) con la estrategia de 3 claves.
- El WMS es en su mayoría operación de transporte interno sin entrega SAP
  (solo 66 pedidos en rango del modelo NS 116xxxx/117xxxx).
- Para ampliar el universo de cierre FES, el cruce relevante es
  `MAD_PEDIDO`/`MAD_NRO_SAP` contra la master en Power BI (tabla calculada),
  no solo VBFA C→J.

## Referencias
- `sql/FLUJO_FES_VBFA_WMS.sql` (query corregida con PASO 0 sin filtro FES)
- Scripts de auditoría: `auditoria_wms.py`, `auditoria_wms2.py`,
  `auditoria_wms3.py`, `auditoria_wms4.py`, `auditoria_final_union.py`
