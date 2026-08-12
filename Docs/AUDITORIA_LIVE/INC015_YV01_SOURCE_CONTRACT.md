# INC-015 — Contrato técnico de fuente para posiciones YV01

## Estado

`INC-015` está bloqueado por fuente.

Diagnóstico confirmado:

- `VBAP_SAP` es una `USER_TABLE` física.
- `dbo.VBAP` no existe en `DMF_VTA_PRD`.
- `YV01` concentra el mayor gap de posiciones: 349.215 cabeceras recientes y 0 posiciones en `VBAP_SAP`.
- La búsqueda de fuentes alternativas en 33 bases visibles no encontró ningún objeto con cobertura YV01.
- La cobertura actual de `Lineas_y_unidades_por_pedidos` (58,3% del universo RE evaluable del refresh auditado) es estructural mientras no exista una fuente de posiciones YV01.

No modificar `Lineas_y_unidades_por_pedidos` hasta que exista una fuente que cumpla este contrato.

---

## Objetivo de la nueva fuente

Exponer en SQL Server las posiciones de pedidos SAP cuyo tipo de documento (`VBAK.AUART`) sea `YV01`, con granularidad de posición de pedido.

La fuente puede ser:

- una tabla replicada;
- una vista sobre una réplica SAP completa;
- una tabla staging alimentada por ETL;
- otro objeto SQL estable accesible desde Power BI.

No se requiere que el objeto se llame `VBAP`; sí se requiere que tenga cobertura funcional equivalente para los pedidos YV01 del universo.

---

## Contrato mínimo de columnas

Columnas obligatorias:

| Campo | Tipo lógico | Uso |
|---|---|---|
| `VBELN` | texto / varchar | Número de pedido SAP; clave de cruce con `Fact_Tracking[PEDIDO]` |
| `POSNR` | texto o entero | Número de posición; permite contar líneas sin depender de duplicados físicos |
| `KWMENG` | numérico | Cantidad solicitada; alimenta `Suma_Unidades` |

Columnas fuertemente recomendadas:

| Campo | Uso |
|---|---|
| `AEDAT` | actualización incremental / auditoría temporal |
| `MATNR` | trazabilidad y validación de posición |
| `WERKS` | validación por centro y futura segmentación |
| `ABGRU` | distinguir posiciones rechazadas/anuladas si negocio lo requiere |
| `PSTYV` | validar categorías de posición |

Si la réplica puede exponer `AUART` ya resuelto, es útil pero no obligatorio: se puede obtener desde `VBAK_SAP` por `VBELN`.

---

## Reglas de calidad obligatorias

1. `VBELN` no puede ser nulo.
2. `POSNR` no puede ser nulo para posiciones válidas.
3. La combinación `VBELN + POSNR` debe ser única en la salida consumible por Power BI, o debe documentarse la regla de deduplicación.
4. `KWMENG` debe conservar el valor SAP de la posición; no preagregar múltiples posiciones en una sola fila.
5. La fuente debe incluir pedidos `YV01` recientes que existan en `VBAK_SAP`.
6. No debe excluir YV01 por tipo de documento, canal o volumen sin una regla de negocio explícita.
7. Debe existir una fecha de actualización o mecanismo operativo que permita comprobar frescura.

---

## Cobertura de aceptación

Antes de modificar Power BI, la fuente candidata debe pasar una auditoría contra `VBAK_SAP`.

Universo de control:

```sql
SELECT DISTINCT
    CONVERT(varchar(20), VBELN) AS VBELN
FROM dbo.VBAK_SAP
WHERE ERDAT > GETDATE() - 90
  AND AUART = 'YV01';
```

La cobertura se calcula como:

```text
pedidos YV01 recientes con >= 1 posición en la nueva fuente
-----------------------------------------------------------
pedidos YV01 recientes en VBAK_SAP
```

Criterios:

- `>= 98%`: candidato APTO para implementación en Power BI.
- `95% a <98%`: candidato PARCIAL; requiere explicar faltantes antes del cambio.
- `<95%`: NO APTO como reemplazo de fuente.

Además, tomar una muestra de al menos 50 pedidos y validar `COUNT(DISTINCT POSNR)` y `SUM(KWMENG)` contra SAP/origen autorizado.

---

## Objeto objetivo recomendado

Si el equipo de datos puede crear un objeto específico en `DMF_VTA_PRD`, propuesta:

```text
dbo.VBAP_YV01_SAP
```

con al menos:

```text
VBELN
POSNR
KWMENG
AEDAT
MATNR
WERKS
```

La tabla/vista puede contener solo YV01 o una réplica VBAP más completa. Si contiene todos los AUART, mejor: permitirá sustituir `VBAP_SAP` de forma general y evitar una unión de fuentes.

---

## Estrategia de implementación Power BI cuando la fuente exista

### Opción preferida — fuente única completa

Si la nueva fuente cubre YV01 y también los AUART que hoy cubre `VBAP_SAP`, reemplazar la consulta actual de `Lineas_y_unidades_por_pedidos` por una única fuente completa.

Agregación esperada:

```sql
SELECT
    CONVERT(varchar(20), P.VBELN) AS Pedido,
    COUNT(DISTINCT P.POSNR) AS Lineas,
    SUM(ISNULL(P.KWMENG, 0)) AS Suma_Unidades
FROM <FUENTE_COMPLETA> AS P
WHERE <ventana temporal validada>
GROUP BY CONVERT(varchar(20), P.VBELN);
```

### Opción secundaria — unión VBAP_SAP + YV01

Solo si no existe una fuente única completa:

- conservar `VBAP_SAP` para AUART actualmente cubiertos;
- agregar la nueva fuente YV01;
- unir a nivel de posición;
- deduplicar por `VBELN + POSNR` antes de agregar;
- luego calcular `Lineas` y `Suma_Unidades`.

No hacer `UNION ALL` agregado por pedido sin control de solapamiento, porque podría duplicar líneas/unidades si una fuente futura empieza a contener YV01 parcialmente.

---

## Validación post-implementación obligatoria

Después del cambio remoto y refresh completo:

1. cobertura de pedidos evaluables con líneas/unidades;
2. cobertura por `AUART`, flujo, canal y mes;
3. pedidos sin match restantes con explicación;
4. comparación de `IN Líneas`, `FA Líneas`, `IN Unidades` y medidas relacionadas antes/después;
5. muestra de pedidos YV01 validada contra SQL;
6. confirmar que FIND-002A, INC-011 e INC-007B siguen GREEN;
7. solo entonces cambiar `INC-015` a GREEN.

---

## Condición de desbloqueo

ChatGPT puede implementar el fix remoto de INC-015 cuando exista un nombre de objeto SQL accesible desde Power BI y la auditoría de cobertura de ese objeto cumpla el criterio anterior.

Hasta ese momento, `INC-015` debe permanecer como:

```text
BLOCKED_SOURCE / SIN_FUENTE_YV01
```
