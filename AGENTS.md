# AGENTS.md — Instrucciones maestras para agentes en NS_V50-PowerBI-ML

## Identidad y rol

Actúa como ingeniero senior de Power BI PBIP, modelo tabular, DAX, Power Query, Python, Git y auditoría técnica.

## Proyecto

- Proyecto local: `C:\Users\alonso.moya\OneDrive - ARTEL S.A\Escritorio\💼 Proyectos\Modelo datos power BI\NS\NS_V50_v15_Error_Python_ndarray_Corregido\NS_V50`
- Repositorio remoto oficial: `https://github.com/sandrano1605/NS_V50-PowerBI-ML.git`
- GitHub: `sandrano1605/NS_V50-PowerBI-ML`

## Objetivo general

Trabajar de manera iterativa sobre el modelo Power BI NS, utilizando:

- archivos PBIP locales;
- MCP del modelo semántico en vivo;
- consultas DAX;
- metadata TMDL;
- resultados reales de los visuales;
- auditoría exportada a CSV/JSON/Markdown;
- Git para control de cambios.

Cada modificación debe quedar:

1. Implementada en el PBIP.
2. Validada estructuralmente.
3. Validada contra el modelo vivo.
4. Documentada con evidencia.
5. Registrada en un commit pequeño.
6. Publicada mediante push.
7. Preparada para auditoría externa por SHA.

No realices varios cambios de negocio independientes en un mismo commit.

---

## 1. Verificación inicial de Git

Abre una terminal en la raíz del proyecto y registra la salida:

```bash
git status
git rev-parse --show-toplevel
git remote -v
git branch --show-current
git log --oneline -10
```

- No ejecutes `git init` si ya existe un repositorio.
- Si la carpeta no está asociada al remoto correcto:
  - `git remote remove origin` (solo si `origin` existe y es incorrecto)
  - `git remote add origin https://github.com/sandrano1605/NS_V50-PowerBI-ML.git`
  - `git fetch origin`
- No sobrescribas archivos ni ejecutes reset, checkout forzado o clean sin documentar previamente el estado local.

## 2. Rama de trabajo

- Trabaja siempre en la rama `work/ns-live-audit`.
- Si no existe: `git switch -c work/ns-live-audit`
- Si existe localmente: `git switch work/ns-live-audit`
- Si existe solo en remoto: `git switch --track origin/work/ns-live-audit`
- Nunca trabajar directamente sobre `main`.
- Publicar la rama: `git push -u origin work/ns-live-audit`

## 3. Protección de archivos

Antes del primer commit, revisar `.gitignore`. No subir:

- credenciales, claves API, contraseñas;
- cadenas de conexión con secretos;
- archivos temporales de Power BI, cachés, archivos locales personales;
- `.pbi/localSettings.json`, archivos `.abf`;
- temporales de Python, `__pycache__`, `.venv`, archivos de bloqueo;
- copias completas repetidas del PBIP;
- datos confidenciales sin anonimizar.

Añadir como mínimo a `.gitignore` si corresponde:

```gitignore
.pbi/localSettings.json
**/.pbi/cache.abf
**/*.abf
**/__pycache__/
**/*.pyc
.venv/
venv/
*.tmp
*.bak
~$*
.DS_Store
Thumbs.db
```

No eliminar reglas existentes sin justificarlo.

Antes de cada commit ejecutar:

```bash
git status --short
git diff --check
```

Buscar secretos en los archivos modificados: `sk-`, `api_key`, `password`, `contraseña`, `pwd=`, `token`, `bearer`, `connectionString`. Si aparece un secreto, detenerse y no hacer commit.

## 4. Estructura de auditoría

Crear dentro del proyecto `Docs/AUDITORIA_LIVE/`:

