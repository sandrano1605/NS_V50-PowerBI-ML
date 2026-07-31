#!/usr/bin/env python3
"""REQ-003: elimina tooltips técnicos en visuales que renderizan SVG/Image URL.

El script recorre todos los visual.json del PBIP, identifica visuales que proyectan
medidas/columnas SVG y fuerza visualTooltip.show=false. No modifica DAX, consultas,
relaciones, filtros, títulos ni lógica de negocio.

Uso desde la raíz del repositorio:
    python tools/fix_svg_hover_req003.py
    python tools/fix_svg_hover_req003.py --check
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = ROOT / "NS.Report" / "definition" / "pages"
EVIDENCE_DIR = ROOT / "Docs" / "AUDITORIA_LIVE" / "latest"

SVG_TOKENS = (
    " svg",
    "svg ",
    "svg_",
    "_svg",
    "imageurl",
    "image url",
    "data:image/svg",
)

# Objetos confirmados por la auditoría REQ-002. Se mantienen como control de cobertura.
EXPECTED_VISUALS = {
    "chart_mensual_3m_v39",
    "critical_table",
    "donut_flujo",
    "f07bd2d60e407e2ddd01",
    "kpi_promesa",
    "sla_panel",
    "summary_month",
    "card_4e4fe7d672d840",
    "table_c57572c4abbe4d",
}


@dataclass
class AuditRow:
    page_id: str
    visual_id: str
    path: str
    svg_fields: str
    tooltip_before: str
    tooltip_after: str
    changed: bool
    status: str


def walk_values(node: Any) -> Iterable[str]:
    """Extrae valores string recursivamente desde un JSON."""
    if isinstance(node, dict):
        for value in node.values():
            yield from walk_values(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk_values(value)
    elif isinstance(node, str):
        yield node


def is_svg_reference(value: str) -> bool:
    normalized = f" {value.strip().lower()} "
    return any(token in normalized for token in SVG_TOKENS)


def collect_svg_fields(data: dict[str, Any]) -> list[str]:
    """Devuelve referencias SVG detectadas solo en la definición del visual/query."""
    visual = data.get("visual", {})
    query = visual.get("query", {})
    objects = visual.get("objects", {})
    candidates = set()

    for value in walk_values(query):
        if is_svg_reference(value):
            candidates.add(value)

    # Algunos visuales guardan el campo de imagen dentro de objetos/selectores.
    for value in walk_values(objects):
        if is_svg_reference(value):
            candidates.add(value)

    return sorted(candidates)


def tooltip_state(data: dict[str, Any]) -> str:
    containers = data.get("visual", {}).get("visualContainerObjects", {})
    tooltip = containers.get("visualTooltip")
    if not tooltip:
        return "AUSENTE/DEFAULT"

    try:
        value = tooltip[0]["properties"]["show"]["expr"]["Literal"]["Value"]
        return str(value)
    except (KeyError, IndexError, TypeError):
        return "CONFIGURACION_NO_ESTANDAR"


def disable_tooltip(data: dict[str, Any]) -> bool:
    visual = data.setdefault("visual", {})
    containers = visual.setdefault("visualContainerObjects", {})
    desired = [
        {
            "properties": {
                "show": {"expr": {"Literal": {"Value": "false"}}},
                "type": {"expr": {"Literal": {"Value": "'Default'"}}},
                "transparency": {"expr": {"Literal": {"Value": "0L"}}},
                "fontSize": {"expr": {"Literal": {"Value": "8L"}}},
            }
        }
    ]

    if containers.get("visualTooltip") == desired:
        return False

    containers["visualTooltip"] = desired
    return True


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"La raíz JSON no es un objeto: {path}")
    return value


def write_json(path: Path, data: dict[str, Any]) -> None:
    # Formato estable y compatible con los archivos PBIP del repositorio.
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")


def run(check_only: bool) -> int:
    if not REPORT_ROOT.exists():
        print(f"ERROR: no existe {REPORT_ROOT}", file=sys.stderr)
        return 2

    rows: list[AuditRow] = []
    detected_visuals: set[str] = set()
    invalid_files: list[str] = []

    for path in sorted(REPORT_ROOT.rglob("visual.json")):
        try:
            data = load_json(path)
        except Exception as exc:  # evidencia explícita, no ocultar errores
            invalid_files.append(f"{path.relative_to(ROOT)}: {exc}")
            continue

        svg_fields = collect_svg_fields(data)
        if not svg_fields:
            continue

        visual_id = str(data.get("name") or path.parent.name)
        page_id = path.parents[2].name
        detected_visuals.add(visual_id)
        before = tooltip_state(data)
        changed = disable_tooltip(data)
        after = tooltip_state(data)

        if changed and not check_only:
            write_json(path, data)

        rows.append(
            AuditRow(
                page_id=page_id,
                visual_id=visual_id,
                path=str(path.relative_to(ROOT)).replace("\\", "/"),
                svg_fields=" | ".join(svg_fields),
                tooltip_before=before,
                tooltip_after=after,
                changed=changed,
                status="OK" if after.lower() == "false" else "ERROR",
            )
        )

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    output = EVIDENCE_DIR / "svg_hover_patch_report.csv"
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(AuditRow("", "", "", "", "", "", False, "")).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))

    missing_expected = sorted(EXPECTED_VISUALS - detected_visuals)
    changed_count = sum(1 for row in rows if row.changed)
    errors = [row for row in rows if row.status != "OK"]

    print(f"Visuales SVG detectados: {len(rows)}")
    print(f"Visuales que requerían ajuste: {changed_count}")
    print(f"Reporte: {output.relative_to(ROOT)}")

    if missing_expected:
        print("ADVERTENCIA: visuales esperados no detectados:")
        for name in missing_expected:
            print(f"  - {name}")

    if invalid_files:
        print("ERROR: JSON inválidos:", file=sys.stderr)
        for item in invalid_files:
            print(f"  - {item}", file=sys.stderr)

    if errors:
        print("ERROR: persisten visuales SVG con tooltip activo:", file=sys.stderr)
        for row in errors:
            print(f"  - {row.path}: {row.tooltip_after}", file=sys.stderr)

    if check_only and changed_count:
        print("CHECK FALLIDO: existen visuales SVG que todavía requieren parche.", file=sys.stderr)
        return 1

    if invalid_files or errors:
        return 1

    print("OK: todos los visuales SVG detectados quedan con tooltip desactivado.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Corrige hover técnico de SVG en PBIP")
    parser.add_argument(
        "--check",
        action="store_true",
        help="No modifica archivos; falla si encuentra tooltips SVG activos.",
    )
    args = parser.parse_args()
    return run(check_only=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
