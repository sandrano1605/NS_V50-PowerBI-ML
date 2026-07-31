# LLM local · Solo prueba y evidencia REQ-005

No modificar PBIP, TMDL, DAX, Power Query, Python, relaciones, preguntas, posiciones ni tooltips.

1. `git switch work/ns-live-audit`
2. `git fetch origin`
3. `git pull --ff-only origin work/ns-live-audit`
4. Abrir `NS.pbip`.
5. Ejecutar **Actualizar todo**.
6. Probar todos los visuales SVG registrados en `Docs/AUDITORIA_LIVE/latest/svg_inventory.csv`.
7. Confirmar que ningún hover muestre `data:image/svg+xml`, XML, URI, DAX o nombre técnico de medida.
8. Confirmar que los SVG rendericen correctamente.
9. Validar mediante MCP: 1.616 evaluables, 360 fuera SLA, NS 77,72%, 251 clientes, 3/27/221, pedidos 4190139455 y 1167577 OK.
10. Generar solamente evidencia y un commit `audit(svg): validar ausencia de hover tecnico en modelo vivo`.

No hacer correcciones. Si algo falla, documentar visual, página y captura.