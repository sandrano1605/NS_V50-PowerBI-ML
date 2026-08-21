import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c = conectar(10); cur = c.cursor()

print("=== ERZET type info ===")
cur.execute("""
SELECT TOP 5
    c.name AS col_name,
    t.name AS type_name,
    c.max_length, c.precision, c.scale
FROM sys.columns c
JOIN sys.types t ON c.user_type_id = t.user_type_id
WHERE c.object_id = OBJECT_ID('dbo.VBAK_SAP') AND c.name = 'ERZET'
""")
for r in cur.fetchall(): print(r)

print("\n=== ERZET conversion test ===")
cur.execute("""
SELECT TOP 5
    ERZET,
    CONVERT(VARCHAR(20), ERZET) AS conv20,
    CONVERT(VARCHAR(6), ERZET) AS conv6,
    CONVERT(VARCHAR(8), ERZET, 108) AS conv108
FROM dbo.VBAK_SAP
WHERE ERZET IS NOT NULL
""")
cols = [d[0] for d in cur.description]
print('\t'.join(cols))
for r in cur.fetchall():
    print('\t'.join(repr(x) for x in r))

print("\n=== Reproducir logica del fix (HORA_VBAK) ===")
cur.execute("""
SELECT
    V.VBELN,
    V.ERZET,
    LTRIM(RTRIM(CONVERT(VARCHAR(6), V.ERZET))) AS trim6,
    RIGHT('000000' + LTRIM(RTRIM(CONVERT(VARCHAR(6), V.ERZET))), 6) AS right6,
    TRY_CONVERT(TIME(0), STUFF(STUFF(RIGHT('000000' + LTRIM(RTRIM(CONVERT(VARCHAR(6), V.ERZET))), 6), 3, 0, ':'), 6, 0, ':')) AS hora_vbak
FROM dbo.VBAK_SAP AS V
WHERE CONVERT(VARCHAR(20), TRY_CONVERT(BIGINT, V.VBELN)) = '1166551'
""")
cols = [d[0] for d in cur.description]
print('\t'.join(cols))
for r in cur.fetchall():
    print('\t'.join(repr(x) for x in r))

print("\n=== Conversion alternativa correcta (REPLACE de ':') ===")
cur.execute("""
SELECT
    V.VBELN,
    V.ERZET,
    CONVERT(VARCHAR(8), V.ERZET, 108) AS hhmmss,
    REPLACE(CONVERT(VARCHAR(8), V.ERZET, 108), ':', '') AS hhmmss_no_colon,
    TRY_CONVERT(TIME(0), REPLACE(CONVERT(VARCHAR(8), V.ERZET, 108), ':', '')) AS t1,
    TRY_CONVERT(TIME(0), CONVERT(VARCHAR(8), V.ERZET, 108)) AS t2
FROM dbo.VBAK_SAP AS V
WHERE CONVERT(VARCHAR(20), TRY_CONVERT(BIGINT, V.VBELN)) = '1166551'
""")
cols = [d[0] for d in cur.description]
print('\t'.join(cols))
for r in cur.fetchall():
    print('\t'.join(repr(x) for x in r))

c.close()
