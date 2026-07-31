# -*- coding: utf-8 -*-
"""
Auditoria NS - Parsing TMDL del modelo v15 en vivo.
Genera:
  00_inventario_modelo.csv
  01_relaciones_modelo.csv
  02_medidas_sla.csv  (detecta SLA fijo 5 / referencias antiguas)
  14_consultas_powerquery.csv
"""
import csv, io, os, re, sys

TMDL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmdl_modelo_v15.txt")
OUT = os.path.dirname(os.path.abspath(__file__))

def read_tmdl():
    with io.open(TMDL_PATH, "r", encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()

def indent(line):
    return len(line) - len(line.lstrip("\t"))

def parse():
    lines = read_tmdl()
    tables = []          # {name, level items}
    rels = []            # lista de dicts
    cultures = []
    current_table = None
    current_column = None
    current_measure = None
    current_partition = None
    current_rel = None
    in_expr = False
    expr_stack = []
    expr_lines = []

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            if current_rel is not None:
                rels.append(current_rel)
                current_rel = None
            continue
        lvl = indent(line)
        text = line.strip()
        m_table = re.match(r"^table (.+)$", text)
        m_rel = re.match(r"^relationship (.+)$", text)
        m_col = re.match(r"^column (.+)$", text)
        m_meas = re.match(r"^measure (.+)$", text)
        m_part = re.match(r"^partition (.+) = m$", text)
        m_cult = re.match(r"^culture (.+)$", text)

        if in_expr:
            # expression body: lines with indent >= expr_base
            if lvl >= expr_base:
                expr_lines.append(text)
                continue
            else:
                if current_measure is not None:
                    current_measure["expression"] = "\n".join(expr_lines)
                in_expr = False
                expr_lines = []

        if m_table:
            current_table = {"name": m_table.group(1), "columns": [], "measures": [], "partitions": [], "annotations": {}}
            tables.append(current_table)
            current_column = None
            current_measure = None
            current_partition = None
        elif m_rel:
            current_rel = {"name": m_rel.group(1)}
        elif m_cult:
            cultures.append(text)
        elif m_col and current_table is not None:
            col = {"name": m_col.group(1), "props": {}}
            current_table["columns"].append(col)
            current_column = col
            current_measure = None
        elif m_meas and current_table is not None:
            meas = {"name": m_meas.group(1), "props": {}, "expression": ""}
            current_table["measures"].append(meas)
            current_measure = meas
            current_column = None
        elif m_part and current_table is not None:
            part = {"name": m_part.group(1), "props": {}, "source": ""}
            current_table["partitions"].append(part)
            current_partition = part
            current_column = None
            current_measure = None
        else:
            if current_rel is not None:
                m_prop = re.match(r"^(\w+): (.+)$", text)
                if m_prop:
                    current_rel[m_prop.group(1)] = m_prop.group(2)
                continue
            # property line: key: value
            m_prop = re.match(r"^(\w+): (.*)$", text)
            if m_prop:
                key, value = m_prop.group(1), m_prop.group(2)
                if current_measure is not None:
                    current_measure["props"][key] = value
                elif current_column is not None:
                    current_column["props"][key] = value
                elif current_partition is not None:
                    current_partition["props"][key] = value
                elif current_table is not None:
                    current_table["annotations"][key] = value
                # expression = ... single line
                if key == "expression":
                    if current_measure is not None:
                        current_measure["expression"] = value
            elif text == "expression" and current_measure is not None:
                in_expr = True
                expr_base = lvl + 1
                expr_lines = []
            elif text == "source" and current_partition is not None:
                # multi-line M: capture until dedent
                in_expr = True
                expr_base = lvl + 1
                expr_lines = []
                current_partition["source"] = ""

    # flush
    if in_expr and current_measure is not None:
        current_measure["expression"] = "\n".join(expr_lines)
    if current_rel is not None:
        rels.append(current_rel)

    return tables, rels, cultures

def safe(s):
    return re.sub(r"\s+", " ", s or "").strip()

def build_inventario(tables):
    rows = []
    for t in tables:
        # tabla
        rows.append({
            "TIPO_OBJETO": "TABLA", "TABLA": t["name"], "NOMBRE": t["name"],
            "TIPO_DATO": "", "EXPRESION": "", "FORMATO": "",
            "CARPETA": "", "VISIBLE": "SI",
            "LINEAGE_TAG": t["annotations"].get("lineageTag", ""),
            "DEPENDENCIAS": "", "OBSERVACION": "partition=" + str(len(t["partitions"]))
        })
        for c in t["columns"]:
            p = c["props"]
            rows.append({
                "TIPO_OBJETO": "COLUMNA", "TABLA": t["name"], "NOMBRE": c["name"],
                "TIPO_DATO": p.get("dataType", ""),
                "EXPRESION": p.get("expression", ""),
                "FORMATO": p.get("formatString", ""),
                "CARPETA": p.get("displayFolder", ""),
                "VISIBLE": "NO" if p.get("isHidden") == "true" else "SI",
                "LINEAGE_TAG": p.get("lineageTag", ""),
                "DEPENDENCIAS": "",
                "OBSERVACION": ("sourceColumn=" + p.get("sourceColumn", "")) if "sourceColumn" in p else "calculada"
            })
        for m in t["measures"]:
            p = m["props"]
            rows.append({
                "TIPO_OBJETO": "MEDIDA", "TABLA": t["name"], "NOMBRE": m["name"],
                "TIPO_DATO": p.get("dataType", ""),
                "EXPRESION": safe(m["expression"]),
                "FORMATO": p.get("formatString", ""),
                "CARPETA": p.get("displayFolder", ""),
                "VISIBLE": "NO" if p.get("isHidden") == "true" else "SI",
                "LINEAGE_TAG": p.get("lineageTag", ""),
                "DEPENDENCIAS": "",
                "OBSERVACION": ""
            })
        for ptn in t["partitions"]:
            rows.append({
                "TIPO_OBJETO": "PARTICION", "TABLA": t["name"], "NOMBRE": ptn["name"],
                "TIPO_DATO": "", "EXPRESION": "", "FORMATO": "",
                "CARPETA": "", "VISIBLE": "SI",
                "LINEAGE_TAG": "", "DEPENDENCIAS": "",
                "OBSERVACION": "mode=" + ptn["props"].get("mode", "") + "; fuente=M"
            })
    return rows

def build_relaciones(rels):
    rows = []
    for r in rels:
        fc = r.get("fromColumn", "").split(".", 1)
        tc = r.get("toColumn", "").split(".", 1)
        rows.append({
            "RELACION": r.get("name", ""),
            "TABLA_ORIGEN": fc[0] if len(fc) == 2 else "",
            "COLUMNA_ORIGEN": fc[1] if len(fc) == 2 else r.get("fromColumn", ""),
            "CARDINALIDAD_ORIGEN": r.get("fromCardinality", ""),
            "TABLA_DESTINO": tc[0] if len(tc) == 2 else "",
            "COLUMNA_DESTINO": tc[1] if len(tc) == 2 else r.get("toColumn", ""),
            "CARDINALIDAD_DESTINO": r.get("toCardinality", ""),
            "DIRECCION_FILTRO": r.get("crossFilteringBehavior", ""),
            "ACTIVA": "SI" if r.get("isActive", "true") == "true" else "NO",
            "SEGURIDAD": r.get("securityFilteringBehavior", ""),
            "AMBIGUA": "", "RIESGO": "", "OBSERVACION": ""
        })
    return rows

def build_medidas_sla(tables):
    rows = []
    for t in tables:
        for m in t["measures"]:
            exp = m["expression"]
            dep = re.findall(r"\[([A-Za-zÁÉÍÓÚÑáéíóúñ0-9_ \-\.\+\%]+)\]", exp)
            dep = [d for d in dep if d != m["name"]]
            usa_5 = bool(re.search(r"(>|>=|=|<|<=|==)\s*5\b|SLA\w*\s*=\s*5|5\s*DH|Santiago.*5|5.*Santiago", exp, re.I))
            usa_zonal = bool(re.search(r"ZONA|Santiago|Regiones|SLA_INTERNO_DH|SLA_OPERACION_DH", exp))
            usa_tracking = bool(re.search(r"TRACKING", exp))
            usa_cerrado = bool(re.search(r"ES_CERRADO|CERRADO", exp))
            usa_cierre = bool(re.search(r"FECHA_CIERRE|FECHA_MANIFIESTO|FECHA_DESPACHO", exp))
            obs = []
            if usa_5 and "SLA_INTERNO_DH" not in exp:
                obs.append("POSIBLE SLA FIJO 5")
            rows.append({
                "MEDIDA": m["name"], "TABLA": t["name"], "EXPRESION_DAX": safe(exp),
                "USA_SLA_FIJO_5": "SI" if usa_5 else "NO",
                "USA_SLA_ZONAL": "SI" if usa_zonal else "NO",
                "USA_TRACKING_TRUE": "SI" if usa_tracking else "NO",
                "USA_PEDIDO_CERRADO": "SI" if usa_cerrado else "NO",
                "USA_FECHA_CIERRE_CORRECTA": "SI" if usa_cierre else "NO",
                "DEPENDENCIAS": ";".join(sorted(set(dep)))[:2000],
                "RESULTADO": "REVISAR" if usa_5 else "OK",
                "OBSERVACION": ";".join(obs)
            })
    return rows

def build_powerquery(tables):
    rows = []
    for t in tables:
        for ptn in t["partitions"]:
            src = ptn.get("source", "") or ptn["props"].get("source", "")
            riesgo = []
            if "Python.Execute" in src:
                riesgo.append("USA_PYTHON")
            if "Table.Buffer" in src:
                riesgo.append("TABLE_BUFFER")
            if "List.Accumulate" in src and "Python" in src:
                riesgo.append("LIST_PYTHON")
            rows.append({
                "CONSULTA": t["name"], "TIPO": "PARTICION_M",
                "FUENTE": "SQL" if "Sql.Database" in src else ("PYTHON" if "Python.Execute" in src else "M"),
                "DEPENDENCIAS": "",
                "CARGA_HABILITADA": "SI", "ERROR": "",
                "USA_PYTHON": "SI" if "Python.Execute" in src else "NO",
                "SCRIPT_PYTHON": src[:4000] if "Python.Execute" in src else "",
                "RIESGO": ";".join(riesgo),
                "OBSERVACION": ("len=" + str(len(src)))
            })
    return rows

def write_csv(name, rows, fieldnames):
    path = os.path.join(OUT, name)
    with io.open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"OK {name}: {len(rows)} filas -> {path}")

