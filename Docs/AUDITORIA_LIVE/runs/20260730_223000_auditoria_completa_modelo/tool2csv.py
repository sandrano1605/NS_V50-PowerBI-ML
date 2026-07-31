# -*- coding: utf-8 -*-
"""
Convierte output de DAX query (formato: header [col],[col]... luego filas csv)
guardado por el MCP en tool-output a CSV limpio.
"""
import csv, io, os, sys, json, re

def tool_output_to_csv(src_path, dst_path):
    with io.open(src_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    # Quitar envoltura JSON si existe
    if content.lstrip().startswith("{"):
        try:
            data = json.loads(content)
            content = data.get("data", content)
        except Exception:
            pass
    lines = content.splitlines()
    # encontrar header: primera linea que empiece con [ y contenga ,
    header_idx = None
    for i, ln in enumerate(lines):
        if ln.startswith("[") and "," in ln:
            header_idx = i
            break
    if header_idx is None:
        # fallback: primera linea
        header_idx = 0
    header = [h.strip().strip("[]").strip('"') for h in lines[header_idx].split(",")]
    rows = []
    for ln in lines[header_idx + 1:]:
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith("{") and ln.endswith("}"):
            continue
        # dividir respetando comillas simples para campos con comas
        parts = []
        cur = ""
        in_q = False
        for ch in ln:
            if ch == '"':
                in_q = not in_q
                cur += ch
            elif ch == "," and not in_q:
                parts.append(cur)
                cur = ""
            else:
                cur += ch
        parts.append(cur)
        if len(parts) == len(header):
            rows.append(parts)
    with io.open(dst_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return len(rows)

if __name__ == "__main__":
    src = sys.argv[1]
    dst = sys.argv[2]
    n = tool_output_to_csv(src, dst)
    print(f"OK {os.path.basename(dst)}: {n} filas")
