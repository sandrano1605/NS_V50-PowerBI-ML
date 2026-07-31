# -*- coding: utf-8 -*-
"""
Auditoria NS - Recalculo independiente de dias habiles y generacion de:
  05_auditoria_dias_habiles.csv
  06_auditoria_pedidos_clave.csv
  07_clientes_recurrentes.csv
  08_permanencia_postfactura.csv
  08b_resumen_permanencia_cliente.csv
"""
import csv, io, os, datetime, re
from collections import defaultdict

OUT = r"C:\Users\ALONSO~1.MOY\AppData\Local\Temp\opencode\AUDITORIA_NS_MODELO_VIVO"

FERIADOS = {
    datetime.date(2025,1,1), datetime.date(2026,1,1), datetime.date(2027,1,1),
    datetime.date(2025,4,18), datetime.date(2026,4,3), datetime.date(2027,3,26),
    datetime.date(2025,4,19), datetime.date(2026,4,4), datetime.date(2027,3,27),
    datetime.date(2025,5,1), datetime.date(2026,5,1), datetime.date(2027,5,1),
    datetime.date(2025,5,21), datetime.date(2026,5,21), datetime.date(2027,5,21),
    datetime.date(2025,6,20), datetime.date(2026,6,21), datetime.date(2027,6,21),
    datetime.date(2025,6,29), datetime.date(2026,6,29), datetime.date(2027,6,28),
    datetime.date(2025,7,16), datetime.date(2026,7,16), datetime.date(2027,7,16),
    datetime.date(2025,8,15), datetime.date(2026,8,15), datetime.date(2027,8,15),
    datetime.date(2025,9,18), datetime.date(2026,9,18), datetime.date(2027,9,18),
    datetime.date(2025,9,19), datetime.date(2026,9,19), datetime.date(2027,9,19),
    datetime.date(2025,10,12), datetime.date(2026,10,12), datetime.date(2027,10,11),
    datetime.date(2025,10,31), datetime.date(2026,10,31), datetime.date(2027,10,31),
    datetime.date(2025,11,1), datetime.date(2026,11,1), datetime.date(2027,11,1),
    datetime.date(2025,11,16), datetime.date(2025,12,8), datetime.date(2026,12,8),
    datetime.date(2027,12,8), datetime.date(2025,12,14), datetime.date(2025,12,25),
    datetime.date(2026,12,25), datetime.date(2027,12,25),
}

def parse_dt(v):
    if v is None or str(v).strip() == "":
        return None
    s = str(v).strip()
    for fmt in ("%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M", "%d-%m-%Y 0:00:00", "%d-%m-%Y"):
        try:
            return datetime.datetime.strptime(s, fmt)
        except ValueError:
            continue
    # ISO
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None

def dh_modelo(inicio, fin):
    """Misma convencion del modelo: excluye dia inicial (I+1), cuenta habiles hasta fin (inclusive)."""
    if inicio is None or fin is None or fin < inicio:
        return None
    if fin == inicio:
        return 0
    d = inicio.date() + datetime.timedelta(days=1)
    fin_d = fin.date()
    if fin_d < d:
        return 0
    n = 0
    while d <= fin_d:
        if d.weekday() < 5 and d not in FERIADOS:
            n += 1
        d += datetime.timedelta(days=1)
    return n

def dh_incluye_inicio(inicio, fin):
    """Alternativa: incluye dia inicial."""
    if inicio is None or fin is None or fin < inicio:
        return None
    d = inicio.date()
    fin_d = fin.date()
    n = 0
    while d <= fin_d:
        if d.weekday() < 5 and d not in FERIADOS:
            n += 1
        d += datetime.timedelta(days=1)
    return n

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

