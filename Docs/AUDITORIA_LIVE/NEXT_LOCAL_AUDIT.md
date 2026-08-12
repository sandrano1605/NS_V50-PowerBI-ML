# Próxima auditoría local — STOP hasta nueva fuente YV01

## Estado

No ejecutar una nueva auditoría INC-015 todavía.

La evidencia publicada en `1ec81ad` confirmó:

- `INC-015 = SIN_FUENTE_YV01_EN_DMF_VTA_PRD`;
- `VBAP_SAP` es `USER_TABLE` física;
- `dbo.VBAP` no existe;
- 7 candidatos con firma de posiciones SAP fueron probados;
- 33 bases visibles fueron inspeccionadas;
- 0 candidatos tuvieron cobertura YV01;
- la cobertura actual 58,3% de líneas/unidades es estructural mientras no exista una fuente YV01.

No repetir búsquedas de objetos ni auditorías del modelo con el mismo estado de fuentes.

## Dependencia externa

Se requiere que SAP / ETL / datos exponga una fuente de posiciones YV01 conforme al contrato:

`Docs/AUDITORIA_LIVE/INC015_YV01_SOURCE_CONTRACT.md`

Preferencia:

- fuente única completa de posiciones SAP, o
- tabla/vista específica YV01 con `VBELN`, `POSNR`, `KWMENG` y, de ser posible, `AEDAT`, `MATNR`, `WERKS`.

## Condición para reactivar auditoría

Solo ejecutar una nueva corrida cuando exista al menos una de estas novedades:

1. un nuevo objeto SQL accesible desde Power BI que contenga posiciones YV01;
2. una réplica/ETL SAP actualizada para incluir YV01;
3. una conexión autorizada a otra fuente (SAP/BW/RFC/otra base) que exponga `VBELN + POSNR + KWMENG`;
4. evidencia del equipo de datos de que un objeto existente cambió su cobertura.

## Primera prueba al desbloquear

Antes de modificar Power BI:

1. medir cobertura YV01 reciente contra `VBAK_SAP`;
2. exigir >=98% para considerarla fuente apta, salvo explicación documentada del residual;
3. validar una muestra >=50 pedidos contra el origen autorizado;
4. comprobar unicidad `VBELN + POSNR`;
5. comparar `COUNT(DISTINCT POSNR)` y `SUM(KWMENG)`.

Si la fuente pasa estas pruebas, publicar evidencia `READY_FOR_CHATGPT` con:

- nombre exacto del objeto;
- schema/base/servidor;
- columnas disponibles;
- cobertura total y por AUART;
- duplicados `VBELN + POSNR`;
- muestra validada;
- recomendación de fuente única vs unión con `VBAP_SAP`.

## Implementación posterior

ChatGPT realizará el cambio remoto de `Lineas_y_unidades_por_pedidos` solo después de esa validación y luego se hará refresh + auditoría post-fix.

Hasta entonces:

```text
INC-015 = BLOCKED_SOURCE / SIN_FUENTE_YV01
```

Los fixes FIND-002A, INC-011 e INC-007B permanecen GREEN.
