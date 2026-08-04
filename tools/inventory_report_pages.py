#!/usr/bin/env python3
from __future__ import annotations

import csv
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
    for key, value in walk_values(data):
        if key in {"queryRef", "nativeQueryRef"} and isinstance(value, str):
            if "." in value and len(value) < 180:
                fields.add(value)
    raw = json.dumps(data, ensure_ascii=False)
    for table, column in re.findall(r'"Entity"\s*:\s*"([^"]+)"[^{}]{0,250}"Property"\s*:\s*"([^"]+)"', raw):
        fields.add(f"{table}.{column}")
    return sorted(fields)


def find_first(data: Any, wanted: str):
    for key, value in walk_values(data):
        if key == wanted:
            return value
    return None


def extract_title(data: Any) -> str | None:
    visual = data.get("visual", {}) if isinstance(data, dict) else {}
    objects = visual.get("visualContainerObjects", {}) if isinstance(visual, dict) else {}
    title = objects.get("title", []) if isinstance(objects, dict) else []
    raw = json.dumps(title, ensure_ascii=False)
    match = re.search(r'"Value"\s*:\s*"\'([^\']*)\'"', raw)
    return match.group(1) if match else None


def visual_summary(path: Path, page_id: str, page_name: str) -> dict[str, Any]:
    data = load_json(path)
    visual = data.get("visual", {}) if isinstance(data, dict) else {}
    position = data.get("position", {}) if isinstance(data, dict) else {}
    visual_type = visual.get("visualType") or find_first(data, "visualType")
    return {
        "page_id": page_id,
        "page_name": page_name,
        "visual_id": path.parent.name,
        "path": path.relative_to(ROOT).as_posix(),
        "visual_type": visual_type,
        "title": extract_title(data),
        "x": position.get("x"),
        "y": position.get("y"),
        "z": position.get("z"),
        "width": position.get("width"),
        "height": position.get("height"),
        "fields": extract_fields(data),
        "has_query": bool(visual.get("query")),
        "schema": data.get("$schema") if isinstance(data, dict) else None,
    }


def copy_visuals(visuals: list[dict[str, Any]], destination: Path) -> list[dict[str, Any]]:
    destination.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    for visual in visuals:
        src = ROOT / visual["path"]
        dst = destination / f"{visual['visual_id']}.json"
        dst.write_text(src.read_text(encoding="utf-8-sig"), encoding="utf-8")
        manifest.append({
            "visual_id": visual["visual_id"],
            "visual_type": visual["visual_type"],
            "title": visual["title"],
            "x": visual["x"],
            "y": visual["y"],
            "width": visual["width"],
            "height": visual["height"],
            "fields": visual["fields"],
            "file": dst.relative_to(ROOT).as_posix(),
        })
    (destination / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


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
            target_full[page_id] = {"page": page, "visuals": summaries}

    template_index: dict[str, list[dict[str, Any]]] = {}
    for visual in all_visuals:
        template_index.setdefault(str(visual["visual_type"]), []).append(visual)

    (OUT / "report_pages_inventory.json").write_text(json.dumps({"pages": pages}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "page_00_02_inventory.json").write_text(json.dumps(target_full, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "report_visual_templates.json").write_text(json.dumps(template_index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    page00 = [v for v in all_visuals if v["page_id"] == "71af1998e2cb472d9799"]
    page02 = [v for v in all_visuals if v["page_id"] == "df1cb253a6314642a469"]
    page00_slicers = [v for v in page00 if v["visual_type"] == "slicer"]

    copy_visuals(page00_slicers, OUT / "page00_slicer_templates")
    page02_manifest = copy_visuals(page02, OUT / "page02_visual_templates")

    with (OUT / "page02_visual_manifest.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["visual_id", "visual_type", "title", "x", "y", "width", "height", "fields"])
        writer.writeheader()
        for visual in page02_manifest:
            row = dict(visual)
            row["fields"] = " | ".join(visual["fields"])
            row.pop("file", None)
            writer.writerow(row)

    # Copiar todas las plantillas de gráficos nativos existentes para selección segura.
    native_types = {"clusteredColumnChart", "clusteredBarChart", "pivotTable", "tableEx", "cardVisual", "textbox", "shape", "slicer"}
    native_templates = [v for v in all_visuals if v["visual_type"] in native_types]
    copy_visuals(native_templates, OUT / "native_visual_templates")

    print(json.dumps({
        "status": "VERDE",
        "pages": len(pages),
        "visuals": len(all_visuals),
        "page00_slicers": len(page00_slicers),
        "page02_visuals": len(page02),
        "native_templates": len(native_templates),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
