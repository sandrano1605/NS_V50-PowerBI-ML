# RESULTADO: Prueba final lienzo 02 profesional — DETENIDA POR ERRORES

**Fecha:** 2026-08-04
**Rama:** work/ns-lienzo-02-ingreso-pedidos
**SHA local:** 9c1df6e1ab78093f13427de5658bbdc910f1680b
**SHA remoto:** 9c1df6e1ab78093f13427de5658bbdc910f1680b
**Dictamen:** 🔴 ROJO — refresh falla, no se puede validar

## Hallazgo 1: Error DAX en la medida `RE Fuera SLA %` (BLOQUEANTE)

**Archivo:** `NS.SemanticModel/definition/tables/Medidas.tmdl` línea 2049

```
measure 'RE Fuera SLA %' = RETURN 1 - [RE NS contexto]
```

La sintaxis DAX es **inválida**: `RETURN 1 - ...` al inicio de una medida no es
válido (RETURN solo se usa dentro de un bloque VAR...RETURN). Debe ser:

```
measure 'RE Fuera SLA %' = 1 - [RE NS contexto]
```

**Error del refresh:**
```
The syntax for 'RETURN' is incorrect (RETURN 1 - [RE NS contexto])
```

**Impacto:** el refresh completo falla; el modelo no puede actualizarse.

## Hallazgo 2: Conexión SQL no accesible (INFRAESTRUCTURA)

`Test-NetConnection 128.1.3.21:1433` → **TcpTestSucceeded: False**

El servidor DMF_VTA_PRD no responde (error 40 - Named Pipes). Esto impide el
refresh de cualquier forma, incluso tras corregir el DAX.

## Imposibilidad de validación

Por ambos errores NO se pudo:
- refrescar el modelo;
- responder Q1 (día líder), Q2 (14:30) ni Q3 (cierre vs resto);
- probar botones ni filtros;
- validar tarjetas, lectura ejecutiva o calidad visual.

## Acción requerida (ChatGPT)

1. Corregir `measure 'RE Fuera SLA %'` → quitar el `RETURN` inicial.
2. Confirmar disponibilidad del servidor SQL 128.1.3.21 (VPN/red).
3. Re-ejecutar el LLM local para la prueba completa.

## Archivos de evidencia

- 00_git_before.txt
- 01_refresh.txt
- RESULTADO.md (este archivo)
