# RESULTADO: Prueba lienzo 02 — Ingreso de Pedidos (2026-08-03)

**Rama:** work/ns-lienzo-02-ingreso-pedidos
**SHA local:** cd8b85ea553e2651c0e151e18a40eab3f646182e
**SHA remoto:** cd8b85ea553e2651c0e151e18a40eab3f646182e
**Dictamen:** ⏸️ DETENIDA — requiere interacción manual (credenciales)

## Estado

La ejecución quedó **detenida por barrera de credenciales**:

1. Proyecto NS.pbip abierto correctamente (PID 27448).
2. Refresh completo iniciado vía MCP (timeout MCP normal a los 30s).
3. Logs de Power BI Desktop muestran **QueryPermissionException**
   (`Microsoft.Mashup.Engine.Interface.QueryPermissionException`) en el
   proceso 27448 — una consulta está pidiendo permiso/credenciales.
4. Power BI Desktop no expone ventanas visibles (diálogo modal de
   credenciales o de permisos esperando confirmación manual).
5. Los conteos de Fact_Tracking / Fact_Pedidos_Auditoria devuelven blank;
   Pedidos_Normal_VBAK sí responde (2.192 filas).

## Causa probable

La rama del lienzo 02 incluye cambios de modelo (Fact_Tracking con
TRAMO_HORA_INGRESO, medidas IN, integración VBAK). Al abrir el proyecto
con un modelo modificado, Power BI Desktop solicita autenticación para las
conexiones SQL (DMF_VTA_PRD / PASO_WMS) o permisos de las consultas nuevas.

## Acción requerida

1. **Usuario:** aceptar/ingresar credenciales en el diálogo de Power BI
   Desktop que está esperando en pantalla (usuario a_moya / solo_lectura).
2. Confirmar que el refresh completa sin errores.
3. Re-ejecutar el LLM local para continuar la validación.

## Validaciones pendientes (no ejecutadas por la detención)

- Q1: día de semana con más pedidos/líneas/unidades.
- Q2: proporción hasta/después de 14:30 y sin hora válida.
- Q3: tendencia por día del mes y aporte por flujo.
- Reconciliaciones de las 3 preguntas.
- Smoke test páginas 00, 01, 01.1, 02.
- Inventario de 23 visuales y 6 filtros.
- 15_incoherencias.csv (obligatorio incluso sin problemas).

## Archivos de evidencia

- 00_git_before.txt
- 01_refresh.txt
- RESULTADO.md (este archivo)
