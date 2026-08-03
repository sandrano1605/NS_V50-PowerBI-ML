#!/usr/bin/env python3
"""Valida el cruce VBAK inline antes de abrir Power BI Desktop."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BASE_SHA = "a8e818604826e689453769103d962cd3537399ed"
ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "PowerQuery" / "VBAK_APPEND"
MASTER_PATH = "NS.SemanticModel/definition/tables/Fact_Pedidos_Auditoria.tmdl"

REQUIRED_FILES = {
    "00_VBAK_SCHEMA_PREFLIGHT.pq": ["sys.columns", "VBAK_SAP", "KNA1_SAP", "ESTADO"],
    "01_VBAK_APPEND_ACTIVO.pq": ["Configuracion = \"DESACTIVADO\"", "Activar = List.Contains"],
    "02_VBAK_ATRIBUTOS_MAYORISTA.pq": ["VBAK_SAP", "KNA1_SAP", "PED_CANAL_CODIGO", "PED_FECHA_HORA"],
    "03_FACT_PEDIDOS_AUDITORIA_APPEND_BLOCK.pq": [
        "JoinKind.LeftAnti", "VBAK_ELEGIBLE_APPEND", "CANDIDATO FES", "VBAK SIN ZART"
    ],
    "04_VBAK_APPEND_CONTROL.pq": [
        "DUPLICADOS_MASTER", "APPEND_REGION_NULA", "APPEND_ES_FES", "APPEND_ES_SALDO"
    ],
    "05_VBAK_APPEND_PREFLIGHT_DETALLE.pq": ["CUARENTENA FES", "VBAK_ELEGIBLE_APPEND"],
    "06_MASTER_APPEND_INLINE_ACTIVE.pq": [
        "VBAK_APPEND_ACTIVO_LOCAL = true",
        "Sql.Database(",
        "ES_FES_VBFA",
        "JoinKind.LeftAnti",
        "VBAK SIN ZART",
        "ResultadoVBAK"
    ],
}


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=False)
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

    inline_path = KIT / "06_MASTER_APPEND_INLINE_ACTIVE.pq"
    if inline_path.exists():
        inline = inline_path.read_text(encoding="utf-8-sig")
        forbidden = {
            "ES_FES\", each true": "No debe marcar FES automáticamente",
            "ES_SALDO\", each true": "No debe marcar SALDO automáticamente",
            "Table.RemoveColumns(MasterBase": "No debe recortar columnas de la master",
        }
        for token, message in forbidden.items():
            if token in inline:
                errors.append(message)

    try:
        changed = [line for line in git("diff", "--name-only", f"{BASE_SHA}...HEAD").splitlines() if line]
        pbip_changes = [p for p in changed if p.startswith("NS.Report/") or p.startswith("NS.SemanticModel/")]
        forbidden_changes = [p for p in pbip_changes if p != MASTER_PATH]
        if forbidden_changes:
            errors.append("Cambios PBIP fuera de alcance: " + ", ".join(forbidden_changes))
        details["git_changed_files"] = changed
        details["pbip_changes"] = pbip_changes
        details["allowed_pbip_change"] = MASTER_PATH
    except Exception as exc:
        errors.append(f"No fue posible validar el alcance Git: {exc}")

    master = ROOT / MASTER_PATH
    if master.exists():
        master_text = master.read_text(encoding="utf-8-sig")
        integration_present = "VBAK_APPEND_ACTIVO_LOCAL = true" in master_text
        details["master_integration_present"] = integration_present
        if integration_present:
            for marker in ["ES_FES_VBFA", "JoinKind.LeftAnti", "VBAK SIN ZART", "in\n\t\t\t\t    ResultadoVBAK"]:
                if marker not in master_text:
                    errors.append(f"Master integrada sin marcador: {marker}")

    result = {
        "status": "VERDE" if not errors else "ROJO",
        "base_sha": BASE_SHA,
        "kit_path": str(KIT.relative_to(ROOT)),
        "details": details,
        "errors": errors,
        "next_step": "Abrir Power BI, actualizar y validar filas VBAK SIN ZART" if not errors else "Corregir antes de abrir Power BI",
    }

    output = ROOT / "Docs/AUDITORIA_LIVE/latest/vbak_append_kit_validation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "VERDE" else 1


if __name__ == "__main__":
    sys.exit(main())
