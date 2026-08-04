#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAGE_ID = "df1cb253a6314642a469"
PAGE_DIR = ROOT / "NS.Report/definition/pages" / PAGE_ID
VISUALS_DIR = PAGE_DIR / "visuals"
MODEL_DIR = ROOT / "NS.SemanticModel/definition/tables"
DOCS = ROOT / "Docs/AUDITORIA_LIVE/latest"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def load_json(path: Path) -> Any:
    return json.loads(read_text(path))


def save_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def literal(value: str) -> dict[str, Any]:
    return {"expr": {"Literal": {"Value": value}}}


def source_ref(entity: str) -> dict[str, Any]:
    return {"SourceRef": {"Entity": entity}}


def column_field(entity: str, prop: str) -> dict[str, Any]:
    return {"Column": {"Expression": source_ref(entity), "Property": prop}}


def measure_field(entity: str, prop: str) -> dict[str, Any]:
    return {"Measure": {"Expression": source_ref(entity), "Property": prop}}


def projection_column(entity: str, prop: str, display: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "field": column_field(entity, prop),
        "queryRef": f"{entity}.{prop}",
        "nativeQueryRef": display or prop,
        "active": True,
    }
    if display:
        result["displayName"] = display
    return result


def projection_measure(prop: str, display: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "field": measure_field("Medidas", prop),
        "queryRef": f"Medidas.{prop}",
        "nativeQueryRef": display or prop,
    }
    if display:
        result["displayName"] = display
    return result


def field_filter(name: str, field: dict[str, Any], kind: str) -> dict[str, Any]:
    return {"name": name, "field": field, "type": kind}


def set_position(data: dict[str, Any], *, name: str, x: float, y: float, width: float, height: float, z: int, tab: int) -> None:
    data["name"] = name
    data["position"] = {
        "x": x,
        "y": y,
        "z": z,
        "height": height,
        "width": width,
        "tabOrder": tab,
    }


def set_title(data: dict[str, Any], text: str, font_size: str = "11D") -> None:
    vco = data.setdefault("visual", {}).setdefault("visualContainerObjects", {})
    vco["title"] = [{
        "properties": {
            "show": literal("true"),
            "text": literal(f"'{text}'"),
            "alignment": literal("'left'"),
            "fontSize": literal(font_size),
            "fontFamily": literal("'Segoe UI Semibold'"),
            "fontColor": {"solid": {"color": literal("'#1B365D'")}},
        }
    }]
    vco.pop("visualTooltip", None)


def recursive_replace(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, dict):
        return {key: recursive_replace(child, replacements) for key, child in value.items()}
    if isinstance(value, list):
        return [recursive_replace(child, replacements) for child in value]
    if isinstance(value, str):
        result = value
        for old, new in replacements.items():
            result = result.replace(old, new)
        return result
    return value


def build_slicer(template: dict[str, Any], *, name: str, x: int, width: int, entity: str | None = None,
                 prop: str | None = None, title: str | None = None, keep_sync: bool = False) -> dict[str, Any]:
    data = copy.deepcopy(template)
    if entity and prop:
        data = recursive_replace(data, {
            "Dim_Pedido": entity,
            "CLASIFICACION": prop,
        })
    if title:
        data = recursive_replace(data, {"CLASIFICACIÓN": title})
    set_position(data, name=name, x=x, y=76, width=width, height=60, z=5000, tab=6000 + x)
    if not keep_sync:
        data.get("visual", {}).pop("syncGroup", None)
        # Eliminar cualquier selección guardada heredada del slicer plantilla.
        objects = data.get("visual", {}).get("objects", {})
        objects.pop("general", None)
        for item in data.get("filterConfig", {}).get("filters", []):
            item.pop("filter", None)
            item.pop("objects", None)
    return data


def build_card(template: dict[str, Any], *, name: str, measure: str, title: str, x: int, width: int) -> dict[str, Any]:
    data = copy.deepcopy(template)
    set_position(data, name=name, x=x, y=150, width=width, height=72, z=7000, tab=7000 + x)
    data["visual"]["query"] = {"queryState": {"Values": {"projections": [projection_measure(measure, title)]}}}
    set_title(data, title, "10D")
    data["filterConfig"] = {"filters": [field_filter(f"{name}_m", measure_field("Medidas", measure), "Advanced")]}
    return data


