# V10 · Corrección de auditoría para FES abiertos

## Caso de control
Pedido `4190139455`.

## Problema corregido
- El pedido tenía despacho físico, pero `PENDIENTE_DESPACHO` permanecía en verdadero porque la regla miraba `FECHA_CIERRE`.
- En FES Regiones, el cierre depende del manifiesto; por ello se confundía despacho pendiente con manifiesto pendiente.
- `DH_LEAD_NORMAL` seguía mostrando 2 DH aunque `INCLUIR_SLA_NORMAL = false`.
- `FECHA_ACTUALIZACION` mostraba la fecha del último pedido cargado y no el momento real del refresh.

## Reglas finales
- `PENDIENTE_DESPACHO = factura presente y despacho ausente`.
- `PENDIENTE_MANIFIESTO_FES = FES con despacho presente y manifiesto ausente`.
- El inicio del estado `MANIFIESTO FES` es la fecha de despacho.
- `DIAS_HASTA_DESPACHO_DH` separa el lead físico hasta despacho.
- `DIAS_ESPERA_MANIFIESTO_DH` mide la espera documental posterior al despacho.
- `TIPO_MEDICION_DIAS` distingue `LEAD CERRADO` de `ANTIGÜEDAD ABIERTA`.
- `DH_LEAD_NORMAL` queda nulo cuando `INCLUIR_SLA_NORMAL = false` en `Fact_Pedidos` y `Fact_Tiempos_Hitos`.
- `FECHA_ACTUALIZACION` usa el momento fijo real del refresh.

## Resultado esperado para 4190139455
- Pendiente despacho: No.
- Pendiente manifiesto FES: Sí.
- Estado actual: Pendiente manifiesto FES.
- Días hasta despacho: 2 DH.
- Lead normal: nulo / sin dato.
- Días internos: antigüedad abierta hasta el refresh, no tiempo de despacho.
