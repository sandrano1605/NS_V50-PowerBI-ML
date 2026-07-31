# REQ-005 · SVG sin hover técnico

La prueba visual demostró que los visuales `tableEx` con medidas `Image URL` pueden mostrar el valor `data:image/svg+xml` aunque se configure un tooltip de página. Por este motivo, todos los visuales que proyectan SVG deben mantener `visualTooltip.show=false`.

Las preguntas de negocio y explicaciones deben permanecer visibles en el lienzo, no depender del hover del SVG.

El LLM local no debe modificar el PBIP. Debe hacer pull, abrir Power BI, ejecutar Actualizar todo y comprobar que ningún SVG muestra código técnico. Solo debe generar evidencia.