# IN02 — Diagnóstico fallback VBAK hora (post-fix eb07b64)

## Situación

El fix `eb07b64` (fallback VBAK.ERZET para canales 43/45 cuando PED_FECHA_HORA=00:00) fue aplicado en el modelo. Sin embargo, **los pedidos con ZERZET_PED=000000 siguen en "Sin hora válida"** (canal 43: 149, canal 45: 35; total 184 en el refresh actual).

El fallback NO está recuperando ningún pedido.

## Causa raíz exacta

`VBAK_SAP.ERZET` es **varchar(8)** con formato texto `'16:03:02'` (incluye `:`).

El SQL del fix hace:

```sql
TRY_CONVERT(
    TIME(0),
    STUFF(
        STUFF(
            RIGHT('000000' + LTRIM(RTRIM(CONVERT(VARCHAR(6), V.ERZET))), 6),
            3, 0, ':'
        ),
        6, 0, ':'
    )
) AS HORA_VBAK
```

Problema: `CONVERT(VARCHAR(6), '16:03:02')` = `'16:03:'` (trunca a 6 caracteres dejando `:` al final).

- `RIGHT('000000' + '16:03:', 6)` = `'16:03:'`
- `STUFF(STUFF('16:03:', 3, 0, ':'), 6, 0, ':')` = formato inválido
- `TRY_CONVERT(TIME(0), ...)` = **NULL**

Resultado: `HORA_VBAK = NULL` para TODOS los pedidos → el fallback nunca aplica.

## Evidencia SQL

```
ERZET       conv6      right6     hora_vbak
'16:03:02'  '16:03:'   '16:03:'   NULL
```

Conversión alternativa correcta:

```
ERZET       conv108      sin_colon  TRY_CONVERT directo
'16:03:02'  '16:03:02'   '160302'   16:03:02  ✓
```

`TRY_CONVERT(TIME(0), ERZET)` directo sobre `'16:03:02'` = `16:03:02` ✓ (SQL Server parsea texto hh:mm:ss).

## Fix correcto recomendado

Reemplazar el bloque `HORA_VBAK` por:

```sql
TRY_CONVERT(TIME(0), LTRIM(RTRIM(CONVERT(VARCHAR(8), V.ERZET)))) AS HORA_VBAK
```

o simplemente:

```sql
TRY_CONVERT(TIME(0), V.ERZET) AS HORA_VBAK
```

Dado que ERZET es varchar(8) texto `HH:MM:SS`, TRY_CONVERT(TIME(0), ERZET) lo parsea correctamente.

## Impacto esperado tras corregir la conversión

- Los ~153 pedidos 43/45 con ZART 000000 y VBAK.ERZET válido pasarán de "Sin hora válida" a "Hasta/Después de 14:30".
- Canal 43: 120 recuperables (99.17%)
- Canal 45: 33 recuperables (100%)
- Restarían ~44 pedidos residuales (diferencia Power BI 197 vs ZART 154 + 20 VBAK + otros)

## Nota

El join PED_KEY sí funciona: los pedidos existen en VBAK_SAP con VTWEG 43/45 y ERZET válido. El único bug es la conversión de formato de hora.
