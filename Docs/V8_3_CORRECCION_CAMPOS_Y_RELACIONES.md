# V8.3 · Corrección de campos y relaciones dinámicas

- Se reemplazó `Fact_Tracking[MES_CREACION]` por `Dim_Fecha[AnioMes]` en los visuales mensuales.
- El parámetro de agrupación quedó limitado a dimensiones relacionadas: Cliente, Vendedor, Canal, Mes y Pedido.
- Vendedor utiliza `Dim_Responsable[RESPONSABLE_CODIGO]`, único campo disponible en esa dimensión.
- Se retiraron `Fact_Tracking[CLASIFICACION]` y `Fact_Tracking[HITO_ACTUAL]` del parámetro dinámico para evitar `InvalidUnconstrainedJoin`.