def build_matrix(template: dict[str, Any]) -> dict[str, Any]:
    data = copy.deepcopy(template)
    set_position(data, name="in_matrix_semana", x=24, y=238, width=552, height=252, z=9000, tab=9000)
    data["visual"]["query"] = {
        "queryState": {
            "Rows": {"projections": [projection_column("Dim_Fecha", "Dia_Semana", "Día de semana")]},
            "Values": {"projections": [
                projection_measure("IN Pedidos", "Pedidos"),
                projection_measure("IN Líneas", "Líneas"),
                projection_measure("IN Unidades", "Unidades"),
            ]},
        },
        "sortDefinition": {
            "sort": [{"field": column_field("Dim_Fecha", "Dia_Semana"), "direction": "Ascending"}],
            "isDefaultSort": True,
        },
    }
    set_title(data, "¿Qué día concentra más pedidos, líneas y unidades?", "10D")
    data["filterConfig"] = {"filters": [
        field_filter("in_mx_dia", column_field("Dim_Fecha", "Dia_Semana"), "Categorical"),
        field_filter("in_mx_ped", measure_field("Medidas", "IN Pedidos"), "Advanced"),
        field_filter("in_mx_lin", measure_field("Medidas", "IN Líneas"), "Advanced"),
        field_filter("in_mx_uni", measure_field("Medidas", "IN Unidades"), "Advanced"),
    ]}
    return data


def build_chart(template: dict[str, Any], *, name: str, visual_type: str, title: str,
                x: int, y: int, width: int, height: int,
                category: tuple[str, str], measure: str,
                series: tuple[str, str] | None = None,
                line_measure: str | None = None,
                tab: int = 10000) -> dict[str, Any]:
    data = copy.deepcopy(template)
    set_position(data, name=name, x=x, y=y, width=width, height=height, z=10000, tab=tab)
    visual = data["visual"]
    visual["visualType"] = visual_type
    state: dict[str, Any] = {
        "Category": {"projections": [projection_column(category[0], category[1])]},
        "Y": {"projections": [projection_measure(measure)]},
    }
    if series:
        state["Series"] = {"projections": [projection_column(series[0], series[1])]} 
    if line_measure:
        state["Y2"] = {"projections": [projection_measure(line_measure, "Promedio")]}
    visual["query"] = {
        "queryState": state,
        "sortDefinition": {
            "sort": [{"field": column_field(category[0], category[1]), "direction": "Ascending"}],
            "isDefaultSort": True,
        },
    }
    visual["objects"] = {
        "labels": [{"properties": {"show": literal("false")}}],
    }
    set_title(data, title, "10D")
    filters = [
        field_filter(f"{name}_cat", column_field(category[0], category[1]), "Categorical"),
        field_filter(f"{name}_val", measure_field("Medidas", measure), "Advanced"),
    ]
    if series:
        filters.append(field_filter(f"{name}_ser", column_field(series[0], series[1]), "Categorical"))
    if line_measure:
        filters.append(field_filter(f"{name}_line", measure_field("Medidas", line_measure), "Advanced"))
    data["filterConfig"] = {"filters": filters}
    return data


def build_textbox(template: dict[str, Any], *, name: str, x: int, y: int, width: int, height: int,
                  lines: list[tuple[str, str, bool]]) -> dict[str, Any]:
    data = copy.deepcopy(template)
    set_position(data, name=name, x=x, y=y, width=width, height=height, z=4000, tab=4000 + y)
    paragraphs = []
    for text, size, bold in lines:
        paragraphs.append({"textRuns": [{
            "value": text,
            "textStyle": {"fontWeight": "bold" if bold else "normal", "fontSize": size},
        }]})
    data["visual"]["objects"]["general"][0]["properties"]["paragraphs"] = paragraphs
    return data


def install_visual(name: str, data: dict[str, Any]) -> None:
    folder = VISUALS_DIR / name
    folder.mkdir(parents=True, exist_ok=True)
    save_json(folder / "visual.json", data)


