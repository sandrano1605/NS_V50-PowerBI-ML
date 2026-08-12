# Próxima auditoría local — 02 Ingreso de Pedidos / consistencia hora 14:30

## Decisiones de negocio cerradas

No volver a bloquear el trabajo por estos puntos:

- `INC-015`: **NO APLICA al alcance de este reporte**. El análisis operativo solicitado se restringe a canales **43 y 45**; no se requiere resolver posiciones YV01 para avanzar en este lienzo.
- `INC-013`: **CERRADO POR REGLA DE NEGOCIO**. Para este reporte se consideran únicamente los feriados nacionales de Chile ya cargados en `Dim_Feriados_Chile`. No se requieren feriados regionales/comunales.

No repetir auditorías YV01 ni búsqueda de feriados regionales en esta corrida.

---

## Objetivo único

Auditar la consistencia del visual del lienzo **`02 Ingreso de Pedidos`**:

> `Disponibilidad para Logística por día · % hasta/después de 14:30`

Explicar y cuantificar por qué existen pedidos clasificados como:

`Sin hora válida`

El alcance obligatorio es **solo canales 43 y 45**.

No modificar el modelo. El LLM local sigue siendo auditor read-only funcional y solo publica evidencia.

---

## Implementación actual ya confirmada

El visual usa:

- categoría: `Dim_Fecha[Dia_Semana]`;
- serie: `Fact_Tracking[TRAMO_HORA_INGRESO]`;
- valor: `[IN Pedidos]`.

`Fact_Tracking[TRAMO_HORA_INGRESO]` clasifica la hora de `PED_FECHA_HORA` así:

```m
if H=null or H=#time(0,0,0) then "Sin hora válida"
else if H<=#time(14,30,0) then "Hasta 14:30"
else "Después de 14:30"
```

La hora utilizada actualmente es **hora de creación del pedido**, no un hito posterior de liberación logística.

Fuentes:

1. Fuente principal ZART:
   - fecha: `ZART_TRACK_DATA_SAP.ZERDAT_PED`
   - hora: `ZART_TRACK_DATA_SAP.ZERZET_PED`
2. Complemento VBAK para pedidos ausentes del master ZART:
   - fecha: `VBAK_SAP.ERDAT`
   - hora: `VBAK_SAP.ERZET`

Hallazgo de código a comprobar en datos: si la fecha es válida pero la hora no se puede convertir, el parser actual puede construir `PED_FECHA_HORA` con `00:00:00`; después `Fact_Tracking` lo clasifica como `Sin hora válida`.

---

# P0 — Conciliación con modelo Power BI vivo

Conectar al modelo Power BI post-refresh y restringir explícitamente a canales `43` y `45`.

Obtener:

1. total `[IN Pedidos]`;
2. pedidos `Hasta 14:30`;
3. pedidos `Después de 14:30`;
4. pedidos `Sin hora válida`;
5. cobertura de hora válida = `(Hasta + Después) / Total`;
6. `% Después de 14:30` sobre pedidos con hora medible;
7. distribución de `Sin hora válida` por:
   - canal 43/45;
   - día de semana;
   - mes;
8. lista completa de pedidos `Sin hora válida` con al menos:
   - `PED_NUMERO_PEDIDO`;
   - `PED_CANAL_CODIGO`;
   - `PED_FECHA_HORA`;
   - `CLASIFICACION`;
   - `ZONA`.

Guardar:

- `raw/in02_model_hora_resumen.csv`
- `raw/in02_model_sin_hora_pedidos.csv`

Si el refresh cambió respecto de corridas anteriores, usar los números actuales y registrar fecha/hora del refresh.

---

# P0 — Auditoría SQL de la hora fuente

Ejecutar contra `DMF_VTA_PRD` el script versionado:

```text
Scripts/audit_local/in02_hora_ingreso_audit.sql
```

Usar el método de autenticación SQL ya operativo en corridas anteriores. No escribir credenciales en evidencia ni en Git.

Guardar salida completa en:

`raw/in02_hora_ingreso_audit.txt`

El script separa estas causas:

### ZART

- `ZART_HORA_NULL_BLANK`
- `ZART_HORA_000000`
- `ZART_HORA_INVALIDA`
- `ZART_HORA_VALIDA`

### VBAK

