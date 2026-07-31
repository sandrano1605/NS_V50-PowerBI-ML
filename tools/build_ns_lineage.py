from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "NS.SemanticModel" / "definition"
REPORT = ROOT / "NS.Report" / "definition"
DOCS = ROOT / "Docs" / "AUDITORIA_LIVE" / "latest" / "lineage"

TABLE_HEADER = re.compile(r"^table\s+(?:'([^']+)'|(.+?))\s*$", re.MULTILINE)
COLUMN_DEF = re.compile(r"^\s*column\s+(?:'([^']+)'|([^\s]+))\s*$", re.MULTILINE)
MEASURE_DEF = re.compile(r"^\s*measure\s+(?:'([^']+)'|(.+?))\s*=", re.MULTILINE)
PARTITION_DEF = re.compile(r"^\s*partition\s+(?:'([^']+)'|(.+?))\s*=", re.MULTILINE)
DAX_COLUMN = re.compile(r"(?:'([^']+)'|([A-Za-z_][\w ]*))\[([^\]]+)\]")
PY_COL = re.compile(r"(?:\b(?:df|dataset|source|data|frame)\s*\[\s*|\.loc\s*\[[^\]]*,\s*)[\"']([^\"']+)[\"']")
M_BRACKET_COL = re.compile(r"(?<![A-Za-z0-9_])\[([A-Za-z_][A-Za-z0-9_ ]+)\]")
QUOTED_NAME = re.compile(r"[\"']([A-Za-z_][A-Za-z0-9_ ]+)[\"']")

KEYWORDS_TO_IGNORE = {
    "true", "false", "null", "each", "let", "in", "type", "table", "list",
    "record", "text", "number", "date", "datetime", "datetimezone", "duration",
}


@dataclass
class SymbolTable:
    columns: set[str] = field(default_factory=set)
    measures: set[str] = field(default_factory=set)
    path: str = ""
    text: str = ""


@dataclass(frozen=True)
class Edge:
    source_type: str
    source_object: str
    target_type: str
    target_object: str
    dependency_kind: str
    file: str
    evidence: str


def clean_name(value: str | None) -> str:
    return (value or "").strip().strip("'")


