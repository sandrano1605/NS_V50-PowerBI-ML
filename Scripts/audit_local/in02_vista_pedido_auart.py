import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c = conectar(30); cur = c.cursor()

print("=== VISTA_PEDIDO: cruce con VBAK (AUART y canal) ===")
# VISTA_PEDIDO tiene solo 808 pedidos - cruzar con VBAK por lookup directo
cur.execute("""
SELECT
    CASE WHEN K.VBELN IS NULL THEN 'SIN_VBAK' ELSE 'CON_VBAK' END AS estado,
    K.AUART,
    RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),K.VTWEG))),2) AS canal,
    COUNT(DISTINCT V.VBELN) AS pedidos
FROM dbo.VISTA_PEDIDO V
LEFT JOIN dbo.VBAK_SAP K ON CONVERT(VARCHAR(20),K.VBELN) = CONVERT(VARCHAR(20),V.VBELN)
GROUP BY CASE WHEN K.VBELN IS NULL THEN 'SIN_VBAK' ELSE 'CON_VBAK' END,
         K.AUART,
         RIGHT('00'+LTRIM(RTRIM(CONVERT(VARCHAR(10),K.VTWEG))),2)
ORDER BY pedidos DESC
""")
for r in cur.fetchall():
    print(f"  {r[0]} AUART={r[1]} canal={r[2]}: {r[3]:,}")

c.close()
