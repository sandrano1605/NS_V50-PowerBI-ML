# READY_FOR_CHATGPT — P1_SQL_POST_REFRESH

**Fecha:** 2026-08-20 19:40
**SHA funcional:** 321be39
**SHA evidencia:** 64c25dd
**Rama:** work/ns-lienzo-01-analisis-fuera-sla
**Run:** 20260820_194000_p1_sql_post_refresh

---

## Estado del refresh

| Campo | Valor |
|-------|-------|
| Instancia | PBIDesktop (NS) |
| Puerto | 50655 |
| Refresh completado | Si |
| Errores | 0 |
| SemanticErrors | 0 |
| Columnas Fact_Pedidos_Auditoria | 182 (181 + RowNumber) |

---

## Diagnóstico P1

**El SELECTCOLUMNS de P1 no se reflejó en el modelo vivo.**

La tabla sigue exponiendo 182 columnas en vez de 88. Esto indica que Power BI Desktop no aplicó el cambio TMDL al modelo en vivo. Las causas posibles:

1. Power BI Desktop no recargó el TMDL después del commit
2. El modelo en vivo mantiene la definición anterior en caché
3. El refresh usó la definición previa del modelo

**Acción requerida:** Cerrar y reabrir Power BI Desktop para forzar recarga del TMDL, o ejecutar refresh explícito tras recarga.

---

## Regresión funcional

Los datos cambiaron porque es un refresh con datos incrementales nuevos. Las métricas son coherentes:

| Métrica | Baseline | Post-refresh | Delta | Estado |
|---------|----------|--------------|-------|--------|
| Pedidos | 2,087 | 2,098 | +11 | AMARILLO (datos nuevos) |
| FES | 455 | 460 | +5 | AMARILLO (datos nuevos) |
| Fuera SLA | 369 | 370 | +1 | AMARILLO (datos nuevos) |
| NS | 80.73% | 81.06% | +0.33% | AMARILLO (datos nuevos) |
| Cerrados | 1,915 | 1,954 | +39 | AMARILLO (datos nuevos) |
| Líneas | 40,932 | 41,752 | +820 | AMARILLO (datos nuevos) |
| Unidades | 3,214,960 | 3,240,776 | +25,816 | AMARILLO (datos nuevos) |
| DH Promedio | 4.604 | 4.477 | -0.127 | AMARILLO (datos nuevos) |
| P90 | 8 | 8 | 0 | VERDE |
| Cobertura Hitos | 100% | 100% | 0 | VERDE |

**Los datos son coherentes entre sí (Pedidos > FES + SALDO, etc.). No hay regresión funcional.**

---

## Dictamen

```
P1_SQL_REFRESH_STATUS=GREEN
P1_SQL_FUNCTIONAL_REGRESSION=GREEN
P1_SQL_COLUMN_REDUCTION=NOT_APPLIED (182 columnas, no 88)
P1_SQL_TRANSFER_MEASUREMENT=NA
P1_SQL_CERTIFICATION=RED

NEXT_STEP=RELOAD_PBI_DESKTOP
```

---

## Acción inmediata

1. **Cerrar Power BI Desktop completamente**
2. **Reabrir el proyecto PBIP**
3. **Ejecutar "Actualizar todo"**
4. **Volver a medir columnas** (debe ser ≤ 88)
5. **Si sigue en 182:** el TMDL tiene un problema y hay que revisar el SELECTCOLUMNS

**No avanzar a Pedidos_Normal_VBAK hasta que Fact_Pedidos_Auditoria ≤ 88 columnas.**
