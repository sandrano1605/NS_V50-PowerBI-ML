#!/usr/bin/env python3
"""Valida el kit de integración VBAK antes de abrir Power BI Desktop.

No interpreta M completo; aplica barreras determinísticas sobre alcance, archivos,
marcadores y controles obligatorios. También verifica que la rama no modifique
el PBIP respecto del punto estable a8e8186.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BASE_SHA = "a8e818604826e689453769103d962cd3537399ed"
ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "PowerQuery" / "VBAK_APPEND"

REQUIRED_FILES = {
    "00_VBAK_SCHEMA_PREFLIGHT.pq": ["sys.columns", "VBAK_SAP", "KNA1_SAP", "ESTADO"],
    "01_VBAK_APPEND_ACTIVO.pq": ["false meta", "IsParameterQuery", "Logical"],
    "02_VBAK_ATRIBUTOS_MAYORISTA.pq": ["VBAK_SAP", "KNA1_SAP", "PED_CANAL_CODIGO", "PED_FECHA_HORA"],
    "03_FACT_PEDIDOS_AUDITORIA_APPEND_BLOCK.pq": [
        "MasterBase = #\"Filas ordenadas\"",
        "JoinKind.LeftAnti",
        "VBAK_ELEGIBLE_APPEND",
        "CANDIDATO FES",
        "MissingField.UseNull",
        "Value.ReplaceType",
        "VBAK SIN ZART",
        "ResultadoVBAK = if VBAK_APPEND_ACTIVO",
    ],
    "04_VBAK_APPEND_CONTROL.pq": [
        "DUPLICADOS_MASTER",
        "APPEND_REGION_NULA",
        "APPEND_ES_FES",
        "APPEND_ES_SALDO",
        "APPEND_SALIDA_SIN_FACTURA",
    ],
    "05_VBAK_APPEND_PREFLIGHT_DETALLE.pq": [
        "CUARENTENA FES",
        "VBAK_ELEGIBLE_APPEND",
        "VBAK_MOTIVO",
    ],
}


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def main() -> int:
    errors: list[str] = []
    details: dict[str, object] = {}

    for name, markers in REQUIRED_FILES.items():
        path = KIT / name
        if not path.exists():
            errors.append(f"Falta archivo: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8-sig")
        missing = [marker for marker in markers if marker not in text]
        if missing:
            errors.append(f"{name}: faltan marcadores {missing}")
        details[name] = {
            "bytes": len(text.encode("utf-8")),
            "lines": len(text.splitlines()),
            "missing_markers": missing,
        }

    append_path = KIT / "03_FACT_PEDIDOS_AUDITORIA_APPEND_BLOCK.pq"
    if append_path.exists():
        append_text = append_path.read_text(encoding="utf-8-sig")
        forbidden = {
            "each true, type logical),\n    AddFES": "No debe marcar FES automáticamente",
            "each true, type logical),\n    AddSaldo": "No debe marcar SALDO automáticamente",
            "Table.RemoveColumns(MasterBase": "No debe recortar columnas de la master",
        }
        for token, message in forbidden.items():
            if token in append_text:
                errors.append(message)

    try:
        changed = [line for line in git("diff", "--name-only", f"{BASE_SHA}...HEAD").splitlines() if line]
        forbidden_changes = [
            path for path in changed
            if path.startswith("NS.Report/") or path.startswith("NS.SemanticModel/")
        ]
        if forbidden_changes:
            errors.append(
                "La rama de preparación no puede modificar todavía el PBIP: "
                + ", ".join(forbidden_changes)
            )
        details["git_changed_files"] = changed
        details["pbip_changes"] = forbidden_changes
    except Exception as exc:  # pragma: no cover - diagnóstico local
        errors.append(f"No fue posible validar el alcance Git: {exc}")

    result = {
        "status": "VERDE" if not errors else "ROJO",
        "base_sha": BASE_SHA,
        "kit_path": str(KIT.relative_to(ROOT)),
        "details": details,
        "errors": errors,
        "next_step": (
            "Abrir Power BI y ejecutar el preflight con VBAK_APPEND_ACTIVO=false"
            if not errors
            else "Corregir errores antes de abrir Power BI"
        ),
    }

    output = ROOT / "Docs" / "AUDITORIA_LIVE" / "latest" / "vbak_append_kit_validation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "VERDE" else 1


if __name__ == "__main__":
    sys.exit(main())
