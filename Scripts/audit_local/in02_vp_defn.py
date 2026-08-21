import sys; sys.path.insert(0,'scripts')
from conexion_sql import conectar
c=conectar(15); cur=c.cursor()

print("=== Definicion VISTA_PEDIDO (primeros 3000 chars) ===")
cur.execute("SELECT OBJECT_DEFINITION(OBJECT_ID('dbo.VISTA_PEDIDO'))")
r = cur.fetchone()
if r and r[0]:
    defn = r[0]
    print(defn[:3000])
    print(f"\n... (total {len(defn)} chars)")
else:
    print("Sin permiso VIEW DEFINITION o escripta cifrada")

c.close()
