# RESULTADO: Cierre definitivo lienzo 02 — PROYECTO NO ABRE (ROJO)

**Fecha:** 2026-08-04
**Rama:** work/ns-lienzo-02-ingreso-pedidos
**SHA local:** b64b000fa229c148718bb5be36144c357c7f932f
**SHA remoto:** b64b000fa229c148718bb5be36144c357c7f932f
**Dictamen:** 🔴 ROJO — el proyecto no abre por error fatal del motor M

## Error exacto

Al abrir NS.pbip, Power BI Desktop muestra:

```
Hay un problema con el contenido de definition en Power BI Project.
Error del motor M: "Microsoft.Data.Mashup.Preview; Se esperaba el token ','".
```

Stack: `BiProjectOperationHandler.LoadFromProject` →
`LocalAnalysisServicesDatabaseCreator.CreateAnalysisServicesDatabaseAsyncImpl` →
`TomDatabase.Update` → "No se han podido guardar las modificaciones en el servidor".

## Causa raíz demostrada

El commit `b64b000` (fix(lienzo-02): cerrar lectura horaria...) eliminó la
declaración `column __Medida` del TMDL de `Medidas`, pero:

1. **La partición M de Medidas sigue generando `__Medida`**:
   ```
   Origen = #table(type table [__Medida = Int64.Type], {{1}})
   ```
   (Medidas.tmdl línea 3520 — el motor M no puede mapear la columna generada
   contra el esquema declarado, que ya no la incluye).

2. **El archivo de cultura `es-ES.tmdl` conserva referencias huérfanas**:
   - línea 11196: "medida.entity___medida"
   - línea 11200: "ConceptualProperty": "__Medida"
   - línea 11209: "__medida"
   (referencias a la columna eliminada, no limpiadas en el commit).

3. `Fact_Tracking.tmdl` (ResultadoUnico = Table.Distinct) se ve sintácticamente
   correcto; el problema está en Medidas.

## Impacto

- El proyecto NO abre → no se puede refrescar ni probar el lienzo 02.
- Q1, Q2, Q3, botones, filtros y persistencia: NO VALIDADOS (bloqueados).

## Acción requerida (ChatGPT)

1. Restaurar la columna `__Medida` en `Medidas.tmdl` (con su lineageTag
   a999e59e-35e3-4a38-82ae-fee350894158) o reescribir la partición M de
   Medidas para que no genere `__Medida`.
2. Limpiar las referencias `__Medida`/`__medida` en `es-ES.tmdl`
   (líneas 11196-11209) si la columna no se restaura.
3. Re-publicar y re-ejecutar el LLM local.

## Archivos de evidencia

- 00_git.txt
- RESULTADO.md (este archivo)
- manifest.json