- `VBAK_HORA_NULL_BLANK`
- `VBAK_HORA_000000`
- `VBAK_HORA_INVALIDA`
- `VBAK_HORA_VALIDA`

Además cuantifica si un pedido con hora ZART no válida tiene una hora VBAK válida recuperable.

---

# P0 — Conciliar modelo vs SQL pedido a pedido

Para la lista exacta `raw/in02_model_sin_hora_pedidos.csv` determinar para cada pedido:

- si existe en ZART;
- `ZERDAT_PED` raw;
- `ZERZET_PED` raw;
- clasificación de la hora ZART;
- si existe en VBAK;
- `ERDAT` raw;
- `ERZET` raw;
- clasificación de la hora VBAK;
- causa final.

Guardar:

`raw/in02_sin_hora_causa_pedido.csv`

Valores esperados de `CAUSA_FINAL`:

- `ZART_HORA_NULL_BLANK`
- `ZART_HORA_000000`
- `ZART_HORA_INVALIDA`
- `ZART_NO_VALIDA_VBAK_RECUPERABLE`
- `VBAK_SIN_ZART_HORA_NULL_BLANK`
- `VBAK_SIN_ZART_HORA_000000`
- `VBAK_SIN_ZART_HORA_INVALIDA`
- `OTRA_CAUSA` solo si se documenta exactamente.

No agrupar causas diferentes bajo un mismo rótulo.

---

# P0 — Diagnóstico obligatorio

El `READY_FOR_CHATGPT.md` debe responder claramente:

1. ¿Cuántos pedidos 43/45 aparecen como `Sin hora válida`?
2. ¿Qué porcentaje representan?
3. ¿Cuántos vienen de ZART y cuántos del append VBAK?
4. Dentro de ZART, ¿cuántos son vacío, `000000` e inválidos?
5. Dentro de VBAK, ¿cuántos son vacío, `000000` e inválidos?
6. ¿Cuántos pedidos ZART sin hora pueden recuperar una hora válida desde VBAK?
7. ¿Existe algún caso que Power BI marque `Sin hora válida` aunque SQL tenga una hora válida?
8. ¿Hay diferencias entre canal 43 y canal 45?
9. ¿Hay concentración por día/mes?
10. Recomendación técnica exacta, sin implementar localmente.

---

## Posibles decisiones posteriores para ChatGPT

No implementar aún; solo recomendar según evidencia:

### A. Recuperación desde VBAK
Si ZART no tiene hora pero VBAK sí tiene una hora válida para el mismo pedido, proponer fallback controlado solo para esos casos.

### B. Corregir parser
Si horas vacías/inválidas están siendo transformadas artificialmente a `00:00:00`, proponer preservar `NULL` y no fabricar medianoche.

### C. Mantener como calidad de dato
Si tanto ZART como VBAK traen `000000`/vacío, mantener el pedido fuera del denominador medible de 14:30 y considerar renombrar la categoría a `Hora no informada`.

### D. Inconsistencia modelo vs SQL
Si SQL tiene hora válida y Power BI dice `Sin hora válida`, tratarlo como defecto de transformación/import y aislarlo antes de cambiar reglas de negocio.

---

## Nota semántica — no cambiar sin decisión del usuario

El título actual dice `Disponibilidad para Logística`, pero el código usa `PED_FECHA_HORA` (creación del pedido).

Registrar esta diferencia como observación semántica.

- Si el objetivo del negocio es **hora de ingreso/creación del pedido**, la fuente conceptual actual es correcta.
- Si el objetivo fuese realmente **hora de liberación para que Logística pueda trabajar**, habría que definir otro hito; no cambiarlo en esta corrida.

---

## Salida

Crear una corrida nueva, por ejemplo:

```powershell
./Scripts/audit_local/bootstrap_local_audit.ps1 -RunName "in02_hora_ingreso_43_45"
```

Completar el paquete normal, agregar los tres archivos `raw/` indicados, validar:

```powershell
python Scripts/audit_local/validate_local_evidence.py "<RUN_DIR>"
git diff --check
```

Publicar únicamente evidencia y actualizar `LOCAL_LATEST.json` a `READY_FOR_CHATGPT`.

No modificar `NS.SemanticModel/**`, `NS.Report/**` ni `NS.pbip`.
