from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

try:
    from json_repair import repair_json
except ImportError:  # pragma: no cover
    repair_json = None

ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = ROOT / "NS.Report" / "definition"
MODEL_ROOT = ROOT / "NS.SemanticModel" / "definition"
OUTPUT = ROOT / "Docs" / "AUDITORIA_LIVE" / "latest" / "structural_validation.json"

TABLE_RE = re.compile(r"^table\s+(?:'([^']+)'|(.+?))\s*$")
MEASURE_RE = re.compile(r"^\s*measure\s+(?:'([^']+)'|([^\s=]+))\s*=")
COLUMN_RE = re.compile(r"^\s*column\s+(?:'([^']+)'|([^\s]+))\s*$")


def iter_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_dicts(child)


def parse_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def repair_invalid_json(path: Path) -> bool:
    try:
        parse_json(path)
        return False
    except json.JSONDecodeError:
        if repair_json is None:
            raise RuntimeError("json-repair is required when --repair is used")
        raw = path.read_text(encoding="utf-8-sig")
        repaired = repair_json(raw, return_objects=True)
        if isinstance(repaired, str):
            repaired = json.loads(repaired)
        path.write_text(
            json.dumps(repaired, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        parse_json(path)
        return True


def unquote_name(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == "'" and value[-1] == "'":
        return value[1:-1]
    return value


def load_symbols() -> dict[str, dict[str, set[str]]]:
    symbols: dict[str, dict[str, set[str]]] = {}
    for path in MODEL_ROOT.rglob("*.tmdl"):
        text = path.read_text(encoding="utf-8-sig")
        table_name: str | None = None
        measures: set[str] = set()
        columns: set[str] = set()
        for line in text.splitlines():
            if table_name is None:
                match = TABLE_RE.match(line)
                if match:
                    table_name = unquote_name(match.group(1) or match.group(2))
                    continue
            measure = MEASURE_RE.match(line)
            if measure:
                measures.add(unquote_name(measure.group(1) or measure.group(2)))
                continue
            column = COLUMN_RE.match(line)
            if column:
                columns.add(unquote_name(column.group(1) or column.group(2)))
        if table_name:
            symbols[table_name] = {"measures": measures, "columns": columns}
    return symbols


def source_entity(ref: dict[str, Any]) -> str | None:
    expression = ref.get("Expression")
    if not isinstance(expression, dict):
        return None
    source_ref = expression.get("SourceRef")
    if not isinstance(source_ref, dict):
        return None
    entity = source_ref.get("Entity") or source_ref.get("Source")
    return entity if isinstance(entity, str) else None


def validate_reference(
    kind: str,
    ref: dict[str, Any],
    symbols: dict[str, dict[str, set[str]]],
    path: Path,
    errors: list[str],
) -> None:
    entity = source_entity(ref)
    prop = ref.get("Property")
    if not entity or not isinstance(prop, str):
        errors.append(f"{path}: referencia {kind} sin Entity/Property")
        return
    table_symbols = symbols.get(entity)
    if table_symbols is None:
        errors.append(f"{path}: tabla referenciada inexistente: {entity}")
        return
    bucket = "measures" if kind == "Measure" else "columns"
    if prop not in table_symbols[bucket]:
        errors.append(f"{path}: {kind} inexistente: {entity}[{prop}]")


def validate_visual(
    path: Path,
    obj: Any,
    symbols: dict[str, dict[str, set[str]]],
    page_sizes: dict[str, tuple[float, float]],
    errors: list[str],
    warnings: list[str],
) -> None:
    if not isinstance(obj, dict):
        errors.append(f"{path}: raíz JSON no es objeto")
        return
    required = ("$schema", "name", "position", "visual")
    for key in required:
        if key not in obj:
            errors.append(f"{path}: falta clave obligatoria {key}")
    position = obj.get("position")
    if isinstance(position, dict):
        for key in ("x", "y", "width", "height"):
            value = position.get(key)
            if not isinstance(value, (int, float)):
                errors.append(f"{path}: position.{key} no es numérico")
        width = position.get("width")
        height = position.get("height")
        if isinstance(width, (int, float)) and width <= 0:
            errors.append(f"{path}: ancho no positivo")
        if isinstance(height, (int, float)) and height <= 0:
            errors.append(f"{path}: alto no positivo")
        page_id = path.parents[1].name
        page_size = page_sizes.get(page_id)
        if page_size:
            page_width, page_height = page_size
            x, y = position.get("x"), position.get("y")
            if all(isinstance(v, (int, float)) for v in (x, y, width, height)):
                if x < -1 or y < -1:
                    errors.append(f"{path}: visual fuera del origen de página")
                if x + width > page_width + 2 or y + height > page_height + 2:
                    warnings.append(f"{path}: visual excede límites de página")
    else:
        errors.append(f"{path}: position inválido")

    visual = obj.get("visual")
    if not isinstance(visual, dict):
        errors.append(f"{path}: visual inválido")
        return
    visual_type = visual.get("visualType")
    if not isinstance(visual_type, str) or not visual_type:
        errors.append(f"{path}: visualType vacío")

    for node in iter_dicts(visual):
        measure = node.get("Measure")
        if isinstance(measure, dict):
            validate_reference("Measure", measure, symbols, path, errors)
            prop = measure.get("Property")
            if isinstance(prop, str) and "SVG" in prop.upper():
                errors.append(f"{path}: aún proyecta medida SVG: {prop}")
        column = node.get("Column")
        if isinstance(column, dict):
            validate_reference("Column", column, symbols, path, errors)

    raw = path.read_text(encoding="utf-8-sig")
    if "data:image/svg+xml" in raw.lower():
        errors.append(f"{path}: contiene URI SVG dinámica")

    title_objects = (
        visual.get("visualContainerObjects", {})
        if isinstance(visual.get("visualContainerObjects"), dict)
        else {}
    )
    title = title_objects.get("title")
    if visual_type not in {"textbox", "image", "actionButton"} and not title:
        warnings.append(f"{path}: visual analítico sin título configurado")


def load_page_sizes(errors: list[str]) -> dict[str, tuple[float, float]]:
    result: dict[str, tuple[float, float]] = {}
    pages_root = REPORT_ROOT / "pages"
    for page_path in pages_root.glob("*/page.json"):
        try:
            page = parse_json(page_path)
        except json.JSONDecodeError as exc:
            errors.append(f"{page_path}: JSON inválido: {exc}")
            continue
        if not isinstance(page, dict):
            errors.append(f"{page_path}: raíz inválida")
            continue
        width = page.get("width")
        height = page.get("height")
        if not isinstance(width, (int, float)) or not isinstance(height, (int, float)):
            errors.append(f"{page_path}: dimensiones de página inválidas")
            continue
        result[page_path.parent.name] = (float(width), float(height))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repair", action="store_true")
    args = parser.parse_args()

    json_paths = sorted(REPORT_ROOT.rglob("*.json"))
    repaired_files: list[str] = []
    syntax_errors: list[str] = []

    if args.repair:
        for path in json_paths:
            try:
                if repair_invalid_json(path):
                    repaired_files.append(str(path.relative_to(ROOT)))
            except Exception as exc:  # noqa: BLE001
                syntax_errors.append(f"{path}: reparación falló: {exc}")

    parsed: dict[Path, Any] = {}
    for path in json_paths:
        try:
            parsed[path] = parse_json(path)
        except Exception as exc:  # noqa: BLE001
            syntax_errors.append(f"{path}: {exc}")

    errors = list(syntax_errors)
    warnings: list[str] = []
    page_sizes = load_page_sizes(errors)
    symbols = load_symbols()

    visual_paths = [p for p in json_paths if p.name == "visual.json"]
    names_by_page: dict[str, set[str]] = defaultdict(set)
    for path in visual_paths:
        obj = parsed.get(path)
        validate_visual(path, obj, symbols, page_sizes, errors, warnings)
        if isinstance(obj, dict) and isinstance(obj.get("name"), str):
            page_id = path.parents[1].name
            name = obj["name"]
            if name in names_by_page[page_id]:
                errors.append(f"{path}: nombre de visual duplicado en página: {name}")
            names_by_page[page_id].add(name)

    report = {
        "status": "VERDE" if not errors else "ROJO",
        "json_total": len(json_paths),
        "visual_total": len(visual_paths),
        "pages_total": len(page_sizes),
        "repaired_count": len(repaired_files),
        "repaired_files": repaired_files,
        "errors_count": len(errors),
        "errors": sorted(set(errors)),
        "warnings_count": len(warnings),
        "warnings": sorted(set(warnings)),
        "checks": {
            "all_json_parse": not syntax_errors,
            "visual_structure": not any("falta clave" in e or "visual inválido" in e for e in errors),
            "model_references": not any("inexistente" in e or "sin Entity" in e for e in errors),
            "no_dynamic_svg_projection": not any("SVG" in e or "svg" in e for e in errors),
            "positive_dimensions": not any("no positivo" in e for e in errors),
            "unique_visual_names_per_page": not any("duplicado" in e for e in errors),
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
