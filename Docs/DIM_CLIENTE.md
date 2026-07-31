# Corrección Dim_Cliente — V38

- `Dim_Cliente` se obtiene con una sola consulta SQL contra `DMF_VTA_PRD`.
- Universo: pedidos creados en los últimos 90 días y canales 42–47.
- Una fila por `CLIENTE_CODIGO`.
- Nombre desde `KNA1_SAP` con clave normalizada.
- Vendedor: asignación vigente; si no existe, la más reciente.
- `Nombre_Cliente` y `Cliente_Vendedor` quedan como tablas ocultas derivadas de `Dim_Cliente`, sin nuevas conexiones a la base.
- Se retiraron tres relaciones automáticas bidireccionales creadas por `Doc_Conclusiones (2)`.
- El archivo `DIM_CLIENTE_SQL_CHECK.sql` permite auditar duplicados y clientes sin maestro.

La consulta no pudo ejecutarse desde este entorno porque el servidor `128.1.3.21:1433` rechazó la conexión externa. La validación realizada aquí es estructural y de lógica SQL/M; el resultado vivo debe confirmarse al actualizar en Power BI dentro de la red corporativa.
