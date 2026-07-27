#!/usr/bin/env python3
"""
Corrige los nombres de los botones de navegación de la página
"00 Resumen Ejecutivo Mayorista" en un proyecto Power BI PBIP/PBIR.

No reemplaza visuales: detecta los actionButton existentes en la franja
superior, conserva posición, formato y acción, y solo corrige el objeto text.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

TARGET_PAGE_DISPLAY_NAME = "00 Resumen Ejecutivo Mayorista"
NAV_LABELS = (
    "RESUMEN EJECUTIVO",
    "TRACKING OPERATIVO",
    "CUELLOS DE BOTELLA",
    "COLA DIARIA",
)
ACTIVE_TEXT_COLOR = "#FFFFFF"
INACTIVE_TEXT_COLOR = "#1B365D"
FONT_FAMILY = "Segoe UI Semibold"
FONT_SIZE = "10D"


@dataclass(frozen=True)
class Candidate:
    path: str
    visual_id: str
    x: float
    y: float
    width: float
    height: float
    current_text: str


@dataclass(frozen=True)
class Change:
    path: str
    visual_id: str
    label: str
    x: float
    text_color: str
    previous_text: str


def literal(value: str) -> dict[str, Any]:
    return {"expr": {"Literal": {"Value": value}}}


def literal_string(value: str) -> dict[str, Any]:
    return literal(f"'{value}'")


def literal_bool(value: bool) -> dict[str, Any]:
    return literal("true" if value else "false")


def solid_color(value: str) -> dict[str, Any]:
    return {"solid": {"color": literal_string(value)}}


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"JSON inválido: {path} | línea {exc.lineno}, columna {exc.colno}: {exc.msg}"
        ) from exc


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def extract_literal(node: Any) -> str:
    if not isinstance(node, dict):
        return ""
    try:
        value = node["expr"]["Literal"]["Value"]
    except (KeyError, TypeError):
        return ""
    return str(value).strip("'")


def find_pages_dir(root: Path) -> Path:
    direct = root / "NS.Report" / "definition" / "pages"
    if direct.is_dir():
        return direct
    matches = sorted(root.glob("*.Report/definition/pages"))
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise RuntimeError("No se encontró la carpeta definition/pages del reporte.")
    raise RuntimeError("Hay múltiples reportes; usa --root en la raíz correcta.")


def find_target_page(pages_dir: Path) -> Path:
    matches: list[Path] = []
    for page_json in pages_dir.glob("*/page.json"):
        data = read_json(page_json)
        if data.get("displayName") == TARGET_PAGE_DISPLAY_NAME:
            matches.append(page_json.parent)
    if len(matches) != 1:
        raise RuntimeError(
            f"Se esperaba una página '{TARGET_PAGE_DISPLAY_NAME}' y se encontraron {len(matches)}."
        )
    return matches[0]


def current_button_text(data: dict[str, Any]) -> str:
    objects = data.get("visual", {}).get("objects", {})
    instances = objects.get("text", [])
    if not isinstance(instances, list):
        return ""
    for instance in instances:
        if isinstance(instance, dict):
            value = extract_literal(instance.get("properties", {}).get("text", {}))
            if value:
                return value
    return ""


def collect_candidates(page_dir: Path) -> list[Candidate]:
    result: list[Candidate] = []
    for path in sorted((page_dir / "visuals").glob("*/visual.json")):
        data = read_json(path)
        visual = data.get("visual", {})
        position = data.get("position", {})
        if visual.get("visualType") != "actionButton":
            continue
        try:
            x = float(position.get("x", 0))
            y = float(position.get("y", 0))
            width = float(position.get("width", 0))
            height = float(position.get("height", 0))
        except (TypeError, ValueError):
            continue
        in_header = (
            y <= 130
            and 100 <= x <= 1050
            and 70 <= width <= 320
            and 24 <= height <= 110
        )
        if in_header:
            result.append(
                Candidate(
                    path=str(path),
                    visual_id=str(data.get("name", path.parent.name)),
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                    current_text=current_button_text(data),
                )
            )
    result.sort(key=lambda item: (item.x, item.y, item.visual_id))
    return result


def ensure_text_instance(instance: dict[str, Any], label: str, color: str) -> None:
    props = instance.setdefault("properties", {})
    props["show"] = literal_bool(True)
    props["text"] = literal_string(label)
    props["fontColor"] = solid_color(color)
    props.setdefault("fontFamily", literal_string(FONT_FAMILY))
    props.setdefault("fontSize", literal(FONT_SIZE))


def patch_button(data: dict[str, Any], label: str, active: bool) -> None:
    visual = data.setdefault("visual", {})
    if visual.get("visualType") != "actionButton":
        raise RuntimeError(f"El visual {data.get('name')} no es actionButton.")
    objects = visual.setdefault("objects", {})
    instances = objects.get("text")
    color = ACTIVE_TEXT_COLOR if active else INACTIVE_TEXT_COLOR
    if not isinstance(instances, list) or not instances:
        instances = [
            {"properties": {}, "selector": {"id": state}}
            for state in ("default", "hover", "selected", "disabled")
        ]
        objects["text"] = instances
    existing_states = {
        str(item.get("selector", {}).get("id", ""))
        for item in instances
        if isinstance(item, dict)
    }
    for item in instances:
        if isinstance(item, dict):
            ensure_text_instance(item, label, color)
    for state in ("default", "hover", "selected", "disabled"):
        if state not in existing_states:
            item = {"properties": {}, "selector": {"id": state}}
            ensure_text_instance(item, label, color)
            instances.append(item)


def validate_page(page_dir: Path) -> dict[str, int]:
    files = [page_dir / "page.json", *sorted((page_dir / "visuals").glob("*/visual.json"))]
    errors: list[str] = []
    for path in files:
        try:
            data = read_json(path)
            objects = data.get("visual", {}).get("objects", {})
            if isinstance(objects, dict) and "visualContainerObjects" in objects:
                errors.append(
                    f"{path}: visualContainerObjects está anidado dentro de objects."
                )
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))
    if errors:
        raise RuntimeError("\n".join(errors))
    return {"files_validated": len(files), "errors": 0}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    page_dir = find_target_page(find_pages_dir(root))
    candidates = collect_candidates(page_dir)

    print(f"Página objetivo: {page_dir}")
    print(f"Botones detectados: {len(candidates)}")
    for item in candidates:
        print(
            f"  x={item.x:>6.1f} y={item.y:>6.1f} "
            f"id={item.visual_id} texto='{item.current_text}'"
        )

    if len(candidates) != len(NAV_LABELS):
        raise RuntimeError(
            "Control de seguridad: se esperaban exactamente 4 actionButton en el encabezado. "
            f"Se detectaron {len(candidates)}. No se modificó ningún archivo."
        )

    changes: list[Change] = []
    for index, (candidate, label) in enumerate(zip(candidates, NAV_LABELS, strict=True)):
        path = Path(candidate.path)
        data = read_json(path)
        changes.append(
            Change(
                path=str(path.relative_to(root)),
                visual_id=candidate.visual_id,
                label=label,
                x=candidate.x,
                text_color=ACTIVE_TEXT_COLOR if index == 0 else INACTIVE_TEXT_COLOR,
                previous_text=candidate.current_text,
            )
        )
        if args.apply:
            patch_button(data, label, index == 0)
            write_json(path, data)

    validation = validate_page(page_dir)
    result = {
        "target_page": TARGET_PAGE_DISPLAY_NAME,
        "page_id": page_dir.name,
        "mode": "apply" if args.apply else "audit",
        "expected_labels": list(NAV_LABELS),
        "changes": [asdict(change) for change in changes],
        "validation": validation,
    }

    if args.report:
        report_path = args.report if args.report.is_absolute() else root / args.report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        write_json(report_path, result)
        print(f"Reporte guardado: {report_path}")

    print(
        "OK: cambios aplicados y JSON validados."
        if args.apply
        else "AUDITORÍA OK: usa --apply para modificar los botones."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