def iter_json(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_json(child)


def load_symbols() -> dict[str, SymbolTable]:
    symbols: dict[str, SymbolTable] = {}
    for path in sorted((MODEL / "tables").glob("*.tmdl")):
        text = path.read_text(encoding="utf-8-sig")
        match = TABLE_HEADER.search(text)
        if not match:
            continue
        table = clean_name(match.group(1) or match.group(2))
        symbols[table] = SymbolTable(
            columns={clean_name(a or b) for a, b in COLUMN_DEF.findall(text)},
            measures={clean_name(a or b) for a, b in MEASURE_DEF.findall(text)},
            path=str(path.relative_to(ROOT)),
            text=text,
        )
    return symbols


def add_edge(edges: set[Edge], **kwargs: str) -> None:
    edges.add(Edge(**kwargs))


def table_mentions(text: str, symbols: dict[str, SymbolTable]) -> set[str]:
    found: set[str] = set()
    for table in symbols:
        if re.search(rf"(?<![A-Za-z0-9_])(?:'{re.escape(table)}'|{re.escape(table)})(?![A-Za-z0-9_])", text):
            found.add(table)
    return found


def extract_model_edges(symbols: dict[str, SymbolTable]) -> tuple[set[Edge], dict[str, set[str]], set[str]]:
    edges: set[Edge] = set()
    table_graph: dict[str, set[str]] = defaultdict(set)
    dynamic_blockers: set[str] = set()

    all_columns: dict[str, set[str]] = {table: data.columns for table, data in symbols.items()}

    for target_table, data in symbols.items():
        text = data.text
        file = data.path
        mentions = table_mentions(text, symbols) - {target_table}
        for source_table in mentions:
            table_graph[source_table].add(target_table)
            add_edge(
                edges,
                source_type="TABLE",
                source_object=source_table,
                target_type="TABLE",
                target_object=target_table,
                dependency_kind="TABLE_REFERENCE",
                file=file,
                evidence=f"{source_table} mencionado en definición de {target_table}",
            )

        for table_a, table_b, column in DAX_COLUMN.findall(text):
            table = clean_name(table_a or table_b)
            if table in symbols and column in all_columns[table]:
                add_edge(
                    edges,
                    source_type="COLUMN",
                    source_object=f"{table}[{column}]",
                    target_type="TABLE_OR_MEASURE_FILE",
                    target_object=target_table,
                    dependency_kind="DAX_OR_M_EXPLICIT",
                    file=file,
                    evidence=f"{table}[{column}]",
                )

        # Conservative M/Python detection: only column names belonging to a table explicitly
        # mentioned in the same file are attributed to that table.
        quoted = {name for name in QUOTED_NAME.findall(text) if name.lower() not in KEYWORDS_TO_IGNORE}
        brackets = set(M_BRACKET_COL.findall(text))
        python_cols = set(PY_COL.findall(text))
        candidate_names = quoted | brackets | python_cols
        for source_table in mentions:
            for column in sorted(candidate_names & all_columns[source_table]):
                kinds: list[str] = []
                if column in python_cols:
                    kinds.append("PYTHON_LITERAL")
                if column in brackets:
                    kinds.append("M_BRACKET")
                if column in quoted:
                    kinds.append("M_OR_PYTHON_STRING")
                add_edge(
                    edges,
                    source_type="COLUMN",
                    source_object=f"{source_table}[{column}]",
                    target_type="TABLE",
                    target_object=target_table,
                    dependency_kind="+".join(kinds) or "TEXT_REFERENCE",
                    file=file,
                    evidence=column,
                )

        lowered = text.lower()
        if "python.execute" in lowered:
            for source_table in mentions:
                dynamic_blockers.add(source_table)
                add_edge(
                    edges,
                    source_type="TABLE",
                    source_object=source_table,
                    target_type="DYNAMIC_CONSUMER",
                    target_object=f"Python.Execute en {target_table}",
                    dependency_kind="FULL_TABLE_OR_DYNAMIC_SCHEMA",
                    file=file,
                    evidence="Python.Execute detectado; requiere prueba de contrato de columnas",
                )
        if "table.schema" in lowered:
            for source_table in mentions:
                dynamic_blockers.add(source_table)
                add_edge(
                    edges,
                    source_type="TABLE",
                    source_object=source_table,
                    target_type="DYNAMIC_CONSUMER",
                    target_object=f"Table.Schema en {target_table}",
                    dependency_kind="SCHEMA_INTROSPECTION",
                    file=file,
                    evidence="Table.Schema consume el esquema completo",
                )
        if re.search(r"table\.columnnames|record\.field|record\.fieldordefault", lowered):
            for source_table in mentions:
                dynamic_blockers.add(source_table)

    return edges, table_graph, dynamic_blockers


def extract_relationship_edges(symbols: dict[str, SymbolTable]) -> set[Edge]:
    edges: set[Edge] = set()
    for path in sorted(MODEL.rglob("*.tmdl")):
        if path.parent.name == "tables":
            continue
        text = path.read_text(encoding="utf-8-sig")
        file = str(path.relative_to(ROOT))
        for table_a, table_b, column in DAX_COLUMN.findall(text):
            table = clean_name(table_a or table_b)
            if table in symbols and column in symbols[table].columns:
                add_edge(
                    edges,
                    source_type="COLUMN",
                    source_object=f"{table}[{column}]",
                    target_type="MODEL_METADATA",
                    target_object=path.stem,
                    dependency_kind="RELATIONSHIP_OR_METADATA",
                    file=file,
                    evidence=f"{table}[{column}]",
                )
    return edges


def extract_report_edges(symbols: dict[str, SymbolTable]) -> set[Edge]:
    edges: set[Edge] = set()
    for path in sorted(REPORT.rglob("*.json")):
        try:
            obj = json.loads(path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError:
            add_edge(
                edges,
                source_type="FILE",
                source_object=str(path.relative_to(ROOT)),
                target_type="ERROR",
                target_object="INVALID_JSON",
                dependency_kind="PARSE_ERROR",
                file=str(path.relative_to(ROOT)),
                evidence="JSON inválido",
            )
            continue
        visual_name = obj.get("name", path.parent.name) if isinstance(obj, dict) else path.parent.name
        file = str(path.relative_to(ROOT))
        for node in iter_json(obj):
            for kind in ("Column", "Measure"):
                ref = node.get(kind)
                if not isinstance(ref, dict):
                    continue
                expression = ref.get("Expression", {})
                source = expression.get("SourceRef", {}) if isinstance(expression, dict) else {}
                table = source.get("Entity") if isinstance(source, dict) else None
                prop = ref.get("Property")
                if not isinstance(table, str) or not isinstance(prop, str) or table not in symbols:
                    continue
                valid = prop in (symbols[table].columns if kind == "Column" else symbols[table].measures)
                add_edge(
                    edges,
                    source_type=kind.upper(),
                    source_object=f"{table}[{prop}]",
                    target_type="VISUAL",
                    target_object=str(visual_name),
                    dependency_kind="REPORT_PROJECTION" if valid else "BROKEN_REPORT_REFERENCE",
                    file=file,
                    evidence=f"{kind}: {table}[{prop}]",
                )
    return edges


def extract_culture_usage(symbols: dict[str, SymbolTable]) -> set[Edge]:
    edges: set[Edge] = set()
    for path in sorted(MODEL.rglob("cultures/*.tmdl")):
        text = path.read_text(encoding="utf-8-sig")
        file = str(path.relative_to(ROOT))
        for table, data in symbols.items():
            for column in data.columns:
                if column in text:
                    add_edge(
                        edges,
                        source_type="COLUMN",
                        source_object=f"{table}[{column}]",
                        target_type="CULTURE",
                        target_object=path.stem,
                        dependency_kind="TRANSLATION_ONLY",
                        file=file,
                        evidence=column,
                    )
    return edges


def downstream_tables(source: str, graph: dict[str, set[str]]) -> set[str]:
    visited: set[str] = set()
    queue: deque[str] = deque(graph.get(source, set()))
    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        queue.extend(graph.get(node, set()))
    return visited


def classify_fpa_columns(
    symbols: dict[str, SymbolTable],
    edges: set[Edge],
    table_graph: dict[str, set[str]],
    dynamic_blockers: set[str],
) -> list[dict[str, str]]:
    source_table = "Fact_Pedidos_Auditoria"
    if source_table not in symbols:
        raise RuntimeError(f"No existe {source_table}")

    by_source: dict[str, list[Edge]] = defaultdict(list)
    for edge in edges:
        by_source[edge.source_object].append(edge)

    downstream = sorted(downstream_tables(source_table, table_graph))
    rows: list[dict[str, str]] = []
    for column in sorted(symbols[source_table].columns):
        key = f"{source_table}[{column}]"
        refs = by_source.get(key, [])
        operational = [e for e in refs if e.dependency_kind != "TRANSLATION_ONLY"]
        translations = [e for e in refs if e.dependency_kind == "TRANSLATION_ONLY"]
        critical_key = any(
            token in column.upper()
            for token in ("PED_NUMERO_PEDIDO", "FECHA_MANIFIESTO", "FECHA_TRANSPORTE", "TRP_")
        )

        if operational:
            status = "CONSERVAR_REFERENCIADA"
            confidence = "ALTA"
            blocker = ""
        elif source_table in dynamic_blockers:
            status = "NO_BORRAR_SIN_PRUEBA_CONTRATO"
            confidence = "BAJA"
            blocker = "Consumidor dinámico detectado (Python.Execute/Table.Schema)"
        elif critical_key:
            status = "CONSERVAR_CLAVE_O_CIERRE"
            confidence = "ALTA"
            blocker = "Clave o fecha operacional crítica"
        else:
            status = "CANDIDATA_A_RECORTAR"
            confidence = "MEDIA"
            blocker = "Requiere prueba SQL/M/Python y refresh A/B"

        rows.append(
            {
                "source_table": source_table,
                "column": column,
                "status": status,
                "confidence": confidence,
                "direct_reference_count": str(len(operational)),
                "translation_reference_count": str(len(translations)),
                "direct_consumers": " | ".join(sorted({e.target_object for e in operational})),
                "dependency_kinds": " | ".join(sorted({e.dependency_kind for e in operational})),
                "downstream_tables": " | ".join(downstream),
                "blocker_or_next_test": blocker,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        if fields:
            writer.writeheader()
            writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Construye trazabilidad conservadora del modelo NS")
    parser.add_argument("--strict", action="store_true", help="Falla si encuentra JSON o referencias rotas")
    args = parser.parse_args()

    symbols = load_symbols()
    model_edges, graph, dynamic_blockers = extract_model_edges(symbols)
    edges = model_edges | extract_relationship_edges(symbols) | extract_report_edges(symbols) | extract_culture_usage(symbols)

    edge_rows = [
        {
            "source_type": e.source_type,
            "source_object": e.source_object,
            "target_type": e.target_type,
            "target_object": e.target_object,
            "dependency_kind": e.dependency_kind,
            "file": e.file,
            "evidence": e.evidence,
        }
        for e in sorted(edges, key=lambda x: (x.source_object, x.target_object, x.file, x.dependency_kind))
    ]
    fpa_rows = classify_fpa_columns(symbols, edges, graph, dynamic_blockers)

    broken = [e for e in edges if e.dependency_kind in {"PARSE_ERROR", "BROKEN_REPORT_REFERENCE"}]
    summary = {
        "status": "ROJO" if broken else "AMARILLO",
        "tables": len(symbols),
        "edges": len(edges),
        "broken_references_or_json": len(broken),
        "dynamic_blocker_tables": sorted(dynamic_blockers),
        "fact_pedidos_auditoria_columns": len(fpa_rows),
        "fpa_keep_or_blocked": sum(1 for r in fpa_rows if r["status"] != "CANDIDATA_A_RECORTAR"),
        "fpa_candidates": sum(1 for r in fpa_rows if r["status"] == "CANDIDATA_A_RECORTAR"),
        "important": [
            "CANDIDATA_A_RECORTAR no significa autorizada para borrar.",
            "Python.Execute y Table.Schema obligan a una prueba de contrato antes/después.",
            "Las métricas dinámicas deben compararse dentro del mismo refresh y ventana temporal.",
        ],
    }

    DOCS.mkdir(parents=True, exist_ok=True)
    write_csv(DOCS / "lineage_edges.csv", edge_rows)
    write_csv(DOCS / "fact_pedidos_auditoria_columns.csv", fpa_rows)
    (DOCS / "lineage_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.strict and broken:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