def modify_master_datetime() -> None:
    path = MODEL_DIR / "Fact_Pedidos_Auditoria.tmdl"
    text = read_text(path)
    old = '''\t\t\t\t                            "    CAST(COALESCE(",
\t\t\t\t                            "        TRY_CONVERT(DATE, CONVERT(VARCHAR(30), V.ERDAT), 112),",
\t\t\t\t                            "        TRY_CONVERT(DATE, CONVERT(VARCHAR(30), V.ERDAT), 103),",
\t\t\t\t                            "        TRY_CONVERT(DATE, CONVERT(VARCHAR(30), V.ERDAT))",
\t\t\t\t                            "    ) AS DATETIME2(0)) AS PED_FECHA_HORA,",'''
    new = '''\t\t\t\t                            "    DATEADD(SECOND,",
\t\t\t\t                            "        CASE",
\t\t\t\t                            "            WHEN TRY_CONVERT(TIME(0), STUFF(STUFF(RIGHT('000000' + LTRIM(RTRIM(CONVERT(VARCHAR(6), V.ERZET))), 6), 3, 0, ':'), 6, 0, ':')) IS NULL THEN 0",
\t\t\t\t                            "            ELSE DATEDIFF(SECOND, CAST('00:00:00' AS TIME), TRY_CONVERT(TIME(0), STUFF(STUFF(RIGHT('000000' + LTRIM(RTRIM(CONVERT(VARCHAR(6), V.ERZET))), 6), 3, 0, ':'), 6, 0, ':')))",
\t\t\t\t                            "        END,",
\t\t\t\t                            "        CAST(COALESCE(",
\t\t\t\t                            "            TRY_CONVERT(DATE, CONVERT(VARCHAR(30), V.ERDAT), 112),",
\t\t\t\t                            "            TRY_CONVERT(DATE, CONVERT(VARCHAR(30), V.ERDAT), 103),",
\t\t\t\t                            "            TRY_CONVERT(DATE, CONVERT(VARCHAR(30), V.ERDAT))",
\t\t\t\t                            "        ) AS DATETIME2(0))",
\t\t\t\t                            "    ) AS PED_FECHA_HORA,",'''
    if old not in text:
        if "RIGHT('000000' + LTRIM(RTRIM(CONVERT(VARCHAR(6), V.ERZET)))" in text:
            return
        raise RuntimeError("No se encontró el bloque de fecha VBAK esperado")
    write_text(path, text.replace(old, new, 1))


def modify_tracking() -> None:
    path = MODEL_DIR / "Fact_Tracking.tmdl"
    text = read_text(path)
    anchor_columns = '''\tcolumn FECHA_PRIMERA_FACTURA
\t\tdataType: dateTime'''
    columns = '''\tcolumn TRAMO_HORA_INGRESO
\t\tdataType: string
\t\tlineageTag: 61000000-0000-4000-8000-000000000001
\t\tsummarizeBy: none
\t\tsourceColumn: TRAMO_HORA_INGRESO
\t\tsortByColumn: ORDEN_TRAMO_HORA_INGRESO

\tcolumn ORDEN_TRAMO_HORA_INGRESO
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: 61000000-0000-4000-8000-000000000002
\t\tsummarizeBy: none
\t\tsourceColumn: ORDEN_TRAMO_HORA_INGRESO

'''
    if "\tcolumn TRAMO_HORA_INGRESO\n" not in text:
        if anchor_columns not in text:
            raise RuntimeError("No se encontró el ancla de columnas Fact_Tracking")
        text = text.replace(anchor_columns, columns + anchor_columns, 1)

    old_m = '''\t\t\t\t    PedFecha = Table.AddColumn(Zona, "PED_FECHA", each if [PED_FECHA_HORA]=null then null else Date.From([PED_FECHA_HORA]), type nullable date),
\t\t\t\t    Fact1 = Table.AddColumn(PedFecha, "FECHA_PRIMERA_FACTURA", each [FAC_P_FECHA_HORA_REAL], type nullable datetime),'''
    new_m = '''\t\t\t\t    PedFecha = Table.AddColumn(Zona, "PED_FECHA", each if [PED_FECHA_HORA]=null then null else Date.From([PED_FECHA_HORA]), type nullable date),
\t\t\t\t    TramoHoraIngreso = Table.AddColumn(PedFecha, "TRAMO_HORA_INGRESO", each let H = try Time.From([PED_FECHA_HORA]) otherwise null in if H=null or H=#time(0,0,0) then "Sin hora válida" else if H<=#time(14,30,0) then "Hasta 14:30" else "Después de 14:30", type text),
\t\t\t\t    OrdenTramoHoraIngreso = Table.AddColumn(TramoHoraIngreso, "ORDEN_TRAMO_HORA_INGRESO", each if [TRAMO_HORA_INGRESO]="Hasta 14:30" then 1 else if [TRAMO_HORA_INGRESO]="Después de 14:30" then 2 else 3, Int64.Type),
\t\t\t\t    Fact1 = Table.AddColumn(OrdenTramoHoraIngreso, "FECHA_PRIMERA_FACTURA", each [FAC_P_FECHA_HORA_REAL], type nullable datetime),'''
    if "TramoHoraIngreso = Table.AddColumn" not in text:
        if old_m not in text:
            raise RuntimeError("No se encontró el ancla M Fact_Tracking")
        text = text.replace(old_m, new_m, 1)
    write_text(path, text)


