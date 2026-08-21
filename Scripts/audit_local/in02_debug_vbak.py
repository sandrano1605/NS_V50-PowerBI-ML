import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c = conectar(10); cur = c.cursor()

# Query exacta del fix (VBAKHoraOrigen) para pedidos de muestra
sql = """
SELECT
    CONVERT(VARCHAR(20), TRY_CONVERT(BIGINT, V.VBELN)) AS PED_KEY,
    V.VBELN,
    V.VTWEG,
    V.ERDAT,
    V.ERZET,
    TRY_CONVERT(TIME(0),
        STUFF(STUFF(RIGHT('000000' + LTRIM(RTRIM(CONVERT(VARCHAR(6), V.ERZET))), 6), 3, 0, ':'), 6, 0, ':')
    ) AS HORA_VBAK
FROM dbo.VBAK_SAP AS V
WHERE CONVERT(VARCHAR(20), TRY_CONVERT(BIGINT, V.VBELN)) IN ('1166551','1166552','1166574','1166596','1166599','4190139307','4190139329','1166496','1166503','4190139326')
"""

print("=== VBAK lookup para pedidos de muestra ===")
cur.execute(sql)
cols = [d[0] for d in cur.description]
print('\t'.join(cols))
rows = cur.fetchall()
for r in rows:
    print('\t'.join(str(x) if x is not None else 'NULL' for x in r))
print(f"({len(rows)} rows)")

# Verificar tambien el filtro VTWEG del fix
print("\n=== VBAK sin filtro VTWEG (mismos pedidos) ===")
cur.execute("""
SELECT V.VBELN, V.VTWEG, V.ERDAT, V.ERZET
FROM dbo.VBAK_SAP AS V
WHERE CONVERT(VARCHAR(20), TRY_CONVERT(BIGINT, V.VBELN)) IN ('1166551','1166552','1166574','1166596','1166599','4190139307','4190139329','1166496','1166503','4190139326')
""")
print('\t'.join([d[0] for d in cur.description]))
for r in cur.fetchall():
    print('\t'.join(str(x) if x is not None else 'NULL' for x in r))

c.close()
