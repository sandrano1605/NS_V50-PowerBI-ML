#!/usr/bin/env python3
"""Corrige y valida dos medidas de texto de ventana temporal en Medidas.tmdl.

La reparación es deliberadamente estrecha:
- elimina formatString numérico de medidas que devuelven texto;
- elimina lineageTag huérfanos/duplicados conocidos;
- no altera las expresiones DAX ni ninguna otra medida.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MODEL_PATH = Path("NS.SemanticModel/definition/tables/Medidas.tmdl")
EVIDENCE_PATH = Path("Docs/AUDITORIA_LIVE/latest/window_measure_validation.json")

TARGETS = {
    "RE Estado último mes": {
        "canonical_lineage": "27000000-0000-4000-8000-000000000153",
        "orphan_lineage": "818ab90d-4ecb-4163-b52b-97af5bb80213",
    },
    "RE Ventana análisis texto": {
        "canonical_lineage": "27000000-0000-4000-8000-000000000152",
        "orphan_lineage": "a05dd22d-ee32-4c06-a3dd-b846de9f6c77",
    },
}


def measure_blocks(lines: list[str]) -> dict[str, tuple[int, int]]:
    starts: list[tuple[str, int]] = []
    for index, line in enumerate(lines):
        if line.startswith("\tmeasure '") and "' =" in line:
            name = line.split("\tmeasure '", 1)[1].split("' =", 1)[0]
            starts.append((name, index))

    blocks: dict[str, tuple[int, int]] = {}
    for pos, (name, start) in enumerate(starts):
        end = starts[pos + 1][1] if pos + 1 < len(starts) else len(lines)
        blocks[name] = (start, end)
    return blocks


def validate(text: str) -> dict[str, object]:
    lines = text.splitlines()
    blocks = measure_blocks(lines)
    errors: list[str] = []
    details: dict[str, object] = {}

    for name, meta in TARGETS.items():
        if name not in blocks:
            errors.append(f"No se encontró la medida: {name}")
            continue
        start, end = blocks[name]
        block = lines[start:end]
        numeric_formats = [line for line in block if line.strip() == "formatString: 0"]
        canonical = [line for line in block if meta["canonical_lineage"] in line]
        orphan = [line for line in lines if meta["orphan_lineage"] in line]
        text_literals = any('"Último mes' in line or '"Período analizado:' in line for line in block)

        if numeric_formats:
            errors.append(f"{name}: conserva formatString numérico 0")
        if len(canonical) != 1:
            errors.append(f"{name}: lineageTag canónico esperado 1, actual {len(canonical)}")
        if orphan:
            errors.append(f"{name}: conserva lineageTag huérfano {meta['orphan_lineage']}")
        if not text_literals:
            errors.append(f"{name}: no se reconoce como medida textual esperada")

        details[name] = {
            "block_start_line": start + 1,
            "block_end_line": end,
            "numeric_format_count": len(numeric_formats),
            "canonical_lineage_count": len(canonical),
            "orphan_lineage_count": len(orphan),
            "text_expression_detected": text_literals,
        }

    return {
        "status": "VERDE" if not errors else "ROJO",
        "file": str(MODEL_PATH),
        "targets": details,
        "errors": errors,
        "scope": "Solo metadatos de dos medidas de texto; DAX sin cambios",
    }


def repair(text: str) -> str:
    lines = text.splitlines(keepends=True)
    blocks = measure_blocks([line.rstrip("\r\n") for line in lines])
    missing = sorted(set(TARGETS) - set(blocks))
    if missing:
        raise RuntimeError(f"Medidas no encontradas: {', '.join(missing)}")

    remove_indexes: set[int] = set()
    for name, meta in TARGETS.items():
        start, end = blocks[name]
        for index in range(start, end):
            if lines[index].strip() == "formatString: 0":
                remove_indexes.add(index)
        for index, line in enumerate(lines):
            if meta["orphan_lineage"] in line:
                remove_indexes.add(index)

    if len(remove_indexes) != 4:
        raise RuntimeError(
            f"Se esperaban exactamente 4 líneas a retirar; se detectaron {len(remove_indexes)}: "
            f"{sorted(i + 1 for i in remove_indexes)}"
        )

    return "".join(line for index, line in enumerate(lines) if index not in remove_indexes)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Solo validar; no modificar")
    args = parser.parse_args()

    original = MODEL_PATH.read_text(encoding="utf-8-sig")
    if not args.check:
        repaired = repair(original)
        MODEL_PATH.write_text(repaired, encoding="utf-8", newline="\n")

    current = MODEL_PATH.read_text(encoding="utf-8-sig")
    result = validate(current)
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "VERDE" else 1


if __name__ == "__main__":
    sys.exit(main())
