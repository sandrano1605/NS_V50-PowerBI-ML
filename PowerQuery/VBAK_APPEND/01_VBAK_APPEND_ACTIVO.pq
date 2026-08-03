// Crear como CONSULTA EN BLANCO normal, no como Parámetro de Power Query.
// MCP puede serializar incorrectamente los parámetros Logical como Text.
// Cambiar solo Configuracion de "DESACTIVADO" a "ACTIVO" después del preflight.
let
    Configuracion = "DESACTIVADO",
    Texto = Text.Upper(Text.Trim(Text.From(Configuracion))),
    Activar = List.Contains({"ACTIVO", "TRUE", "1", "SI", "SÍ"}, Texto)
in
    Activar