def modify_measures() -> None:
    path = MODEL_DIR / "Medidas.tmdl"
    text = read_text(path)
    if "\tmeasure 'IN Pedidos'" in text:
        return
    anchor = "\n\tcolumn __Medida\n"
    if anchor not in text:
        raise RuntimeError("No se encontró columna __Medida")
    measures = '''
\t/// Pedidos ingresados en el contexto seleccionado, abiertos y cerrados.
\tmeasure 'IN Pedidos' = DISTINCTCOUNT(Fact_Tracking[PED_NUMERO_PEDIDO])
\t\tformatString: #,0
\t\tdisplayFolder: 04. Análisis Fuera SLA\\Carga y SLA
\t\tlineageTag: 61000000-0000-4000-8000-000000000101

\tmeasure 'IN Líneas' =
\t\t\tVAR PedidosContexto = VALUES(Fact_Tracking[PED_NUMERO_PEDIDO])
\t\t\tRETURN CALCULATE(SUM(Lineas_y_unidades_por_pedidos[Lineas]), TREATAS(PedidosContexto, Lineas_y_unidades_por_pedidos[Pedido]))
\t\tformatString: #,0
\t\tdisplayFolder: 04. Análisis Fuera SLA\\Carga y SLA
\t\tlineageTag: 61000000-0000-4000-8000-000000000102

\tmeasure 'IN Unidades' =
\t\t\tVAR PedidosContexto = VALUES(Fact_Tracking[PED_NUMERO_PEDIDO])
\t\t\tRETURN CALCULATE(SUM(Lineas_y_unidades_por_pedidos[Suma_Unidades]), TREATAS(PedidosContexto, Lineas_y_unidades_por_pedidos[Pedido]))
\t\tformatString: #,0
\t\tdisplayFolder: 04. Análisis Fuera SLA\\Carga y SLA
\t\tlineageTag: 61000000-0000-4000-8000-000000000103

\tmeasure 'IN Promedio Pedidos Día' = AVERAGEX(ALLSELECTED(Dim_Fecha[Dia_Mes]), CALCULATE([IN Pedidos]))
\t\tformatString: #,0.0
\t\tdisplayFolder: 04. Análisis Fuera SLA\\Carga y SLA
\t\tlineageTag: 61000000-0000-4000-8000-000000000104

\tmeasure 'IN Promedio Líneas Día' = AVERAGEX(ALLSELECTED(Dim_Fecha[Dia_Mes]), CALCULATE([IN Líneas]))
\t\tformatString: #,0.0
\t\tdisplayFolder: 04. Análisis Fuera SLA\\Carga y SLA
\t\tlineageTag: 61000000-0000-4000-8000-000000000105

\tmeasure 'IN Promedio Unidades Día' = AVERAGEX(ALLSELECTED(Dim_Fecha[Dia_Mes]), CALCULATE([IN Unidades]))
\t\tformatString: #,0.0
\t\tdisplayFolder: 04. Análisis Fuera SLA\\Carga y SLA
\t\tlineageTag: 61000000-0000-4000-8000-000000000106
'''
    write_text(path, text.replace(anchor, measures + anchor, 1))


