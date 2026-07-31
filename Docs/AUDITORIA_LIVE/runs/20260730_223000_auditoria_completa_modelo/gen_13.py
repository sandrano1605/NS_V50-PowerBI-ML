# -*- coding: utf-8 -*-
"""
Genera 13_objetos_lienzos.csv con inventario de visuales de las paginas 00 y 01.
"""
import csv, io, os, json, glob

ROOT = r"C:\Users\alonso.moya\OneDrive - ARTEL S.A\Escritorio\💼 Proyectos\Modelo datos power BI\NS\NS_V50_v15_Error_Python_ndarray_Corregido\NS_V50\NS.Report\definition\pages"
OUT = r"C:\Users\ALONSO~1.MOY\AppData\Local\Temp\opencode\AUDITORIA_NS_MODELO_VIVO"

PAGES = {
    "71af1998e2cb472d9799": "00 Resumen Ejecutivo",
    "a1b2c3d4e5f6071829": "01 Analisis Fuera SLA",
    "ed2a2fead6d24153bee1": "01.1 Auditoria por Pedido",
}

def read_json(path):
    try:
        with io.open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}

rows = []
for page_id, page_name in PAGES.items():
    page_dir = os.path.join(ROOT, page_id)
    page_file = os.path.join(page_dir, "page.json")
    page_data = read_json(page_file)
    display = page_data.get("displayName", page_name)
    # filtros de pagina
    page_filters = []
    pf_file = os.path.join(page_dir, "pageFilters.json")
    if os.path.exists(pf_file):
        pf = read_json(pf_file)
        for f in pf.get("filters", []):
            ent = f.get("field", {}).get("Column", {}).get("Expression", {}).get("SourceRef", {}).get("Entity", "")
            prop = f.get("field", {}).get("Column", {}).get("Property", "")
            page_filters.append(f"{ent}.{prop}")
    visuals_dir = os.path.join(page_dir, "visuals")
    if not os.path.isdir(visuals_dir):
        continue
    for vdir in sorted(os.listdir(visuals_dir)):
        vpath = os.path.join(visuals_dir, vdir, "visual.json")
        if not os.path.exists(vpath):
            continue
        v = read_json(vpath)
        if "error" in v:
            rows.append({"PAGINA": display, "ID_VISUAL": vdir, "NOMBRE_VISUAL": vdir,
                         "TIPO_VISUAL": "ERROR", "TITULO": v["error"], "SUBTITULO": "",
                         "TABLAS_USADAS": "", "COLUMNAS_USADAS": "", "MEDIDAS_USADAS": "",
                         "FILTROS_VISUAL": "", "FILTROS_PAGINA": ";".join(page_filters),
                         "FILTROS_REPORTE": "", "ORDENAMIENTO": "", "DRILLTHROUGH": "",
                         "TOOLTIP": "", "VISIBLE": "SI", "X": "", "Y": "", "ANCHO": "", "ALTO": "",
                         "SUPERPOSICION": "", "RESPONDE_PREGUNTA_NEGOCIO": "", "OBSERVACION": "ERROR LECTURA"})
            continue
        vtype = v.get("visual", {}).get("visualType", "")
        pos = v.get("position", {})
        title = ""
        try:
            title = v["visual"]["visualContainerObjects"]["title"][0]["properties"]["text"]["expr"]["Literal"]["Value"].strip("'")
        except Exception:
            pass
        # proyecciones
        proj = v.get("visual", {}).get("query", {}).get("queryState", {}).get("Values", {}).get("projections", [])
        tablas = set(); cols = set(); medidas = set()
        for p in proj:
            f = p.get("field", {})
            if "Measure" in f:
                medidas.add(f["Measure"].get("Property", ""))
                ent = f["Measure"].get("Expression", {}).get("SourceRef", {}).get("Entity", "")
                if ent:
                    tablas.add(ent)
            elif "Column" in f:
                cols.add(f["Column"].get("Property", ""))
                ent = f["Column"].get("Expression", {}).get("SourceRef", {}).get("Entity", "")
                if ent:
                    tablas.add(ent)
        # ordenamiento
        sort = []
        try:
            for s in v["visual"]["query"]["queryState"]["sortDefinition"]["sort"]:
                f = s.get("field", {})
                if "Measure" in f:
                    sort.append(f["Measure"].get("Property", "") + " " + s.get("direction", ""))
                elif "Column" in f:
                    sort.append(f["Column"].get("Property", "") + " " + s.get("direction", ""))
        except Exception:
            pass
        # filtros visual
        vfilters = []
        for f in v.get("filterConfig", {}).get("filters", []):
            field = f.get("field", {})
            if "Measure" in field:
                vfilters.append("M:" + field["Measure"].get("Property", ""))
            elif "Column" in field:
                vfilters.append("C:" + field["Column"].get("Property", ""))
        # tooltip
        tooltip = ""
        try:
            tt = v["visual"]["visualContainerObjects"]["visualTooltip"][0]["properties"]
            if tt.get("show", {}).get("expr", {}).get("Literal", {}).get("Value") == "true":
                tooltip = tt.get("section", {}).get("expr", {}).get("Literal", {}).get("Value", "")
        except Exception:
            pass
        rows.append({
            "PAGINA": display, "ID_VISUAL": vdir, "NOMBRE_VISUAL": vdir, "TIPO_VISUAL": vtype,
            "TITULO": title, "SUBTITULO": "",
            "TABLAS_USADAS": ";".join(sorted(tablas)),
            "COLUMNAS_USADAS": ";".join(sorted(cols))[:1500],
            "MEDIDAS_USADAS": ";".join(sorted(medidas))[:2000],
            "FILTROS_VISUAL": ";".join(vfilters)[:1500],
            "FILTROS_PAGINA": ";".join(page_filters)[:1500],
            "FILTROS_REPORTE": "", "ORDENAMIENTO": ";".join(sort)[:500],
            "DRILLTHROUGH": "", "TOOLTIP": tooltip, "VISIBLE": "SI",
            "X": pos.get("x", ""), "Y": pos.get("y", ""), "ANCHO": pos.get("width", ""), "ALTO": pos.get("height", ""),
            "SUPERPOSICION": "", "RESPONDE_PREGUNTA_NEGOCIO": "", "OBSERVACION": ""
        })

with io.open(os.path.join(OUT, "13_objetos_lienzos.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["PAGINA","ID_VISUAL","NOMBRE_VISUAL","TIPO_VISUAL","TITULO","SUBTITULO",
        "TABLAS_USADAS","COLUMNAS_USADAS","MEDIDAS_USADAS","FILTROS_VISUAL","FILTROS_PAGINA","FILTROS_REPORTE",
        "ORDENAMIENTO","DRILLTHROUGH","TOOLTIP","VISIBLE","X","Y","ANCHO","ALTO","SUPERPOSICION",
        "RESPONDE_PREGUNTA_NEGOCIO","OBSERVACION"])
    w.writeheader()
    for r in rows:
        w.writerow(r)
print(f"OK 13_objetos_lienzos.csv: {len(rows)} filas")
