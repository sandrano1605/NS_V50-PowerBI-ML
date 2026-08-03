# Integración controlada VBAK → Fact_Pedidos_Auditoria

## Estado de partida

- Rama base estable: `work/ns-lineage-audit`
- SHA base: `a8e818604826e689453769103d962cd3537399ed`
- Master observada: 1.973 pedidos
- `Pedidos_Normal_VBAK`: 2.158 pedidos
- Diferencia observada previamente: 257 pedidos
- Relación vigente: `Fact_Pedidos_Auditoria[PED_NUMERO_PEDIDO]` ↔ `Pedidos_Normal_VBAK[VBELN]`

Los 257 son **candidatos**, no una autorización para agregarlos sin controles. El append automático solo incorpora pedidos normales con canal 42–47, cliente, región, fecha de pedido y secuencia operativa coherente. Candidatos FES quedan en cuarentena hasta contar con clasificación VBFA.

## Archivos y nombres exactos de consultas

| Orden | Archivo | Nombre que debe tener en Power Query | Carga |
|---:|---|---|---|
| 0 | `00_VBAK_SCHEMA_PREFLIGHT.pq` | `VBAK_SCHEMA_PREFLIGHT` | Desactivada |
| 1 | `01_VBAK_APPEND_ACTIVO.pq` | `VBAK_APPEND_ACTIVO` | Parámetro lógico |
| 2 | `02_VBAK_ATRIBUTOS_MAYORISTA.pq` | `VBAK_ATRIBUTOS_MAYORISTA` | Desactivada |
| 3 | `05_VBAK_APPEND_PREFLIGHT_DETALLE.pq` | `VBAK_APPEND_PREFLIGHT_DETALLE` | Desactivada |
| 4 | `03_FACT_PEDIDOS_AUDITORIA_APPEND_BLOCK.pq` | Bloque dentro de `Fact_Pedidos_Auditoria` | La master conserva su carga |
| 5 | `04_VBAK_APPEND_CONTROL.pq` | `VBAK_APPEND_CONTROL` | Activar temporalmente para evidencia |

## Barrera 1 · Validación del kit

Ejecutar desde la raíz del repositorio:

```powershell
python tools/validate_vbak_append_kit.py
```

Resultado obligatorio:

```text
status = VERDE
pbip_changes = []
```

La rama de preparación no modifica `NS.Report` ni `NS.SemanticModel` antes de trabajar en Power BI Desktop.

## Barrera 2 · Preflight SQL

Crear `VBAK_SCHEMA_PREFLIGHT` y actualizarla. Todas las filas deben quedar `ESTADO = OK`.

Si falta una columna, detener la implementación. No cambiar nombres ni adivinar equivalencias.

## Barrera 3 · Candidatos con append desactivado

1. Crear `VBAK_APPEND_ACTIVO` con valor `false`.
2. Crear `VBAK_ATRIBUTOS_MAYORISTA`.
3. Crear `VBAK_APPEND_PREFLIGHT_DETALLE`.
4. Actualizar únicamente estas consultas.
5. Exportar el detalle y revisar:
   - pedidos únicos;
   - canal 42–47;
   - cliente y región informados;
   - fecha de pedido;
   - secuencia pedido → entrega → factura → salida;
   - candidatos FES en cuarentena;
   - motivo de cada fila no elegible.

La cantidad elegible puede ser menor a 257. No se debe forzar la diferencia.

## Inserción del bloque en la master

Abrir el Editor avanzado de `Fact_Pedidos_Auditoria`.

El final actual contiene:

```powerquery
    #"Filas ordenadas" = Table.Sort(FiltradoCanalesMayoristas,{{"PED_FECHA_HORA", Order.Descending}})
in
    #"Filas ordenadas"
```

Realizar exactamente estos cambios:

1. Agregar una coma al final del paso `#"Filas ordenadas"`.
2. Pegar a continuación todo el contenido de `03_FACT_PEDIDOS_AUDITORIA_APPEND_BLOCK.pq`.
3. Cambiar el resultado final por:

```powerquery
in
    ResultadoVBAK
```

No modificar el SQL original, nombres de columnas ni pasos previos.

## Prueba A · Parámetro FALSE

Con `VBAK_APPEND_ACTIVO = false`:

- refrescar `Fact_Pedidos_Auditoria`;
- refrescar el modelo completo;
- confirmar que la master mantiene el mismo conteo del snapshot;
- confirmar que no cambian métricas ni casos de regresión;
- ejecutar `VBAK_APPEND_CONTROL`;
- `VBAK_APPEND_FILAS` debe ser 0;
- `DUPLICADOS_MASTER` debe ser 0.

Si el resultado cambia con `false`, revertir el bloque.

## Prueba B · Parámetro TRUE

Cambiar únicamente `VBAK_APPEND_ACTIVO` a `true` y refrescar.

Controles obligatorios:

- `DUPLICADOS_MASTER = 0`;
- `APPEND_CLAVE_NULA = 0`;
- `APPEND_CANAL_FUERA = 0`;
- `APPEND_REGION_NULA = 0`;
- `APPEND_ES_FES = 0`;
- `APPEND_ES_SALDO = 0`;
- `APPEND_SALIDA_SIN_FACTURA = 0`;
- todas las filas agregadas tienen `PED_TEXTO_ESTADO = VBAK SIN ZART`;
- todas las filas agregadas tienen `AUD_ESTADO_GENERAL = REVISAR` y `AUD_REQUIERE_REVISION = true`.

## Tratamiento de fechas y cierre

Para filas elegibles normales:

- pedido: `VBAK_SAP.ERDAT + ERZET`;
- entrega: `Pedidos_Normal_VBAK[fecha_entrega]`;
- factura: `Pedidos_Normal_VBAK[fecha_factura]`;
- despacho/cierre normal: `Pedidos_Normal_VBAK[fecha_salida]`;
- primera y última fecha se igualan cuando VBAK solo dispone de una fecha;
- no se crean fechas FES ni manifiestos;
- no se infiere SALDO;
- candidatos con `fecha_fes` quedan fuera del append.

## Validación del modelo vivo

Después del refresh con `true`:

1. Confirmar que el proyecto abre sin error.
2. Confirmar que `Fact_Tracking` incluye las nuevas filas como cartera viva.
3. Los pedidos abiertos no deben entrar en la cohorte histórica cerrada.
4. Los pedidos cerrados solo entran si tienen salida válida.
5. Verificar `4190139455` y `1167577` sin regresión.
6. Comparar páginas 00 y 01 con filtros equivalentes.
7. Validar `Resultado`/Python sin errores.
8. Registrar conteos nuevos; no exigir snapshots históricos fijos.

## Rollback inmediato

El append puede desactivarse sin borrar código:

```text
VBAK_APPEND_ACTIVO = false
```

Si el modelo no abre o el refresh falla:

```powershell
git restore NS.Report NS.SemanticModel
git reset --hard a8e818604826e689453769103d962cd3537399ed
```

Usar `reset --hard` únicamente en la rama de trabajo y con el proyecto cerrado.

## Regla de publicación

El primer commit local debe contener únicamente los cambios normalizados por Power BI después de una prueba A y B verde. La evidencia debe ir en un segundo commit.
