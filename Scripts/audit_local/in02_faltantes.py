import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c=conectar(120); cur=c.cursor()

# Reconstruir temp tables
cur.execute("""
IF OBJECT_ID('tempdb..#zart') IS NOT NULL DROP TABLE #zart;
SELECT DISTINCT CONVERT(VARCHAR(20), ZVBELN_PED) AS pedido
INTO #zart
FROM dbo.ZART_TRACK_DATA_SAP
WHERE ZERDAT_PED >= DATEADD(MONTH,-3,CAST(GETDATE() AS DATE));
IF OBJECT_ID('tempdb..#vbap') IS NOT NULL DROP TABLE #vbap;
SELECT DISTINCT CONVERT(VARCHAR(20), VBELN) AS pedido
INTO #vbap
FROM dbo.VBAP_SAP;
""")

print("=== Los 2 pedidos ZART 3M SIN posiciones en VBAP ===")
cur.execute("""
SELECT Z.pedido
FROM #zart Z
LEFT JOIN #vbap V ON V.pedido = Z.pedido
WHERE V.pedido IS NULL
""")
faltantes = [r[0] for r in cur.fetchall()]
print(f"  Faltantes: {faltantes}")

# Para cada faltante, ver si existe en VBAP con formato distinto
for p in faltantes:
    print(f"\n=== Pedido {p}: busqueda en VBAP por formatos ===")
    cur.execute("""
    SELECT COUNT(*) FROM dbo.VBAP_SAP WHERE VBELN = CAST(? AS BIGINT)
    """, (p,))
    print(f"  VBAP con CAST BIGINT: {cur.fetchone()[0]:,}")
    cur.execute("""
    SELECT TOP 3 VBELN, LEN(VBELN) FROM dbo.VBAP_SAP WHERE VBELN LIKE ?
    """, (f'%{p}%',))
    for r in cur.fetchall():
        print(f"    LIKE %{p}%: VBELN={r[0]} (len={r[1]})")

c.close()
