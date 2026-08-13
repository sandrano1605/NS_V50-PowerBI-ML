# AUDITORÍA INTEGRAL — Tramo Logística/Operaciones (Flujo Normal)

## 1. Cómo se lee "Logística" en el modelo

La jerarquía ejecutiva (`Dim_Vista_Ejecutiva`) divide el flujo Normal en 2 macroprocesos:

```
1. Administrativo · SLA 1 DH
   ├ Creación → Comercial/SAC        (CREACION_COMERCIAL)
   ├ Comercial/SAC → Crédito          (COMERCIAL_CREDITO)
   └ Crédito → Ingreso a Logística    (CREDITO_ENTREGA)

2. Operaciones · SLA total 4 DH  ← aquí está "Logística"
   ├ Ingreso a Logística → Facturación  (ENTREGA_FACTURACION)
   └ Facturación → Despacho             (FACTURACION_DESPACHO)
```

"Logística" NO es un macroproceso separado: es el tramo **Operaciones**,
que arranca en "Ingreso a Logística" y termina en "Despacho".

## 2. Métricas internas del tramo operacional

| Código | Definición (TMDL) | Inicio | Fin |
|---|---|---|---|
| ENTREGA_FACTURACION | Ingreso Logística → Facturación | ENT_E | FAC_E |
| FACTURACION_DESPACHO | Facturación → Despacho | FAC_E | TRP_E |
| LOGISTICA_TOTAL | Entrega + transporte | ENT_E | TRP_E |
| OPERACIONES_TOTAL | Ingreso Logística + transporte | ENT_E | TRP_E |
| LEAD_CREACION_DESPACHO | Lead end-to-end | PED | TRP_E |

## 3. Valores vivos (modelo post-refresh)

| Métrica | Zona | Promedio | P90 | SLA | Fuera KPI |
|---|---|---|---|---|---|
| ENTREGA_FACTURACION | Santiago | 0,66 | 2 | 3 | 36 |
| ENTREGA_FACTURACION | Regiones | 0,86 | 2 | 3 | 94 |
| FACTURACION_DESPACHO | Santiago | 0,66 | 1 | 1 | 120 |
| FACTURACION_DESPACHO | Regiones | 0,58 | 1 | 1 | 143 |
| OPERACIONES_TOTAL | Santiago | 2,03 | 4 | **3** | 165 |
| OPERACIONES_TOTAL | Regiones | 2,46 | 5 | **4** | 239 |

## 4. HALLAZGO CRÍTICO — inconsistencia de SLA en la etiqueta

El macroproceso se llama **"Operaciones · SLA total 4 DH"**, pero:

- `OPERACIONES_TOTAL` tiene SLA zonal **3 DH (Santiago) / 4 DH (Regiones)** (línea 604 TMDL).
- El "4 DH" de la etiqueta corresponde al **SLA interno TOTAL** (1 admin + 3 op Santiago = 4),
  NO al tramo operacional puro.

**Consecuencia**: en Santiago, el tramo operacional tiene SLA 3 DH (no 4).
La etiqueta "SLA total 4 DH" es correcta como *SLA interno total*, pero ambigua
junto a la métrica OPERACIONES_TOTAL cuyo SLA real es 3/4. Verificar si el
negocio quiere "4 DH" = admin+op, o "3 DH" = solo op en Santiago.

## 5. Casos borde detectados (ESTADO_TRAZABILIDAD)

| Métrica | VÁLIDA | HITO OMITIDO | SEC. INVÁLIDA | SOLAPAMIENTO | PENDIENTE | NO INICIADO |
|---|---|---|---|---|---|---|
| ADMIN_TOTAL | 1662 | 175 | 93 | 114 | 53 | 0 |
| ENTREGA_FACTURACION | 1876 | 65 | 53 | 6 | 44 | 53 |
| FACTURACION_DESPACHO | 1499 | 0 | 61 | 0 | 1 | 97 |
| OPERACIONES_TOTAL | 1917 | 0 | 80 | 0 | 47 | 53 |
| LOGISTICA_TOTAL | 1502 | 0 | 58 | 0 | 45 | 53 |
| LEAD_CREACION_DESPACHO | 1504 | 0 | 56 | 0 | 98 | 0 |

