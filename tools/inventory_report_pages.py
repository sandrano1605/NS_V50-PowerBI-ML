#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAGES_ROOT = ROOT / "NS.Report/definition/pages"
OUT = ROOT / "Docs/AUDITORIA_LIVE/latest"
TARGET_PAGES = {"71af1998e2cb472d9799", "df1cb253a6314642a469"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def walk_values(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from walk_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_values(child)


def extract_fields(data: Any) -> list[str]:
    fields: set[str] = set()
    entity = None
    for key, value in walk_values(data):
        if key == "Entity" and isinstance(value, str):
            entity = value
        elif key in {"Property", "Measure"} and isinstance(value, str):
            fields.add(f"{entity or '?'}[{value}]")
    raw = json.dumps(data, ensure_ascii=False)
    for match in re.findall(r"(?:'([^']+)'|([A-Za-z0-9_ ]+))\[([^\]]+)\]", raw):
        table = match[0] or match[1]
        fields.add(f"{table}[{match[2]}]")
    return sorted(fields)


def find_first(data: Any, wanted: str):
    for key, value in walk_values(data):
        if key == wanted:
            return value
    return None


def visual_summary(path: Path, page_id: str, page_name: str) -> dict[str, Any]:
    data = load_json(path)
    visual = data.get("visual", {}) if isinstance(data, dict) else {}
    position = data.get("position", {}) if isinstance(data, dict) else {}
    visual_type = visual.get("visualType") or find_first(data, "visualType")
    title_texts: list[str] = []
    for key, value in walk_values(data):
        if key in {"text", "expr"} and isinstance(value, str) and len(value) <= 250:
            title_texts.append(value)
    return {
        "page_id": page_id,
        "page_name": page_name,
        "visual_id": path.parent.name,
        "path": path.relative_to(ROOT).as_posix(),
        "visual_type": visual_type,
        "x": position.get("x"),
        "y": position.get("y"),
        "z": position.get("z"),
        "width": position.get("width"),
        "height": position.get("height"),
        "fields": extract_fields(data),
        "possible_texts": sorted(set(title_texts))[:30],
        "has_query": bool(visual.get("query")),
        "schema": data.get("$schema") if isinstance(data, dict) else None,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    pages: list[dict[str, Any]] = []
    all_visuals: list[dict[str, Any]] = []
    target_full: dict[str, Any] = {}

    for page_dir in sorted(p for p in PAGES_ROOT.iterdir() if p.is_dir()):
        page_file = page_dir / "page.json"
        if not page_file.exists():
            continue
        page = load_json(page_file)
        page_id = page_dir.name
        page_name = page.get("displayName", page_id)
        visual_files = sorted((page_dir / "visuals").glob("*/visual.json")) if (page_dir / "visuals").exists() else []
        summaries = [visual_summary(v, page_id, page_name) for v in visual_files]
        pages.append({
            "page_id": page_id,
            "display_name": page_name,
            "width": page.get("width"),
            "height": page.get("height"),
            "visibility": page.get("visibility"),
            "visual_count": len(summaries),
            "visual_types": sorted({str(v["visual_type"]) for v in summaries}),
        })
        all_visuals.extend(summaries)
        if page_id in TARGET_PAGES:
            target_full[page_id] = {
                "page": page,
                "visuals": summaries,
            }

    template_index: dict[str, list[dict[str, Any]]] = {}
    for visual in all_visuals:
        template_index.setdefault(str(visual["visual_type"]), []).append(visual)

    (OUT / "report_pages_inventory.json").write_text(
        json.dumps({"pages": pages}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUT / "page_00_02_inventory.json").write_text(
        json.dumps(target_full, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUT / "report_visual_templates.json").write_text(
        json.dumps(template_index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Copias completas de slicers de página 00 para reutilización exacta.
    slicer_dir = OUT / "page00_slicer_templates"
    slicer_dir.mkdir(parents=True, exist_ok=True)
    page00 = [v for v in all_visuals if v["page_id"] == "71af1998e2cb472d9799" and v["visual_type"] == "slicer"]
    manifest = []
    for visual in page00:
        src = ROOT / visual["path"]
        dst = slicer_dir / f"{visual['visual_id']}.json"
        dst.write_text(src.read_text(encoding="utf-8-sig"), encoding="utf-8")
        manifest.append({"visual_id": visual["visual_id"], "fields": visual["fields"], "file": dst.relative_to(ROOT).as_posix()})
    (slicer_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "VERDE",
        "pages": len(pages),
        "visuals": len(all_visuals),
        "page00_slicers": len(page00),
        "outputs": [
            "Docs/AUDITORIA_LIVE/latest/report_pages_inventory.json",
            "Docs/AUDITORIA_LIVE/latest/page_00_02_inventory.json",
            "Docs/AUDITORIA_LIVE/latest/report_visual_templates.json",
            "Docs/AUDITORIA_LIVE/latest/page00_slicer_templates/manifest.json",
        ],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
