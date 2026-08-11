# Estado actual — handoff LLM local → ChatGPT remoto

## Rama

`work/ns-lienzo-02-ingreso-pedidos`

## Regla de SHA

- Último SHA funcional/auditoría antes de preparar este handoff: `352fb33dc65938232a55003b7fe54fc1de61699e`.
- El protocolo y scripts de auditoría se agregaron después de ese SHA.
- **El LLM local debe ejecutar `git rev-parse HEAD` y `git ls-remote` al comenzar. Ese SHA real es el único SHA válido de la corrida.**

## Separación de responsabilidades

### LLM local

Solo:

- recupera implementación actual;
- inspecciona TMDL/M/DAX/JSON/relaciones/visuales;
- consulta el modelo vivo cuando esté disponible;
- diagnostica;
- cuantifica;
- genera y publica evidencia.

No implementa fixes.

### ChatGPT remoto

- recupera `LOCAL_LATEST.json` y `READY_FOR_CHATGPT.md`;
- contrasta evidencia;
- decide con el usuario los puntos de negocio;
- implementa cambios;
- solicita una nueva auditoría local para validación cuando corresponda.

---

# Estado validado antes del próximo run local

| INC | Estado de referencia | Próxima acción local |
|---|---|---|
| INC-005 | 🟢 Multiselect RE validado | regresión |
| INC-006 | 🟢 Corte afecta preparación/promesa, impacto corte→NS = 0 | revalidar código actual |
| INC-007A | 🟢 0 FES cerrados sin manifiesto real en datos auditados | recontar |
| INC-007B | 🔴 Fallback TRP estructural en `FECHA_MANIFIESTO` | confirmar + cuantificar impacto actual |
| INC-008 | 🟢/doc corregida | revalidar implementación |
| INC-009 | 🟢 14 medidas FA multiselect en prueba viva | regresión |
| INC-010 | 🟢 cubierto por INC-005 | regresión |
| INC-011 | 🟠 U vs RE: 1.962 vs 1.898 en auditoría previa | explicar pedidos exactos y causa |
| INC-012 | 🟢 SLA legacy 5 DH fuera de visuales NS oficiales | confirmar bindings |
| INC-013 | 🟠 feriados regionales no resueltos | medir o marcar necesidad de datos/regla |
| INC-014 | 🟢 14:30 = análisis carga | confirmar que ningún KPI SLA lo usa |
| INC-015 | 🟠 cobertura VBAP no cuantificada | cuantificar cobertura y efecto |

---

# Números de referencia a NO asumir sin revalidar

Auditoría previa:

- total fuente: 2.048 pedidos;
- cerrados evaluables RE: 1.898;
- en SLA: 1.547;
- fuera SLA: 351;
- RE NS: 81,5%;
- U cerrados: 1.962;
- U NS observado: 78,8%;
- diferencia histórica de denominador: 64 pedidos;
- diferidos por corte en Hitos: 946;
- FES cerrados con manifiesto real: 437;
- FES cerrados solo por TRP en datos auditados: 0.

Estos números son **baseline de comparación**, no resultado garantizado de la nueva corrida.

---

# Evidencia reciente relevante

- `runs/20260810_232706_auditoria_integral_modelo_lienzos/05_sla_reloj_actual_vs_corte.csv`
- `runs/20260810_232706_auditoria_integral_modelo_lienzos/08_multiselect_lienzo00.csv`
- `runs/20260810_232706_auditoria_integral_modelo_lienzos/10_multiselect_lienzo01_fa_fix.csv`
- `runs/20260810_232706_auditoria_integral_modelo_lienzos/13_medidas_u_vs_re.csv`
- `runs/20260810_232706_auditoria_integral_modelo_lienzos/15_incoherencias.csv`
- `runs/20260810_232706_auditoria_integral_modelo_lienzos/DICTAMEN.md`

## Commits de referencia

- `abc5de3382b774046787e90b07dbdc2f50b0896e` — prueba viva multiselect FA / INC-009 verde.
- `352fb33dc65938232a55003b7fe54fc1de61699e` — reevaluación INC-006 y actualización del dictamen.

---

# Inicio de la próxima auditoría local

El LLM local debe leer:

1. `Docs/AUDITORIA_LIVE/LOCAL_LLM_AUDIT_PROTOCOL.md`
2. `Docs/AUDITORIA_LIVE/local_audit_config.json`
3. `Docs/AUDITORIA_LIVE/LOCAL_LLM_PROMPT.md`
4. este archivo;
5. `regression_cases.csv` como expectativa histórica, no como verdad.

Luego:

```powershell
./Scripts/audit_local/bootstrap_local_audit.ps1
```

Y al finalizar:

```powershell
python Scripts/audit_local/validate_local_evidence.py "<RUN_DIR>"
```

El paquete solo está listo para implementación remota cuando `LOCAL_LATEST.json` apunte a una corrida con estado `READY_FOR_CHATGPT` y la evidencia haya sido publicada sin cambios funcionales.
