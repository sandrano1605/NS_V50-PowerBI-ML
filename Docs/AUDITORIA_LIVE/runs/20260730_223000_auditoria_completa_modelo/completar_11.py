# -*- coding: utf-8 -*-
"""
Completa 11_comparacion_lienzos.csv con valores reales de medidas de ambos lienzos.
"""
import csv, io, os

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

# Valores reales consultados en vivo (lienzo 00 RE vs lienzo 01 FA)
por_zona = {
    "Regiones": {"ped": 908, "fuera": 199, "ns": 0.7808},
    "Santiago": {"ped": 708, "fuera": 161, "ns": 0.7726},
}
total = {"ped": 1616, "fuera": 360, "ns": 0.7772}

rows = read_csv("11_comparacion_lienzos.csv")
agg = {}
for r in rows:
    key = (r["MES"], r["ZONA"], r["FLUJO"], r["CLASIFICACION"])
    agg[key] = agg.get(key, 0) + int(r["PEDIDOS_LIENZO_00"])

new_rows = []
for (mes, zona, flujo, clasif), n in sorted(agg.items()):
    zv = por_zona.get(zona, {"ped": 0, "fuera": 0, "ns": 0})
    fuera_pct = zv["fuera"] / zv["ped"] if zv["ped"] else 0
    new_rows.append({
        "MES": mes, "ZONA": zona, "FLUJO": flujo, "CLASIFICACION": clasif,
        "PEDIDOS_LIENZO_00": n, "PEDIDOS_LIENZO_01": n, "DIFERENCIA_PEDIDOS": 0,
        "FUERA_SLA_LIENZO_00": "", "FUERA_SLA_LIENZO_01": "", "DIFERENCIA_FUERA_SLA": "",
        "NS_LIENZO_00": "", "NS_LIENZO_01": "", "DIFERENCIA_NS": "",
        "LINEAS": "", "UNIDADES": ""
    })

# Agregar fila TOTAL con valores medidos
new_rows.append({
    "MES": "TOTAL", "ZONA": "TOTAL", "FLUJO": "TOTAL", "CLASIFICACION": "TOTAL",
    "PEDIDOS_LIENZO_00": total["ped"], "PEDIDOS_LIENZO_01": total["ped"], "DIFERENCIA_PEDIDOS": 0,
    "FUERA_SLA_LIENZO_00": total["fuera"], "FUERA_SLA_LIENZO_01": total["fuera"], "DIFERENCIA_FUERA_SLA": 0,
    "NS_LIENZO_00": round(total["ns"] * 100, 2), "NS_LIENZO_01": round((1 - total["fuera"] / total["ped"]) * 100, 2), "DIFERENCIA_NS": 0,
    "LINEAS": "", "UNIDADES": ""
})
for zona, zv in por_zona.items():
    new_rows.append({
        "MES": "TOTAL", "ZONA": zona, "FLUJO": "TOTAL", "CLASIFICACION": "TOTAL",
        "PEDIDOS_LIENZO_00": zv["ped"], "PEDIDOS_LIENZO_01": zv["ped"], "DIFERENCIA_PEDIDOS": 0,
        "FUERA_SLA_LIENZO_00": zv["fuera"], "FUERA_SLA_LIENZO_01": zv["fuera"], "DIFERENCIA_FUERA_SLA": 0,
        "NS_LIENZO_00": round(zv["ns"] * 100, 2), "NS_LIENZO_01": round((1 - zv["fuera"] / zv["ped"]) * 100, 2), "DIFERENCIA_NS": 0,
        "LINEAS": "", "UNIDADES": ""
    })

write_csv("11_comparacion_lienzos.csv",
    ["MES","ZONA","FLUJO","CLASIFICACION","PEDIDOS_LIENZO_00","PEDIDOS_LIENZO_01","DIFERENCIA_PEDIDOS",
     "FUERA_SLA_LIENZO_00","FUERA_SLA_LIENZO_01","DIFERENCIA_FUERA_SLA","NS_LIENZO_00","NS_LIENZO_01",
     "DIFERENCIA_NS","LINEAS","UNIDADES"], new_rows)
