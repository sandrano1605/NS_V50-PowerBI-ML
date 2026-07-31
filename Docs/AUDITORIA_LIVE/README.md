# AUDITORIA LIVE — NS_V50-PowerBI-ML

Estructura de auditoría en vivo para el modelo Power BI NS (PBIP).

## Estructura

```text
Docs/AUDITORIA_LIVE/
├── README.md            ← este archivo
├── CURRENT.md           ← estado del último cambio
├── manifest.json        ← manifest de la última ejecución
├── regression_cases.csv ← casos de regresión obligatorios
├── runs/
│   └── YYYYMMDD_HHMMSS_nombre_cambio/
│       ├── 00_resumen.md
│       ├── 01_git_before.txt
│       ├── 02_archivos_modificados.csv
│       ├── 03_medidas_afectadas.csv
│       ├── 04_objetos_visuales_afectados.csv
│       ├── 05_consultas_dax_ejecutadas.md
│       ├── 06_resultados_antes.csv
│       ├── 07_resultados_despues.csv
│       ├── 08_comparacion_antes_despues.csv
│       ├── 09_casos_auditoria.csv
│       ├── 10_validacion_modelo.json
│       ├── 11_validacion_visual.json
│       ├── 12_git_after.txt
│       └── RESULTADO.md
└── latest/
    ├── manifest.json
    ├── RESULTADO.md
    ├── comparacion.csv
    └── casos_auditoria.csv
```

## Protocolo

1. Verificación git inicial (`git status`, remote, branch, log).
2. Rama de trabajo: `work/ns-live-audit` (nunca main).
3. Protección de archivos: `.gitignore` y búsqueda de secretos antes de cada commit.
4. Manifest JSON por ejecución (ver `manifest.json`).
5. Evidencia "antes" completa antes de modificar.
6. Cambio unitario, validación estructural + modelo vivo.
7. Evidencia "después" + comparación.
8. Commit funcional + commit de auditoría separado.
9. Push a `work/ns-live-audit` y verificación por SHA.

## Reglas de negocio vigentes

- Universo: pedidos cerrados y evaluables (equivalente TRACKING TRUE documentado).
- Cierre FES/FES+SALDO = último manifiesto; NORMAL/SALDO = último despacho.
- SLA interno: Santiago 4 DH / Regiones 5 DH.
- Promesa cliente: Santiago 5 DH / Regiones 7 DH.
- Clientes fuera SLA: mostrar todos (>=1 mes); orden 3M → 2M → 1M; luego pedidos y DH.
