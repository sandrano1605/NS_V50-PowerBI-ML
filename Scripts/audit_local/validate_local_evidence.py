#!/usr/bin/env python3
"""Valida que una corrida del LLM local sea consumible por ChatGPT remoto.

No modifica el modelo ni la evidencia. Solo valida estructura, estados y trazabilidad.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


REQUIRED_FILES = [
    "00_manifest.json",
    "01_git_state.txt",
    "02_environment.txt",
    "03_model_inventory.csv",
    "04_code_findings.csv",
    "05_business_rule_matrix.csv",
    "06_live_queries.md",
    "07_live_results.csv",
    "08_regression_cases_results.csv",
    "09_inc_status.csv",
    "10_visual_bindings.csv",
    "11_data_quality.csv",
    "12_recommendations.csv",
    "READY_FOR_CHATGPT.md",
    "RESULTADO.md",
]

CSV_REQUIRED_COLUMNS = {
    "03_model_inventory.csv": {
        "LAYER", "OBJECT_TYPE", "OBJECT_NAME", "FILE_PATH", "STATUS", "DETAIL"
    },
    "04_code_findings.csv": {
        "FINDING_ID", "SEVERITY", "STATUS", "LAYER", "OBJECT_TYPE", "OBJECT_NAME",
        "FILE_PATH", "LINE_START", "LINE_END", "RULE", "EXPECTED", "ACTUAL",
        "EVIDENCE_FILE", "CONFIDENCE", "REQUIRES_BUSINESS_DECISION",
        "RECOMMENDED_CHANGE", "NOTES"
    },
    "05_business_rule_matrix.csv": {
        "RULE_ID", "RULE", "EXPECTED_CURRENT_RULE", "CODE_IMPLEMENTATION",
        "DATA_RESULT", "STATUS", "EVIDENCE", "NOTES"
    },
    "07_live_results.csv": {
        "TEST_ID", "CATEGORY", "METRIC", "DIMENSION", "SELECTION", "VALUE",
        "EXPECTED", "STATUS", "EVIDENCE", "NOTES"
    },
    "08_regression_cases_results.csv": {
        "PEDIDO", "CASO", "HISTORICAL_EXPECTED", "CURRENT_ACTUAL", "STATUS",
        "EVIDENCE", "NOTES"
    },
    "09_inc_status.csv": {
        "INC_ID", "PREVIOUS_STATUS", "CURRENT_STATUS", "SEVERITY", "IMPACT_CURRENT",
        "EVIDENCE", "REQUIRES_BUSINESS_DECISION", "RECOMMENDATION"
    },
    "10_visual_bindings.csv": {
        "PAGE", "VISUAL", "OBJECT_PATH", "MEASURES_FIELDS", "FILTERS", "SORT",
        "SLICER_INTERACTION", "STATUS", "EVIDENCE", "NOTES"
    },
    "11_data_quality.csv": {
        "CHECK_ID", "CATEGORY", "OBJECT", "METRIC", "VALUE", "EXPECTED", "STATUS",
        "EVIDENCE", "NOTES"
    },
    "12_recommendations.csv": {
        "PRIORITY", "FINDING_ID", "TARGET_FILE", "TARGET_OBJECT", "RECOMMENDED_CHANGE",
        "WHY", "EXPECTED_IMPACT", "VALIDATION_REQUIRED", "BUSINESS_DECISION_REQUIRED"
    },
}

REQUIRED_INC_IDS = {
    "INC-005", "INC-006", "INC-007A", "INC-007B", "INC-008", "INC-009",
    "INC-010", "INC-011", "INC-012", "INC-013", "INC-014", "INC-015"
}

BAD_PLACEHOLDERS = (
    "PENDIENTE\n",
    "PENDIENTE\r\n",
    "Estado: EN_PROCESO",
    "status\": \"RUNNING\"",
)

ALLOWED_FINDING_STATUS = {
    "CONFIRMADO", "FALSO_POSITIVO", "NECESITA_DATOS", "DECISION_NEGOCIO", "NO_EJECUTADO"
}
ALLOWED_SEVERITY = {"RED", "ORANGE", "YELLOW", "INFO"}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = list(reader)
    return headers, rows


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    if len(sys.argv) != 2:
        print("USO: python Scripts/audit_local/validate_local_evidence.py <RUN_DIR>")
        return 2

    run_dir = Path(sys.argv[1]).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not run_dir.is_dir():
        print(f"VALIDACION_EVIDENCIA=ERROR\nRUN_DIR_NO_EXISTE={run_dir}")
        return 1

    for name in REQUIRED_FILES:
        p = run_dir / name
        if not p.exists():
            fail(errors, f"FALTA_ARCHIVO:{name}")
        elif p.stat().st_size == 0:
            fail(errors, f"ARCHIVO_VACIO:{name}")

    if errors:
        print("VALIDACION_EVIDENCIA=ERROR")
        for e in errors:
            print(e)
        return 1

    manifest_path = run_dir / "00_manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except Exception as exc:  # noqa: BLE001
        fail(errors, f"MANIFEST_JSON_INVALIDO:{exc}")
        manifest = {}

    for key in ("run_id", "branch", "local_sha", "audit_mode", "status", "validation_status"):
        if not manifest.get(key):
            fail(errors, f"MANIFEST_CAMPO_FALTANTE:{key}")

    if manifest.get("audit_mode") != "READ_ONLY_FUNCTIONAL_EVIDENCE_WRITER":
        fail(errors, f"AUDIT_MODE_INVALIDO:{manifest.get('audit_mode')}")

    if manifest.get("status") not in {"COMPLETED", "READY_FOR_CHATGPT"}:
        fail(errors, f"MANIFEST_STATUS_NO_FINAL:{manifest.get('status')}")

    if manifest.get("validation_status") not in {"READY", "OK", "PENDING_VALIDATOR"}:
        fail(errors, f"MANIFEST_VALIDATION_STATUS_INVALIDO:{manifest.get('validation_status')}")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for name, required_cols in CSV_REQUIRED_COLUMNS.items():
        path = run_dir / name
        try:
            headers, rows = read_csv(path)
        except Exception as exc:  # noqa: BLE001
            fail(errors, f"CSV_INVALIDO:{name}:{exc}")
            continue

        missing = sorted(required_cols - set(headers))
        if missing:
            fail(errors, f"CSV_COLUMNAS_FALTANTES:{name}:{'|'.join(missing)}")
        if not rows:
            fail(errors, f"CSV_SIN_FILAS_EXPLICITAS:{name}")
        csv_rows[name] = rows

    findings = csv_rows.get("04_code_findings.csv", [])
    seen_ids: set[str] = set()
    for idx, row in enumerate(findings, start=2):
        fid = (row.get("FINDING_ID") or "").strip()
        if not fid:
            fail(errors, f"FINDING_SIN_ID:fila={idx}")
        elif fid in seen_ids:
            fail(errors, f"FINDING_ID_DUPLICADO:{fid}")
        else:
            seen_ids.add(fid)

        severity = (row.get("SEVERITY") or "").strip().upper()
        status = (row.get("STATUS") or "").strip().upper()
        if severity not in ALLOWED_SEVERITY:
            fail(errors, f"FINDING_SEVERITY_INVALIDA:{fid}:{severity}")
        if status not in ALLOWED_FINDING_STATUS:
            fail(errors, f"FINDING_STATUS_INVALIDO:{fid}:{status}")

        if severity in {"RED", "ORANGE", "YELLOW"} and status == "CONFIRMADO":
            if not (row.get("EVIDENCE_FILE") or "").strip():
                fail(errors, f"FINDING_CONFIRMADO_SIN_EVIDENCIA:{fid}")
            if not (row.get("RECOMMENDED_CHANGE") or "").strip():
                fail(errors, f"FINDING_CONFIRMADO_SIN_RECOMENDACION:{fid}")

    inc_rows = csv_rows.get("09_inc_status.csv", [])
    inc_ids = {(r.get("INC_ID") or "").strip() for r in inc_rows}
    missing_incs = sorted(REQUIRED_INC_IDS - inc_ids)
    if missing_incs:
        fail(errors, f"INCS_NO_REVALIDADOS:{'|'.join(missing_incs)}")

    ready_text = (run_dir / "READY_FOR_CHATGPT.md").read_text(encoding="utf-8-sig")
    result_text = (run_dir / "RESULTADO.md").read_text(encoding="utf-8-sig")
    combined = ready_text + "\n" + result_text

    for placeholder in BAD_PLACEHOLDERS:
        if placeholder in combined:
            fail(errors, f"PLACEHOLDER_NO_RESUELTO:{placeholder.strip()}")

    required_ready_sections = [
        "## Resumen",
        "## Hallazgos RED confirmados",
        "## Hallazgos ORANGE confirmados",
        "## Falsos positivos relevantes",
        "## Decisiones de negocio necesarias",
        "## Cambios recomendados para implementación remota",
        "## Evidencia principal",
        "## No resuelto",
    ]
    for section in required_ready_sections:
        if section not in ready_text:
            fail(errors, f"READY_SECCION_FALTANTE:{section}")

    live_rows = csv_rows.get("07_live_results.csv", [])
    if live_rows and all((r.get("STATUS") or "").strip().upper() == "NO_EJECUTADO" for r in live_rows):
        warnings.append("PRUEBAS_VIVAS_NO_EJECUTADAS")

    regression_rows = csv_rows.get("08_regression_cases_results.csv", [])
    if regression_rows and all((r.get("STATUS") or "").strip().upper() == "NO_EJECUTADO" for r in regression_rows):
        warnings.append("REGRESION_NO_EJECUTADA")

    if errors:
        print("VALIDACION_EVIDENCIA=ERROR")
        for e in errors:
            print(e)
        for w in warnings:
            print(f"WARNING:{w}")
        return 1

    print("VALIDACION_EVIDENCIA=OK")
    print(f"RUN_DIR={run_dir}")
    print(f"RUN_ID={manifest.get('run_id')}")
    print(f"AUDITED_SHA={manifest.get('local_sha')}")
    print(f"FINDINGS={len(findings)}")
    print(f"INCS_REVALIDATED={len(inc_ids & REQUIRED_INC_IDS)}/{len(REQUIRED_INC_IDS)}")
    for w in warnings:
        print(f"WARNING:{w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
