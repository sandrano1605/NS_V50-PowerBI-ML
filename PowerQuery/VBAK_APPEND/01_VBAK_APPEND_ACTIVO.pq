// Crear como parámetro/consulta escalar en Power Query.
// Mantener FALSE durante el preflight. Cambiar a TRUE solo con todos los controles verdes.
false meta [
    IsParameterQuery = true,
    Type = "Logical",
    IsParameterQueryRequired = true,
    Description = "Activa el append controlado de pedidos VBAK faltantes en Fact_Pedidos_Auditoria."
]
