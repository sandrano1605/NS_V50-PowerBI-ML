import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c=conectar(60); cur=c.cursor()

print("=== Distribucion de largo de VBELN en VBAP_SAP ===")
cur.execute("""
SELECT LEN(VBELN) AS largo, COUNT(DISTINCT VBELN) AS pedidos
FROM dbo.VBAP_SAP
GROUP BY LEN(VBELN)
ORDER BY largo
""")
for r in cur.fetchall():
    print(f"  len={r[0]}: {r[1]:,}")

print("\n=== Prefijos de VBELN de 10 digitos ===")
cur.execute("""
SELECT TOP 20 LEFT(VBELN,4) AS prefijo, COUNT(DISTINCT VBELN) AS pedidos
FROM dbo.VBAP_SAP
WHERE LEN(VBELN) = 10
GROUP BY LEFT(VBELN,4)
ORDER BY pedidos DESC
""")
for r in cur.fetchall():
    print(f"  prefijo {r[0]}: {r[1]:,}")

print("\n=== VBELN de 7 digitos: prefijos ===")
cur.execute("""
SELECT TOP 10 LEFT(VBELN,3) AS prefijo, COUNT(DISTINCT VBELN) AS pedidos
FROM dbo.VBAP_SAP
WHERE LEN(VBELN) = 7
GROUP BY LEFT(VBELN,3)
ORDER BY pedidos DESC
""")
for r in cur.fetchall():
    print(f"  prefijo {r[0]}: {r[1]:,}")

print("\n=== Comparar: VBELN con prefijo 1221 -> el sufijo ===")
cur.execute("""
SELECT TOP 15 VBELN, RIGHT(VBELN,7) AS sufijo7
FROM dbo.VBAP_SAP
WHERE VBELN LIKE '1221%'
""")
for r in cur.fetchall():
    print(f"  {r[0]} -> {r[1]}")

c.close()
