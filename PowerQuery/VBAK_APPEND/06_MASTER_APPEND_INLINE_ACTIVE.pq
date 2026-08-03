    VBAK_APPEND_ACTIVO_LOCAL = true,

    FnNormalizaPedidoVBAK = (Valor as any) as nullable text =>
        let
            Texto = try Text.Trim(Text.From(Valor)) otherwise null,
            Numero = if Texto = null or Texto = "" then null else try Int64.FromText(Texto) otherwise null
        in
            if Texto = null or Texto = "" then null
            else if Numero <> null then Text.From(Numero)
            else let SinCeros = Text.TrimStart(Texto, "0") in if SinCeros = "" then "0" else SinCeros,

    FnDHAppendVBAK = (Inicio as any, Fin as any) as nullable number =>
        let
            I = try Date.From(Inicio) otherwise null,
            F = try Date.From(Fin) otherwise null,
            Feriados = List.Buffer(List.Transform(Dim_Feriados_Chile[Fecha], each Date.From(_))),
            Fechas = if I = null or F = null or F < I then {} else if F = I then {} else List.Dates(Date.AddDays(I, 1), Duration.Days(F - I), #duration(1, 0, 0, 0)),
            Habiles = List.Select(Fechas, each Date.DayOfWeek(_, Day.Monday) < 5 and not List.Contains(Feriados, _))
        in
            if I = null or F = null or F < I then null else List.Count(Habiles),

    MasterBaseVBAK = #"Filas ordenadas",
    MasterKeysVBAK =
        Table.Distinct(
            Table.TransformColumns(
                Table.SelectColumns(MasterBaseVBAK, {"PED_NUMERO_PEDIDO"}),
                {{"PED_NUMERO_PEDIDO", each FnNormalizaPedidoVBAK(_), type nullable text}}
            ),
            {"PED_NUMERO_PEDIDO"}
        ),

    VBAKSqlOrigen =
        Sql.Database(
            "128.1.3.21",
            "DMF_VTA_PRD",
            [
                Query =
                    Text.Combine(
                        {
                            "SET NOCOUNT ON;",
                            "SELECT",
                            "    CONVERT(VARCHAR(20), V.VBELN) AS PED_NUMERO_PEDIDO,",
                            "    LTRIM(RTRIM(CONVERT(VARCHAR(30), V.KUNNR))) AS PED_CODIGO_CLIENTE,",
                            "    RIGHT('00' + LTRIM(RTRIM(CONVERT(VARCHAR(10), V.VTWEG))), 2) AS PED_CANAL_CODIGO,",
                            "    CAST(NULL AS VARCHAR(20)) AS PED_CONDICION_EXPEDICION_CODIGO,",
                            "    TRY_CONVERT(DECIMAL(18,2), V.NETWR) AS PED_VALOR_NETO,",
                            "    NULLIF(LTRIM(RTRIM(CONVERT(VARCHAR(10), V.WAERK))), '') AS PED_MONEDA,",
                            "    NULLIF(LTRIM(RTRIM(CONVERT(VARCHAR(20), V.LIFSK))), '') AS PED_BLOQUEO_ENTREGA,",
                            "    CAST(NULL AS VARCHAR(20)) AS PED_ESTADO_CREDITO,",
                            "    NULLIF(LTRIM(RTRIM(CONVERT(VARCHAR(100), V.BSTNK))), '') AS PED_ORDEN_COMPRA_CLIENTE,",
                            "    CAST(NULL AS VARCHAR(200)) AS PED_CIUDAD,",
                            "    NULLIF(LTRIM(RTRIM(CONVERT(VARCHAR(30), K.REGIO))), '') AS PED_REGION,",
                            "    CAST(COALESCE(",
                            "        TRY_CONVERT(DATE, CONVERT(VARCHAR(30), V.ERDAT), 112),",
                            "        TRY_CONVERT(DATE, CONVERT(VARCHAR(30), V.ERDAT), 103),",
                            "        TRY_CONVERT(DATE, CONVERT(VARCHAR(30), V.ERDAT))",
                            "    ) AS DATETIME2(0)) AS PED_FECHA_HORA,",
                            "    CONVERT(BIT, CASE WHEN EXISTS (",
                            "        SELECT 1",
                            "        FROM dbo.VBFA_SAP AS F",
                            "        WHERE F.VBTYP_V = 'C'",
                            "          AND F.VBTYP_N = 'C'",
                            "          AND TRY_CONVERT(BIGINT, F.VBELV) = TRY_CONVERT(BIGINT, V.VBELN)",
                            "    ) THEN 1 ELSE 0 END) AS ES_FES_VBFA",
                            "FROM dbo.VBAK_SAP AS V",
                            "LEFT JOIN dbo.KNA1_SAP AS K",
                            "    ON TRY_CONVERT(BIGINT, K.KUNNR) = TRY_CONVERT(BIGINT, V.KUNNR)",
                            "WHERE V.AUART IN ('ZEDI','ZMAY','ZMAN','ZPDA','ZVGF','ZREL','ZVGM','ZTAN','TAN')",
                            "  AND COALESCE(",
                            "        TRY_CONVERT(DATE, CONVERT(VARCHAR(30), V.ERDAT), 112),",
                            "        TRY_CONVERT(DATE, CONVERT(VARCHAR(30), V.ERDAT), 103),",
                            "        TRY_CONVERT(DATE, CONVERT(VARCHAR(30), V.ERDAT))",
                            "      ) >= DATEADD(MONTH, -3, CAST(GETDATE() AS DATE));"
                        },
                        "#(lf)"
                    )
            ]
        ),

    VBAKSqlTipos =
        Table.TransformColumnTypes(
            VBAKSqlOrigen,
            {
                {"PED_NUMERO_PEDIDO", type text},
                {"PED_CODIGO_CLIENTE", type text},
                {"PED_CANAL_CODIGO", type text},
                {"PED_CONDICION_EXPEDICION_CODIGO", type text},
                {"PED_VALOR_NETO", type number},
                {"PED_MONEDA", type text},
                {"PED_BLOQUEO_ENTREGA", type text},
                {"PED_ESTADO_CREDITO", type text},
                {"PED_ORDEN_COMPRA_CLIENTE", type text},
                {"PED_CIUDAD", type text},
                {"PED_REGION", type text},
                {"PED_FECHA_HORA", type datetime},
                {"ES_FES_VBFA", type logical}
            }
        ),

    VBAKSqlKey =
        Table.TransformColumns(
            VBAKSqlTipos,
            {{"PED_NUMERO_PEDIDO", each FnNormalizaPedidoVBAK(_), type nullable text}}
        ),

    VBAKSqlUnico = Table.Distinct(Table.SelectRows(VBAKSqlKey, each [PED_NUMERO_PEDIDO] <> null), {"PED_NUMERO_PEDIDO"}),

    VBAKOperacionBase =
        Table.SelectColumns(
            Pedidos_Normal_VBAK,
            {"VBELN", "fecha_pedido", "fecha_entrega", "fecha_contabiliza", "fecha_factura", "fecha_fes", "fecha_salida"},
            MissingField.UseNull
        ),

    VBAKOperacionKey =
        Table.AddColumn(
            VBAKOperacionBase,
            "PED_NUMERO_PEDIDO",
            each FnNormalizaPedidoVBAK([VBELN]),
            type nullable text
        ),

    VBAKOperacionUnica =
        Table.Group(
            Table.SelectRows(VBAKOperacionKey, each [PED_NUMERO_PEDIDO] <> null),
            {"PED_NUMERO_PEDIDO"},
            {
                {"VBAK_FECHA_ENTREGA", each try List.Min(List.RemoveNulls([fecha_entrega])) otherwise null, type nullable date},
                {"VBAK_FECHA_CONTABILIZA", each try List.Min(List.RemoveNulls([fecha_contabiliza])) otherwise null, type nullable date},
                {"VBAK_FECHA_FACTURA", each try List.Min(List.RemoveNulls([fecha_factura])) otherwise null, type nullable date},
                {"VBAK_FECHA_FES", each try List.Min(List.RemoveNulls([fecha_fes])) otherwise null, type nullable date},
                {"VBAK_FECHA_SALIDA", each try List.Max(List.RemoveNulls([fecha_salida])) otherwise null, type nullable datetime}
            }
        ),

    VBAKConOperacionJoin =
        Table.NestedJoin(
            VBAKSqlUnico,
            {"PED_NUMERO_PEDIDO"},
            VBAKOperacionUnica,
            {"PED_NUMERO_PEDIDO"},
            "OPERACION",
            JoinKind.LeftOuter
        ),

    VBAKConOperacion =
        Table.ExpandTableColumn(
            VBAKConOperacionJoin,
            "OPERACION",
            {"VBAK_FECHA_ENTREGA", "VBAK_FECHA_CONTABILIZA", "VBAK_FECHA_FACTURA", "VBAK_FECHA_FES", "VBAK_FECHA_SALIDA"},
            {"VBAK_FECHA_ENTREGA", "VBAK_FECHA_CONTABILIZA", "VBAK_FECHA_FACTURA", "VBAK_FECHA_FES", "VBAK_FECHA_SALIDA"}
        ),

    VBAKFaltantes =
        Table.NestedJoin(
            VBAKConOperacion,
            {"PED_NUMERO_PEDIDO"},
            MasterKeysVBAK,
            {"PED_NUMERO_PEDIDO"},
            "MASTER",
            JoinKind.LeftAnti
        ),

    VBAKElegibles =
        Table.SelectRows(
            VBAKFaltantes,
            each
                [PED_NUMERO_PEDIDO] <> null
                and List.Contains({"42", "43", "44", "45", "46", "47"}, [PED_CANAL_CODIGO])
                and [PED_CODIGO_CLIENTE] <> null and Text.Trim([PED_CODIGO_CLIENTE]) <> ""
                and [PED_REGION] <> null and Text.Trim([PED_REGION]) <> ""
                and [PED_FECHA_HORA] <> null
                and [ES_FES_VBFA] <> true
                and [VBAK_FECHA_FES] = null
                and ([VBAK_FECHA_ENTREGA] = null or Date.From([VBAK_FECHA_ENTREGA]) >= Date.From([PED_FECHA_HORA]))
                and ([VBAK_FECHA_FACTURA] = null or Date.From([VBAK_FECHA_FACTURA]) >= Date.From([PED_FECHA_HORA]))
                and ([VBAK_FECHA_SALIDA] = null or ([VBAK_FECHA_FACTURA] <> null and Date.From([VBAK_FECHA_SALIDA]) >= Date.From([VBAK_FECHA_FACTURA])))
        ),

    VBAKAddResponsable = Table.AddColumn(VBAKElegibles, "PED_RESPONSABLE", each null, type nullable text),
    VBAKAddCentro = Table.AddColumn(VBAKAddResponsable, "PED_CENTRO", each null, type nullable text),
    VBAKAddCanal = Table.AddColumn(VBAKAddCentro, "PED_CANAL", each null, type nullable text),
    VBAKAddCondicion = Table.AddColumn(VBAKAddCanal, "PED_CONDICION_EXPEDICION", each null, type nullable text),
    VBAKAddServicio = Table.AddColumn(VBAKAddCondicion, "SERV_TIPO_SERVICIO", each null, type nullable text),
    VBAKAddServicioPlan = Table.AddColumn(VBAKAddServicio, "SERV_TIPO_SERVICIO_PLANIFICADO", each null, type nullable text),
    VBAKAddOTIF = Table.AddColumn(VBAKAddServicioPlan, "OTIF_ESTADO_PEDIDO", each if [VBAK_FECHA_SALIDA] = null then "ABIERTO VBAK" else "CERRADO VBAK", type text),
    VBAKAddEstado = Table.AddColumn(VBAKAddOTIF, "PED_TEXTO_ESTADO", each "VBAK SIN ZART", type text),
    VBAKAddFES = Table.AddColumn(VBAKAddEstado, "ES_FES", each false, type logical),
    VBAKAddSaldo = Table.AddColumn(VBAKAddFES, "ES_SALDO", each false, type logical),
    VBAKAddReglaFES = Table.AddColumn(VBAKAddSaldo, "REGLA_CLASIFICACION_FES", each "NO FES; VALIDADO VBFA C-C", type text),
    VBAKAddReglaSaldo = Table.AddColumn(VBAKAddReglaFES, "REGLA_CLASIFICACION_SALDO", each "NO SALDO; SIN EVIDENCIA DE FACTURAS DIFERIDAS", type text),
    VBAKAddSegmento = Table.AddColumn(VBAKAddReglaSaldo, "SEGMENTO_ANALISIS", each "FLUJO NORMAL", type text),
    VBAKAddIncluir = Table.AddColumn(VBAKAddSegmento, "INCLUIR_SLA_NORMAL", each true, type logical),
    VBAKAddEntregaP = Table.AddColumn(VBAKAddIncluir, "ENT_P_FECHA_HORA", each if [VBAK_FECHA_ENTREGA] = null then null else DateTime.From([VBAK_FECHA_ENTREGA]), type nullable datetime),
    VBAKAddEntregaU = Table.AddColumn(VBAKAddEntregaP, "ENT_U_FECHA_HORA", each [ENT_P_FECHA_HORA], type nullable datetime),
    VBAKAddFacturaP = Table.AddColumn(VBAKAddEntregaU, "FAC_P_FECHA_HORA_REAL", each if [VBAK_FECHA_FACTURA] = null then null else DateTime.From([VBAK_FECHA_FACTURA]), type nullable datetime),
    VBAKAddFacturaU = Table.AddColumn(VBAKAddFacturaP, "FAC_U_FECHA_HORA", each [FAC_P_FECHA_HORA_REAL], type nullable datetime),
    VBAKAddTransporteP = Table.AddColumn(VBAKAddFacturaU, "TRP_P_FECHA_HORA", each if [VBAK_FECHA_SALIDA] = null then null else DateTime.From([VBAK_FECHA_SALIDA]), type nullable datetime),
    VBAKAddTransporteU = Table.AddColumn(VBAKAddTransporteP, "TRP_U_FECHA_HORA", each [TRP_P_FECHA_HORA], type nullable datetime),
    VBAKAddFacturaAjustada = Table.AddColumn(VBAKAddTransporteU, "FAC_FECHA_OPERATIVA_AJUSTADA", each [FAC_P_FECHA_HORA_REAL], type nullable datetime),
    VBAKAddDHLead = Table.AddColumn(VBAKAddFacturaAjustada, "DH_LEAD_NORMAL", each FnDHAppendVBAK([PED_FECHA_HORA], [TRP_U_FECHA_HORA]), Int64.Type),
    VBAKAddDHEntrega = Table.AddColumn(VBAKAddDHLead, "DH_ENTREGA_COMPLETA_100", each [DH_LEAD_NORMAL], Int64.Type),
    VBAKAddDHDespacho = Table.AddColumn(VBAKAddDHEntrega, "DH_DESPACHO", each FnDHAppendVBAK([FAC_P_FECHA_HORA_REAL], [TRP_U_FECHA_HORA]), Int64.Type),
    VBAKAddDHFacturaUltima = Table.AddColumn(VBAKAddDHDespacho, "DH_PRIMERA_FACTURA_A_ULTIMO_DESPACHO", each [DH_DESPACHO], Int64.Type),
    VBAKAddDHBrecha = Table.AddColumn(VBAKAddDHFacturaUltima, "DH_BRECHA_PRIMER_ULTIMO_DESPACHO", each if [TRP_U_FECHA_HORA] = null then null else 0, Int64.Type),
    VBAKAddMes = Table.AddColumn(VBAKAddDHBrecha, "MES_CREACION", each Date.ToText(Date.From([PED_FECHA_HORA]), "yyyy-MM"), type text),
    VBAKAddDia = Table.AddColumn(VBAKAddMes, "DIA_MES_CREACION", each Date.Day(Date.From([PED_FECHA_HORA])), Int64.Type),
    VBAKAddTramo = Table.AddColumn(VBAKAddDia, "TRAMO_MES_CALENDARIO", each let D = [DIA_MES_CREACION] in if D <= 7 then "01-07" else if D <= 14 then "08-14" else if D <= 21 then "15-21" else "22-FIN", type text),
    VBAKAddAudEstado = Table.AddColumn(VBAKAddTramo, "AUD_ESTADO_GENERAL", each "REVISAR", type text),
    VBAKAddAudNormal = Table.AddColumn(VBAKAddAudEstado, "AUD_ESTADO_FLUJO_NORMAL", each "REVISAR", type text),
    VBAKAddAudFES = Table.AddColumn(VBAKAddAudNormal, "AUD_ESTADO_FLUJO_FES", each "NO APLICA", type text),
    VBAKAddAudSaldo = Table.AddColumn(VBAKAddAudFES, "AUD_ESTADO_FLUJO_SALDO", each "NO APLICA", type text),
    VBAKAddAudPrincipal = Table.AddColumn(VBAKAddAudSaldo, "AUD_PRINCIPAL_INCONGRUENCIA", each "VBAK SIN ZART; VALIDAR TRAZABILIDAD", type text),
    VBAKAddAudRevision = Table.AddColumn(VBAKAddAudPrincipal, "AUD_REQUIERE_REVISION", each true, type logical),
    VBAKAddAudCrit = Table.AddColumn(VBAKAddAudRevision, "AUD_TOTAL_CRITICAS", each 0, Int64.Type),
    VBAKAddAudAdv = Table.AddColumn(VBAKAddAudCrit, "AUD_TOTAL_ADVERTENCIAS", each 1, Int64.Type),
    VBAKAddAudTotal = Table.AddColumn(VBAKAddAudAdv, "AUD_TOTAL_INCONGRUENCIAS", each 1, Int64.Type),

    ColumnasMasterVBAK = Table.ColumnNames(MasterBaseVBAK),
    VBAKProyectadoMaster = Table.SelectColumns(VBAKAddAudTotal, ColumnasMasterVBAK, MissingField.UseNull),
    VBAKTipadoMaster = Value.ReplaceType(VBAKProyectadoMaster, Value.Type(MasterBaseVBAK)),
    MasterConVBAK =
        Value.ReplaceType(
            Table.Sort(
                Table.Combine({MasterBaseVBAK, VBAKTipadoMaster}, ColumnasMasterVBAK),
                {{"PED_FECHA_HORA", Order.Descending}}
            ),
            Value.Type(MasterBaseVBAK)
        ),
    ResultadoVBAK = if VBAK_APPEND_ACTIVO_LOCAL then MasterConVBAK else MasterBaseVBAK
