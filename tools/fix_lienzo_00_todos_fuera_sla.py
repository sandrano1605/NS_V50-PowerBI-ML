from __future__ import annotations

import json
from pathlib import Path

MEDIDAS = Path("NS.SemanticModel/definition/tables/Medidas.tmdl")
VISUAL = Path(
    "NS.Report/definition/pages/71af1998e2cb472d9799/visuals/critical_table/visual.json"
)


def replace_measure_block(text: str, measure_name: str, replacement: str, *, include_previous_comment: str | None = None) -> str:
    measure_marker = f"\tmeasure '{measure_name}' ="
    measure_start = text.index(measure_marker)
    start = text.index(include_previous_comment) if include_previous_comment else measure_start
    lineage_start = text.index("\n\t\tlineageTag:", measure_start)
    return text[:start] + replacement.rstrip() + text[lineage_start:]


def main() -> None:
    medidas = MEDIDAS.read_text(encoding="utf-8")

    full_table_measure = r'''	/// Tabla completa de pedidos fuera SLA. Conserva el nombre técnico por compatibilidad con los visuales existentes.
	measure 'RE TT Días Top 10' =
			VAR PedidoActual = SELECTEDVALUE(Fact_Tracking[PED_NUMERO_PEDIDO])
			VAR FlujoSel = SELECTEDVALUE(Dim_Vista_Ejecutiva[Flujo])
			VAR ZonaSel = SELECTEDVALUE(Dim_Rango_Entrega[Zona])
			VAR MinDH = SELECTEDVALUE(Dim_Rango_Entrega[MinDH])
			VAR MaxDH = SELECTEDVALUE(Dim_Rango_Entrega[MaxDH])
			VAR TieneRango = HASONEVALUE(Dim_Rango_Entrega[Rango])
			VAR EsPedidoFueraSLA =
				NOT ISBLANK(PedidoActual)
					&& CALCULATE(
						COUNTROWS(Fact_Tracking),
						KEEPFILTERS(
							FILTER(
								Fact_Tracking,
								Fact_Tracking[ES_CERRADO] = TRUE()
									&& NOT ISBLANK(Fact_Tracking[DIAS_INTERNOS_DH])
									&& Fact_Tracking[CUMPLE_SLA_INTERNO] = FALSE()
									&& (
										ISBLANK(FlujoSel)
											|| (CONTAINSSTRING(FlujoSel, "Flujo Normal") && Fact_Tracking[CLASIFICACION] = "NORMAL")
											|| (CONTAINSSTRING(FlujoSel, "FES") && Fact_Tracking[CLASIFICACION] IN {"FES", "FES + SALDO"})
											|| (CONTAINSSTRING(FlujoSel, "Saldos") && Fact_Tracking[CLASIFICACION] = "SALDO")
									)
									&& (ISBLANK(ZonaSel) || Fact_Tracking[ZONA] = ZonaSel)
									&& (
										NOT TieneRango
											|| (
												Fact_Tracking[DIAS_INTERNOS_DH] >= MinDH
													&& (ISBLANK(MaxDH) || Fact_Tracking[DIAS_INTERNOS_DH] <= MaxDH)
											)
									)
							)
						)
					) > 0
			RETURN
				IF(EsPedidoFueraSLA, MAX(Fact_Tracking[DIAS_INTERNOS_DH]))
		formatString: 0 "DH"
		displayFolder: 02. Resumen Ejecutivo\09. Tooltip
'''

    medidas = replace_measure_block(
        medidas,
        "RE TT Días Top 10",
        full_table_measure,
        include_previous_comment="\t/// Tooltip compacto.",
    )

    dynamic_title = r'''	measure 'RE TT Título' =
			VAR Flujo = SELECTEDVALUE(Dim_Vista_Ejecutiva[Flujo])
			VAR Zona = SELECTEDVALUE(Dim_Rango_Entrega[Zona])
			VAR Rango = SELECTEDVALUE(Dim_Rango_Entrega[Rango])
			VAR Contexto = COALESCE(Flujo, IF(NOT ISBLANK(Zona), Zona & IF(NOT ISBLANK(Rango), " · " & Rango, ""), "Universo cerrado"))
			VAR FlujoSel = SELECTEDVALUE(Dim_Vista_Ejecutiva[Flujo])
			VAR ZonaSel = SELECTEDVALUE(Dim_Rango_Entrega[Zona])
			VAR MinDH = SELECTEDVALUE(Dim_Rango_Entrega[MinDH])
			VAR MaxDH = SELECTEDVALUE(Dim_Rango_Entrega[MaxDH])
			VAR TieneRango = HASONEVALUE(Dim_Rango_Entrega[Rango])
			VAR CohorteFuera =
				FILTER(
					Fact_Tracking,
					Fact_Tracking[ES_CERRADO] = TRUE()
						&& NOT ISBLANK(Fact_Tracking[DIAS_INTERNOS_DH])
						&& Fact_Tracking[CUMPLE_SLA_INTERNO] = FALSE()
						&& (
							ISBLANK(FlujoSel)
								|| (CONTAINSSTRING(FlujoSel, "Flujo Normal") && Fact_Tracking[CLASIFICACION] = "NORMAL")
								|| (CONTAINSSTRING(FlujoSel, "FES") && Fact_Tracking[CLASIFICACION] IN {"FES", "FES + SALDO"})
								|| (CONTAINSSTRING(FlujoSel, "Saldos") && Fact_Tracking[CLASIFICACION] = "SALDO")
						)
						&& (ISBLANK(ZonaSel) || Fact_Tracking[ZONA] = ZonaSel)
						&& (NOT TieneRango || (Fact_Tracking[DIAS_INTERNOS_DH] >= MinDH && (ISBLANK(MaxDH) || Fact_Tracking[DIAS_INTERNOS_DH] <= MaxDH)))
				)
			VAR MinCre = MINX(CohorteFuera, Fact_Tracking[PED_FECHA_HORA])
			VAR MaxCre = MAXX(CohorteFuera, Fact_Tracking[PED_FECHA_HORA])
			VAR PedidosFuera = [RE Pedidos fuera SLA contexto]
			RETURN
				"PEDIDOS FUERA SLA · "
					& FORMAT(PedidosFuera, "#,##0", "es-CL") & " pedidos mostrados"
					& " · " & COALESCE(FORMAT(MinCre, "dd-MM-yyyy"), "--") & " a " & COALESCE(FORMAT(MaxCre, "dd-MM-yyyy"), "--")
					& " · " & Contexto
		displayFolder: 02. Resumen Ejecutivo\09. Tooltip
'''

    medidas = replace_measure_block(medidas, "RE TT Título", dynamic_title)
    MEDIDAS.write_text(medidas, encoding="utf-8")

    visual_text = VISUAL.read_text(encoding="utf-8")
    old_title = "PEDIDOS CRÍTICOS · HITO DOMINANTE Y MOTIVO OPERATIVO"
    new_title = "PEDIDOS FUERA SLA · HITO DOMINANTE Y MOTIVO OPERATIVO"
    if old_title not in visual_text:
        raise RuntimeError("No se encontró el título anterior del visual")
    visual_text = visual_text.replace(old_title, new_title, 1)
    json.loads(visual_text)
    VISUAL.write_text(visual_text, encoding="utf-8")

    section = medidas.split("measure 'RE TT Días Top 10' =", 1)[1].split("measure 'RE TT Cliente' =", 1)[0]
    checks = {
        "sin_TOPN_15": "TOPN(15" not in section,
        "sin_TopPedidos": "TopPedidos" not in section,
        "solo_fuera_SLA": "CUMPLE_SLA_INTERNO] = FALSE()" in section,
        "titulo_dinamico": "PEDIDOS FUERA SLA ·" in medidas,
        "titulo_visual": new_title in visual_text,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise RuntimeError(f"Fallaron controles: {failed}")
    print(json.dumps({"status": "VERDE_ESTRUCTURAL", **checks}, ensure_ascii=False))


if __name__ == "__main__":
    main()