def main():
    cohorte = read_csv("03_cohorte_tracking.csv")
    fechas = read_csv("04_auditoria_fechas.csv")
    print("Cohorte:", len(cohorte), "| Fechas:", len(fechas))

    # ============ 05_auditoria_dias_habiles.csv ============
    rows05 = []
    n_diff = 0
    for r in cohorte[:400]:  # muestra 400 para no hacer 1600 * iteracion de fechas lenta... mejor todas con logica eficiente
        pass
    # Rehacer con todas las filas
    rows05 = []
    for r in cohorte:
        creacion = parse_dt(r["FECHA_CREACION_HORA"])
        cierre = parse_dt(r["FECHA_CIERRE"])
        dias_modelo = r["DIAS_INTERNOS_DH"]
        dias_rec = dh_modelo(creacion, cierre)
        dias_rec_inc = dh_incluye_inicio(creacion, cierre)
        sla = r["SLA_INTERNO_DH"]
        cumple_m = r["CUMPLE_SLA_INTERNO"]
        cumple_r = None
        if dias_rec is not None and sla:
            cumple_r = str(dias_rec <= int(sla)).upper()
        coincide = (dias_modelo == str(dias_rec)) if dias_modelo not in ("", "None", None) else (dias_rec is None)
        if dias_modelo not in ("", "None", None) and dias_rec is not None and str(dias_modelo) != str(dias_rec):
            n_diff += 1
        obs = "CONVENCION_EXCLUYE_INICIAL"
        if dias_rec_inc is not None and dias_rec is not None and dias_rec_inc != dias_rec:
            obs += ";CONV_INCLUYE_INICIAL=" + str(dias_rec_inc)
        rows05.append({
            "PEDIDO": r["PEDIDO"], "FECHA_INICIO": r["FECHA_CREACION_HORA"],
            "FECHA_FIN": r["FECHA_CIERRE"], "DIAS_MODELO": dias_modelo,
            "DIAS_RECALCULADOS": dias_rec, "DIFERENCIA": (int(dias_modelo) - dias_rec) if dias_modelo not in ("","None",None) and dias_rec is not None else "",
            "SLA_INTERNO": sla, "CUMPLE_MODELO": cumple_m, "CUMPLE_RECALCULADO": cumple_r,
            "COINCIDE_RESULTADO": coincide, "OBSERVACION": obs
        })
    write_csv("05_auditoria_dias_habiles.csv",
        ["PEDIDO","FECHA_INICIO","FECHA_FIN","DIAS_MODELO","DIAS_RECALCULADOS","DIFERENCIA","SLA_INTERNO","CUMPLE_MODELO","CUMPLE_RECALCULADO","COINCIDE_RESULTADO","OBSERVACION"], rows05)
    print(f"   Diferencia modelo vs recalculado: {n_diff}")

    # ============ 06_auditoria_pedidos_clave.csv ============
    clave_ids = {"4190139455", "1167577"}
    rows06 = []
    for r in cohorte:
        if r["PEDIDO"] in clave_ids:
            rows06.append(r)
    # muestras
    grupos = {"FES cerrado": [], "FES abierto": [], "NORMAL cerrado": [], "SALDO cerrado": [],
              "FES+SALDO cerrado": [], "Santiago": [], "Regiones": [], "exactamente en SLA": [],
              "1 dia fuera": [], "factura=manifiesto": [], "trp P != U": []}
    for r in cohorte:
        cerrado = r["ES_CERRADO"] == "True"
        flujo = r["CLASIFICACION"]
        if flujo == "FES" and cerrado and len(grupos["FES cerrado"]) < 5:
            grupos["FES cerrado"].append(r)
        if flujo == "FES" and not cerrado and len(grupos["FES abierto"]) < 5:
            grupos["FES abierto"].append(r)
        if flujo == "NORMAL" and cerrado and len(grupos["NORMAL cerrado"]) < 5:
            grupos["NORMAL cerrado"].append(r)
        if flujo == "SALDO" and cerrado and len(grupos["SALDO cerrado"]) < 5:
            grupos["SALDO cerrado"].append(r)
        if flujo == "FES + SALDO" and cerrado and len(grupos["FES+SALDO cerrado"]) < 5:
            grupos["FES+SALDO cerrado"].append(r)
        if r["ZONA_GEOGRAFICA"] == "Santiago" and len(grupos["Santiago"]) < 5:
            grupos["Santiago"].append(r)
        if r["ZONA_GEOGRAFICA"] == "Regiones" and len(grupos["Regiones"]) < 5:
            grupos["Regiones"].append(r)
        try:
            dias = int(r["DIAS_INTERNOS_DH"]); sla = int(r["SLA_INTERNO_DH"])
        except (ValueError, TypeError):
            continue
        if dias == sla and len(grupos["exactamente en SLA"]) < 5:
            grupos["exactamente en SLA"].append(r)
        if dias == sla + 1 and len(grupos["1 dia fuera"]) < 5:
            grupos["1 dia fuera"].append(r)
        fp = parse_dt(r["FECHA_PRIMERA_FACTURA"]); fm = parse_dt(r["FECHA_MANIFIESTO"])
        if fp and fm and fp.date() == fm.date() and len(grupos["factura=manifiesto"]) < 5:
            grupos["factura=manifiesto"].append(r)
    # agrupar todos los seleccionados sin duplicar
    visto = set()
    for g, items in grupos.items():
        for r in items:
            if r["PEDIDO"] not in visto:
                rows06.append({"PEDIDO": r["PEDIDO"], "GRUPO": g, **{k: v for k, v in r.items() if k != "PEDIDO"}})
                visto.add(r["PEDIDO"])
    # datos recalculados
    for r in rows06:
        creacion = parse_dt(r["FECHA_CREACION_HORA"])
        cierre = parse_dt(r["FECHA_CIERRE"])
        r["DIAS_RECALCULADOS"] = dh_modelo(creacion, cierre)
        r["DIAS_MODELO"] = r["DIAS_INTERNOS_DH"]
        r["SLA_INTERNO"] = r["SLA_INTERNO_DH"]
        r["SLA_CLIENTE"] = r["SLA_CLIENTE_DH"]
        r["CUMPLE_MODELO"] = r["CUMPLE_SLA_INTERNO"]
        try:
            dm = int(r["DIAS_MODELO"]); sla = int(r["SLA_INTERNO"])
            r["CUMPLE_RECALCULADO"] = str(dm <= sla)
        except (ValueError, TypeError):
            r["CUMPLE_RECALCULADO"] = ""
    write_csv("06_auditoria_pedidos_clave.csv",
        ["PEDIDO","GRUPO","CLASIFICACION","FLUJO","ZONA_GEOGRAFICA","REGION","ES_CERRADO","FECHA_CREACION","FECHA_CREACION_HORA",
         "FECHA_PRIMERA_FACTURA","FECHA_ULTIMA_FACTURA","FECHA_DESPACHO","FECHA_MANIFIESTO","FECHA_CIERRE",
         "DIAS_MODELO","DIAS_RECALCULADOS","SLA_INTERNO","SLA_CLIENTE","CUMPLE_MODELO","CUMPLE_RECALCULADO",
         "EXCESO_SLA_INTERNO_DH","CLIENTE","VENDEDOR","CANAL","VALOR_PEDIDO"], rows06)

    # ============ 07_clientes_recurrentes.csv ============
    # Por cliente: meses con pedidos fuera SLA (solo cerrados), usando AnioMes de la fecha de creacion
    # Ventana 3M: periodos 0,1,2 de Dim_Periodo_3M
    pedidos_por_cliente = defaultdict(list)
    for r in cohorte:
        try:
            dias = int(r["DIAS_INTERNOS_DH"])
        except (ValueError, TypeError):
            continue
        creacion = parse_dt(r["FECHA_CREACION_HORA"])
        if creacion is None:
            continue
        anio_mes = "%04d-%02d" % (creacion.year, creacion.month)
        fuera = (r["ES_CERRADO"] == "True") and dias > int(r["SLA_INTERNO_DH"])
        pedidos_por_cliente[r["CLIENTE"]].append({
            "anio_mes": anio_mes, "fuera": fuera, "dias": dias, "flujo": r["CLASIFICACION"],
            "vendedor": r["VENDEDOR"], "valor": r["VALOR_PEDIDO"], "pedido": r["PEDIDO"], "sla": r["SLA_INTERNO_DH"]
        })
    # meses de la ventana (del cohorte)
    meses = sorted({p["anio_mes"] for lista in pedidos_por_cliente.values() for p in lista})
    ventana = meses[-3:] if len(meses) >= 3 else meses
    rows07 = []
    for cli, lista in pedidos_por_cliente.items():
        meses_fuera = sorted({p["anio_mes"] for p in lista if p["fuera"] and p["anio_mes"] in ventana})
        n_fuera = len(meses_fuera)
        clasif = "Recurrente 3M" if n_fuera == 3 else ("Recurrente 2M" if n_fuera == 2 else ("Puntual 1M" if n_fuera == 1 else "Sin incumplimiento"))
        total = len([p for p in lista if p["anio_mes"] in ventana])
        fuera_total = len([p for p in lista if p["fuera"] and p["anio_mes"] in ventana])
        pct = (fuera_total / total * 100) if total else 0
        prom = sum(p["dias"] for p in lista if p["fuera"] and p["anio_mes"] in ventana) / fuera_total if fuera_total else None
        # P90
        vals = sorted(p["dias"] for p in lista if p["fuera"] and p["anio_mes"] in ventana)
        p90 = None
        if vals:
            idx = max(0, int(0.9 * len(vals)) - 1)
            p90 = vals[idx]
        flujos = sorted({p["flujo"] for p in lista if p["fuera"] and p["anio_mes"] in ventana})
        vendedores = sorted({p["vendedor"] for p in lista if p["fuera"] and p["anio_mes"] in ventana})
        m1 = ventana[0] if len(ventana) >= 1 else ""
        m2 = ventana[1] if len(ventana) >= 2 else ""
        m3 = ventana[2] if len(ventana) >= 3 else ""
        def fuera_en(m):
            return "SI" if any(p["fuera"] and p["anio_mes"] == m for p in lista) else "NO"
        rows07.append({
            "CLIENTE": cli, "VENDEDOR": ";".join(vendedores), "FLUJO": ";".join(flujos),
            "MES_1": m1, "FUERA_SLA_MES_1": fuera_en(m1),
            "MES_2": m2, "FUERA_SLA_MES_2": fuera_en(m2),
            "MES_3": m3, "FUERA_SLA_MES_3": fuera_en(m3),
            "MESES_FUERA_SLA": n_fuera, "CLASIFICACION_RECURRENCIA": clasif,
            "PEDIDOS_TOTAL": total, "PEDIDOS_FUERA_SLA": fuera_total,
            "PORCENTAJE_FUERA_SLA": round(pct, 2) if pct is not None else "",
            "PROMEDIO_DH_FUERA_SLA": round(prom, 2) if prom is not None else "",
            "P90_DH_FUERA_SLA": p90
        })
    write_csv("07_clientes_recurrentes.csv",
        ["CLIENTE","VENDEDOR","FLUJO","MES_1","FUERA_SLA_MES_1","MES_2","FUERA_SLA_MES_2","MES_3","FUERA_SLA_MES_3",
         "MESES_FUERA_SLA","CLASIFICACION_RECURRENCIA","PEDIDOS_TOTAL","PEDIDOS_FUERA_SLA","PORCENTAJE_FUERA_SLA",
         "PROMEDIO_DH_FUERA_SLA","P90_DH_FUERA_SLA"], rows07)

    # ============ 08_permanencia_postfactura.csv ============
    rows08 = []
    for r in cohorte:
        factura = parse_dt(r["FECHA_PRIMERA_FACTURA"])
        flujo = r["CLASIFICACION"]
        cierre_of = parse_dt(r["FECHA_MANIFIESTO"]) if flujo in ("FES", "FES + SALDO") else parse_dt(r["FECHA_DESPACHO"])
        dias_pf = dh_modelo(factura, cierre_of) if factura and cierre_of else None
        rows08.append({
            "PEDIDO": r["PEDIDO"], "CLIENTE": r["CLIENTE"], "VENDEDOR": r["VENDEDOR"],
            "FLUJO": flujo, "TRACKING": "SI", "ES_CERRADO": r["ES_CERRADO"],
            "FACTURA_INICIO": r["FECHA_PRIMERA_FACTURA"], "CIERRE_OFICIAL": str(cierre_of) if cierre_of else "",
            "TIPO_CIERRE": "MANIFIESTO" if flujo in ("FES", "FES + SALDO") else "DESPACHO",
            "DIAS_POSTFACTURA_DH": dias_pf, "MAYOR_15_DH": "SI" if dias_pf and dias_pf > 15 else "NO",
            "MAYOR_20_DH": "SI" if dias_pf and dias_pf > 20 else "NO", "VALOR_PEDIDO": r["VALOR_PEDIDO"]
        })
    write_csv("08_permanencia_postfactura.csv",
        ["PEDIDO","CLIENTE","VENDEDOR","FLUJO","TRACKING","ES_CERRADO","FACTURA_INICIO","CIERRE_OFICIAL","TIPO_CIERRE",
         "DIAS_POSTFACTURA_DH","MAYOR_15_DH","MAYOR_20_DH","VALOR_PEDIDO"], rows08)

    # 08b resumen por cliente
    agg = defaultdict(lambda: {"n15": 0, "n20": 0, "dias": [], "valor": 0.0, "flujos": set()})
    for r in rows08:
        if r["MAYOR_15_DH"] == "SI":
            k = r["CLIENTE"]
            agg[k]["n15"] += 1
            agg[k]["dias"].append(float(r["DIAS_POSTFACTURA_DH"]))
            agg[k]["valor"] += float(r["VALOR_PEDIDO"] or 0)
            if r["MAYOR_20_DH"] == "SI":
                agg[k]["n20"] += 1
            agg[k]["flujos"].add(r["FLUJO"])
    rows08b = []
    for cli, a in agg.items():
        vals = sorted(a["dias"])
        p90 = vals[max(0, int(0.9 * len(vals)) - 1)]
        rows08b.append({
            "CLIENTE": cli, "FLUJO": ";".join(sorted(a["flujos"])), "PEDIDOS_MAYOR_15": a["n15"],
            "PEDIDOS_MAYOR_20": a["n20"], "PROMEDIO_DH_SOLO_MAYOR_15": round(sum(a["dias"]) / len(a["dias"]), 2),
            "P90_DH_SOLO_MAYOR_15": p90, "VALOR_SOLO_MAYOR_15": round(a["valor"], 2)
        })
    write_csv("08b_resumen_permanencia_cliente.csv",
        ["CLIENTE","FLUJO","PEDIDOS_MAYOR_15","PEDIDOS_MAYOR_20","PROMEDIO_DH_SOLO_MAYOR_15","P90_DH_SOLO_MAYOR_15","VALOR_SOLO_MAYOR_15"], rows08b)

if __name__ == "__main__":
    main()
