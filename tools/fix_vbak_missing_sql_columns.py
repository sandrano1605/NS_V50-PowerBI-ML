#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "master": ROOT / "NS.SemanticModel/definition/tables/Fact_Pedidos_Auditoria.tmdl",
    "inline": ROOT / "PowerQuery/VBAK_APPEND/06_MASTER_APPEND_INLINE_ACTIVE.pq",
    "atributos": ROOT / "PowerQuery/VBAK_APPEND/02_VBAK_ATRIBUTOS_MAYORISTA.pq",
    "preflight": ROOT / "PowerQuery/VBAK_APPEND/00_VBAK_SCHEMA_PREFLIGHT.pq",
}
EVIDENCE = ROOT / "Docs/AUDITORIA_LIVE/latest/vbak_sql_columns_fix.json"

INLINE_REPLACEMENTS = {
    "\"    NULLIF(LTRIM(RTRIM(CONVERT(VARCHAR(20), V.VSBED))), '') AS PED_CONDICION_EXPEDICION_CODIGO,\"":
        "\"    CAST(NULL AS VARCHAR(20)) AS PED_CONDICION_EXPEDICION_CODIGO,\"",
    "\"    NULLIF(LTRIM(RTRIM(CONVERT(VARCHAR(20), V.CMGST))), '') AS PED_ESTADO_CREDITO,\"":
        "\"    CAST(NULL AS VARCHAR(20)) AS PED_ESTADO_CREDITO,\"",
    "\"    NULLIF(LTRIM(RTRIM(CONVERT(VARCHAR(200), K.ORT01))), '') AS PED_CIUDAD,\"":
        "\"    CAST(NULL AS VARCHAR(200)) AS PED_CIUDAD,\"",
}

REPLACEMENTS = {
    "master": INLINE_REPLACEMENTS,
    "inline": INLINE_REPLACEMENTS,
    "atributos": {
        "        NULLIF(LTRIM(RTRIM(CONVERT(VARCHAR(10), V.VSBED))), '') AS PED_CONDICION_EXPEDICION_CODIGO,":
            "        CAST(NULL AS VARCHAR(10)) AS PED_CONDICION_EXPEDICION_CODIGO,",
        "        NULLIF(LTRIM(RTRIM(CONVERT(VARCHAR(10), V.CMGST))), '') AS PED_ESTADO_CREDITO,":
            "        CAST(NULL AS VARCHAR(10)) AS PED_ESTADO_CREDITO,",
        "        NULLIF(LTRIM(RTRIM(CONVERT(VARCHAR(100), K.ORT01))), '') AS PED_CIUDAD,":
            "        CAST(NULL AS VARCHAR(100)) AS PED_CIUDAD,",
    },
}

PREFLIGHT_REMOVE = [
    "    SELECT 'VBAK_SAP', 'VSBED' UNION ALL\n",
    "    SELECT 'VBAK_SAP', 'CMGST' UNION ALL\n",
    "    SELECT 'KNA1_SAP', 'ORT01' UNION ALL\n",
]

FORBIDDEN = ("V.VSBED", "V.CMGST", "K.ORT01")


def main() -> int:
    changes: dict[str, int] = {}
    errors: list[str] = []

    for key, path in FILES.items():
        text = path.read_text(encoding="utf-8-sig")
        original = text
        count = 0

        for old, new in REPLACEMENTS.get(key, {}).items():
            occurrences = text.count(old)
            if occurrences != 1:
                errors.append(f"{key}: reemplazo esperado 1 vez, actual {occurrences}: {old[:80]}")
            else:
                text = text.replace(old, new, 1)
                count += 1

        if key == "preflight":
            for line in PREFLIGHT_REMOVE:
                occurrences = text.count(line)
                if occurrences != 1:
                    errors.append(f"preflight: línea esperada 1 vez, actual {occurrences}: {line.strip()}")
                else:
                    text = text.replace(line, "", 1)
                    count += 1

        if text != original:
            path.write_text(text, encoding="utf-8", newline="\n")
        changes[key] = count

    for key, path in FILES.items():
        text = path.read_text(encoding="utf-8-sig")
        for token in FORBIDDEN:
            if token in text:
                errors.append(f"{key}: referencia prohibida persistente {token}")

    master = FILES["master"].read_text(encoding="utf-8-sig")
    required_outputs = (
        "CAST(NULL AS VARCHAR(20)) AS PED_CONDICION_EXPEDICION_CODIGO",
        "CAST(NULL AS VARCHAR(20)) AS PED_ESTADO_CREDITO",
        "CAST(NULL AS VARCHAR(200)) AS PED_CIUDAD",
        "NULLIF(LTRIM(RTRIM(CONVERT(VARCHAR(30), K.REGIO))), '') AS PED_REGION",
    )
    for token in required_outputs:
        if token not in master:
            errors.append(f"master: salida requerida ausente {token}")

    result = {
        "status": "VERDE" if not errors else "ROJO",
        "changes": changes,
        "schema_preserved_with_typed_nulls": True,
        "removed_invalid_columns": ["VBAK_SAP.VSBED", "VBAK_SAP.CMGST", "KNA1_SAP.ORT01"],
        "preserved_existing_columns": ["VBAK_SAP.LIFSK", "KNA1_SAP.REGIO"],
        "errors": errors,
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
