// PEGAR EN Fact_Pedidos_Auditoria DESPUÉS DEL PASO #"Filas ordenadas".
// Luego reemplazar el `in #"Filas ordenadas"` por `in ResultadoVBAK`.
// Requiere las consultas: VBAK_APPEND_ACTIVO y VBAK_ATRIBUTOS_MAYORISTA.

    MasterBase = #"Filas ordenadas",

    FnNormalizaPedido = (Valor as any) as nullable text =>
        let
            Texto = try Text.Trim(Text.From(Valor)) otherwise null,
            Numero = if Texto = null or Texto = "" then null else try Int64.FromText(Texto) otherwise null,
            Salida =
                if Texto = null or Texto = "" then null
                else if Numero <> null then Text.From(Numero)
                else
                    let SinCeros = Text.TrimStart(Texto, "0")
                    in if SinCeros = "" then "0" else SinCeros
        in
            Salida,

    FeriadosVBAK = List.Buffer(List.Transform(Dim_Feriados_Chile[Fecha], each Date.From(_))),

    FnDHVBAK = (Inicio as any, Fin as any) as nullable number =>
        let
            I = try Date.From(Inicio) otherwise null,
            F = try Date.From(Fin) otherwise null,
            Fechas =
                if I = null or F = null or F < I then {}
                else if F = I then {}
                else List.Dates(Date.AddDays(I, 1), Duration.Days(F - I), #duration(1, 0, 0, 0)),
            Habiles = List.Select(Fechas, each Date.DayOfWeek(_, Day.Monday) < 5 and not List.Contains(FeriadosVBAK, _))
        in
            if I = null or F = null or F < I then null else List.Count(Habiles),

    FnUltimos7DHMes = (Fecha as any) as nullable logical =>
        let
            F = try Date.From(Fecha) otherwise null,
            InicioMes = if F = null then null else Date.StartOfMonth(F),
            FinMes = if F = null then null else Date.EndOfMonth(F),
            FechasMes = if F = null then {} else List.Dates(InicioMes, Duration.Days(FinMes - InicioMes) + 1, #duration(1, 0, 0, 0)),
            HabilesMes = List.Select(FechasMes, each Date.DayOfWeek(_, Day.Monday) < 5 and not List.Contains(FeriadosVBAK, _)),
            Ultimos7 = List.LastN(HabilesMes, 7)
        in
            if F = null then null else List.Contains(Ultimos7, F),

    MasterKeys =
        Table.Distinct(
            Table.TransformColumns(
                Table.SelectColumns(MasterBase, {"PED_NUMERO_PEDIDO"}),
                {{"PED_NUMERO_PEDIDO", each FnNormalizaPedido(_), type nullable text}}
            ),
            {"PED_NUMERO_PEDIDO"}
        ),

    VBAKAtributos =
        Table.TransformColumns(
            VBAK_ATRIBUTOS_MAYORISTA,
            {{"PED_NUMERO_PEDIDO", each FnNormalizaPedido(_), type nullable text}}
        ),

    VBAKOperativoSeleccion =
        Table.SelectColumns(
            Pedidos_Normal_VBAK,
            {"VBELN", "fecha_pedido", "fecha_entrega", "fecha_contabiliza", "fecha_factura", "fecha_fes", "fecha_salida"},
            MissingField.UseNull
        ),

    VBAKOperativoKey =
        Table.AddColumn(
            VBAKOperativoSeleccion,
            "PED_NUMERO_PEDIDO",
            each FnNormalizaPedido([VBELN]),
            type nullable text
        ),

    VBAKOperativoUnico =
        Table.Group(
            Table.SelectRows(VBAKOperativoKey, each [PED_NUMERO_PEDIDO] <> null),
            {"PED_NUMERO_PEDIDO"},
            {
                {"fecha_pedido", each try List.Min(List.RemoveNulls([fecha_pedido])) otherwise null, type nullable date},
                {"fecha_entrega", each try List.Min(List.RemoveNulls([fecha_entrega])) otherwise null, type nullable date},
                {"fecha_contabiliza", each try List.Min(List.RemoveNulls([fecha_contabiliza])) otherwise null, type nullable date},
                {"fecha_factura", each try List.Min(List.RemoveNulls([fecha_factura])) otherwise null, type nullable date},
                {"fecha_fes", each try List.Min(List.RemoveNulls([fecha_fes])) otherwise null, type nullable date},
                {"fecha_salida", each try List.Max(List.RemoveNulls([fecha_salida])) otherwise null, type nullable datetime}
            }
        ),

    VBAKConOperacionJoin =
        Table.NestedJoin(
            VBAKAtributos,
            {"PED_NUMERO_PEDIDO"},
            VBAKOperativoUnico,
            {"PED_NUMERO_PEDIDO"},
            "OPERACION",
            JoinKind.LeftOuter
        ),

    VBAKConOperacion =
        Table.ExpandTableColumn(
            VBAKConOperacionJoin,
            "OPERACION",
            {"fecha_pedido", "fecha_entrega", "fecha_contabiliza", "fecha_factura", "fecha_fes", "fecha_salida"},
            {"VBAK_FECHA_PEDIDO", "VBAK_FECHA_ENTREGA", "VBAK_FECHA_CONTABILIZA", "VBAK_FECHA_FACTURA", "VBAK_FECHA_FES", "VBAK_FECHA_SALIDA"}
        ),

    VBAKFaltantes =
        Table.NestedJoin(
            VBAKConOperacion,
            {"PED_NUMERO_PEDIDO"},
            MasterKeys,
            {"PED_NUMERO_PEDIDO"},
            "MASTER",
            JoinKind.LeftAnti
        ),

    VBAKConControles =
        Table.AddColumn(
            VBAKFaltantes,
            "VBAK_ELEGIBLE_APPEND",
            each
                let
                    Pedido = [PED_NUMERO_PEDIDO],
                    Canal = [PED_CANAL_CODIGO],
                    Cliente = [PED_CODIGO_CLIENTE],
                    Region = [PED_REGION],
                    FechaPedido = [PED_FECHA_HORA],
                    FechaEntrega = [VBAK_FECHA_ENTREGA],
                    FechaFactura = [VBAK_FECHA_FACTURA],
                    FechaSalida = [VBAK_FECHA_SALIDA],
                    FechaFES = [VBAK_FECHA_FES],
                    SecuenciaOK =
                        FechaPedido <> null
                        and (FechaEntrega = null or Date.From(FechaEntrega) >= Date.From(FechaPedido))
                        and (FechaFactura = null or Date.From(FechaFactura) >= Date.From(FechaPedido))
                        and (FechaSalida = null or (FechaFactura <> null and Date.From(FechaSalida) >= Date.From(FechaFactura)))
                in
                    Pedido <> null
                    and List.Contains({"42", "43", "44", "45", "46", "47"}, Canal)
                    and Cliente <> null and Text.Trim(Cliente) <> ""
                    and Region <> null and Text.Trim(Region) <> ""
                    and FechaPedido <> null
                    and FechaFES = null
                    and SecuenciaOK,
            type logical
        ),

    VBAKConMotivo =
        Table.AddColumn(
            VBAKConControles,
            "VBAK_MOTIVO_NO_ELEGIBLE",
            each
                if [VBAK_ELEGIBLE_APPEND] then null
                else if [PED_NUMERO_PEDIDO] = null then "PEDIDO INVALIDO"
                else if not List.Contains({"42", "43", "44", "45", "46", "47"}, [PED_CANAL_CODIGO]) then "CANAL FUERA DE MAYORISTA"
                else if [PED_CODIGO_CLIENTE] = null or Text.Trim([PED_CODIGO_CLIENTE]) = "" then "SIN CLIENTE"
                else if [PED_REGION] = null or Text.Trim([PED_REGION]) = "" then "SIN REGION; NO ASIGNAR SLA ZONAL"
                else if [PED_FECHA_HORA] = null then "SIN FECHA DE PEDIDO"
                else if [VBAK_FECHA_FES] <> null then "CANDIDATO FES; REQUIERE CLASIFICACION VBFA"
                else if [VBAK_FECHA_ENTREGA] <> null and Date.From([VBAK_FECHA_ENTREGA]) < Date.From([PED_FECHA_HORA]) then "ENTREGA ANTES DEL PEDIDO"
                else if [VBAK_FECHA_FACTURA] <> null and Date.From([VBAK_FECHA_FACTURA]) < Date.From([PED_FECHA_HORA]) then "FACTURA ANTES DEL PEDIDO"
                else if [VBAK_FECHA_SALIDA] <> null and [VBAK_FECHA_FACTURA] = null then "SALIDA SIN FACTURA"
                else if [VBAK_FECHA_SALIDA] <> null and Date.From([VBAK_FECHA_SALIDA]) < Date.From([VBAK_FECHA_FACTURA]) then "SALIDA ANTES DE FACTURA"
                else "REVISAR DATOS VBAK",
            type nullable text
        ),

    VBAKElegibles = Table.SelectRows(VBAKConMotivo, each [VBAK_ELEGIBLE_APPEND] = true),

    AddResponsable = Table.AddColumn(VBAKElegibles, "PED_RESPONSABLE", each null, type nullable text),
    AddCentro = Table.AddColumn(AddResponsable, "PED_CENTRO", each null, type nullable text),
    AddCanalTexto = Table.AddColumn(AddCentro, "PED_CANAL", each null, type nullable text),
    AddCondicionTexto = Table.AddColumn(AddCanalTexto, "PED_CONDICION_EXPEDICION", each null, type nullable text),
    AddServicio = Table.AddColumn(AddCondicionTexto, "SERV_TIPO_SERVICIO", each null, type nullable text),
    AddServicioPlan = Table.AddColumn(AddServicio, "SERV_TIPO_SERVICIO_PLANIFICADO", each null, type nullable text),
    AddOTIF = Table.AddColumn(AddServicioPlan, "OTIF_ESTADO_PEDIDO", each if [VBAK_FECHA_SALIDA] <> null then "CIERRE VBAK" else "ABIERTO VBAK", type text),
    AddTextoEstado = Table.AddColumn(AddOTIF, "PED_TEXTO_ESTADO", each "VBAK SIN ZART", type text),
    AddFES = Table.AddColumn(AddTextoEstado, "ES_FES", each false, type logical),
    AddSaldo = Table.AddColumn(AddFES, "ES_SALDO", each false, type logical),
    AddReglaFES = Table.AddColumn(AddSaldo, "REGLA_CLASIFICACION_FES", each "NO FES; FILTRO SEGURO VBAK", type text),
    AddReglaSaldo = Table.AddColumn(AddReglaFES, "REGLA_CLASIFICACION_SALDO", each "NO SALDO; UNA FECHA DE FACTURA", type text),
    AddSegmento = Table.AddColumn(AddReglaSaldo, "SEGMENTO_ANALISIS", each "FLUJO NORMAL", type text),
    AddIncluirSLA = Table.AddColumn(AddSegmento, "INCLUIR_SLA_NORMAL", each true, type logical),

    AddEntregaP = Table.AddColumn(AddIncluirSLA, "ENT_P_FECHA_HORA", each if [VBAK_FECHA_ENTREGA] = null then null else DateTime.From([VBAK_FECHA_ENTREGA]), type nullable datetime),
    AddEntregaU = Table.AddColumn(AddEntregaP, "ENT_U_FECHA_HORA", each [ENT_P_FECHA_HORA], type nullable datetime),
    AddFacturaP = Table.AddColumn(AddEntregaU, "FAC_P_FECHA_HORA_REAL", each if [VBAK_FECHA_FACTURA] = null then null else DateTime.From([VBAK_FECHA_FACTURA]), type nullable datetime),
    AddFacturaU = Table.AddColumn(AddFacturaP, "FAC_U_FECHA_HORA", each [FAC_P_FECHA_HORA_REAL], type nullable datetime),
    AddTransporteP = Table.AddColumn(AddFacturaU, "TRP_P_FECHA_HORA", each if [VBAK_FECHA_SALIDA] = null then null else DateTime.From([VBAK_FECHA_SALIDA]), type nullable datetime),
    AddTransporteU = Table.AddColumn(AddTransporteP, "TRP_U_FECHA_HORA", each [TRP_P_FECHA_HORA], type nullable datetime),
    AddFacturaAjustada = Table.AddColumn(AddTransporteU, "FAC_FECHA_OPERATIVA_AJUSTADA", each [FAC_P_FECHA_HORA_REAL], type nullable datetime),

    AddDHLead = Table.AddColumn(AddFacturaAjustada, "DH_LEAD_NORMAL", each FnDHVBAK([PED_FECHA_HORA], [TRP_U_FECHA_HORA]), Int64.Type),
    AddDHEntregaCompleta = Table.AddColumn(AddDHLead, "DH_ENTREGA_COMPLETA_100", each [DH_LEAD_NORMAL], Int64.Type),
    AddDHDespacho = Table.AddColumn(AddDHEntregaCompleta, "DH_DESPACHO", each FnDHVBAK([FAC_P_FECHA_HORA_REAL], [TRP_U_FECHA_HORA]), Int64.Type),
    AddDHFacturaUltDesp = Table.AddColumn(AddDHDespacho, "DH_PRIMERA_FACTURA_A_ULTIMO_DESPACHO", each [DH_DESPACHO], Int64.Type),
    AddDHBrechaDesp = Table.AddColumn(AddDHFacturaUltDesp, "DH_BRECHA_PRIMER_ULTIMO_DESPACHO", each if [TRP_U_FECHA_HORA] = null then null else 0, Int64.Type),
    AddDHEntBrecha = Table.AddColumn(AddDHBrechaDesp, "DH_ENT_PRIMERA_ULTIMA", each if [ENT_P_FECHA_HORA] = null then null else 0, Int64.Type),
    AddDHFacBrecha = Table.AddColumn(AddDHEntBrecha, "DH_FAC_PRIMERA_ULTIMA", each if [FAC_P_FECHA_HORA_REAL] = null then null else 0, Int64.Type),

    AddMes = Table.AddColumn(AddDHFacBrecha, "MES_CREACION", each Date.ToText(Date.From([PED_FECHA_HORA]), "yyyy-MM"), type text),
    AddDia = Table.AddColumn(AddMes, "DIA_MES_CREACION", each Date.Day(Date.From([PED_FECHA_HORA])), Int64.Type),
    AddTramo = Table.AddColumn(AddDia, "TRAMO_MES_CALENDARIO", each let D = [DIA_MES_CREACION] in if D <= 7 then "01-07" else if D <= 14 then "08-14" else if D <= 21 then "15-21" else "22-FIN", type text),
    AddU7 = Table.AddColumn(AddTramo, "ES_ULTIMOS_7_DIAS_HABILES_MES", each FnUltimos7DHMes([PED_FECHA_HORA]), type nullable logical),

    AddAudEstado = Table.AddColumn(AddU7, "AUD_ESTADO_GENERAL", each "REVISAR", type text),
    AddAudNormal = Table.AddColumn(AddAudEstado, "AUD_ESTADO_FLUJO_NORMAL", each "REVISAR", type text),
    AddAudFES = Table.AddColumn(AddAudNormal, "AUD_ESTADO_FLUJO_FES", each "NO APLICA", type text),
    AddAudSaldo = Table.AddColumn(AddAudFES, "AUD_ESTADO_FLUJO_SALDO", each "NO APLICA", type text),
    AddAudPrincipal = Table.AddColumn(AddAudSaldo, "AUD_PRINCIPAL_INCONGRUENCIA", each "VBAK SIN REGISTRO ZART; VALIDAR TRAZABILIDAD", type text),
    AddAudRevision = Table.AddColumn(AddAudPrincipal, "AUD_REQUIERE_REVISION", each true, type logical),
    AddAudCrit = Table.AddColumn(AddAudRevision, "AUD_TOTAL_CRITICAS", each 0, Int64.Type),
    AddAudAdv = Table.AddColumn(AddAudCrit, "AUD_TOTAL_ADVERTENCIAS", each 1, Int64.Type),
    AddAudTotal = Table.AddColumn(AddAudAdv, "AUD_TOTAL_INCONGRUENCIAS", each 1, Int64.Type),

    ColumnasMaster = Table.ColumnNames(MasterBase),
    VBAKProyectado = Table.SelectColumns(AddAudTotal, ColumnasMaster, MissingField.UseNull),
    VBAKTipado = Value.ReplaceType(VBAKProyectado, Value.Type(MasterBase)),

    MasterConVBAK =
        Value.ReplaceType(
            Table.Sort(
                Table.Combine({MasterBase, VBAKTipado}, ColumnasMaster),
                {{"PED_FECHA_HORA", Order.Descending}}
            ),
            Value.Type(MasterBase)
        ),

    ResultadoVBAK = if VBAK_APPEND_ACTIVO then MasterConVBAK else MasterBase
