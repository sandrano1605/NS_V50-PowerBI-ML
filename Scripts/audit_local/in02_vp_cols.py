import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c=conectar(15); cur=c.cursor()
cur.execute("SELECT TOP 1 * FROM dbo.VISTA_PEDIDO")
cols = [d[0] for d in cur.description]
print('Columnas VISTA_PEDIDO:')
for col in cols: print(f'  {col}')
c.close()
