#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "NS.Report/definition/report.json"
PAGE = ROOT / "NS.Report/definition/pages/df1cb253a6314642a469"
BOOKMARKS = ROOT / "NS.Report/definition/bookmarks"
EVIDENCE = ROOT / "Docs/AUDITORIA_LIVE/latest/lienzo_02_bookmark_validation.json"

CHARTS = [
    "in_chart_pedidos_dia_mes",
    "in_chart_lineas_dia_mes",
    "in_chart_unidades_dia_mes",
]

BOOKMARK_EXPECTED = {
    "b9128c5f202a5c05b8c6": "in_chart_pedidos_dia_mes",
    "28bcc015c63284b1ea20": "in_chart_lineas_dia_mes",
    "0a642a9eca955eab8d61": "in_chart_unidades_dia_mes",
}

BUTTONS = {
    "57f10ff400d0000bd6d2": ("VER POR PEDIDOS", "Mostrar tendencia de pedidos", "b9128c5f202a5c05b8c6"),
    "8dab02c301ebb2810320": ("VER POR LINEAS", "Mostrar tendencia de líneas", "28bcc015c63284b1ea20"),
    "2155081fa518460cc812": ("VER POR UNIDADES", "Mostrar tendencia de unidades", "0a642a9eca955eab8d61"),
}


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def literal(value: str) -> dict:
    return {"expr": {"Literal": {"Value": f"'{value}'"}}}


def fix_report() -> int:
    data = read(REPORT)
    filters = data.setdefault("filterConfig", {}).setdefault("filters", [])
    kept = []
    removed = 0
    for item in filters:
        col = (((item.get("field") or {}).get("Column") or {}))
        entity = (((col.get("Expression") or {}).get("SourceRef") or {}).get("Entity"))
        prop = col.get("Property")
        if entity == "Fact_Tracking" and prop == "PED_CANAL_CODIGO":
            removed += 1
        else:
            kept.append(item)
    data["filterConfig"]["filters"] = kept
    write(REPORT, data)
    return removed


def fix_button(visual_id: str, label: str, tooltip: str, bookmark: str):
    path = PAGE / "visuals" / visual_id / "visual.json"
    data = read(path)
    visual = data["visual"]
    text_states = visual.setdefault("objects", {}).setdefault("text", [])
    for state in text_states:
        state.setdefault("properties", {})["text"] = literal(label)
    links = visual.setdefault("visualContainerObjects", {}).setdefault("visualLink", [])
    if len(links) != 1:
        raise RuntimeError(f"{visual_id}: visualLink esperado 1, actual {len(links)}")
    props = links[0].setdefault("properties", {})
    props["tooltip"] = literal(tooltip)
    props["bookmark"] = literal(bookmark)
    titles = visual["visualContainerObjects"].setdefault("title", [])
    if titles:
        titles[0].setdefault("properties", {})["text"] = literal(label)
    write(path, data)


def validate_bookmark(bookmark: str, visible: str) -> dict:
    path = BOOKMARKS / f"{bookmark}.bookmark.json"
    data = read(path)
    targets = data.get("options", {}).get("targetVisualNames", [])
    filters = data.get("explorationState", {}).get("filters", {})
    containers = (
        data.get("explorationState", {})
        .get("sections", {})
        .get("df1cb253a6314642a469", {})
        .get("visualContainers", {})
    )
    states = {}
    for chart in CHARTS:
        display = ((containers.get(chart) or {}).get("singleVisual") or {}).get("display")
        states[chart] = "hidden" if display == {"mode": "hidden"} else "visible"
    expected = {chart: ("visible" if chart == visible else "hidden") for chart in CHARTS}
    errors = []
    if targets != CHARTS:
        errors.append(f"targets={targets}")
    if filters not in ({}, None):
        errors.append("filters_no_vacios")
    if states != expected:
        errors.append(f"states={states}, expected={expected}")
    return {"bookmark": bookmark, "targets": targets, "filters": filters, "states": states, "errors": errors}


def validate_button(visual_id: str, label: str, tooltip: str, bookmark: str) -> dict:
    data = read(PAGE / "visuals" / visual_id / "visual.json")
    visual = data["visual"]
    text_values = []
    for state in visual.get("objects", {}).get("text", []):
        text_values.append(state.get("properties", {}).get("text", {}).get("expr", {}).get("Literal", {}).get("Value"))
    link = visual.get("visualContainerObjects", {}).get("visualLink", [])[0]["properties"]
    actual_tooltip = link["tooltip"]["expr"]["Literal"]["Value"]
    actual_bookmark = link["bookmark"]["expr"]["Literal"]["Value"]
    expected_label = f"'{label}'"
    errors = []
    if any(value != expected_label for value in text_values):
        errors.append(f"textos={text_values}")
    if actual_tooltip != f"'{tooltip}'":
        errors.append(f"tooltip={actual_tooltip}")
    if actual_bookmark != f"'{bookmark}'":
        errors.append(f"bookmark={actual_bookmark}")
    return {"visual": visual_id, "texts": text_values, "tooltip": actual_tooltip, "bookmark": actual_bookmark, "errors": errors}


def main() -> int:
    removed = fix_report()
    for visual_id, (label, tooltip, bookmark) in BUTTONS.items():
        fix_button(visual_id, label, tooltip, bookmark)

    report = read(REPORT)
    global_filters = report.get("filterConfig", {}).get("filters", [])
    bookmarks = [validate_bookmark(b, v) for b, v in BOOKMARK_EXPECTED.items()]
    buttons = [validate_button(v, *meta) for v, meta in BUTTONS.items()]
    errors = []
    if global_filters:
        errors.append(f"global_filters={global_filters}")
    for item in bookmarks + buttons:
        errors.extend(item["errors"])
    result = {
        "status": "VERDE" if not errors else "ROJO",
        "global_channel_filters_removed": removed,
        "global_filters_remaining": len(global_filters),
        "bookmarks": bookmarks,
        "buttons": buttons,
        "errors": errors,
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    write(EVIDENCE, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
