# READY FOR CHATGPT

RUN_ID: 20260811_181759_post_fix_inc011_inc015_evidencia_viva_085bfec
Rama: work/ns-lienzo-02-ingreso-pedidos
SHA local auditado: 085bfec7531f57bd5894641e397a0ce99938680d
SHA remoto al iniciar: 085bfec7531f57bd5894641e397a0ce99938680d
Commit evidencia: POR_PUBLICAR_TRAS_VALIDACION
Working tree sucio al iniciar: true (cambios preexistentes en NS.Report/** generados por Power BI Desktop; NO incluidos en el commit de evidencia)
Power BI: puerto 58835, base 56a5226e-f60b-4fc8-b6ef-199e71440797, modelo con datos (FECHA_ACTUALIZACION 2026-08-11 15:04). Sin refresh ejecutado por el auditor.

## Resumen

Corrida complementaria a `20260811_123620_post_fix_title_vbap_denominador_d7158cb`.
En la corrida previa el tool MCP DAX fallaba y dejó PENDIENTES INC-011 e INC-015.
En esta sesión el tool `powerbi-modeling_dax_query_operations` funcionó y se
resolvieron técnicamente:

1. **FIND-002A (ROJO)**: `RE TT Título` sigue roto en el SHA 085bfec. El error
   DAX `OrdenRango` aparece en las 12 combinaciones; los números NO regresionan.
2. **INC-011 (ORANGE → causa identificada)**: 55 cerrados sin DH (no 64; el corte
   previo era otro refresh). 100% tienen `FECHA_CIERRE=FECHA_DESPACHO=2020-09-24
   22:47:00` (fecha centinela) con cierre anterior a creación → `FnDH` null.
3. **INC-015 (ORANGE → causa identificada)**: hipótesis de ceros a la izquierda
   **FALSO_POSITIVO**. 806 sin match (41,7%) y 778 de ellos existen en VBAK. La
   causa está en la fuente `VBAP_SAP` (filtro `AEDAT>=GETDATE()-730` o contenido).
4. **INC-007B (ROJO estructural → impacto 0)**: fallback TRP existe en código
   pero 437/437 FES cerrados usan manifiesto real; 0 usan TRP.

## Hallazgos RED confirmados

- **FIND-002A** — `RE TT Título` (Medidas.tmdl): `CONCATENATEX(VALUES(Dim_Rango_Entrega[Rango]), ..., Dim_Rango_Entrega[OrdenRango], ASC)` lanza "No se puede determinar un valor único para la columna OrdenRango". Estado de la medida en el modelo: `SemanticError`. Visual afectado: `tt_context` (página 22a1b2c3d4e5f6071829).
- **FIND-001** — `Fact_Tracking.FECHA_MANIFIESTO` permite fallback TRP (líneas 353-358). Impacto actual 0 pero riesgo estructural; requiere decisión de negocio.

## Hallazgos ORANGE confirmados

- **INC-015** — Cobertura VBAP 58,3% (1.128/1.934). 806 sin match; 778 existen en VBAK. Hipótesis de padding descartada con evidencia (0 ceros en ambas tablas; match numérico sin mejora; derivados 7↔10 = 0).
- **INC-011** — 55 cerrados sin DH por fecha centinela. Quedan fuera del denominador RE (2,8% del universo). Requiere decisión de negocio sobre filtro/corrección.
- **INC-007B** — fallback TRP estructural pendiente de decisión.

## Falsos positivos relevantes

- **INC-015 hipótesis de ceros a la izquierda**: FALSO_POSITIVO. `Lineas_y_unidades_por_pedidos[Pedido]` y `Fact_Tracking[PED_NUMERO_PEDIDO]` no tienen claves con padding. El match normalizado no mejora (1.128 = 1.128).
- **Casos de regresión**: 10 de 11 coinciden. Solo `4190139455` difiere (histórico FES → actual NORMAL), explicado porque la regla FES requiere pedido posterior C-C que el pedido no cumple (`REGLA_CLASIFICACION_FES='SIN PEDIDO POSTERIOR C-C'`). La implementación actual es consistente; el CSV es hipótesis histórica y no se edita.

## Decisiones de negocio necesarias

1. **Cierre FES**: ¿FES debe cerrar solo por manifiesto VBFA/VTTP, eliminando el fallback TRP? (FIND-001). Impacto actual 0.
2. **Fecha centinela**: ¿los 55 pedidos con `FECHA_CIERRE=2020-09-24 22:47` deben filtrarse en origen o corregirse? Afectan 2,8% del universo.
3. **Denominador NS oficial**: U (incluye los 55) vs RE (los excluye). No decidido en esta corrida.
4. **Feriados regionales**: falta fuente confiable (INC-013).

## Cambios recomendados para implementación remota

1. `NS.SemanticModel/definition/tables/Medidas.tmdl` → medida `RE TT Título`:
   reemplazar `Dim_Rango_Entrega[OrdenRango]` por `MIN(Dim_Rango_Entrega[OrdenRango])`
   en el sort-by del CONCATENATEX de `RangoTexto` (o quitar el sort).
2. `NS.SemanticModel/definition/tables/Lineas_y_unidades_por_pedidos.tmdl` →
   revisar fuente `VBAP_SAP` y filtro `AEDAT>=GETDATE()-730`; evaluar join contra
   `Pedidos_Normal_VBAK`.
3. `NS.SemanticModel/definition/tables/Fact_Tracking.tmdl` → decisión sobre fecha
   centinela y fallback TRP (con aprobación de negocio).

## Evidencia principal

- `raw/find002_titulo_12_combinaciones.csv` — 12 combinaciones, título + métricas.
- `raw/inc011_cerrados_sin_dh.md` — lista completa de 55 pedidos y diagnóstico.
- `raw/inc015_cobertura_vbap.md` — cuantificación completa de cobertura y causa.
- `raw/inc007b_fes_trp.md` — cuantificación FES manifiesto real vs TRP.
- `raw/regresion_viva.md` — 11 casos de regresión con detalle del discrepante.
- `07_live_results.csv` — 42 pruebas vivas tabuladas.

## No resuelto

- Impacto exacto en líneas/unidades si se corrigiera la fuente VBAP (requiere fix primero).
- Causa exacta de por qué `VBAP_SAP` no contiene 806 pedidos (requiere acceso a la vista SQL).
- Decisión de negocio para INC-011 (fecha centinela) e INC-013 (feriados regionales).
- Validación visual en Power BI Desktop del tooltip (requiere fix aplicado).
