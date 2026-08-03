let
    FnNormalizaPedido = (Valor as any) as nullable text =>
        let
            Texto = try Text.Trim(Text.From(Valor)) otherwise null,
            Numero = if Texto = null or Texto = "" then null else try Int64.FromText(Texto) otherwise null
        in
            if Texto = null or Texto = "" then null
            else if Numero <> null then Text.From(Numero)
            else let SinCeros = Text.TrimStart(Texto, "0") in if SinCeros = "" then "0" else SinCeros,

    Master = Fact_Pedidos_Auditoria,
    MasterConKey = Table.TransformColumns(Master, {{"PED_NUMERO_PEDIDO", each FnNormalizaPedido(_), type nullable text}}),
    MasterOriginal = Table.SelectRows(MasterConKey, each [PED_TEXTO_ESTADO] <> "VBAK SIN ZART" or [PED_TEXTO_ESTADO] = null),
    MasterAppend = Table.SelectRows(MasterConKey, each [PED_TEXTO_ESTADO] = "VBAK SIN ZART"),

    Fuente = Table.TransformColumns(VBAK_ATRIBUTOS_MAYORISTA, {{"PED_NUMERO_PEDIDO", each FnNormalizaPedido(_), type nullable text}}),
    FuenteUnica = Table.Distinct(Table.SelectRows(Fuente, each [PED_NUMERO_PEDIDO] <> null), {"PED_NUMERO_PEDIDO"}),

    DuplicadosMasterTabla =
        Table.SelectRows(
            Table.Group(MasterConKey, {"PED_NUMERO_PEDIDO"}, {{"FILAS", each Table.RowCount(_), Int64.Type}}),
            each [PED_NUMERO_PEDIDO] <> null and [FILAS] > 1
        ),

    FuenteEnMaster =
        Table.NestedJoin(
            FuenteUnica,
            {"PED_NUMERO_PEDIDO"},
            Table.Distinct(Table.SelectColumns(MasterConKey, {"PED_NUMERO_PEDIDO"})),
            {"PED_NUMERO_PEDIDO"},
            "MASTER",
            JoinKind.Inner
        ),

    FuenteFaltante =
        Table.NestedJoin(
            FuenteUnica,
            {"PED_NUMERO_PEDIDO"},
            Table.Distinct(Table.SelectColumns(MasterConKey, {"PED_NUMERO_PEDIDO"})),
            {"PED_NUMERO_PEDIDO"},
            "MASTER",
            JoinKind.LeftAnti
        ),

    Controles =
        #table(
            type table [CONTROL = text, VALOR = Int64.Type, ESTADO = text, REGLA = text],
            {
                {"MASTER_TOTAL", Table.RowCount(MasterConKey), "INFO", "Conteo total luego del refresh"},
                {"MASTER_ORIGINAL", Table.RowCount(MasterOriginal), "INFO", "Filas distintas del marcador VBAK SIN ZART"},
                {"VBAK_APPEND_FILAS", Table.RowCount(MasterAppend), if VBAK_APPEND_ACTIVO then "REVISAR" else "INFO", "Debe ser 0 con parámetro FALSE; con TRUE debe coincidir con elegibles"},
                {"VBAK_FUENTE_UNICA", Table.RowCount(FuenteUnica), "INFO", "Universo VBAK mayorista 3M"},
                {"VBAK_FUENTE_EN_MASTER", Table.RowCount(FuenteEnMaster), "INFO", "Cobertura total de la relación por pedido"},
                {"VBAK_FUENTE_FALTANTE", Table.RowCount(FuenteFaltante), "INFO", "Incluye cuarentena FES y filas no elegibles"},
                {"DUPLICADOS_MASTER", Table.RowCount(DuplicadosMasterTabla), if Table.RowCount(DuplicadosMasterTabla) = 0 then "VERDE" else "ROJO", "Debe ser 0"},
                {"APPEND_CLAVE_NULA", Table.RowCount(Table.SelectRows(MasterAppend, each [PED_NUMERO_PEDIDO] = null)), if Table.RowCount(Table.SelectRows(MasterAppend, each [PED_NUMERO_PEDIDO] = null)) = 0 then "VERDE" else "ROJO", "Debe ser 0"},
                {"APPEND_CANAL_FUERA", Table.RowCount(Table.SelectRows(MasterAppend, each not List.Contains({"42","43","44","45","46","47"}, [PED_CANAL_CODIGO]))), if Table.RowCount(Table.SelectRows(MasterAppend, each not List.Contains({"42","43","44","45","46","47"}, [PED_CANAL_CODIGO]))) = 0 then "VERDE" else "ROJO", "Debe ser 0"},
                {"APPEND_REGION_NULA", Table.RowCount(Table.SelectRows(MasterAppend, each [PED_REGION] = null or Text.Trim(Text.From([PED_REGION])) = "")), if Table.RowCount(Table.SelectRows(MasterAppend, each [PED_REGION] = null or Text.Trim(Text.From([PED_REGION])) = "")) = 0 then "VERDE" else "ROJO", "Debe ser 0 para no asignar SLA zonal incorrecto"},
                {"APPEND_ES_FES", Table.RowCount(Table.SelectRows(MasterAppend, each [ES_FES] = true)), if Table.RowCount(Table.SelectRows(MasterAppend, each [ES_FES] = true)) = 0 then "VERDE" else "ROJO", "FES queda en cuarentena hasta clasificación VBFA"},
                {"APPEND_ES_SALDO", Table.RowCount(Table.SelectRows(MasterAppend, each [ES_SALDO] = true)), if Table.RowCount(Table.SelectRows(MasterAppend, each [ES_SALDO] = true)) = 0 then "VERDE" else "ROJO", "No inferir SALDO con una sola fecha"},
                {"APPEND_SALIDA_SIN_FACTURA", Table.RowCount(Table.SelectRows(MasterAppend, each [TRP_U_FECHA_HORA] <> null and [FAC_P_FECHA_HORA_REAL] = null)), if Table.RowCount(Table.SelectRows(MasterAppend, each [TRP_U_FECHA_HORA] <> null and [FAC_P_FECHA_HORA_REAL] = null)) = 0 then "VERDE" else "ROJO", "Debe ser 0"},
                {"APPEND_MARCADOS_REVISION", Table.RowCount(Table.SelectRows(MasterAppend, each [AUD_REQUIERE_REVISION] = true and [AUD_ESTADO_GENERAL] = "REVISAR")), if Table.RowCount(MasterAppend) = Table.RowCount(Table.SelectRows(MasterAppend, each [AUD_REQUIERE_REVISION] = true and [AUD_ESTADO_GENERAL] = "REVISAR")) then "VERDE" else "ROJO", "Toda fila VBAK debe quedar trazable y en revisión"}
            }
        )
in
    Controles
