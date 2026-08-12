# Próxima auditoría local — descubrir fuente de posiciones YV01

## Estado confirmado

`INC-015` ya tiene causa raíz técnica confirmada por evidencia `a55afbf`:

- `VBAP_SAP` = `USER_TABLE` física.
- `dbo.VBAP` no existe en `DMF_VTA_PRD`.
- `YV01` = 349.215 headers recientes y 0 posiciones en `VBAP_SAP`.
- La cobertura 58,3% de `Lineas_y_unidades_por_pedidos` es estructural.
- Hipótesis `AEDAT`, ceros/padding y refresh quedan descartadas.

No repetir la auditoría anterior.

## Objetivo único

Determinar si `DMF_VTA_PRD` ya contiene **otra tabla o vista** que tenga posiciones de pedidos `YV01` y que pueda abastecer:

- `Pedido` (`VBELN`)
- `Lineas` (idealmente `POSNR` o granularidad equivalente)
- `Suma_Unidades` (idealmente `KWMENG` o cantidad equivalente)

El auditor local es read-only funcional. No modificar Power BI ni objetos SQL.

## Preflight

```powershell
git fetch origin
git pull --ff-only origin work/ns-lienzo-02-ingreso-pedidos
git rev-parse HEAD
git ls-remote origin refs/heads/work/ns-lienzo-02-ingreso-pedidos
```

LOCAL y REMOTO deben coincidir.

## P0 — Ejecutar descubrimiento SQL

Ejecutar contra `DMF_VTA_PRD` el script versionado:

```text
Scripts/audit_local/inc015_yv01_source_discovery.sql
```

El script solo usa `SELECT` y tablas temporales de sesión.

Guardar salida completa en:

```text
raw/inc015_yv01_source_discovery.txt
```

## P0 — Resultado obligatorio

Reportar las siguientes secciones:

1. `OBJETOS CON NOMBRE RELACIONADO A VBAP / YV01 / POSICION`
2. `CANDIDATOS POR FIRMA DE COLUMNAS`
3. `PROBE MUESTRA YV01 (200 HEADERS)`
4. `COBERTURA COMPLETA PARA CANDIDATOS CON HITS`

Para cada candidato con `matched_sample_headers > 0`, informar:

- schema / objeto / tipo;
- si tiene `POSNR`;
- si tiene `KWMENG`;
- si tiene `MATNR`;
- cobertura de la muestra;
- cobertura completa YV01 reciente;
- cantidad de filas encontradas.

## Dictamen

Emitir exactamente una de estas salidas:

### `FUENTE_YV01_COMPLETA_ENCONTRADA`
Existe un objeto con cobertura YV01 material y columnas suficientes para calcular líneas y unidades.

Recomendación: entregar nombre exacto del objeto y SQL agregado equivalente a:

```sql
SELECT
    VBELN AS Pedido,
    COUNT(*) AS Lineas,
    SUM(ISNULL(KWMENG,0)) AS Suma_Unidades
FROM <FUENTE>
GROUP BY VBELN;
```

No modificar el modelo localmente.

### `FUENTE_YV01_PARCIAL_ENCONTRADA`
Existe cobertura material, pero faltan `KWMENG` o granularidad fiable para líneas/unidades.

Recomendación: documentar qué sí permite calcular y qué columna/fuente falta.

### `SIN_FUENTE_YV01_EN_DMF_VTA_PRD`
Ningún objeto con firma de posición tiene hits YV01 relevantes.

Recomendación: no modificar `Lineas_y_unidades_por_pedidos`; solicitar/exponer nueva réplica o vista desde SAP/BW para posiciones YV01.

## Sanidad mínima

No repetir la regresión integral. Solo registrar que siguen vigentes como baseline:

- RE evaluables: 1.941 (salvo refresh nuevo documentado)
- match actual: 1.131 / 1.941 = 58,3%
- FIND-002A GREEN
- INC-011 GREEN
- INC-007B GREEN

## Entrega

Crear paquete de evidencia normal, incluir la salida SQL y actualizar `LOCAL_LATEST.json` a `READY_FOR_CHATGPT`.

No implementar cambios funcionales en `NS.SemanticModel/**` ni `NS.Report/**`.
