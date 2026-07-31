# LLM local · Solo ejecución y evidencia de trazabilidad

## Regla absoluta

No modificar:

- SQL de producción;
- procedimientos almacenados;
- Power Query/M;
- Python;
- DAX;
- relaciones;
- columnas;
- visuales;
- reglas de cierre;
- SLA.

No borrar ninguna columna.

## Recuperación

```powershell
git fetch origin
git switch work/ns-lineage-audit
git pull --ff-only origin work/ns-lineage-audit
git status --short
git rev-parse HEAD
```

## Ejecución 1 · Trazabilidad estática

```powershell
python tools/build_ns_lineage.py --strict
```

Si el comando falla, registrar el error. No corregir el modelo.

## Ejecución 2 · Procedimiento VBFA

Ejecutar en SQL Server:

```text
sql/AUDIT_STP_GET_VBFA_TRAMO_FILTRO.sql
```

La llamada obligatoria es:

```sql
EXEC dbo.STP_GET_VBFA_TRAMO_FILTRO
    'M-J', 'C', '01-07-2026', '02-07-2026';
```

Exportar definición, parámetros, contrato y resultados.

## Ejecución 3 · Modelo vivo

1. Abrir el PBIP estable basado en `8be7824`.
2. Ejecutar Actualizar todo.
3. Conectar MCP.
4. Registrar fecha/hora, fecha mínima y máxima del contexto.
5. Exportar esquemas y conteos de:
   - Fact_Pedidos_Auditoria;
   - Fact_Tracking;
   - Fact_Hitos_Operacionales;
   - Fact_Pedidos;
   - Fact_Tiempos_Hitos;
   - Resultado;
   - auditoria;
   - Bloque_comercial;
   - Lineas_y_unidades_por_pedidos.
6. Exportar el contrato real de entrada de Python.
7. Comparar SP versus modelo por pedido.
8. Validar 4190139455 y 1167577.

## Métricas

No usar valores antiguos como constantes.

Registrar el snapshot actual y su ventana. La última ejecución informada fue:

- 1.907 evaluables;
- 394 fuera SLA;
- 79,34% NS;
- 265 clientes;
- recurrencia 4/36/225.

Solo comparar resultados generados en el mismo refresh.

## Evidencia

Crear:

```text
Docs/AUDITORIA_LIVE/runs/<timestamp>_trazabilidad_completa/
```

Según la estructura indicada en `REQ008_TRAZABILIDAD_COMPLETA.md`.

## Commit permitido

```powershell
git add Docs/AUDITORIA_LIVE
git commit -m "audit(lineage): registrar trazabilidad completa SQL a visual"
git push origin work/ns-lineage-audit
```

No agregar cambios en `NS.Report`, `NS.SemanticModel`, `sql/` ni `tools/`.
