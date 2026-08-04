## ADDENDUM 2026-08-04: Decision final de ChatGPT (commit d8d250a2)

### Decision
**No excluir los 54 pedidos del indicador oficial ni modificar DAX.**

El indicador oficial conserva todos los pedidos que cumplen:
- ES_CERRADO = TRUE
- DIAS_INTERNOS_DH con valor
- CUMPLE_SLA_INTERNO = FALSE

Quitarlos mejoraria artificialmente el NS y ocultaria incumplimientos reales.

### Correccion al informe publicado
Las cifras 232, 109 y 54 **NO estan reconciliadas como un mismo universo**:

| Cifra | Que representa |
|---|---|
| 232 | Pedidos fuera SLA del contexto KPI de los lienzos 00 y 01 |
| 109 | Conteo informado solo para junio y julio (59 + 50) |
| 54 | Valor observado dentro de la tabla agrupada o su contexto visual |

La explicacion de que "los 54 son el subconjunto del mes vigente" es una
**hipotesis, no una reconciliacion terminada** (no se publico lista de 54
numeros de pedido distintos). La tabla tiene totales desactivados; un valor 54
puede corresponder a una combinacion especifica de cliente/vendedor/flujo.

**Esto no cambia la decision**: no existe fundamento para excluir pedidos
oficialmente fuera de SLA.

### Dictamen final
| Control | Estado |
|---|---|
| Botones de navegacion eliminados | APROBADO |
| Modelo semantico afectado | NO |
| Pedidos oficialmente fuera SLA | VALIDOS |
| Excluir los 54 | RECHAZADO |
| Modificar DAX | NO REQUERIDO |
| Evidencia de tres ejemplos | VALIDA |
| Evidencia exhaustiva de los 54 | NO PUBLICADA |
| Reconciliacion 232-109-54 | CONTEXTOS DISTINTOS |
| Estado de los tres lienzos | OPERATIVOS |

Referencia: `Docs/AUDITORIA_LIVE/DECISION_54_PEDIDOS_FUERA_SLA.md`
