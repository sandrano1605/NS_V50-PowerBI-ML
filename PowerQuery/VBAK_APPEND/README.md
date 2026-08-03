# VBAK → Fact_Pedidos_Auditoria · cruce inline activo

## Estado

El cruce ya está incorporado directamente en:

```text
NS.SemanticModel/definition/tables/Fact_Pedidos_Auditoria.tmdl
```

No es necesario crear parámetros, consultas auxiliares ni pegar código en Power Query.

La implementación activa corresponde a:

```text
06_MASTER_APPEND_INLINE_ACTIVE.pq
```

Los archivos `00` a `05` se conservan como material de preflight y trazabilidad de las iteraciones anteriores; no deben crearse nuevamente en el modelo.

## Regla de integración

La master conserva su universo original y agrega solamente pedidos faltantes que cumplan simultáneamente:

- pedido válido y no existente en la master, mediante `LeftAnti`;
- fecha dentro de los últimos tres meses móviles;
- clase de pedido permitida;
- canal 42–47;
- cliente informado;
- región informada;
- fecha de pedido válida;
- no aparece como FES en VBFA `C→C`;
- no tiene `fecha_fes` en `Pedidos_Normal_VBAK`;
- entrega no anterior al pedido;
- factura no anterior al pedido;
- salida solo cuando existe factura y no es anterior a ella.

## Fuentes

- atributos de pedido: `VBAK_SAP`;
- ciudad y región: `KNA1_SAP`;
- clasificación FES: `VBFA_SAP`, flujo `C→C`;
- fechas de entrega, factura y salida: `Pedidos_Normal_VBAK`.

## Trazabilidad de filas agregadas

Todas las filas nuevas quedan identificadas con:

```text
PED_TEXTO_ESTADO = VBAK SIN ZART
AUD_ESTADO_GENERAL = REVISAR
AUD_REQUIERE_REVISION = true
ES_FES = false
ES_SALDO = false
```

No se inventan manifiestos ni fechas FES. Tampoco se infiere SALDO a partir de una sola factura.

## Validación local

```powershell
git fetch origin
git switch work/ns-vbak-master-append
git pull --ff-only origin work/ns-vbak-master-append
python tools/validate_vbak_append_kit.py
```

Después abrir `NS.pbip`, ejecutar `Actualizar todo` y validar mediante MCP:

- total de filas de la master;
- filas con marcador `VBAK SIN ZART`;
- duplicados por pedido = 0;
- claves nulas = 0;
- canales fuera de 42–47 = 0;
- regiones nulas = 0;
- filas VBAK clasificadas FES o SALDO = 0;
- salida sin factura = 0;
- tablas derivadas y Python sin error;
- pedidos `4190139455` y `1167577` sin regresión.

El conteo `1.973` era un snapshot histórico. No debe utilizarse como total fijo porque la master trabaja con `GETDATE()` y una ventana móvil.

## Rollback

El interruptor está dentro de la master:

```powerquery
VBAK_APPEND_ACTIVO_LOCAL = true
```

Ante un error confirmado en modelo vivo, cambiarlo a `false` desde Power Query Desktop o restaurar la rama al punto estable `a8e818604826e689453769103d962cd3537399ed`. El LLM local no debe realizar ese cambio sin instrucción explícita.
