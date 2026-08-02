# REQ-009 · Medidas temporales de texto

Este commit activa la reparación determinística de:

- `RE Estado último mes`
- `RE Ventana análisis texto`

Alcance permitido:

- retirar `formatString: 0` de ambas medidas de texto;
- retirar los dos `lineageTag` huérfanos conocidos;
- conservar exactamente las expresiones DAX;
- validar el archivo antes de publicar la reparación.
