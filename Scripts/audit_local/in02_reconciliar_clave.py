import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c=conectar(60); cur=c.cursor()

print("=== Pedido 1168066: existe en VBAK? con que formato? ===")
cur.execute("""
SELECT VBELN, LEN(VBELN), AUART, VTWEG, ERDAT
FROM dbo.VBAK_SAP
WHERE VBELN IN ('1168066', '1221168066', 1168066, 1221168066)
""")
for r in cur.fetchall():
    print(f"  {r}")

print("\n=== Pedido 1168066: en ZART? ===")
cur.execute("""
SELECT ZVBELN_PED, LEN(ZVBELN_PED), ZERDAT_PED, ZVTWEG
FROM dbo.ZART_TRACK_DATA_SAP
WHERE ZVBELN_PED IN ('1168066', '1221168066', 1168066, 1221168066)
""")
for r in cur.fetchall():
    print(f"  {r}")

print("\n=== Los 2 faltantes: busqueda completa en VBAK por ambos formatos ===")
for p in ['1168066', '1168568']:
    cur.execute("""
    SELECT VBELN, AUART, VTWEG, ERDAT FROM dbo.VBAK_SAP WHERE VBELN = ? OR VBELN = ?
    """, (p, '1221'+p))
    rows = cur.fetchall()
    print(f"  Pedido {p}:")
    for r in rows:
        print(f"    VBAK: {r}")

c.close()
