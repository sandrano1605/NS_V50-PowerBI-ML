# RESULTADO: Validación cruce VBAK inline — modelo vivo (2026-08-03)

**Rama:** work/ns-vbak-master-append
**HEAD:** 5ef34be3b26d9668a7d91014488002fe29d94873 (corrección SQL aplicada)
**Kit:** VERDE (master_integration_present=true)

## Resultado general: VALIDACIÓN COMPLETA — controles OK

### Conteos (validación 1-3)
| Métrica | Valor |
|---|---|
| MASTER_TOTAL | **1.926** |
| Filas VBAK SIN ZART | **685** |
| MASTER_ORIGINAL | **1.241** (1.926 - 685 ✅) |

### Controles de calidad (validaciones 4-11)
| Control | Resultado |
|---|---|
| Duplicados por pedido | **0** ✅ (685+1241=1926 exacto) |
| Claves nulas en filas VBAK | **0** ✅ |
| Canales fuera de 42-47 | **0** ✅ (solo 42,43,44,45,46,47 presentes) |
| Regiones nulas | **0** ✅ (13 regiones válidas 01-13) |
| ES_FES=true en filas VBAK | **0** ✅ (solo False en 685) |
| ES_SALDO=true en filas VBAK | **0** ✅ (solo False en 685) |
| Salida sin factura | **0** ✅ (473 con salida, todas con factura) |
| AUD_ESTADO_GENERAL=REVISAR | **685/685 (100%)** ✅ |

### Tablas refrescan (validación 12)
| Tabla | Filas |
|---|---|
| Fact_Tracking | 1.926 |
| Fact_Pedidos | 1.926 |
| Fact_Tiempos_Hitos | 52.002 |
| Fact_Hitos_Operacionales | 21.825 |
| Resultado | 1.926 |

### Python (validación 13)
- `tools/validate_vbak_append_kit.py`: status=VERDE, pbip_changes=[Fact_Pedidos_Auditoria.tmdl] (permitido)

## Hallazgo: pedido 1167577 ausente (validación 14)

- **4190139455**: presente ✅ (ES_FES=False, sin regresión).
- **1167577**: **NO encontrado** en master, Fact_Tracking, Dim_Pedido,
  Fact_Hitos_Operacionales, Fact_Tiempos_Hitos ni Resultado.

### Verificación en base (DMF_VTA_PRD)
El pedido SÍ existe en la base:
- VBAK_SAP: pedido=1167577, fecha=30-06-2026, AUART=ZMAY, VTWEG=42 (canal Mayorista, dentro de ventana 3M)
- VBFA: flujo C→M (91785067, 01-07-2026), C→T (84086655, 02-07-2026), C→O (91785332, 02-07-2026)

### Causa probable (no corregida)
El pedido tiene flujo FES (C→C con factura/entrega/manifiesto). La integración
VBAK lo excluye como candidato (cuarentena FES: `VBAK_FECHA_FES <> null`), y la
master original pudo haberlo perdido por el cambio de ventana móvil o porque el
universo ZART ya no lo clasifica dentro de los 3 meses. NO se corrigió (prohibido).

## Nota de conteo
No se compara contra 1.973 (snapshot histórico fijo). La master usa GETDATE() y
ventana móvil de 3 meses; el total actual es 1.926.

## Archivos
- Este RESULTADO.md
- 01_kit_validation.json (kit VERDE)
- 02_snapshot_modelo.csv (conteos de tablas)
