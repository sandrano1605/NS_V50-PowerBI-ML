# V8.2 — Corrección TMDL de indentación

Se corrigió el error `Indentation` reportado por Power BI Desktop en `tables/Medidas.tmdl`.

Las siguientes expresiones se serializaron en una sola línea TMDL para evitar ambigüedad de sangría:

- FA FES Fuera SLA
- FA FES Fin Mes
- FA Líneas FES
- FA Unidades FES
- FA Arrastre Mes Siguiente

No se modificó la lógica DAX, las relaciones, los parámetros de campos ni el diseño del reporte.
