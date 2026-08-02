#!/usr/bin/env python3
"""Repara y valida dos medidas textuales de ventana temporal en Medidas.tmdl.

Alcance exacto por medida:
- retirar el formatString numérico incrustado en la expresión DAX;
- llevar displayFolder al nivel correcto de metadato de medida;
- retirar el lineageTag incrustado en la expresión;
- conservar el lineageTag real de la medida y todo el DAX.

La columna oculta __Medida y su formatString: 0 deben permanecer intactos.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MODEL_PATH = Path("NS.SemanticModel/definition/tables/Medidas.tmdl")
EVIDENCE_PATH = Path("Docs/AUDITORIA_LIVE/latest/window_measure_validation.json")
DISPLAY_FOLDER = "02. Resumen Ejecutivo\\14. Ventana Temporal"

TARGETS = {
    "RE Estado último mes": {
        "valid_lineage": "818ab90d-4ecb-4163-b52b-97af5bb80213",
        "embedded_lineage": "27000000-0000-4000-8000-000000000153",
        "literal": '"Último mes parcial"',
    },
    "RE Ventana análisis texto": {
        "valid_lineage": "a05dd22d-ee32-4c06-a3dd-b846de9f6c77",
        "embedded_lineage": "27000000-0000-4000-8000-000000000152",
        "literal": '"Período analizado: "',
    },
}

TOP_LEVEL_PREFIXES = (
    "\tmeasure ",
    "\tcolumn ",
    "\tpartition ",
    "\thierarchy ",
    "\tcalculationGroup ",
    "\tannotation ",
)


def is_top_level_object(line: str) -> bool:
    return line.startswith(TOP_LEVEL_PREFIXES)


def measure_blocks(lines: list[str]) -> dict[str, tuple[int, int]]:
    blocks: dict[str, tuple[int, int]] = {}
    for start, line in enumerate(lines):
        if not (line.startswith("\tmeasure '") and "' =" in line):
            continue
        name = line.split("\tmeasure '", 1)[1].split("' =", 1)[0]
        end = len(lines)
        for index in range(start + 1, len(lines)):
            if is_top_level_object(lines[index]):
                end = index
                break
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
        bad_formats = [line for line in block if line == "\t\t\tformatString: 0"]
        good_folders = [line for line in block if line == f"\t\tdisplayFolder: {DISPLAY_FOLDER}"]
        bad_folders = [line for line in block if line == f"\t\t\tdisplayFolder: {DISPLAY_FOLDER}"]
        valid_lineages = [line for line in block if line == f"\t\tlineageTag: {meta['valid_lineage']}"]
        embedded_lineages = [line for line in block if meta["embedded_lineage"] in line]
        literal_ok = any(meta["literal"] in line for line in block)

        if bad_formats:
            errors.append(f"{name}: conserva formatString numérico dentro del DAX")
        if len(good_folders) != 1:
            errors.append(f"{name}: displayFolder válido esperado 1, actual {len(good_folders)}")
        if bad_folders:
            errors.append(f"{name}: displayFolder continúa incrustado en el DAX")
        if len(valid_lineages) != 1:
            errors.append(f"{name}: lineageTag real esperado 1, actual {len(valid_lineages)}")
        if embedded_lineages:
            errors.append(f"{name}: conserva lineageTag incrustado {meta['embedded_lineage']}")
        if not literal_ok:
            errors.append(f"{name}: no se reconoce la expresión textual esperada")

        details[name] = {
            "block_start_line": start + 1,
            "block_end_line": end,
            "embedded_numeric_format_count": len(bad_formats),
            "valid_display_folder_count": len(good_folders),
            "embedded_display_folder_count": len(bad_folders),
            "valid_lineage_count": len(valid_lineages),
            "embedded_lineage_count": len(embedded_lineages),
            "text_expression_detected": literal_ok,
        }

    hidden_column_format = "\tcolumn __Medida\n\t\tdataType: int64\n\t\tisHidden\n\t\tformatString: 0"
    hidden_column_ok = hidden_column_format in text
    if not hidden_column_ok:
        errors.append("La columna __Medida perdió su formatString: 0 válido")

    return {
        "status": "VERDE" if not errors else "ROJO",
        "file": str(MODEL_PATH),
        "targets": details,
        "hidden_column_format_preserved": hidden_column_ok,
        "errors": errors,
        "scope": "Dos medidas de texto; expresiones DAX y columna __Medida preservadas",
    }


def repair(text: str) -> str:
    raw_lines = text.splitlines(keepends=True)
    plain_lines = [line.rstrip("\r\n") for line in raw_lines]
    blocks = measure_blocks(plain_lines)
    missing = sorted(set(TARGETS) - set(blocks))
    if missing:
        raise RuntimeError(f"Medidas no encontradas: {', '.join(missing)}")

    remove_indexes: set[int] = set()
    replacements: dict[int, str] = {}

    for name, meta in TARGETS.items():
        start, end = blocks[name]
        format_indexes = [i for i in range(start, end) if plain_lines[i] == "\t\t\tformatString: 0"]
        folder_indexes = [
            i for i in range(start, end)
            if plain_lines[i] == f"\t\t\tdisplayFolder: {DISPLAY_FOLDER}"
        ]
        lineage_indexes = [
            i for i in range(start, end)
            if plain_lines[i] == f"\t\t\tlineageTag: {meta['embedded_lineage']}"
        ]
        valid_lineages = [
            i for i in range(start, end)
            if plain_lines[i] == f"\t\tlineageTag: {meta['valid_lineage']}"
        ]

        if len(format_indexes) != 1:
            raise RuntimeError(f"{name}: formatString incrustado esperado 1, actual {len(format_indexes)}")
        if len(folder_indexes) != 1:
            raise RuntimeError(f"{name}: displayFolder incrustado esperado 1, actual {len(folder_indexes)}")
        if len(lineage_indexes) != 1:
            raise RuntimeError(f"{name}: lineageTag incrustado esperado 1, actual {len(lineage_indexes)}")
        if len(valid_lineages) != 1:
            raise RuntimeError(f"{name}: lineageTag real esperado 1, actual {len(valid_lineages)}")

        remove_indexes.update(format_indexes)
        remove_indexes.update(lineage_indexes)
        folder_index = folder_indexes[0]
        newline = "\r\n" if raw_lines[folder_index].endswith("\r\n") else "\n"
        replacements[folder_index] = f"\t\tdisplayFolder: {DISPLAY_FOLDER}{newline}"

    if len(remove_indexes) != 4 or len(replacements) != 2:
        raise RuntimeError(
            "Alcance inesperado: "
            f"remociones={len(remove_indexes)}, reemplazos={len(replacements)}"
        )

    output: list[str] = []
    for index, line in enumerate(raw_lines):
        if index in remove_indexes:
            continue
        output.append(replacements.get(index, line))
    return "".join(output)


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
    EVIDENCE_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "VERDE" else 1


if __name__ == "__main__":
    sys.exit(main())
