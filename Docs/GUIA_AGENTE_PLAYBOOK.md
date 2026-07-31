# 📘 NS V50 — Guía del Proyecto para Agentes

## 🎯 Objetivo del Proyecto

Dashboard ejecutivo **NS V50** para monitorear el **Nivel de Servicio (NS)** del canal Mayorista (canales 42-47) de ARTEL S.A.
Mide el flujo completo desde creación del pedido hasta despacho (NORMAL) o manifiesto (FES).

**Pregunta de negocio principal:** ¿Estamos cumpliendo el SLA interno de 5 DH?

---

## 🧠 Contexto para el Agente

### Proyectos activos (2 rutas)
| Proyecto | Ruta |
|---|---|
| NS_V50 (principal) | OneDrive - ARTEL S.A\Escritorio\💼 Proyectos\Modelo datos power BI\NS\NS_V50\NS_V50 |
| NS_V50_COMPLETO_MICROFLUJO | OneDrive - ARTEL S.A\Escritorio\💼 Proyectos\NS_V50_COMPLETO_MICROFLUJO |

### Archivo de entrada
NS.pbip → Doble clic o Start-Process -FilePath "C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe" -ArgumentList '"ruta\NS.pbip"'

### Páginas del reporte
| Página | ID | Propósito |
|---|---|---|
| 00 Resumen Ejecutivo Mayorista | 71af1998e2cb472d9799 | Dashboard principal con KPIs, evolución 3M, matriz de hitos, tabla crítica |
| 01 Análisis Fuera SLA | 1b2c3d4e5f6071829 | **NUEVA** — Investigación de pedidos fuera SLA y tesis FES |

### Filtros disponibles
- Mes (Dim_Periodo_3M.Etiqueta)
- Flujo (Dim_Vista_Ejecutiva.Flujo)
- Clasificación (Dim_Pedido.CLASIFICACION)
- Zona (Dim_Rango_Entrega.Zona)

---

## 🗺️ Flujo Completo del Negocio

`
PED_FECHA_HORA → COM → CRD → ENT → PIC → PAC → FAC → TRP (NORMAL) / MANIFIESTO (FES)
`

**Clasificaciones:**
- **NORMAL** → Cierre = Despacho (TRP). SLA interno zonal: Santiago 4 DH; Regiones 5 DH.
- **FES** (Factura Especial) → Se factura "en verde" y la operación va después. Cierre = Manifiesto. Ciclo más largo.
- **SALDO** → Cierre = TRP (usa última factura).

### Métricas clave
| Métrica | Fórmula | Propósito |
|---|---|---|
| NS Interno | Pedidos ≤5 DH / Total cerrados | % de cumplimiento interno |
| En SLA | DIAS_INTERNOS_DH ≤ 5 | Pedidos que cumplen |
| Fuera SLA | DIAS_INTERNOS_DH > SLA_INTERNO_DH | Pedidos que exceden |
| Promedio DH | AVERAGE(DIAS_INTERNOS_DH) | Tiempo promedio |
| P90 DH | PERCENTILE(..., 0.9) | Percentil 90 |

---

## ✅ MEJORES PRÁCTICAS (DO's)

### 1. TMDL y Modelo Semántico
- ✅ Usar **TREATAS** para dimensiones desconectadas (Dim_Vista_Ejecutiva)
- ✅ Preferir CALCULATE(DISTINCTCOUNT(…), TREATAS(…)) sobre medidas sin filtro
- ✅ Crear medidas en la tabla Medidas con displayFolder para organización
- ✅ Usar HITO_OMITIDO = FALSE solo cuando se necesiten datos **reales** (no heredados)
- ✅ Para contar pedidos que **alcanzaron** un hito (con o sin herencia): NO usar filtro HITO_OMITIDO

### 2. Reporte PBIP
- ✅ Archivos JSON en **UTF-8 sin BOM** (Power BI lo rechaza con BOM)
- ✅ Usar [System.Text.UTF8Encoding]::new(False) al escribir JSON
- ✅ Las páginas se auto-descubren desde la carpeta pages/
- ✅ Al copiar una página: copiar carpeta completa, cambiar 
ame y displayName en page.json
- ✅ Cada visual es una subcarpeta dentro de isuals/ con isual.json adentro

### 3. Conexiones MCP
- ✅ Primero buscar puerto con Get-NetTCPConnection | Where-Object LocalPort -ge 50000
- ✅ Verificar proceso con Get-Process -Id 14872
- ✅ Usar ConnectFolder para conectar a TMDL directamente
- ✅ Las medidas creadas en vivo NO persisten al cerrar Power BI → siempre escribir también al TMDL
- ✅ Al crear medidas en TMDL vía ConnectFolder, se escriben directo al archivo Medidas.tmdl

### 4. Live vs TMDL
- ✅ Live session (PBIDesktop-NS-*) → rápido para crear/verificar medidas
- ✅ TMDL (ConnectFolder) → persisten los cambios en el proyecto
- ✅ **Siempre hacer ambos**: crear en vivo, luego escribir al TMDL
- ✅ Al reconectar, buscar el nuevo puerto (msmdsrv se reinicia si PBI se cierra)

### 5. Documentación
- ✅ Dejar documentos en Docs/ del proyecto
- ✅ Incluir preguntas de negocio que responde cada visual
- ✅ Incluir datos clave del mes actual (julio 2026)
- ✅ Incluir próximos pasos sugeridos

---

## ❌ ANTIPATRONES (DON'Ts) — Errores Comunes

