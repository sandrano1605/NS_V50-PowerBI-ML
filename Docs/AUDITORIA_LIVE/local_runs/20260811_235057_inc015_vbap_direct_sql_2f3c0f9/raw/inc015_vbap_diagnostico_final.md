# INC-015 — DIAGNÓSTICO SQL DIRECTO (COMPLETO)

## Ejecución
- Servidor: 128.1.3.21 · Base: DMF_VTA_PRD
- Usuario: A_MOYA (SQL auth, vía pyodbc + ODBC Driver 17)
- Fecha: 2026-08-11

---

## 1. Naturaleza de VBAP_SAP

**VBAP_SAP es una USER_TABLE (tabla física)**, tipo `U`, creada el `2024-04-15`.
- **No es** una vista (VIEW).
- **No es** un sinónimo (SYNONYM).
- **No tiene** definición en `sql_modules` (consistente con tabla física).
- **No tiene** dependencias registradas en `sys.sql_expression_dependencies`.
- **dbo.VBAP NO existe** — no hay tabla base alternativa.

→ Diagnóstico: `VBAP_SAP_ES_TABLA_REPLICADA_INCOMPLETA`.

---

## 2. Cobertura VBAK_SAP → VBAP_SAP

| Métrica | Valor |
|---|---|
| Headers VBAK_SAP (ERDAT ≥ GETDATE()-90) | **366.091** |
| Headers con posiciones en VBAP_SAP (AEDAT ≥ GETDATE()-730) | **1.524** |
| **Cobertura global** | **0,42%** |

---

## 3. Gap por AUART (del universo VBAK últimos 90 días)

| AUART | Headers VBAK | En VBAP_SAP | % |
|---|---|---|---|
| **YV01** | **349.215** | **0** | **0,00%** |
| YV03 | 11.156 | 11 | 0,10% |
| YD01 | 1.715 | 0 | 0,00% |
| ZMAY | 1.009 | 664 | 65,81% |
| ZPDA | 981 | 466 | 47,50% |
| ZPPO | 875 | 1 | 0,11% |
| YPA | 219 | 173 | 79,00% |
| ZYPA | 218 | 0 | 0,00% |
| YPP | 174 | 17 | 9,77% |
| ZYPP | 159 | 1 | 0,63% |
| ZVGM | 124 | 91 | 73,39% |
| YPB | 92 | 25 | 27,17% |
| ZYPB | 87 | 74 | 85,06% |
| Otros | 67 | 1 | ~1,5% |

---

## 4. Diagnóstico final

**CAUSA: YV01_EXCLUIDO_DE_VBAP_SAP**

- `YV01` representa **95,4% de los headers VBAK** en los últimos 90 días (349.215 de 366.091).
- `VBAP_SAP` tiene **0 posiciones YV01**.
- El universo Mayorista del modelo Power BI (canales 42-47) se alimenta predominantemente de pedidos YV01.
- Las posiciones que SÍ están en VBAP_SAP corresponden a otros AUART (ZMAY, ZPDA, YPA, ZVGM, etc.) que tienen coberturas entre 47% y 85%.
- Esto explica la cobertura de **58,3%** en el modelo Power BI: los ~1.131 pedidos con match son de los AUART que VBAP_SAP sí cubre (ZMAY/ZPDA/etc.), y los ~810 sin match son YV01 y otros AUART sin cobertura.

## 5. Recomendación para ChatGPT

1. **No modificar VBAP_SAP** — es una tabla replicada con exclusión deliberada de YV01 (posiblemente por volumen o propósito específico).
2. **Buscar fuente alternativa de posiciones YV01**:
   - Si existe `VBAP` en otra base o schema (no en `dbo` de `DMF_VTA_PRD`), usarla.
   - Si la fuente SAP estándar `VBAP` es accesible vía RFC/BW, crear una vista que la exponga.
   - Si los pedidos YV01 tienen sus líneas en otra tabla (ej. `VBAP_YV01`), documentarla.
3. **Alternativa inmediata**: usar `Pedidos_Normal_VBAK` para las cabeceras y cruzar con la fuente de posiciones que corresponda para YV01.
