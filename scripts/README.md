# Scripts de Test — Trazabilidad VBFA y modelo NS

Plantillas reutilizables para auditar la trazabilidad SQL→modelo del proyecto NS.

## Uso

Todos los scripts conectan a `128.1.3.21/DMF_VTA_PRD` con autenticación SQL.
Las credenciales se pasan por variables de entorno (NUNCA hardcodear en el repo):

```powershell
$env:NS_SQL_UID = "tu_usuario"
$env:NS_SQL_PWD = "tu_password"
```

> Alternativa: los scripts incluyen valores de ejemplo al final. Reemplázalos localmente si es necesario,
> pero no los commitees.

## Inventario de plantillas

| Script | Propósito |
|---|---|
| `test_00_conexion_integrada.py` | Prueba conexión con autenticación integrada de Windows |
| `test_00b_select_integrada.py` | Prueba SELECTs con Windows integrada |
| `test_01_conexion_sql.py` | Prueba conexión SQL auth (UID/PWD) |
| `test_02_select_definicion_parametros.py` | SELECT sys.procedures + sys.parameters (definición SP) |
| `test_03_esquema_vbfa_vttp.py` | Esquema de tablas dbo.VBFA_SAP y dbo.VTTP_SAP |
| `test_04_codigos_vbfa.py` | Valores de VBTYP_V / VBTYP_N en VBFA |
| `test_05_interpretacion_tramo.py` | Interpreta parámetros SP (M-J = rango, C = pedido) |
| `test_06_ventanas_borde.py` | Ventanas de fecha (borde 30-06/03-07, solicitada 01-07/02-07) |
| `test_07_diagnostico_fechas.py` | Diagnostica ERDAT_DATE y formatos de fecha |
| `test_08_evidencia_vbfa_completa.py` | Genera TODA la evidencia de reconciliación VBFA |
| `test_09_finalizar_reconciliacion.py` | Actualiza RESULTADO.md y manifest del run |
| `test_10_evidencia_vbfa_inicial.py` | Plantilla de evidencia inicial VBFA |
| `test_11_verificar_evidencia.py` | Verifica los CSV generados |

## Orden recomendado

```powershell
# 1. Conectar
python scripts/test_01_conexion_sql.py
# 2. Explorar esquema
python scripts/test_03_esquema_vbfa_vttp.py
# 3. Interpretar códigos
python scripts/test_04_codigos_vbfa.py
python scripts/test_05_interpretacion_tramo.py
# 4. Ventanas
python scripts/test_06_ventanas_borde.py
# 5. Evidencia completa
python scripts/test_08_evidencia_vbfa_completa.py
python scripts/test_09_finalizar_reconciliacion.py
```

## Notas

- **Nunca ejecutar el SP** `STP_GET_VBFA_TRAMO_FILTRO` en producción sin autorización.
  Los tests usan solo SELECT de lectura.
- La lógica del SP se descubre por datos: `M-J` = rango `VBTYP_V IN ('M','J')`, `C` = pedido posterior.
- VBFA tiene duplicados a la granularidad `VBELV+VBELN+ERDAT+ERZET` (1.706 grupos) — el SP deduplica.
- Los pedidos clave (4190139455, 1167577) no están en el tramo VBFA M→C; su cierre es por manifiesto.
