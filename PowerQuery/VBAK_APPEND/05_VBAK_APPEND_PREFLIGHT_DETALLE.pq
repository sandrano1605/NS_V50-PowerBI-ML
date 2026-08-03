let
    FnNormalizaPedido = (Valor as any) as nullable text =>
        let
            Texto = try Text.Trim(Text.From(Valor)) otherwise null,
            Numero = if Texto = null or Texto = "" then null else try Int64.FromText(Texto) otherwise null
        in
            if Texto = null or Texto = "" then null
            else if Numero <> null then Text.From(Numero)
            else let SinCeros = Text.TrimStart(Texto, "0") in if SinCeros = "" then "0" else SinCeros,

    MasterKeys =
        Table.Distinct(
            Table.TransformColumns(
                Table.SelectColumns(Fact_Pedidos_Auditoria, {"PED_NUMERO_PEDIDO"}),
                {{"PED_NUMERO_PEDIDO", each FnNormalizaPedido(_), type nullable text}}
            ),
            {"PED_NUMERO_PEDIDO"}
        ),

    Atributos =
        Table.TransformColumns(
            VBAK_ATRIBUTOS_MAYORISTA,
            {{"PED_NUMERO_PEDIDO", each FnNormalizaPedido(_), type nullable text}}
        ),

    OperacionBase =
        Table.SelectColumns(
            Pedidos_Normal_VBAK,
            {"VBELN", "fecha_pedido", "fecha_entrega", "fecha_contabiliza", "fecha_factura", "fecha_fes", "fecha_salida"},
            MissingField.UseNull
        ),

    OperacionKey = Table.AddColumn(OperacionBase, "PED_NUMERO_PEDIDO", each FnNormalizaPedido([VBELN]), type nullable text),

    OperacionUnica =
        Table.Group(
            Table.SelectRows(OperacionKey, each [PED_NUMERO_PEDIDO] <> null),
            {"PED_NUMERO_PEDIDO"},
            {
                {"VBAK_FECHA_PEDIDO", each try List.Min(List.RemoveNulls([fecha_pedido])) otherwise null, type nullable date},
                {"VBAK_FECHA_ENTREGA", each try List.Min(List.RemoveNulls([fecha_entrega])) otherwise null, type nullable date},
                {"VBAK_FECHA_CONTABILIZA", each try List.Min(List.RemoveNulls([fecha_contabiliza])) otherwise null, type nullable date},
                {"VBAK_FECHA_FACTURA", each try List.Min(List.RemoveNulls([fecha_factura])) otherwise null, type nullable date},
                {"VBAK_FECHA_FES", each try List.Min(List.RemoveNulls([fecha_fes])) otherwise null, type nullable date},
                {"VBAK_FECHA_SALIDA", each try List.Max(List.RemoveNulls([fecha_salida])) otherwise null, type nullable datetime}
            }
        ),

    ConOperacionJoin = Table.NestedJoin(Atributos, {"PED_NUMERO_PEDIDO"}, OperacionUnica, {"PED_NUMERO_PEDIDO"}, "OPERACION", JoinKind.LeftOuter),
    ConOperacion =
        Table.ExpandTableColumn(
            ConOperacionJoin,
            "OPERACION",
            {"VBAK_FECHA_PEDIDO", "VBAK_FECHA_ENTREGA", "VBAK_FECHA_CONTABILIZA", "VBAK_FECHA_FACTURA", "VBAK_FECHA_FES", "VBAK_FECHA_SALIDA"}
        ),

    Faltantes = Table.NestedJoin(ConOperacion, {"PED_NUMERO_PEDIDO"}, MasterKeys, {"PED_NUMERO_PEDIDO"}, "MASTER", JoinKind.LeftAnti),

    ConElegibilidad =
        Table.AddColumn(
            Faltantes,
            "VBAK_ELEGIBLE_APPEND",
            each
                let
                    FechaPedido = [PED_FECHA_HORA],
                    FechaEntrega = [VBAK_FECHA_ENTREGA],
                    FechaFactura = [VBAK_FECHA_FACTURA],
                    FechaSalida = [VBAK_FECHA_SALIDA],
                    SecuenciaOK =
                        FechaPedido <> null
                        and (FechaEntrega = null or Date.From(FechaEntrega) >= Date.From(FechaPedido))
                        and (FechaFactura = null or Date.From(FechaFactura) >= Date.From(FechaPedido))
                        and (FechaSalida = null or (FechaFactura <> null and Date.From(FechaSalida) >= Date.From(FechaFactura)))
                in
                    [PED_NUMERO_PEDIDO] <> null
                    and List.Contains({"42", "43", "44", "45", "46", "47"}, [PED_CANAL_CODIGO])
                    and [PED_CODIGO_CLIENTE] <> null and Text.Trim([PED_CODIGO_CLIENTE]) <> ""
                    and [PED_REGION] <> null and Text.Trim([PED_REGION]) <> ""
                    and FechaPedido <> null
                    and [VBAK_FECHA_FES] = null
                    and SecuenciaOK,
            type logical
        ),

    ConMotivo =
        Table.AddColumn(
            ConElegibilidad,
            "VBAK_MOTIVO",
            each
                if [VBAK_ELEGIBLE_APPEND] then "ELEGIBLE NORMAL"
                else if [PED_NUMERO_PEDIDO] = null then "PEDIDO INVALIDO"
                else if not List.Contains({"42", "43", "44", "45", "46", "47"}, [PED_CANAL_CODIGO]) then "CANAL FUERA DE MAYORISTA"
                else if [PED_CODIGO_CLIENTE] = null or Text.Trim([PED_CODIGO_CLIENTE]) = "" then "SIN CLIENTE"
                else if [PED_REGION] = null or Text.Trim([PED_REGION]) = "" then "SIN REGION; NO ASIGNAR SLA ZONAL"
                else if [PED_FECHA_HORA] = null then "SIN FECHA DE PEDIDO"
                else if [VBAK_FECHA_FES] <> null then "CUARENTENA FES; REQUIERE CLASIFICACION VBFA"
                else if [VBAK_FECHA_ENTREGA] <> null and Date.From([VBAK_FECHA_ENTREGA]) < Date.From([PED_FECHA_HORA]) then "ENTREGA ANTES DEL PEDIDO"
                else if [VBAK_FECHA_FACTURA] <> null and Date.From([VBAK_FECHA_FACTURA]) < Date.From([PED_FECHA_HORA]) then "FACTURA ANTES DEL PEDIDO"
                else if [VBAK_FECHA_SALIDA] <> null and [VBAK_FECHA_FACTURA] = null then "SALIDA SIN FACTURA"
                else if [VBAK_FECHA_SALIDA] <> null and Date.From([VBAK_FECHA_SALIDA]) < Date.From([VBAK_FECHA_FACTURA]) then "SALIDA ANTES DE FACTURA"
                else "REVISAR DATOS VBAK",
            type text
        ),

    Seleccion =
        Table.SelectColumns(
            ConMotivo,
            {
                "PED_NUMERO_PEDIDO",
                "PED_CODIGO_CLIENTE",
                "PED_CANAL_CODIGO",
                "PED_REGION",
                "PED_CIUDAD",
                "VBAK_CLASE_PEDIDO",
                "PED_FECHA_HORA",
                "HORA_PEDIDO_DISPONIBLE",
                "VBAK_FECHA_ENTREGA",
                "VBAK_FECHA_FACTURA",
                "VBAK_FECHA_FES",
                "VBAK_FECHA_SALIDA",
                "VBAK_ELEGIBLE_APPEND",
                "VBAK_MOTIVO"
            },
            MissingField.UseNull
        ),

    Orden = Table.Sort(Seleccion, {{"VBAK_ELEGIBLE_APPEND", Order.Descending}, {"PED_FECHA_HORA", Order.Descending}, {"PED_NUMERO_PEDIDO", Order.Ascending}})
in
    Orden