```text
Docs/AUDITORIA_LIVE/
├── README.md
├── CURRENT.md
├── manifest.json
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

`latest` debe contener una copia pequeña de la evidencia más reciente. No copiar allí todo el historial.

## 5. Manifest de cada ejecución

Cada auditoría debe crear un `manifest.json` con este esquema:

```json
{
  "project": "NS_V50-PowerBI-ML",
  "run_id": "YYYYMMDD_HHMMSS_nombre_cambio",
  "timestamp_local": "ISO-8601",
  "branch": "work/ns-live-audit",
  "base_commit": "<SHA antes del cambio>",
  "result_commit": "<SHA después del commit o PENDING>",
  "power_bi_model": "NS",
  "pbip_path": "NS.pbip",
  "model_live_access": true,
  "mcp_connected": true,
  "refresh_executed": true,
  "refresh_result": "OK|ERROR|PARCIAL",
  "structural_validation": "OK|ERROR",
  "semantic_validation": "OK|ERROR",
  "visual_validation": "OK|ERROR",
  "business_rule_validation": "OK|ERROR",
  "status": "VERDE|AMARILLO|ROJO",
  "changed_files": [],
  "changed_measures": [],
  "changed_visuals": [],
  "executed_dax_queries": [],
  "known_limitations": [],
  "critical_findings": []
}
```

Después del commit, actualizar `result_commit` con el SHA real.

## 6. Protocolo antes de modificar

Antes de cualquier modificación:

1. Comprobar que Power BI Desktop tiene abierto el PBIP correcto.
2. Conectar el MCP al modelo semántico activo.
3. Identificar: nombre del modelo, puerto local, tablas, medidas, relaciones, páginas, visuales afectados.
4. Exportar resultado actual del visual afectado.
5. Exportar medidas involucradas.
6. Exportar casos de prueba.
7. Guardar `git status` y SHA inicial.
8. Crear carpeta de run.
9. No modificar hasta completar la evidencia "antes".

Registrar en `01_git_before.txt`:

```bash
git status
git branch --show-current
git rev-parse HEAD
git log -1 --stat
```

## 7. Protocolo de cambio

Para cada requerimiento:

- A. Crear una sola unidad de trabajo. Ejemplos correctos: corregir visual de clientes fuera SLA; corregir cierre FES; modificar SLA zonal; corregir consulta Python; alinear tarjetas de un lienzo. No combinar esas tareas en un solo commit.
- B. Identificar dependencias (medidas DAX, columnas, relaciones, consultas Power Query, scripts Python, visuales, SVG, tooltips, filtros, drillthrough, parámetros).
- C. Modificar los archivos PBIP.
- D. Validar sintaxis: JSON válido, TMDL válido, expresiones DAX reconocibles, Power Query sin error, Python compilable, referencias existentes, lineageTag sin duplicados.
- E. Abrir o recargar el PBIP.
- F. Ejecutar `Actualizar todo`.
- G. Verificar el modelo en vivo mediante MCP.
- H. Exportar la evidencia "después".

## 8. Validación del modelo vivo

No validar solamente leyendo archivos PBIP. Debe consultarse el modelo cargado en Power BI Desktop mediante MCP. Validar: conteos, medidas, filtros, contexto, casos específicos, resultado exacto de visuales, coherencia entre lienzos.

Para cada medida modificada exportar:

```text
MEDIDA
EXPRESION_DAX
RESULTADO_ANTES
RESULTADO_DESPUES
RESULTADO_RECALCULADO
DIFERENCIA
ESTADO
OBSERVACION
```

No usar una medida dependiente para validar la medida original. Recalcular desde columnas base cuando sea posible.

## 9. Reglas de negocio actuales

**Universo histórico:**

- Todos los flujos.
- Solo pedidos cerrados y evaluables.
- La definición analítica equivalente a TRACKING TRUE debe quedar documentada explícitamente.
- No mezclar pedidos abiertos con NS histórico.

**Cierre:**

- FES y FES + SALDO: último manifiesto.
- NORMAL: último despacho válido.
- SALDO: último despacho de cierre total.

**SLA interno:**

- Santiago: 4 DH.
- Regiones: 5 DH.

**Promesa cliente:**

- Santiago: 5 DH.
- Regiones: 7 DH.

**Composición:**

- Santiago: 1 administración + 3 operación + 1 última milla.
- Regiones: 1 administración + 4 operación + 2 última milla.

**Clientes fuera SLA:**

- Mostrar todos los clientes con al menos un mes fuera SLA.
- Recurrente 3M: 3 meses. Recurrente 2M: 2 meses. Puntual 1M: 1 mes.
- Orden principal: meses fuera SLA descendente.
- Orden secundario: pedidos fuera SLA descendente.
- Orden terciario: promedio DH fuera SLA descendente.

## 10. Casos de regresión obligatorios

Mantener siempre `Docs/AUDITORIA_LIVE/regression_cases.csv`. Debe incluir como mínimo: `4190139455`, `1167577`, y casos adicionales:

- FES cerrado; FES sin manifiesto; NORMAL cerrado; SALDO cerrado; FES + SALDO cerrado;
- Santiago exactamente 4 DH; Santiago 5 DH; Regiones exactamente 5 DH; Regiones 6 DH;
- factura y manifiesto el mismo día; primer y último transporte diferentes;
- pedido con múltiples facturas; pedido con múltiples despachos.

Columnas:

```text
PEDIDO
CASO
FLUJO_ESPERADO
ZONA_ESPERADA
CIERRE_ESPERADO
SLA_ESPERADO
CUMPLE_ESPERADO
FUENTE_CIERRE_ESPERADA
ACTIVO
```

Cada cambio debe volver a ejecutar todos los casos activos.

## 11. Evidencia rápida para auditoría externa

`Docs/AUDITORIA_LIVE/CURRENT.md` debe permitir que otro auditor comprenda rápidamente el último cambio. Formato:

```markdown
# Estado actual
- Rama:
- Commit:
- Fecha:
- Requerimiento:
- Estado:
- Refresh:
- Modelo vivo:
- Archivos modificados:

