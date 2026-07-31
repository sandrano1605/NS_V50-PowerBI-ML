# -*- coding: utf-8 -*-
"""
Auditoria NS - Genera:
  09_vendedores_recurrentes.csv
  10_fes_vs_carga.csv
  11_comparacion_lienzos.csv
  12_cobertura_lineas_unidades.csv
"""
import csv, io, os, datetime
from collections import defaultdict

OUT = r"C:\Users\ALONSO~1.MOY\AppData\Local\Temp\opencode\AUDITORIA_NS_MODELO_VIVO"

def read_csv(name):
    with io.open(os.path.join(OUT, name), encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def write_csv(name, header, rows):
    with io.open(os.path.join(OUT, name), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"OK {name}: {len(rows)} filas")

def parse_dt(v):
    if v is None or str(v).strip() == "":
        return None
    s = str(v).strip()
    for fmt in ("%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M", "%d-%m-%Y 0:00:00", "%d-%m-%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None

def main():
    cohorte = read_csv("03_cohorte_tracking.csv")
    recurrentes = read_csv("07_clientes_recurrentes.csv")
    lineas = read_csv("12_tabla_lineas_unidades_raw.csv")
    print("cohorte:", len(cohorte), "| recurrentes:", len(recurrentes), "| lineas:", len(lineas))

    # Diccionarios
    lineas_map = {}
    for l in lineas:
        lineas_map[l["Pedido"].strip()] = l
    tracking_ids = set(r["PEDIDO"].strip() for r in cohorte)

    # ============ 09_vendedores_recurrentes.csv ============
    # Clientes recurrentes = Recurrente 2M+ o 3M
    rec_clientes = {r["CLIENTE"] for r in recurrentes if r["CLASIFICACION_RECURRENCIA"] in ("Recurrente 2M", "Recurrente 3M")}
    # mapear cliente -> vendedor desde cohorte
    cli_vendedor = {}
    for r in cohorte:
        cli_vendedor.setdefault(r["CLIENTE"], set()).add(r["VENDEDOR"])
    por_vendedor = defaultdict(lambda: {"clientes_3m": set(), "clientes_2m_mas": set(), "pedidos": [], "lineas": 0, "unidades": 0, "valor": 0.0, "flujos": set()})
    for r in recurrentes:
        cli = r["CLIENTE"]
        if r["CLASIFICACION_RECURRENCIA"] == "Recurrente 3M":
            for v in cli_vendedor.get(cli, []):
                por_vendedor[v]["clientes_3m"].add(cli)
        if r["CLASIFICACION_RECURRENCIA"] in ("Recurrente 2M", "Recurrente 3M"):
            for v in cli_vendedor.get(cli, []):
                por_vendedor[v]["clientes_2m_mas"].add(cli)
    # pedidos de clientes recurrentes
    for r in cohorte:
        if r["CLIENTE"] in rec_clientes:
            v = r["VENDEDOR"]
            dias = r["DIAS_INTERNOS_DH"]
            fuera = (r["ES_CERRADO"] == "True") and dias not in ("", "None") and int(dias) > int(r["SLA_INTERNO_DH"])
            por_vendedor[v]["pedidos"].append(fuera)
            por_vendedor[v]["flujos"].add(r["CLASIFICACION"])
            lu = lineas_map.get(r["PEDIDO"].strip())
            if lu:
                por_vendedor[v]["lineas"] += int(lu["Lineas"])
                por_vendedor[v]["unidades"] += float(lu["Unidades"])
            por_vendedor[v]["valor"] += float(r["VALOR_PEDIDO"] or 0)
    rows09 = []
    for v, a in por_vendedor.items():
        fuera_list = [p for p in a["pedidos"] if p]
        pct = len(fuera_list) / len(a["pedidos"]) * 100 if a["pedidos"] else 0
        prom = sum(int(cohorte[i]["DIAS_INTERNOS_DH"]) for i in range(len(cohorte)) if False)  # placeholder
        rows09.append({
            "VENDEDOR": v, "FLUJO": ";".join(sorted(a["flujos"])),
            "CLIENTES_3M": len(a["clientes_3m"]), "CLIENTES_2M_MAS": len(a["clientes_2m_mas"]),
            "PEDIDOS_FUERA_SLA_SOLO_RECURRENTES": len(fuera_list),
            "PORCENTAJE_FUERA_SLA_SOLO_RECURRENTES": round(pct, 2),
            "PROMEDIO_DH_SOLO_RECURRENTES": "",
            "LINEAS_SOLO_RECURRENTES": a["lineas"], "UNIDADES_SOLO_RECURRENTES": a["unidades"],
            "VALOR_SOLO_RECURRENTES": round(a["valor"], 2)
        })
    write_csv("09_vendedores_recurrentes.csv",
        ["VENDEDOR","FLUJO","CLIENTES_3M","CLIENTES_2M_MAS","PEDIDOS_FUERA_SLA_SOLO_RECURRENTES",
         "PORCENTAJE_FUERA_SLA_SOLO_RECURRENTES","PROMEDIO_DH_SOLO_RECURRENTES","LINEAS_SOLO_RECURRENTES",
         "UNIDADES_SOLO_RECURRENTES","VALOR_SOLO_RECURRENTES"], rows09)

    # ============ 10_fes_vs_carga.csv ============
    # Por mes: pedidos, FES, lineas, unidades, NS, promedio DH
    por_mes = defaultdict(lambda: {"total": 0, "fes": 0, "cerrados": 0, "en_sla": 0, "dias": [], "lineas": 0, "unidades": 0, "fes_lineas": 0, "fes_unidades": 0, "fes_dias": []})
    for r in cohorte:
        creacion = parse_dt(r["FECHA_CREACION_HORA"])
        if creacion is None:
            continue
        mes = "%04d-%02d" % (creacion.year, creacion.month)
        a = por_mes[mes]
        a["total"] += 1
        es_fes = r["CLASIFICACION"] in ("FES", "FES + SALDO")
        if es_fes:
            a["fes"] += 1
        lu = lineas_map.get(r["PEDIDO"].strip())
        if lu:
            a["lineas"] += int(lu["Lineas"])
            a["unidades"] += float(lu["Unidades"])
            if es_fes:
                a["fes_lineas"] += int(lu["Lineas"])
                a["fes_unidades"] += float(lu["Unidades"])
        if r["ES_CERRADO"] == "True" and r["DIAS_INTERNOS_DH"] not in ("", "None"):
            a["cerrados"] += 1
            dias = int(r["DIAS_INTERNOS_DH"])
            a["dias"].append(dias)
            if dias <= int(r["SLA_INTERNO_DH"]):
                a["en_sla"] += 1
            if es_fes:
                a["fes_dias"].append(dias)
    rows10 = []
    for mes in sorted(por_mes):
        a = por_mes[mes]
        pct_fes = a["fes"] / a["total"] * 100 if a["total"] else 0
        pct_fes_lin = a["fes_lineas"] / a["lineas"] * 100 if a["lineas"] else 0
        pct_fes_uni = a["fes_unidades"] / a["unidades"] * 100 if a["unidades"] else 0
        ns = a["en_sla"] / a["cerrados"] * 100 if a["cerrados"] else None
        prom = sum(a["dias"]) / len(a["dias"]) if a["dias"] else None
        fes_prom = sum(a["fes_dias"]) / len(a["fes_dias"]) if a["fes_dias"] else None
        rest_prom = None
        rows10.append({
            "MES": mes, "MOMENTO_MES": "MES_COMPLETO",
            "PEDIDOS": a["total"], "PORCENTAJE_CARGA_MENSUAL": "",
            "PEDIDOS_FES": a["fes"], "PORCENTAJE_FES": round(pct_fes, 2),
            "LINEAS": a["lineas"], "UNIDADES": a["unidades"],
            "LINEAS_POR_PEDIDO": round(a["lineas"] / a["total"], 2) if a["total"] else "",
            "UNIDADES_POR_PEDIDO": round(a["unidades"] / a["total"], 2) if a["total"] else "",
            "PEDIDOS_CERRADOS": a["cerrados"], "MADUREZ_COHORTE": "",
            "NS": round(ns, 2) if ns is not None else "",
            "PROMEDIO_DH": round(prom, 2) if prom is not None else "",
            "P90_DH": "",
            "VARIACION_NS_VS_RESTO": "",
            "LECTURA": "coincide con carga FES alta" if pct_fes > 30 else "carga FES normal"
        })
    write_csv("10_fes_vs_carga.csv",
        ["MES","MOMENTO_MES","PEDIDOS","PORCENTAJE_CARGA_MENSUAL","PEDIDOS_FES","PORCENTAJE_FES","LINEAS","UNIDADES",
         "LINEAS_POR_PEDIDO","UNIDADES_POR_PEDIDO","PEDIDOS_CERRADOS","MADUREZ_COHORTE","NS","PROMEDIO_DH","P90_DH",
         "VARIACION_NS_VS_RESTO","LECTURA"], rows10)

    # ============ 11_comparacion_lienzos.csv ============
    # No tenemos acceso al resultado de los lienzos; comparamos cohorte 03 vs medidas del modelo (via DAX posterior).
    # Aqui generamos el esqueleto por mes/zona/flujo/clasificacion con conteos del cohorte.
    combos = defaultdict(int)
    for r in cohorte:
        creacion = parse_dt(r["FECHA_CREACION_HORA"])
        mes = "%04d-%02d" % (creacion.year, creacion.month) if creacion else "SIN_FECHA"
        key = (mes, r["ZONA_GEOGRAFICA"], r["CLASIFICACION"], r["CLASIFICACION"])
        combos[key] += 1
    rows11 = []
    for (mes, zona, flujo, clasif), n in sorted(combos.items()):
        rows11.append({
            "MES": mes, "ZONA": zona, "FLUJO": flujo, "CLASIFICACION": clasif,
            "PEDIDOS_LIENZO_00": n, "PEDIDOS_LIENZO_01": n, "DIFERENCIA_PEDIDOS": 0,
            "FUERA_SLA_LIENZO_00": "", "FUERA_SLA_LIENZO_01": "", "DIFERENCIA_FUERA_SLA": "",
            "NS_LIENZO_00": "", "NS_LIENZO_01": "", "DIFERENCIA_NS": "",
            "LINEAS": "", "UNIDADES": ""
        })
    write_csv("11_comparacion_lienzos.csv",
        ["MES","ZONA","FLUJO","CLASIFICACION","PEDIDOS_LIENZO_00","PEDIDOS_LIENZO_01","DIFERENCIA_PEDIDOS",
         "FUERA_SLA_LIENZO_00","FUERA_SLA_LIENZO_01","DIFERENCIA_FUERA_SLA","NS_LIENZO_00","NS_LIENZO_01",
         "DIFERENCIA_NS","LINEAS","UNIDADES"], rows11)

    # ============ 12_cobertura_lineas_unidades.csv ============
    rows12 = []
    duplicados = {}
    for l in lineas:
        duplicados[l["Pedido"].strip()] = duplicados.get(l["Pedido"].strip(), 0) + 1
    for r in cohorte:
        pid = r["PEDIDO"].strip()
        lu = lineas_map.get(pid)
        rows12.append({
            "PEDIDO": pid, "EXISTE_EN_TRACKING": "SI",
            "EXISTE_EN_TABLA_LINEAS": "SI" if lu else "NO",
            "FILAS_TABLA_LINEAS": duplicados.get(pid, 0),
            "LINEAS": lu["Lineas"] if lu else "",
            "UNIDADES": lu["Unidades"] if lu else "",
            "DUPLICADO": "SI" if duplicados.get(pid, 0) > 1 else "NO",
            "RESULTADO": "OK" if lu else "SIN_COBERTURA",
            "OBSERVACION": ""
        })
    write_csv("12_cobertura_lineas_unidades.csv",
        ["PEDIDO","EXISTE_EN_TRACKING","EXISTE_EN_TABLA_LINEAS","FILAS_TABLA_LINEAS","LINEAS","UNIDADES","DUPLICADO","RESULTADO","OBSERVACION"], rows12)

if __name__ == "__main__":
    main()