### Interpretación de casos borde:
- **HITO OMITIDO**: un hito vacío hereda la fecha anterior y mide 0 DH (regla correcta).
  Ej: ENTREGA_FACTURACION con 65 omisiones (facturación hereda entrega).
- **SECUENCIA INVÁLIDA** (FECHA_FIN < FECHA_INICIO): ~53-80 casos por métrica.
  En OPERACIONES_TOTAL hay 80 con promedio DIAS_HABILES = 0 (se excluyen del dato).
  → El `FnDiasHabiles` retorna NULL cuando Fin < Inicio, por eso TIENE_DATO=FALSE.
- **SOLAPAMIENTO / REPROCESO**: 114 casos en ADMIN_TOTAL (fechas que se solapan).

## 6. Consistencia de medidas DAX (RE Promedio hito DH / RE P90)

Las medidas filtran `TIENE_DATO = TRUE()` → excluyen correctamente:
- SECUENCIA INVÁLIDA (DIAS_HABILES null)
- PENDIENTE / NO INICIADO (FECHA_FIN null)

El `RE Código nivel matriz` mapea:
- Subproceso → METRICA_CODIGO específica
- Macroproceso "Administrativo" → ADMIN_TOTAL
- Macroproceso "Operaciones" → OPERACIONES_TOTAL
- Nivel integral (sin macroproceso) → MAYORISTA_CIERRE_TOTAL

**Correcto.** Las medidas respetan el nivel jerárquico.

## 7. Cobertura de datos

- OPERACIONES_TOTAL: 2.097 pedidos, 1.942 con dato (92,6%), 155 sin dato (pendientes/inválidas).
- El denominador de cobertura es `RE Pedidos matriz` (cohorte cerrada evaluable).

## 8. Verificación Python — columnas crudas ZART

Las columnas fuente reales (ZART_TRACK_DATA_SAP) son compuestas (fecha+hora):

| Hito | Columnas crudas |
|---|---|
| Crédito (CRD) | ZP_UDATE_CRD + ZP_UTIME_CRD |
| Entrega (ENT) | ZP_ERDAT_ENT + ZP_ERZET_ENT |
| Factura (FAC) | ZP_ERDAT_FAC + ZP_UZEIT_FAC |
| Transporte (TRP) | ZP_ERDAT_TRP + ZP_UZEIT_TRP |
| Comercial (COM) | ZP_ERDAT_COM + ZP_ERZET_COM |

### Nulos en fechas de hitos (universo 3M, 2.035 pedidos):

| Hito | Nulos | % | Lectura |
|---|---|---|---|
| CRD (crédito) | 1.139 | 56% | Crédito no gestionado por separado → hereda comercial (0 DH) |
| FAC (factura) | 108 | 5,3% | Facturación hereda entrega |
| ENT (entrega) | 63 | 3,1% | Entrega hereda crédito |
| TRP (transporte) | 37 | 1,8% | Sin despacho aún |

### Muestra cruda (pedido 1162206):
```
PED: 2026-01-06 08:19  CRD: NULL (sin crédito)  ENT: 09:59  FAC: 2026-01-07 11:57  TRP: 2026-01-07 13:11
```
Lectura: el pedido no pasó por crédito (CRD null), entró a logística 08:19→09:59
(0 DH), facturó al día siguiente, despachó 13:11. ENTREGA_FACTURACION ≈ 1 DH,
FACTURACION_DESPACHO ≈ 0 DH. Coherente con el modelo.

## 9. Consistencia modelo vs Python

- Las columnas crudas confirman la lógica de herencia del TMDL (hito null → hereda anterior, 0 DH).
- Los promedios del modelo (ENTREGA_FACTURACION 0,77 DH; FACTURACION_DESPACHO 0,62 DH) son coherentes con la muestra cruda.
- CRD null 56% explica por qué "Crédito" promedia ~0,4-0,5 DH (la mayoría 0).

## 10. Dictamen

- ✅ Lectura de Logística correcta (subproceso de Operaciones).
- ✅ Regla de herencia de hitos omitidos correcta (0 DH).
- ✅ Medidas DAX filtran TIENE_DATO correctamente.
- ⚠️ **Etiqueta "SLA total 4 DH" ambigua** vs SLA real 3/4 por zona (DECISION_NEGOCIO).
- ⚠️ 80+ casos SECUENCIA INVÁLIDA en tramo operacional (calidad de dato, excluidos correctamente).
