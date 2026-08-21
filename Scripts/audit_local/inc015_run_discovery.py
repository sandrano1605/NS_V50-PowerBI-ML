import sys, os
sys.path.insert(0, 'scripts')
from conexion_sql import conectar

sql_path = r'scripts\audit_local\inc015_yv01_source_discovery.sql'
run_dir = r'Docs\AUDITORIA_LIVE\local_runs\20260812_084605_inc015_yv01_source_discovery_c3031e0\raw'

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
                if not batch:
                    break
                for r in batch:
                    vals = [str(v)[:300] if v is not None else 'NULL' for v in r]
                    all_output.append('\t'.join(vals))
            all_output.append('---')
        if not cur.nextset():
            break
except Exception as e:
    all_output.append(f'ERROR: {str(e)[:500]}')
finally:
    conn.close()

out_path = os.path.join(run_dir, 'inc015_yv01_source_discovery.txt')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(all_output))

print(f'Saved {len(all_output)} lines')
# Print all output (it should be manageable)
for l in all_output:
    print(l)
