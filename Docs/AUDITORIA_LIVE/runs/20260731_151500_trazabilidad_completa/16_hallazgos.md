# Hallazgos

1. Auditor estatico: AMARILLO (4 tablas con consumidor dinamico: Dim_Cliente, Fact_Pedidos_Auditoria, Fact_Tracking, Resultado)
2. Columnas FPA: 181 clasificadas (87 CONSERVAR + 94 NO_BORRAR_SIN_PRUEBA_CONTRATO). Las 94 NO estan autorizadas a borrar.
3. Python.Execute en Resultado: 86 columnas de salida exportadas. Contrato real de entrada PENDIENTE de leer el script Python.
4. Procedimiento VBFA: NO ejecutado (requiere acceso SQL Server 128.1.3.21/DMF_VTA_PRD). El script sql/AUDIT_STP_GET_VBFA_TRAMO_FILTRO.sql esta listo.
5. Snapshot actual difiere del historico (1616/360/77,72%): 1907/394/79,34% - normal por ventana movil GETDATE().
6. Pedidos clave 4190139455 y 1167577: cierran por manifiesto, cumplen SLA. OK.
