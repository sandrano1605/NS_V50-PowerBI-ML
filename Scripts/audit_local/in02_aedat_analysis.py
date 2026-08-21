import sys, time; sys.path.insert(0,'scripts')
from conexion_sql import conectar

c = conectar(timeout=300)
cur = c.cursor()

print("="*72)
print("1) FECHAS DEL UNIVERSO (VBAK canales 42-47, ultimos 6 meses)")
print("="*72)
cur.execute("""
SELECT
    MIN(K.ERDAT) AS min_erdat,
    MAX(K.ERDAT) AS max_erdat,
    COUNT(DISTINCT K.VBELN) AS pedidos_universo
FROM dbo.VBAK_SAP K
WHERE K.ERDAT >= DATEADD(MONTH,-6,CAST(GETDATE() AS DATE))
  AND RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),K.VTWEG))),2) IN ('42','43','44','45','46','47')
""")
r = cur.fetchone()
print(f"  Min ERDAT: {r[0]} | Max ERDAT: {r[1]} | Pedidos: {r[2]:,}")
try:
    ultimo = time.strptime(str(r[1]), '%d-%m-%Y')
    dias = (time.time() - time.mktime(ultimo))/86400
    print(f"  Ultimo pedido hace: {dias:,.0f} dias")
except Exception as e:
    print(f"  (fecha max: {r[1]})")

print()
print("="*72)
print("2) DISTRIBUCION DE MAX(AEDAT) POR PEDIDO DEL UNIVERSO (VBAK 6M canales 42-47)")
print("="*72)
print("   Para cada pedido reciente, cual es el AEDAT mas nuevo de sus posiciones VBAP")
cur.execute("""
SELECT bucket, COUNT(*) AS pedidos FROM (
    SELECT K.VBELN,
        CASE
            WHEN MAX(V.AEDAT) >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE)) THEN 'A: AEDAT<=3M (dentro 90d)'
            WHEN MAX(V.AEDAT) >= DATEADD(MONTH,-4,CAST(GETDATE() AS DATE)) THEN 'B: AEDAT 3-4M (dentro 120d)'
            WHEN MAX(V.AEDAT) >= DATEADD(MONTH,-6,CAST(GETDATE() AS DATE)) THEN 'C: AEDAT 4-6M'
            WHEN MAX(V.AEDAT) >= DATEADD(MONTH,-12,CAST(GETDATE() AS DATE)) THEN 'D: AEDAT 6-12M'
            WHEN MAX(V.AEDAT) >= DATEADD(MONTH,-24,CAST(GETDATE() AS DATE)) THEN 'E: AEDAT 12-24M'
            ELSE 'F: AEDAT >24M o SIN posiciones'
        END AS bucket
    FROM dbo.VBAK_SAP K
    LEFT JOIN dbo.VBAP_SAP V ON V.VBELN = K.VBELN
    WHERE K.ERDAT >= DATEADD(MONTH,-6,CAST(GETDATE() AS DATE))
      AND RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),K.VTWEG))),2) IN ('42','43','44','45','46','47')
    GROUP BY K.VBELN
) t
GROUP BY bucket
ORDER BY bucket
""")
rows = cur.fetchall()
for r in rows:
    print(f"  {r[0]}: {r[1]:,}")

print()
print("="*72)
print("3) COBERTURA POTENCIAL POR VENTANA (pedidos con posiciones dentro de la ventana)")
print("="*72)
cur.execute("""
SELECT
    COUNT(*) AS total_universo,
    SUM(CASE WHEN max_aedat >= DATEADD(MONTH,-4,CAST(GETDATE() AS DATE)) THEN 1 ELSE 0 END) AS con_pos_120d,
    SUM(CASE WHEN max_aedat >= DATEADD(MONTH,-24,CAST(GETDATE() AS DATE)) THEN 1 ELSE 0 END) AS con_pos_730d
FROM (
    SELECT K.VBELN, MAX(V.AEDAT) AS max_aedat
    FROM dbo.VBAK_SAP K
    LEFT JOIN dbo.VBAP_SAP V ON V.VBELN = K.VBELN
    WHERE K.ERDAT >= DATEADD(MONTH,-6,CAST(GETDATE() AS DATE))
      AND RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),K.VTWEG))),2) IN ('42','43','44','45','46','47')
    GROUP BY K.VBELN
) t
""")
r = cur.fetchone()
total = r[0]
p120 = r[1]
p730 = r[2]
print(f"  Universo VBAK 6M 42-47: {total:,}")
print(f"  Con posiciones AEDAT<=120d: {p120:,} ({p120*100.0/total:.1f}%)")
print(f"  Con posiciones AEDAT<=730d: {p730:,} ({p730*100.0/total:.1f}%)")
print(f"  PERDIDA con 120d vs 730d: {p730-p120:,} pedidos ({(p730-p120)*100.0/total:.1f}%)")

c.close()
