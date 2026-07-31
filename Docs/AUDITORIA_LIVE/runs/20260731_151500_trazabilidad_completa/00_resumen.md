# RUN 2026-07-31 15:11 - Trazabilidad completa SQL a visual

## Rama: work/ns-lineage-audit
## HEAD: 5965551c8743d8245310727a228a3a77fb8feff7

## Ejecutado
1. Auditor estatico: python tools/build_ns_lineage.py --strict -> AMARILLO
2. Columnas Fact_Pedidos_Auditoria: 181 (87 CONSERVAR + 94 NO_BORRAR_SIN_PRUEBA_CONTRATO)
3. Modelo vivo MCP: snapshot 1907/394/79,34%/265 (4/36/225)
4. Pedidos clave: 4190139455 OK, 1167577 OK

## Pendiente
- Procedimiento VBFA: requiere ejecucion en SQL Server 128.1.3.21/DMF_VTA_PRD (sin acceso directo)
- Python contract: esquema Resultado exportado (86 columnas)
