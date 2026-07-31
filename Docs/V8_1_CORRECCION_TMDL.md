# V8.1 · Corrección TMDL

Se corrigieron cinco medidas cuya expresión DAX multilínea comenzaba en la misma línea de la declaración `measure`. En TMDL, las expresiones multilínea deben comenzar en una línea indentada posterior al signo `=`.

Medidas corregidas:
- FA FES Fuera SLA
- FA FES Fin Mes
- FA Líneas FES
- FA Unidades FES
- FA Arrastre Mes Siguiente

Validaciones locales:
- JSON válido.
- Sin declaraciones de medida con patrón multilínea inválido `= CALCULATE(`.
- Sin cambios en relaciones, visuales, consultas M ni lógica DAX.
