# REQ-008 · Trazabilidad completa de `Fact_Pedidos_Auditoria` y VBFA

## Rama

`work/ns-lineage-audit`

## Objetivo

Construir una trazabilidad reproducible desde la fuente SQL hasta cada visual del reporte, incluyendo:

1. Procedimientos almacenados y consultas SQL.
2. Power Query/M.
3. Tablas derivadas.
4. Python.Execute.
5. Relaciones, claves y metadatos.
6. Medidas DAX.
7. Visuales y tooltips.
8. Traducciones del modelo.
9. Candidatos de columnas a conservar o recortar.

No se autoriza borrar columnas durante esta fase.

---

# 1. Fuentes que deben quedar trazadas

## Fuente maestra

- `Fact_Pedidos_Auditoria`
- 181 columnas actuales, verificadas desde el TMDL/modelo vivo.

## Tablas consumidoras directas o indirectas

- `Fact_Tracking`
- `Fact_Hitos_Operacionales`
- `Fact_Pedidos`
- `Fact_Tiempos_Hitos`
- `Resultado`
- `auditoria`
- `Dim_Pedido`
- `Cliente_Vendedor`
- cualquier otra tabla detectada por el auditor automático.

## Fuentes externas independientes

- `Bloque_comercial`
- `Lineas_y_unidades_por_pedidos`
- otras consultas SQL/API que no dependan de `Fact_Pedidos_Auditoria`.

Deben figurar como ramas independientes, no como consumidoras de la tabla maestra.

---

# 2. Procedimiento VBFA obligatorio

Auditar exactamente:

```sql
EXEC dbo.STP_GET_VBFA_TRAMO_FILTRO
    'M-J',
    'C',
    '01-07-2026',
    '02-07-2026';
```

Usar:

```text
sql/AUDIT_STP_GET_VBFA_TRAMO_FILTRO.sql
```

No asumir el significado de `M-J` o `C`. Debe demostrarse desde:

- definición del procedimiento;
- parámetros;
- filtros VBFA;
- códigos de tipo documental;
- esquema de salida;
- resultados reales.

## Evidencia requerida del SP

- definición SQL completa;
- fecha de última modificación;
- parámetros y tipos;
- contrato de salida;
- resultado 01-07-2026 a 02-07-2026;
- resultado de control 30-06-2026 a 03-07-2026;
- cantidad de filas;
- cantidad de pedidos originales;
- duplicados;
- primera y última fecha por pedido;
- mapeo entre pedido posterior, entrega, manifiesto y transporte;
- comparación con el modelo.

---

# 3. Regla de cierre FES

La trazabilidad debe demostrar, no inferir:

```text
FES/FES + SALDO → último manifiesto válido
NORMAL/SALDO    → último despacho válido
```

La última fecha de transporte puede actuar como respaldo únicamente cuando:

1. el manifiesto no está informado;
2. el procedimiento y el flujo SAP prueban que el transporte representa el cierre oficial;
3. no corresponde a sincronización, creación técnica o evento intermedio.

Campos obligatorios de reconciliación:

- `PRIMERA_FECHA_PEDIDO_POSTERIOR`
- `ULTIMA_FECHA_PEDIDO_POSTERIOR`
- `PRIMERA_FECHA_ENTREGA_POSTERIOR`
- `ULTIMA_FECHA_ENTREGA_POSTERIOR`
- `PRIMERA_FECHA_MANIFIESTO`
- `ULTIMA_FECHA_MANIFIESTO`
- última fecha de transporte disponible;
- `FECHA_CIERRE`;
- `FUENTE_CIERRE`;
- `DIAS_INTERNOS_DH`;
- `SLA_INTERNO_DH`;
- cumplimiento.

Casos obligatorios:

- `4190139455`
- `1167577`

---

# 4. Auditor automático de dependencias

Ejecutar:

```powershell
python tools/build_ns_lineage.py --strict
```

Salidas:

```text
Docs/AUDITORIA_LIVE/latest/lineage/lineage_edges.csv
Docs/AUDITORIA_LIVE/latest/lineage/fact_pedidos_auditoria_columns.csv
Docs/AUDITORIA_LIVE/latest/lineage/lineage_summary.json
```

El auditor busca dependencias en:

- TMDL;
- M;
- DAX;
- Python;
- relaciones;
- JSON de visuales;
- traducciones.

## Estados permitidos por columna

- `CONSERVAR_REFERENCIADA`
- `CONSERVAR_CLAVE_O_CIERRE`
- `NO_BORRAR_SIN_PRUEBA_CONTRATO`
- `CANDIDATA_A_RECORTAR`