def build_report() -> None:
    page_path = PAGE_DIR / "page.json"
    page = load_json(page_path)
    page["displayName"] = "02 Ingreso de Pedidos"
    page.pop("visibility", None)
    page["height"] = 940
    page["width"] = 1600
    save_json(page_path, page)

    templates = DOCS / "page02_visual_templates"
    native = DOCS / "native_visual_templates"
    slicers = DOCS / "page00_slicer_templates"

    # Retirar visuales operacionales antiguos que serán reemplazados.
    for old in ["table_cef7a98ad59848", "table_f0e8d63e5a444c"]:
        shutil.rmtree(VISUALS_DIR / old, ignore_errors=True)

    title_template = load_json(templates / "text_6d7cf337c16a45.json")
    title = build_textbox(
        title_template,
        name="text_6d7cf337c16a45",
        x=24, y=0, width=840, height=58,
        lines=[
            ("02 INGRESO DE PEDIDOS", "20pt", True),
            ("Cuándo entra la carga y en qué momento queda disponible para Logística", "9pt", False),
        ],
    )
    install_visual("text_6d7cf337c16a45", title)

    note = build_textbox(
        title_template,
        name="in_nota_cierre",
        x=586, y=151, width=990, height=70,
        lines=[
            ("LECTURA DEL LIENZO", "10pt", True),
            ("Cierre = últimos 7 días hábiles · barras = flujo · línea = promedio del período filtrado", "9pt", False),
        ],
    )
    install_visual("in_nota_cierre", note)

    card_template = load_json(templates / "table_62c6c02944b14e.json")
    install_visual("table_9601cabf413a41", build_card(card_template, name="table_9601cabf413a41", measure="IN Pedidos", title="Pedidos ingresados", x=24, width=170))
    install_visual("table_62c6c02944b14e", build_card(card_template, name="table_62c6c02944b14e", measure="IN Líneas", title="Líneas ingresadas", x=206, width=170))
    install_visual("table_bad13c26c1d64f", build_card(card_template, name="table_bad13c26c1d64f", measure="IN Unidades", title="Unidades ingresadas", x=388, width=170))

    month_template = load_json(slicers / "slicer_mes_3m_v39.json")
    month = build_slicer(month_template, name="sync_mes_3m_v39", x=24, width=190, keep_sync=True)
    install_visual("sync_mes_3m_v39", month)

    class_template = load_json(slicers / "slicer_clasif.json")
    zone_template = load_json(slicers / "slicer_zona.json")
    install_visual("in_slicer_flujo", build_slicer(class_template, name="in_slicer_flujo", x=226, width=190, entity="Fact_Tracking", prop="CLASIFICACION", title="FLUJO"))
    install_visual("in_slicer_zona", build_slicer(zone_template, name="in_slicer_zona", x=428, width=180, entity="Fact_Tracking", prop="ZONA", title="ZONA"))
    install_visual("in_slicer_responsable", build_slicer(class_template, name="in_slicer_responsable", x=620, width=250, entity="Dim_Responsable", prop="RESPONSABLE_CODIGO", title="RESPONSABLE"))
    install_visual("in_slicer_canal", build_slicer(class_template, name="in_slicer_canal", x=882, width=190, entity="Dim_Canal", prop="CANAL", title="CANAL"))
    install_visual("in_slicer_momento", build_slicer(class_template, name="in_slicer_momento", x=1084, width=292, entity="Dim_Fecha", prop="Momento_Mes", title="MOMENTO DEL MES"))

    matrix_template = load_json(native / "3b0d647a439385b325bd.json")
    install_visual("in_matrix_semana", build_matrix(matrix_template))

    chart_template = load_json(templates / "chart_924aca87b5094c.json")
    cutoff = build_chart(
        chart_template,
        name="chart_924aca87b5094c",
        visual_type="hundredPercentStackedColumnChart",
        title="¿Qué proporción queda disponible hasta o después de las 14:30?",
        x=590, y=238, width=986, height=252,
        category=("Dim_Fecha", "Dia_Semana"),
        measure="IN Pedidos",
        series=("Fact_Tracking", "TRAMO_HORA_INGRESO"),
        tab=10000,
    )
    install_visual("chart_924aca87b5094c", cutoff)

    trends = [
        ("in_chart_pedidos_dia_mes", "Pedidos por día del mes · tendencia de cierre", 24, "IN Pedidos", "IN Promedio Pedidos Día"),
        ("in_chart_lineas_dia_mes", "Líneas por día del mes · tendencia de cierre", 540, "IN Líneas", "IN Promedio Líneas Día"),
        ("in_chart_unidades_dia_mes", "Unidades por día del mes · tendencia de cierre", 1056, "IN Unidades", "IN Promedio Unidades Día"),
    ]
    for index, (name, title_text, x, measure, avg) in enumerate(trends):
        chart = build_chart(
            chart_template,
            name=name,
            visual_type="lineStackedColumnComboChart",
            title=title_text,
            x=x, y=516, width=500 if x < 1056 else 520, height=392,
            category=("Dim_Fecha", "Dia_Mes"),
            measure=measure,
            series=("Fact_Tracking", "CLASIFICACION"),
            line_measure=avg,
            tab=11000 + index,
        )
        install_visual(name, chart)


