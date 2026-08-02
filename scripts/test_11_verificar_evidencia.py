# -*- coding: utf-8 -*-
import csv, io, sys
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\alonso.moya\OneDrive - ARTEL S.A\Escritorio\💼 Proyectos\Modelo datos power BI\NS\NS_V50_v15_Error_Python_ndarray_Corregido\NS_V50\Docs\AUDITORIA_LIVE\runs\20260802_190000_vbfa_reconciliacion"

print("=== 09_comparacion_sp_modelo.csv ===")
with io.open(p + r"\09_comparacion_sp_modelo.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        print(f"  {r['PEDIDO']}: VBFA primera={r['VBFA_PRIMERA']} ultima={r['VBFA_ULTIMA']}")

print("=== 06_vbfa_granularidad.csv ===")
with io.open(p + r"\06_vbfa_granularidad.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        print(f"  total={r['TOTAL']} ped_orig={r['PEDIDOS_ORIG']} doc_post={r['DOC_POST']}")

print("=== 04_vbfa_tramo_borde.csv ===")
with io.open(p + r"\04_vbfa_tramo_borde.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        print(f"  {r['RANGO']}: total={r['TOTAL']} ped_orig={r['PEDIDOS_ORIG']} doc_post={r['DOC_POST']}")

print("=== 07_vbfa_duplicados.csv ===")
with io.open(p + r"\07_vbfa_duplicados.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))
print(f"  {len(rows)} grupos duplicados (primero 3):")
for r in rows[:3]:
    print(f"   {r}")
