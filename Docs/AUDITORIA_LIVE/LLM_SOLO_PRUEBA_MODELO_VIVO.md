# Instrucción final al LLM local — solo prueba y evidencia

El repositorio ya contiene las correcciones funcionales. No modificar PBIP, TMDL, DAX, Power Query, Python, relaciones, posiciones, preguntas ni tooltips.

## Recuperación

```powershell
git switch work/ns-live-audit
git fetch origin
git pull --ff-only origin work/ns-live-audit
git status --short
git rev-parse HEAD
```

## Trabajo permitido

1. Abrir `NS.pbip`.
2. Ejecutar **Actualizar todo**.
3. Conectar MCP al modelo vivo.
4. Comprobar que los visuales SVG decorativos no muestran código técnico.
5. Comprobar que los 10 visuales analíticos listados en `REQ004_TARGETS.csv` conservan su tooltip de negocio ReportPage y no muestran `data:image/svg+xml`, XML, URI ni DAX.
6. Validar las 12 filas de `latest/business_questions_matrix.csv` contra el resultado real del visual.
7. Validar medidas y regresión sin modificar nada.
8. Generar únicamente evidencia en un nuevo run.

## Resultados obligatorios

- Pedidos evaluables: 1.616
- Pedidos fuera SLA: 360
- NS: 77,72%
- Clientes fuera SLA: 251
- Recurrente 3M: 3
- Recurrente 2M: 27
- Puntual 1M: 221
- Pedido 4190139455: OK
- Pedido 1167577: OK
- Santiago: SLA interno 4 DH
- Regiones: SLA interno 5 DH
- FES/FES + SALDO: cierre por último manifiesto; respaldo por última fecha de transporte válida solo cuando el manifiesto no esté informado y el transporte represente el cierre oficial.

## Evidencia

Crear `Docs/AUDITORIA_LIVE/runs/<timestamp>_validacion_final_modelo_vivo/` con:

- `00_resumen.md`
- `01_refresh.txt`
- `02_preguntas_visuales.csv`
- `03_medidas_modelo_vivo.csv`
- `04_tooltips_svg.csv`
- `05_regresion_pedidos.csv`
- `06_coherencia_lienzos.csv`
- `07_limitaciones.md`
- `RESULTADO.md`
- `manifest.json`

## Estado

- VERDE: refresh OK, métricas coinciden, 12/12 preguntas coherentes, ningún SVG muestra código y los 10 tooltips de negocio funcionan.
- AMARILLO: no aparece código, pero existe diferencia visual o tooltip de negocio incompleto.
- ROJO: refresh falla, cambia una métrica, aparece código SVG o una pregunta no coincide con el visual.

Realizar solamente un commit de evidencia:

```powershell
git add Docs/AUDITORIA_LIVE
git commit -m "audit(modelo): registrar validacion final en vivo"
git push origin work/ns-live-audit
```