def validate() -> dict[str, Any]:
    errors: list[str] = []
    required_measures = [
        "IN Pedidos", "IN Líneas", "IN Unidades",
        "IN Promedio Pedidos Día", "IN Promedio Líneas Día", "IN Promedio Unidades Día",
    ]
    medidas = read_text(MODEL_DIR / "Medidas.tmdl")
    for measure in required_measures:
        if medidas.count(f"measure '{measure}'") != 1:
            errors.append(f"Medida ausente o duplicada: {measure}")

    tracking = read_text(MODEL_DIR / "Fact_Tracking.tmdl")
    for token in ["TRAMO_HORA_INGRESO", "ORDEN_TRAMO_HORA_INGRESO", "#time(14,30,0)", "Sin hora válida"]:
        if token not in tracking:
            errors.append(f"Fact_Tracking no contiene: {token}")

    master = read_text(MODEL_DIR / "Fact_Pedidos_Auditoria.tmdl")
    if "V.ERZET" not in master or "PED_FECHA_HORA" not in master:
        errors.append("La integración VBAK no combina ERDAT + ERZET")

    page = load_json(PAGE_DIR / "page.json")
    if page.get("displayName") != "02 Ingreso de Pedidos":
        errors.append("Nombre de página incorrecto")
    if "visibility" in page:
        errors.append("La página sigue oculta")

    expected = {
        "sync_mes_3m_v39": "slicer",
        "in_slicer_flujo": "slicer",
        "in_slicer_zona": "slicer",
        "in_slicer_responsable": "slicer",
        "in_slicer_canal": "slicer",
        "in_slicer_momento": "slicer",
        "in_matrix_semana": "pivotTable",
        "chart_924aca87b5094c": "hundredPercentStackedColumnChart",
        "in_chart_pedidos_dia_mes": "lineStackedColumnComboChart",
        "in_chart_lineas_dia_mes": "lineStackedColumnComboChart",
        "in_chart_unidades_dia_mes": "lineStackedColumnComboChart",
    }
    names: set[str] = set()
    visual_types: dict[str, str] = {}
    for file in VISUALS_DIR.glob("*/visual.json"):
        try:
            data = load_json(file)
        except Exception as exc:
            errors.append(f"JSON inválido {file}: {exc}")
            continue
        name = data.get("name")
        if name in names:
            errors.append(f"Nombre visual duplicado: {name}")
        names.add(name)
        visual_types[file.parent.name] = data.get("visual", {}).get("visualType")
        pos = data.get("position", {})
        if pos:
            if (pos.get("x", 0) + pos.get("width", 0)) > 1600.01 or (pos.get("y", 0) + pos.get("height", 0)) > 940.01:
                errors.append(f"Visual fuera del lienzo: {file.parent.name}")
        raw = json.dumps(data, ensure_ascii=False)
        if "Python" in raw or "data:image/svg+xml" in raw or '"visualType": "image"' in raw:
            errors.append(f"Visual técnico no permitido: {file.parent.name}")

    for name, expected_type in expected.items():
        if visual_types.get(name) != expected_type:
            errors.append(f"{name}: esperado {expected_type}, actual {visual_types.get(name)}")

    old_fields = ["OP Días Exceso", "OP Pedidos Fuera KPI", "OP Cuello de Botella", "OP Valor Afectado", "OP Cobertura Hitos %"]
    page_raw = "\n".join(read_text(p) for p in VISUALS_DIR.glob("*/visual.json"))
    for old in old_fields:
        if old in page_raw:
            errors.append(f"Campo antiguo aún presente en página 02: {old}")

    result = {
        "status": "VERDE" if not errors else "ROJO",
        "page": PAGE_ID,
        "display_name": page.get("displayName"),
        "visual_count": len(visual_types),
        "required_visuals": expected,
        "measures": required_measures,
        "filters": ["Mes - Año", "Flujo", "Zona", "Responsable", "Canal", "Momento del mes"],
        "business_questions": {
            "Q1": "Día de semana con mayor pedidos, líneas y unidades",
            "Q2": "Disponibilidad hasta/después de 14:30 y sin hora válida",
            "Q3": "Tendencia por día del mes y aporte por flujo para pedidos, líneas y unidades",
        },
        "errors": errors,
    }
    save_json(DOCS / "lienzo_02_build_validation.json", result)
    return result


def main() -> int:
    modify_master_datetime()
    modify_tracking()
    modify_measures()
    build_report()
    result = validate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "VERDE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
