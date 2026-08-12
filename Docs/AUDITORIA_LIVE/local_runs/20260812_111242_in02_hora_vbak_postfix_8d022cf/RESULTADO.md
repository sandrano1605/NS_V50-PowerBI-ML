# RESULTADO — IN02 fallback VBAK post-fix

RUN_ID: 20260812_111242_in02_hora_vbak_postfix_8d022cf
Estado: COMPLETED

## IN02-002 BUG_CONVERSION_ERZET (RED)

El fix eb07b64 no recupera pedidos porque VBAK_SAP.ERZET es varchar(8) con ':' y
CONVERT(VARCHAR(6)) trunca dejando ':' final, rompiendo TRY_CONVERT(TIME).

Fix correcto: TRY_CONVERT(TIME(0), ERZET) directo.

Estado actual canales 43/45:
- Sin hora valida: 184 (43:149, 45:35)
- Hasta 14:30: 687
- Despues 14:30: 692
