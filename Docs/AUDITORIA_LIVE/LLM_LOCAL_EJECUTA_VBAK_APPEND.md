# LLM local · Validación del cruce VBAK ya integrado

ChatGPT ya dejó el cruce activo dentro de `Fact_Pedidos_Auditoria`. No debes crear consultas, parámetros, pegar bloques ni editar TMDL.

## Recuperación

```powershell
git fetch origin
git switch work/ns-vbak-master-append
git pull --ff-only origin work/ns-vbak-master-append
git status --short
git rev-parse HEAD
python tools/validate_vbak_append_kit.py
```

El repositorio debe quedar limpio y el validador debe devolver `status = VERDE`.

## Trabajo único permitido

1. Abrir `NS.pbip`.
2. Ejecutar `Actualizar todo`.
3. Conectar MCP al modelo vivo.
4. Comprobar el cruce ya existente.
5. Generar evidencia.
6. No corregir el modelo.

## Qué está integrado

- anti-join por pedido normalizado;
- ventana móvil de tres meses;
- pedidos de clases `ZEDI`, `ZMAY`, `ZMAN`, `ZPDA`, `ZVGF`, `ZREL`, `ZVGM`, `ZTAN`, `TAN`;
- canales 42–47;
- atributos de VBAK y región/ciudad de KNA1;
- exclusión FES por flujo VBFA `C→C` y por `fecha_fes`;
- cliente, región y fecha de pedido obligatorios;
- secuencia pedido → entrega → factura → salida validada;
- marcador `PED_TEXTO_ESTADO = VBAK SIN ZART`;
- filas agregadas con `AUD_ESTADO_GENERAL = REVISAR` y `AUD_REQUIERE_REVISION = true`.

## Validaciones obligatorias

No usar `1.973` como total fijo: era un snapshot histórico. La fuente usa `GETDATE()` y la ventana cambia diariamente.

En el mismo refresh registrar:

- `MASTER_TOTAL`;
- `VBAK_APPEND_FILAS` = filas con `PED_TEXTO_ESTADO = "VBAK SIN ZART"`;
- `MASTER_ORIGINAL_ACTUAL = MASTER_TOTAL - VBAK_APPEND_FILAS`;
- duplicados por `PED_NUMERO_PEDIDO` = 0;
- claves nulas en filas VBAK = 0;
- canales fuera de 42–47 = 0;
- regiones nulas = 0;
- `ES_FES = true` en filas VBAK = 0;
- `ES_SALDO = true` en filas VBAK = 0;
- salida sin factura = 0;
- todas las filas VBAK marcadas `REVISAR`;
- `Fact_Tracking`, `Fact_Pedidos`, `Fact_Tiempos_Hitos`, `Fact_Hitos_Operacionales` y `Resultado` refrescan sin error;
- Python ejecuta sin error;
- pedidos `4190139455` y `1167577` no presentan regresión;
- páginas 00, 01 y 01.1 abren y muestran datos.

## Evidencia

Crear solamente:

```text
Docs/AUDITORIA_LIVE/runs/<timestamp>_vbak_master_inline_live/
├── 00_git.txt
├── 01_refresh.txt
├── 02_conteos_master.csv
├── 03_filas_vbak.csv
├── 04_controles_calidad.csv
├── 05_tablas_derivadas.csv
├── 06_pedidos_clave.csv
├── 07_smoke_visual.txt
├── RESULTADO.md
└── manifest.json
```

Si el refresh falla, registrar el mensaje exacto y detenerse. No modificar DAX, M, TMDL, relaciones, Python ni visuales.

Commit permitido:

```text
audit(vbak): validar cruce inline en modelo vivo
```