`CANDIDATA_A_RECORTAR` no autoriza su eliminación.

---

# 5. Corrección del análisis 87/94

El análisis previo de 87 necesarias y 94 borrables debe tratarse como hipótesis inicial.

Antes de aprobarlo se debe comprobar:

1. que el total de nombres únicos sea exactamente 181;
2. que conservar y recortar no tengan intersección;
3. que la unión cubra las 181 columnas;
4. que los subtotales de cada grupo coincidan con sus nombres;
5. que no existan columnas usadas mediante acceso dinámico;
6. que Python no dependa del esquema completo;
7. que `Table.Schema` sea aceptado como cambio funcional si se recorta;
8. que traducciones huérfanas sean eliminadas o actualizadas;
9. que relaciones, `sortByColumn`, filtros y visuales no queden rotos.

## Advertencia Python

`Resultado` contiene `Python.Execute`. Debe generarse un contrato real de entrada:

- columnas recibidas por Python;
- columnas leídas explícitamente;
- columnas leídas dinámicamente;
- columnas obligatorias aunque estén vacías;
- tipos esperados;
- resultado del script antes y después del recorte.

Ninguna columna de entrada a Python puede borrarse únicamente porque no aparezca en una búsqueda simple.

---

# 6. Prueba A/B antes de recortar

## A · Modelo actual

Registrar en un único refresh:

- fecha/hora de actualización;
- fecha mínima y máxima;
- cantidad de filas de cada tabla;
- esquema de cada tabla;
- relaciones activas;
- errores Power Query/Python;
- métricas principales;
- casos de pedidos.

## B · Modelo candidato

Aplicar el recorte en una rama separada y repetir exactamente la misma prueba.

## Criterios de igualdad

Deben coincidir dentro del mismo snapshot:

- pedidos evaluables;
- fuera SLA;
- NS;
- clientes fuera SLA;
- recurrencia 3M/2M/1M;
- SLA zonal;
- fecha de cierre;
- días hábiles;
- resultados Python;
- tablas y relaciones;
- visuales.

Los valores `1.616 / 360 / 77,72% / 251` son un snapshot histórico, no una constante.

Última validación informada:

- pedidos evaluables: `1.907`;
- fuera SLA: `394`;
- NS: `79,34%`;
- clientes fuera SLA: `265`;
- recurrencia: `4 / 36 / 225`.

Esos valores también cambiarán cuando cambie `GETDATE()` o la fuente. Toda comparación debe usar el mismo refresh y ventana.

---

# 7. Entregables del modelo vivo

Crear:

```text
Docs/AUDITORIA_LIVE/runs/<timestamp>_trazabilidad_completa/
```

Con:

```text
00_resumen.md
01_procedimiento_definicion.sql
02_procedimiento_parametros.csv
03_procedimiento_esquema_salida.csv
04_vbfa_tramo_raw.csv
05_vbfa_tramo_control_borde.csv
06_vbfa_primera_ultima_fecha.csv
07_vbfa_duplicados.csv
08_lineage_edges.csv
09_fpa_columnas_clasificadas.csv
10_python_input_contract.csv
11_relaciones_y_claves.csv
12_medidas_y_visuales.csv
13_comparacion_sp_modelo.csv
14_pedidos_clave.csv
15_snapshot_metricas.csv
16_hallazgos.md
RESULTADO.md
manifest.json
```

---

# 8. Estado final

## VERDE

- 181/181 columnas clasificadas;
- 0 referencias rotas;
- SP documentado y ejecutado;
- resultados VBFA reconciliados;
- Python con contrato explícito;
- casos clave coinciden;
- candidatos de recorte probados A/B;
- ningún visual, relación o medida roto.

## AMARILLO

- trazabilidad completa, pero existen consumidores dinámicos o diferencias no resueltas;
- no se autoriza recorte.

## ROJO

- columnas sin clasificar;
- referencias rotas;
- procedimiento no reconciliado;
- Python falla;
- métricas o cierres cambian sin explicación.

---

# 9. Trabajo permitido al LLM local

El LLM local no debe decidir qué columnas borrar.

Solo debe:

1. recuperar `work/ns-lineage-audit`;
2. ejecutar el auditor;
3. ejecutar el SQL de auditoría;
4. conectar MCP;
5. generar evidencia del modelo vivo;
6. informar diferencias;
7. hacer un commit únicamente de evidencia.

Commit permitido:

```text
audit(lineage): registrar trazabilidad completa SQL a visual
```