# Qué cambió
# Qué no cambió
# Medidas afectadas
# Visuales afectados
# Casos probados
# Resultados antes y después
# Riesgos pendientes
# Archivos de evidencia
# Instrucción para reproducir
```

Además crear `Docs/AUDITORIA_LIVE/latest/comparacion.csv`:

```text
OBJETO
METRICA
ANTES
DESPUES
ESPERADO
DIFERENCIA
ESTADO
EVIDENCIA
```

Y `Docs/AUDITORIA_LIVE/latest/casos_auditoria.csv`:

```text
PEDIDO
FLUJO
ZONA
FECHA_CREACION
FACTURA
DESPACHO
MANIFIESTO
CIERRE
DIAS_DH
SLA_DH
CUMPLE
RESULTADO_ESPERADO
COINCIDE
OBSERVACION
```

## 12. Commit

Solo hacer commit si: refresh finalizó; no hay errores de Power Query; no hay error Python; TMDL válido; JSON válido; casos de regresión ejecutados; evidencia generada; `CURRENT.md` actualizado; `manifest.json` actualizado; no existen secretos.

Formato obligatorio del commit:

```text
tipo(área): descripción breve
```

Tipos: `fix`, `feat`, `refactor`, `audit`, `docs`, `test`, `chore`.

Ejemplos válidos:

```text
fix(lienzo-01): incluir clientes fuera SLA de 1 a 3 meses
fix(fes): usar último manifiesto como cierre oficial
fix(python): alinear Series de SLA con índice del dataframe
audit(modelo): registrar validación viva posterior al cambio
```

No usar mensajes genéricos como: cambios, actualización, arreglos, versión nueva.

Antes del commit:

```bash
git diff --stat
git diff --check
git status --short
```

Commit:

```bash
git add NS.Report NS.SemanticModel Docs/AUDITORIA_LIVE
git add .gitignore
git commit -m "fix(lienzo-01): incluir clientes fuera SLA de 1 a 3 meses"
```

No agregar archivos no relacionados. Después:

```bash
git rev-parse HEAD
git show --stat --oneline HEAD
git status --short
```

Guardar esto en `12_git_after.txt`. Actualizar el manifest con el SHA final. Si actualizar el manifest produce un segundo cambio, realizar un commit de auditoría separado:

```bash
git add Docs/AUDITORIA_LIVE
git commit -m "audit(lienzo-01): registrar evidencia del cambio"
```

## 13. Push

Después de validar:

```bash
git push origin work/ns-live-audit
git ls-remote origin refs/heads/work/ns-live-audit
```

Entregar siempre: repositorio, rama, SHA, mensaje del commit, lista de archivos modificados, ruta de la evidencia, resultado del refresh, estado VERDE/AMARILLO/ROJO.

Formato final de respuesta:

```text
REPOSITORIO:
sandrano1605/NS_V50-PowerBI-ML

RAMA:
work/ns-live-audit

COMMIT:
<SHA completo>

COMMIT CORTO:
<SHA 7 caracteres>

MENSAJE:
<mensaje>

REFRESH:
OK|ERROR

ESTADO:
VERDE|AMARILLO|ROJO

EVIDENCIA:
Docs/AUDITORIA_LIVE/runs/<run_id>/

ARCHIVOS MODIFICADOS:
...

HALLAZGOS:
...

LIMITACIONES:
...
```

## 14. Primer trabajo a realizar (ya aplicado y pendiente de commit)

Visual: CLIENTES QUE REPITEN FUERA SLA

Requerimiento:

1. Mostrar todos los clientes que estuvieron fuera SLA al menos una vez durante los últimos 3 meses.
2. Cambiar las cinco medidas Visible para que utilicen `[FA Meses Fuera SLA Cliente] >= 1`.
3. Dejar de excluir a los clientes Puntual 1M.
4. Ordenar por: meses fuera SLA descendente; pedidos fuera SLA descendente; promedio DH fuera SLA descendente.
5. Actualizar el título a: `CLIENTES FUERA SLA · FRECUENCIA EN LOS ÚLTIMOS 3 MESES`.
6. Actualizar el subtítulo a: `Recurrente 3M → Recurrente 2M → Puntual 1M`.
7. Mantener cliente, vendedor y flujo.
8. No cambiar la cohorte de los lienzos 00 y 01.
9. No cambiar el SLA.
10. No cambiar la lógica de cierre FES.

Resultados esperados del modelo vivo:

- Recurrente 3M: 3 clientes.
- Recurrente 2M: 27 clientes.
- Puntual 1M: 221 clientes.
- Total de clientes fuera SLA: 251.
- Pedidos evaluados: 1.616.
- Pedidos fuera SLA: 360.
- NS: 77,72%.
- Diferencia entre lienzo 00 y lienzo 01: 0.

Si cualquiera de estos resultados cambia sin explicación, marcar el run como ROJO y no hacer push del cambio funcional. Sí se puede hacer un commit de auditoría para documentar el fallo, pero no publicar como correcto el cambio funcional.
