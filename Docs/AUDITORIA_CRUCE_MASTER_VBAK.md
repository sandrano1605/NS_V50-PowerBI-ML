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

### Auditoría fina completada (red restablecida 2026-08-03)
Los 53 FES sin manifiesto se auditaron contra PASO_WMS por las 3 claves:

| Clave de búsqueda en WMS | Resultado |
|---|---|
| MAD_PEDIDO | 0 encontrados |
| MAD_NRO_SAP | 0 encontrados |
| MAD_ENTREGA (63 entregas VBFA de los 27 pedidos NS) | 0 encontrados |

**Conclusión**: los 53 FES sin manifiesto NO tienen ningún registro en el WMS por
ninguna clave. Son casos legítimos sin transporte manual cargado — no hay
manifiestos perdidos ni cruces incompletos. El universo de cierre FES está
completo al 100%: todo lo que el WMS tiene se cruza.

Script de auditoría: `auditoria_fes_sin_manifiesto.py` (temp OpenCode).

## Archivos modificados
- `NS.SemanticModel/definition/relationships.tmdl`: agregada relación 0B1.
- `NS.SemanticModel/definition/tables/Pedidos_Normal_VBAK.tmdl`: corrección
  previa de columna condicional (commit ae9b020).

## Commit
- Relación + documentación del cruce con la master.