### 🚫 1. Tablas calculadas DAX sin columnas
**Error:** Usar daxExpression en Create table sin que el motor evalúe las columnas.
**Síntoma:** Tabla creada pero solo tiene RowNumber (sin columnas de datos).
**Solución:** Usar **M expression** con columns explícitas para tablas derivadas desde otras tablas del modelo.

### 🚫 2. Escribir JSON con UTF-8 BOM
**Error:** ConvertTo-Json en PowerShell escribe con BOM.
**Síntoma:** Power BI Desktop rechaza: *"Only text with UTF8 encoding without BOM is supported"*.
**Solución:** [System.IO.File]::WriteAllText(, , [System.Text.UTF8Encoding]::new(False))

### 🚫 3. No usar TREATAS con dimensiones desconectadas
**Error:** Medida DISTINCTCOUNT en Fact_Hitos_Operacionales sin filtrar por Dim_Vista_Ejecutiva.
**Síntoma:** Todos los subprocesos muestran el MIMO número (el total).
**Solución:** CALCULATE(…, TREATAS(VALUES(Dim_Vista_Ejecutiva[METRICA_CODIGO]), …))

### 🚫 4. Filtrar por HITO_OMITIDO sin entender la lógica de herencia
**Error:** HITO_OMITIDO = FALSE para contar pedidos que alcanzaron un hito.
**Síntoma:** Subestima gravemente los pedidos (ej: 37 vs 232 esperados).
**Causa:** Cuando un hito no tiene fecha real pero un hito posterior sí, hereda la fecha anterior y se marca OMITIDO.
**Solución:** NO filtrar por HITO_OMITIDO. Contar todos los pedidos con fila en el hito.

### 🚫 5. No persistir medidas en el TMDL
**Error:** Crear medidas solo en la sesión viva (MCP API).
**Síntoma:** Al cerrar Power BI Desktop, las medidas desaparecen.
**Solución:** Crear también via ConnectFolder al TMDL del proyecto.

### 🚫 6. Confundir los 2 proyectos NS_V50
**Error:** Modificar un proyecto pensando que es el otro.
**Síntoma:** "No encuentro la medida que creé".
**Solución:** Verificar siempre conectándose al TMDL correspondiente. Ambos tienen estructuras similares pero pueden divergir.

### 🚫 7. Ruta con emoji 💼 en OneDrive
**Error:** Usar la ruta completa con emoji en comandos PowerShell.
**Síntoma:** Caracteres extraños, rutas no encontradas.
**Solución:** Usar [System.IO.File]::ReadAllText() en vez de Get-Content. El emoji se representa como ?? en PowerShell.

### 🚫 8. TOPN fijo en medidas de tabla crítica
**Error:** TOPN(10, ...) para mostrar pedidos críticos.
**Síntoma:** Faltan 5 pedidos en la tabla.
**Solución:** TOPN(15, ...) para capturar todos los fuera de SLA.

### 🚫 9. No verificar si el puerto de msmdsrv cambió
**Error:** Usar el mismo puerto después de cerrar/reabrir Power BI.
**Síntoma:** "Connection is not open".
**Solución:** Get-NetTCPConnection | Where-Object LocalPort -ge 50000 cada vez.

---

## 📊 Estado Actual — Julio 2026

| Métrica | Valor |
|---|---|
| Total pedidos | 232 |
| Cerrados (con salida) | 219 |
| Abiertos (en proceso) | 13 |
| En SLA (según objetivo zonal 4/5 DH) | 204 |
| Fuera SLA (sobre objetivo zonal 4/5 DH) | 15 |
| NS Interno | 92,0% |
| Promedio DH | 3,1 DH |
| P90 DH | 5,0 DH |

### Los 15 fuera de SLA
- 10 FES, 5 NORMAL
- FES fuera SLA promedian ~13 DH vs SLA interno zonal de 4/5 DH
- Hito dominante: "FES: Entrega posterior → Manifiesto"

---

## 🔬 TESIS EN INVESTIGACIÓN (Página 01 Análisis Fuera SLA)

**Hipótesis:** "Me están metiendo FES a fin de mes para llegar a los presupuestos, y eso genera una ola a principios del mes siguiente que merma el SLA de los pedidos de principio de mes."

**Preguntas a responder:**
1. ¿Hay clientes recurrentes fuera de SLA? ¿Por flujo?
2. ¿Por qué FES demora más en cerrar?
3. ¿Entran más pedidos a fin de mes? ¿Son FES?
4. ¿Esos clientes se repiten?
5. ¿Qué vendedor tiene más clientes fuera de SLA?

---

## 📁 Documentos en Docs/

| Archivo | Contenido |
|---|---|
| RESUMEN_EJECUTIVO_MAYORISTA_GUIA.md | Preguntas que responde el dashboard |
| ANALISIS_FUERA_SLA_PREGUNTAS.md | Preguntas de negocio + tesis FES |
| GUIA_AGENTE_PLAYBOOK.md | **ESTE** — Prácticas, antipatrones y contexto |

---

## 🔧 Comandos Útiles

`powershell
# Encontrar puerto de Power BI Desktop
Get-NetTCPConnection -State Listen | Where-Object LocalPort -ge 50000

# Leer archivo JSON del reporte
[System.IO.File]::ReadAllText("ruta\visual.json", [System.Text.Encoding]::UTF8)

# Escribir JSON sin BOM
[System.IO.File]::WriteAllText(, , [System.Text.UTF8Encoding]::new(False))

# Listar conexiones MCP activas
Get-Process -Name msmdsrv, PBIDesktop -ErrorAction SilentlyContinue

# Abrir proyecto en Power BI Desktop
Start-Process -FilePath "C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe" -ArgumentList '"ruta\NS.pbip"'
`

---

*Versión: 29-07-2026. Mantener actualizado con cada cambio significativo.*