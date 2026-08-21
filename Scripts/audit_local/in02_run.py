import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar

sql_path = r'scripts\audit_local\in02_hora_ingreso_audit.sql'
run_dir = r'Docs\AUDITORIA_LIVE\local_runs\20260812_100137_in02_hora_ingreso_43_45_549fea2\raw'

with open(sql_path, 'r', encoding='utf-8') as f:
    sql = f.read()

conn = conectar(timeout=120)
cur = conn.cursor()
all_output = []

try:
    cur.execute(sql)
    while True:
        if cur.description:
            cols = [d[0] for d in cur.description]
            all_output.append('\t'.join(cols))
            while True:
                batch = cur.fetchmany(500)
                if not batch: break
                for r in batch:
                    vals = [str(v)[:200] if v is not None else 'NULL' for v in r]
                    all_output.append('\t'.join(vals))
            all_output.append('---')
        if not cur.nextset(): break
except Exception as e:
    all_output.append(f'ERROR: {str(e)[:500]}')
finally:
    conn.close()

import os
out = os.path.join(run_dir, 'in02_hora_ingreso_result.txt')
with open(out, 'w', encoding='utf-8') as f:
    f.write('\n'.join(all_output))

print(f'Saved {len(all_output)} lines')
# Print summary lines (not all 197 rows)
for l in all_output:
    if '---' in l or 'PEDIDO' in l or 'CANAL' in l or 'CAUSA' in l or 'causa' in l or 'Total' in l or 'Recuperable' in l or 'VBAK' in l or 'ZART' in l or 'CONTEXTO' in l or 'RESUMEN' in l or l.startswith('\t'):
        pass
    else:
        print(l)
