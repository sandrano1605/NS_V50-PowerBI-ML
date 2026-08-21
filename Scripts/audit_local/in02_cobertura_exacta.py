import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c=conectar(120); cur=c.cursor()

print("=== VBAP_SAP: distribucion por largo, y cuantos de 7 digitos coinciden con ZART ===")

# Temp ZART 3M con clave exacta
cur.execute("""
IF OBJECT_ID('tempdb..#zart') IS NOT NULL DROP TABLE #zart;
SELECT DISTINCT CONVERT(VARCHAR(20), ZVBELN_PED) AS pedido
INTO #zart
FROM dbo.ZART_TRACK_DATA_SAP
WHERE ZERDAT_PED >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE));
""")

print("1) ZART 3M: largo de clave")
cur.execute("SELECT LEN(pedido) AS largo, COUNT(*) FROM #zart GROUP BY LEN(pedido) ORDER BY largo")
for r in cur.fetchall():
    print(f"   len={r[0]}: {r[1]:,}")

# VBAP 7 digitos
print("\n2) VBAP_SAP: pedidos de 7 digitos (clave exacta)")
cur.execute("""
IF OBJECT_ID('tempdb..#vbap7') IS NOT NULL DROP TABLE #vbap7;
SELECT DISTINCT CONVERT(VARCHAR(20), VBELN) AS pedido
INTO #vbap7
FROM dbo.VBAP_SAP
WHERE LEN(VBELN) = 7;
""")
cur.execute("SELECT COUNT(*) FROM #vbap7")
print(f"   VBAP 7 digitos: {cur.fetchone()[0]:,}")

# Cruce ZART (7 digitos) vs VBAP 7 digitos
print("\n3) Cobertura: ZART 3M de 7 digitos vs VBAP de 7 digitos")
cur.execute("""
SELECT
    SUM(CASE WHEN LEN(Z.pedido)=7 THEN 1 ELSE 0 END) AS zart_7d,
    SUM(CASE WHEN LEN(Z.pedido)=7 AND V.pedido IS NOT NULL THEN 1 ELSE 0 END) AS en_vbap_7d
FROM #zart Z
LEFT JOIN #vbap7 V ON V.pedido = Z.pedido
""")
r = cur.fetchone()
print(f"   ZART 7 digitos: {r[0]:,}")
print(f"   En VBAP 7 digitos (exacto): {r[1]:,} ({r[1]*100.0/r[0] if r[0] else 0:.1f}%)")

# Que largo tienen los pedidos ZART 3M
print("\n4) Muestra ZART 3M: pedidos y largo")
cur.execute("""
SELECT TOP 10 pedido, LEN(pedido) FROM #zart ORDER BY pedido
""")
for r in cur.fetchall():
    print(f"   {r[0]} (len={r[1]})")

c.close()
