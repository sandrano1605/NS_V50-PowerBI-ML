# VBAK master inline

Cruce activo preparado para aplicar sobre `Fact_Pedidos_Auditoria`.

Alcance:

- anti-join por pedido normalizado;
- canales 42–47;
- exclusión FES por VBFA C→C y por `fecha_fes`;
- cliente y región obligatorios;
- secuencia pedido/entrega/factura/salida validada;
- marcador `VBAK SIN ZART`;
- sin cambios en visuales, DAX, relaciones o Python.
