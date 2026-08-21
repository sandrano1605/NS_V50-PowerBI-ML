import sys
sys.path.insert(0, 'scripts')
from conexion_sql import conectar

conn = conectar(timeout=15)
cur = conn.cursor()

# Check AUART of the universe orders vs VBAP coverage
print("=== VBAK AUART distribution (May-Aug 2026) ===")
cur.execute("""
    SELECT K.AUART, COUNT(DISTINCT K.VBELN) AS total,
           COUNT(DISTINCT V.VBELN) AS in_vbap
    FROM VBAK_SAP K
    LEFT JOIN VBAP_SAP V ON V.VBELN = K.VBELN AND V.AEDAT >= GETDATE()-730
    WHERE K.ERDAT >= '2026-05-01'
    GROUP BY K.AUART
    ORDER BY total DESC
""")
print("AUART\ttotal\tin_vbap\tpct")
for r in cur.fetchall():
    pct = r[2]*100.0/r[1] if r[1] > 0 else 0
    print(f"{r[0]}\t{r[1]}\t{r[2]}\t{pct:.1f}%")

print("\n=== VBAP_SAP: total positions, min/max dates ===")
cur.execute("SELECT COUNT(*) AS positions, COUNT(DISTINCT VBELN) AS distinct_orders, MIN(AEDAT) AS min_aedat, MAX(AEDAT) AS max_aedat FROM VBAP_SAP")
for r in cur.fetchall():
    print(f"positions={r[0]}, orders={r[1]}, aedat={r[2]} to {r[3]}")

print("\n=== VBAP_SAP: AUART distribution (via VBAK join) ===")
cur.execute("""
    SELECT K.AUART, COUNT(DISTINCT V.VBELN) AS orders
    FROM VBAP_SAP V
    JOIN VBAK_SAP K ON K.VBELN = V.VBELN
    GROUP BY K.AUART
    ORDER BY orders DESC
""")
print("AUART\torders")
for r in cur.fetchall():
    print(f"{r[0]}\t{r[1]}")

conn.close()
