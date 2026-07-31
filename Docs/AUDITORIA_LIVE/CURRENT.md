# Estado actual

- Rama: work/ns-live-audit
- Commit: PENDING (primer import del proyecto)
- Fecha: 2026-07-31
- Requerimiento: Visual "CLIENTES QUE REPITEN FUERA SLA" — mostrar todos los clientes fuera SLA (>= 1 mes), ordenar por recurrencia, actualizar título
- Estado: VERDE
- Refresh: OK (modelo v15 con datos cargados, 1.695 pedidos / 1.616 evaluables)
- Modelo vivo: Validado vía MCP (Resultados: 251 clientes = 3+27+221)
- Archivos modificados: Medidas.tmdl (5 medidas), visual.json fa_clientes_recurrentes, .gitignore, Docs/AUDITORIA_LIVE, AGENTS.md

# Qué cambió

1. Las 5 medidas "Visible" de recurrencia cambian de `IF([FA Meses Fuera SLA Cliente] >= 2, ...)` a `>= 1`:
   - FA Meses Fuera SLA Cliente Visible
   - FA Recurrencia Cliente Visible
   - FA Pedidos Fuera SLA Cliente Visible
   - FA % Fuera SLA Cliente Visible
   - FA DH Fuera SLA Cliente Visible
2. El visual `fa_clientes_recurrentes` ordena por:
   - FA Meses Fuera SLA Cliente Visible DESC
   - FA Pedidos Fuera SLA Cliente Visible DESC
   - FA DH Fuera SLA Cliente Visible DESC
3. Título actualizado a: "1. CLIENTES FUERA SLA · FRECUENCIA EN LOS ÚLTIMOS 3 MESES → Recurrente 3M → 2M → 1M"

# Qué no cambió

- Cohorte de los lienzos 00 y 01 (1.616 pedidos evaluados).
- SLA interno (Santiago 4 DH / Regiones 5 DH).
- Promesa cliente (Santiago 5 DH / Regiones 7 DH).
- Lógica de cierre FES (manifiesto) y NORMAL/SALDO (despacho).
- Campos del visual (cliente, vendedor, flujo).
- Ninguna otra medida del modelo.

# Medidas afectadas

| Medida | Antes | Después |
|---|---|---|
| FA Meses Fuera SLA Cliente Visible | >= 2 | >= 1 |
| FA Recurrencia Cliente Visible | >= 2 | >= 1 |
| FA Pedidos Fuera SLA Cliente Visible | >= 2 | >= 1 |
| FA % Fuera SLA Cliente Visible | >= 2 | >= 1 |
| FA DH Fuera SLA Cliente Visible | >= 2 | >= 1 |

# Visuales afectados

- `fa_clientes_recurrentes` (página "01 Análisis Fuera SLA") — sort + título.

# Casos probados

- Pedidos clave: 4190139455, 1167577 (ambos FES, cierran por manifiesto, cumplen SLA).
- Recurrente 3M: 3 clientes. Recurrente 2M: 27. Puntual 1M: 221. Total: 251.
- Lienzos 00 vs 01: 1.616 pedidos / 360 fuera SLA / NS 77,72% / diferencia 0.

# Resultados antes y después

| Métrica | Antes | Después | Esperado |
|---|---|---|---|
| Clientes visibles | 30 (2M+) | 251 (todos) | 251 |
| Recurrente 3M | 3 | 3 | 3 |
| Recurrente 2M | 27 | 27 | 27 |
| Puntual 1M | excluidos | 221 | 221 |
| Pedidos evaluados | 1.616 | 1.616 | 1.616 |
| Fuera SLA | 360 | 360 | 360 |
| NS | 77,72% | 77,72% | 77,72% |
| Diferencia lienzos | 0 | 0 | 0 |

# Riesgos pendientes

- Validación de renderizado visual requiere abrir Power BI Desktop (instancia cerrada al persistir visual.json en disco).
- Power BI Desktop sobrescribió la edición directa del visual.json al cerrar; se reaplicó con la instancia cerrada. Si se abre Power BI y se guarda, el sort/título persisten porque ya están en disco.
- El subtítulo se integró al título porque tableEx no expone subtítulo nativo en este esquema.

# Archivos de evidencia

- `Docs/AUDITORIA_LIVE/runs/20260731_033000_visual_clientes_fuera_sla/` (00 a 12 + RESULTADO.md)
- `Docs/AUDITORIA_LIVE/latest/` (manifest.json, RESULTADO.md, comparacion.csv, casos_auditoria.csv)
- `Docs/AUDITORIA_LIVE/regression_cases.csv` (12 casos activos)

# Instrucción para reproducir

1. Abrir `NS.pbip` en Power BI Desktop.
2. `Actualizar todo` (1.695 pedidos / 1.616 evaluables).
3. Ir a página "01 Análisis Fuera SLA".
4. Verificar tabla "1. CLIENTES FUERA SLA · FRECUENCIA EN LOS ÚLTIMOS 3 MESES":
   - 251 filas visibles.
   - Primer bloque: 3 clientes Recurrente 3M.
   - Segundo bloque: 27 clientes Recurrente 2M.
   - Tercer bloque: 221 Puntual 1M.
5. Cambiar el slicer de mes: la tabla no debe perder los meses (medida con REMOVEFILTERS/TREATAS).
