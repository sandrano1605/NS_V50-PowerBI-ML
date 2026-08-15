# PBIP Design Template — NS Mayorista

Plantilla reutilizable de **design system visual + patrones DAX** extraída del
reporte Power BI `NS` (Nivel de Servicio Mayorista).

No incluye la capa de datos ni la lógica de negocio específica de NS (FES, SALDO,
canales 42-47, feriados chilenos). Esos son propios del proyecto origen.

## Qué contiene

| Carpeta | Contenido | Uso |
|---|---|---|
| `design-system.md` | Paleta, tipografía y componentes SVG parametrizados | Copiar estilos a otro reporte |
| `dax-patterns.md` | Patrones DAX reutilizables (jerarquía desconectada, medida Visible, tabla config) | Replicar la arquitectura de medidas |
| `tablas-config/` | TMDL plantilla de tablas de parámetros editables | Que el negocio cambie metas sin tocar DAX |

## Cómo usarla en otro proyecto

1. Copiar esta carpeta al nuevo repo.
2. Reemplazar la fuente de datos (SQL → la tuya).
3. Ajustar `Config_SLA` / `Config_Promesa` con tus metas.
4. Reemplazar textos y colores en los SVG (ver `design-system.md`).
5. Mapear tus dimensiones a la jerarquía ejecutiva (flujo/macroproceso/subproceso).

## Origen

- Repositorio: `sandrano1605/NS_V50-PowerBI-ML`
- Rama: `work/ns-lienzo-01-analisis-fuera-sla`
- Reporte: `NS.pbip` (Power BI PBIP)

## Nota

Los SVG están como **medidas DAX** que devuelven `data:image/svg+xml,...`.
Se usan en visuales de tipo `cardVisual`/imagen sin HTML personalizado.