def main():
    tables, rels, cultures = parse()
    print("Tablas parseadas:", len(tables))
    print("Relaciones:", len(rels))
    print("Culturas:", cultures)

    inv = build_inventario(tables)
    write_csv("00_inventario_modelo.csv", inv, [
        "TIPO_OBJETO","TABLA","NOMBRE","TIPO_DATO","EXPRESION","FORMATO","CARPETA","VISIBLE","LINEAGE_TAG","DEPENDENCIAS","OBSERVACION"])

    rel = build_relaciones(rels)
    write_csv("01_relaciones_modelo.csv", rel, [
        "RELACION","TABLA_ORIGEN","COLUMNA_ORIGEN","CARDINALIDAD_ORIGEN","TABLA_DESTINO","COLUMNA_DESTINO","CARDINALIDAD_DESTINO","DIRECCION_FILTRO","ACTIVA","SEGURIDAD","AMBIGUA","RIESGO","OBSERVACION"])

    med = build_medidas_sla(tables)
    write_csv("02_medidas_sla.csv", med, [
        "MEDIDA","TABLA","EXPRESION_DAX","USA_SLA_FIJO_5","USA_SLA_ZONAL","USA_TRACKING_TRUE","USA_PEDIDO_CERRADO","USA_FECHA_CIERRE_CORRECTA","DEPENDENCIAS","RESULTADO","OBSERVACION"])

    pq = build_powerquery(tables)
    write_csv("14_consultas_powerquery.csv", pq, [
        "CONSULTA","TIPO","FUENTE","DEPENDENCIAS","CARGA_HABILITADA","ERROR","USA_PYTHON","SCRIPT_PYTHON","RIESGO","OBSERVACION"])

    n_revisar = sum(1 for r in med if r["RESULTADO"] == "REVISAR")
    print(f"\nTotal medidas: {len(med)} | Con SLA fijo 5 potencial: {n_revisar}")

if __name__ == "__main__":
    main()
