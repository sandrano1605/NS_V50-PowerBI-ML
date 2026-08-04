# RESULTADO: Pedido 4190139948 — flujo FES C→C existe pero NO clasificado (2026-08-04)

**Rama:** work/ns-lienzo-02-ingreso-pedidos
**SHA:** 40602323b15fc722db27b2e917c16d8e03eb15bc
**Dictamen:** 🔴 ROJO — bug de clasificación FES en integración VBAK

## Pregunta del usuario

> 4190139948 ¿cómo aparece? Tiene pedido FES 1168016 en VBFA (VBELV=4190139948, C→C 0001168002).
> ¿Sería un FES por la regla C→C? ¿Qué pasa entonces?

## Respuesta: SÍ es FES por regla C→C, pero el modelo NO lo clasifica así

### 1. Flujo VBFA confirmado en la base (DMF_VTA_PRD)

```
C 4190139948 → C 0001168002   (02-07-2026)  ← flujo C→C EXISTE
C 4190139948 → J 0082389564   (02-07-2026)  entrega original
C 4190139948 → J 0082389593   (02-07-2026)  entrega posterior
C 4190139948 → M 0091785353   (02-07-2026)  manifiesto
C 4190139948 → R 4940745546   (02-07-2026)  factura
```

### 2. AUART en VBAK_SAP

| Pedido | AUART | VTWEG | Rol |
|---|---|---|---|
| 4190139948 | **ZPDA** | 43 | Original |
| 0001168002 | **ZPPO** | 43 | Posterior FES |
| 1168016 | ZMAY | 46 | Posterior del flujo |

### 3. Estado en la master (modelo)

- 4190139948: **NO está en la master** (ni master ni tracking con ese ID).
- 1168002: **NO está en la master**.
- 1168016: SÍ está, pero como:
  ```
  PED_TEXTO_ESTADO = "VBAK SIN ZART"
  ES_FES = False
  REGLA_CLASIFICACION_FES = "NO FES; VALIDADO VBFA C-C"
  SEGMENTO_ANALISIS = "FLUJO NORMAL"
  ```

## Causa raíz (bug)

`Fact_Pedidos_Auditoria.tmdl` línea **4496** (bloque de integración VBAK):

```m
VBAKAddReglaFES = Table.AddColumn(VBAKAddSaldo, "REGLA_CLASIFICACION_FES",
    each "NO FES; VALIDADO VBFA C-C", type text),
```

Cuando un pedido es incorporado por el append VBAK, la columna
`REGLA_CLASIFICACION_FES` se llena con la etiqueta **FIJA**
`"NO FES; VALIDADO VBFA C-C"`, sin verificar realmente el flujo VBFA.

El pedido original 4190139948 (AUART=ZPDA) no quedó en el universo principal
`#FACT_NS_MASTER_AUD_V3` (por no tener cierre/factura dentro de la ventana),
y sus pedidos posteriores FES (1168xxx) fueron agregados por el append VBAK
con la etiqueta fija NO FES.

## Impacto

- Pedidos que son FES por la regla C→C quedan como NORMAL/NO FES.
- Universo FES subestimado; NS y lienzos distorsionados.
- 523 pedidos del Excel data_sap.xlsx afectados (misma causa).

## Corrección requerida (ChatGPT)

El bloque VBAK (línea ~4496) debe **verificar el flujo VBFA C→C** antes de
etiquetar. Si el pedido original tiene C→C en VBFA (como 4190139948→1168002),
debe clasificarse como FES, no con la etiqueta fija.

## Archivos

- 00_git.txt
- RESULTADO.md
