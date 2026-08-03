# Auditoría: Cruce Pedidos_Normal_VBAK ↔ Master (2026-08-03)

## Objetivo
Verificar cuántos pedidos del universo FES/Normal (`Pedidos_Normal_VBAK`,
2.158 pedidos) se encuentran en la master (`Fact_Pedidos_Auditoria`) y crear la
relación en el modelo para que filtren juntos.

## Resultado del cruce (verificado en modelo en vivo)

| Métrica | Cantidad | % |
|---|---|---|
| Universo Pedidos_Normal_VBAK | 2.158 | 100% |
| **Se encuentran en la master** | **1.902** | **88%** |
| No están en la master | 256 | 12% |
| Master total | 1.973 | - |

## Clasificación de los 1.902 que se cruzan

| Clasificación | Con manifiesto | Sin manifiesto | Total |
|---|---|---|---|
| FES | 386 | 53 | 439 |
| NORMAL | 1.371 | 92 | 1.463 |
| **Total** | **1.757** | **145** | **1.902** |

## Relación creada en el modelo

```tmdl
relationship 53000000-0000-4000-8000-0000000000B1
	fromColumn: Fact_Pedidos_Auditoria.PED_NUMERO_PEDIDO
	toColumn: Pedidos_Normal_VBAK.VBELN
```

- Tipos compatibles: string ↔ string.
- Cardinalidad: Many (master) → One (VBAK).
- Verificada en vivo: la consulta `RELATED('Pedidos_Normal_VBAK'[fecha_salida])`
  desde la master devuelve los valores correctos.
- Resultado agregado: de 1.973 pedidos de la master, **1.757 tienen manifiesto**
  en VBAK y **216 no**.

## Los 53 FES sin manifiesto (candidatos de cierre)
Composición: 28 pedidos NS (116xxxx, 27-may a 31-jul 2026) + 25 pedidos 4190xxxxxx.

### Auditoría de reconexión pendiente
El análisis fino de los 53 FES sin manifiesto contra PASO_WMS (por MAD_PEDIDO /
MAD_ENTREGA / MAD_NRO_SAP) quedó **pendiente por caída de red**: el servidor
128.1.3.60 no estaba accesible al momento de la auditoría. Al reconectar, ejecutar:
- `auditoria_fes_sin_manifiesto.py` (script temporal en temp de OpenCode)
  para confirmar si existe registro WMS por alguna clave alternativa.

Decisión previa validada: NO cruzar por NRO_SAP/PEDIDO genérico del WMS porque
suelen ser números internos (11, 111, 1...) que generan falsos positivos.

## Archivos modificados
- `NS.SemanticModel/definition/relationships.tmdl`: agregada relación 0B1.
- `NS.SemanticModel/definition/tables/Pedidos_Normal_VBAK.tmdl`: corrección
  previa de columna condicional (commit ae9b020).

## Commit
- Relación + documentación del cruce con la master.
