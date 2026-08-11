# AUDITORÍA LIVE — NS_V50-PowerBI-ML

Este directorio contiene la evidencia histórica y el protocolo vigente de auditoría del modelo Power BI NS.

## Flujo vigente — agosto 2026

La auditoría opera con separación de roles:

- **LLM local:** recupera, inspecciona, prueba, diagnostica y genera evidencia. No implementa fixes.
- **ChatGPT remoto:** consume la evidencia versionada y realiza las modificaciones técnicas sobre el repositorio.

Rama actual de trabajo:

`work/ns-lienzo-02-ingreso-pedidos`

El auditor local debe comenzar por:

1. `LOCAL_LLM_AUDIT_PROTOCOL.md`
2. `local_audit_config.json`
3. `LOCAL_LLM_PROMPT.md`
4. `CURRENT.md`
5. `regression_cases.csv`

Y ejecutar:

```powershell
./Scripts/audit_local/bootstrap_local_audit.ps1
```

Al terminar debe validar:

```powershell
python Scripts/audit_local/validate_local_evidence.py "<RUN_DIR>"
```

## Regla crítica de escritura

El LLM local puede escribir únicamente:

```text
Docs/AUDITORIA_LIVE/local_runs/<RUN_ID>/**
Docs/AUDITORIA_LIVE/LOCAL_LATEST.json
```

No debe modificar `NS.SemanticModel`, `NS.Report`, `NS.pbip`, scripts funcionales, el dictamen oficial ni código de negocio.

Si encuentra un error, lo documenta con ruta, objeto, evidencia, impacto y fix recomendado. La implementación se realiza posteriormente desde el entorno remoto.

---

## Estructura actual

```text
Docs/AUDITORIA_LIVE/
├── README.md
├── CURRENT.md
├── LOCAL_LLM_AUDIT_PROTOCOL.md
├── LOCAL_LLM_PROMPT.md
├── local_audit_config.json
├── LOCAL_LATEST.json
├── manifest.json
├── regression_cases.csv
├── local_runs/
│   └── YYYYMMDD_HHMMSS_auditoria_integral_SHA7/
│       ├── 00_manifest.json
│       ├── 01_git_state.txt
│       ├── 02_environment.txt
│       ├── 03_model_inventory.csv
│       ├── 04_code_findings.csv
│       ├── 05_business_rule_matrix.csv
│       ├── 06_live_queries.md
│       ├── 07_live_results.csv
│       ├── 08_regression_cases_results.csv
│       ├── 09_inc_status.csv
│       ├── 10_visual_bindings.csv
│       ├── 11_data_quality.csv
│       ├── 12_recommendations.csv
│       ├── READY_FOR_CHATGPT.md
│       ├── RESULTADO.md
│       └── raw/
├── runs/
│   └── ... auditorías históricas versionadas ...
└── latest/
    └── ... artefactos históricos del flujo anterior ...
```

## Qué es autoritativo

Para una nueva corrida local:

- `LOCAL_LATEST.json` indica el último paquete local disponible.
- `local_audit_config.json` define permisos, baseline y preguntas prioritarias.
- `LOCAL_LLM_AUDIT_PROTOCOL.md` define el método.
- `CURRENT.md` resume el estado de handoff actual.

`manifest.json` y `latest/` contienen historial del flujo anterior y **no deben usarse como SHA actual sin verificar Git**.

---

## Reglas de negocio que siempre deben revalidarse

- Universo Mayorista: canales 42–47.
- Clasificación exclusiva: NORMAL / FES / SALDO / FES+SALDO.
- NORMAL/SALDO: cierre por despacho válido.
- FES/FES+SALDO: regla de negocio esperada de cierre por manifiesto oficial VBFA/VTTP; verificar implementación real de `Fact_Tracking`.
- SLA interno: Santiago 4 DH / Regiones 5 DH.
- Operación: Santiago 3 DH / Regiones 4 DH.
- Promesa cliente: Santiago 5 DH / Regiones 7 DH.
- Multiselect de flujo/zona debe conservar el conjunto seleccionado, no abrir el universo.
- Corte de ingreso 14:00 L–J / 12:00 viernes: actualmente debe demostrarse si afecta preparación/promesa o NS.
- Corte 14:30 lienzo 02: análisis de carga, no SLA.
- Líneas/unidades: validar cobertura real VBAP/TREATAS.

No asumir que `regression_cases.csv` sigue siendo correcto: cada fila es una expectativa histórica que debe contrastarse contra código y datos actuales.

---

## Pendientes prioritarios para el próximo auditor local

1. `INC-011`: explicar y listar exactamente la diferencia de denominadores U vs RE.
2. `INC-015`: cuantificar cobertura VBAP y efecto en líneas/unidades.
3. `INC-007B`: confirmar fallback TRP en `FECHA_MANIFIESTO` y cuantificar impacto actual.
4. `INC-013`: determinar si feriados regionales generan impacto medible o requieren fuente/regla adicional.
5. Ejecutar regresión de los INC actualmente verdes y detectar problemas nuevos.

El resultado final debe quedar resumido en `READY_FOR_CHATGPT.md` para consumo remoto directo.
