# Tarea UX-3 — Cerrar `00 Resumen Ejecutivo Mayorista`

## Objetivo único

Corregir los cuatro botones de navegación del encabezado de la página **00 Resumen Ejecutivo Mayorista**, asegurando que el texto sea visible, que las acciones existentes se conserven y que el PBIP abra sin errores.

## Línea base

- Repositorio: `sandrano1605/NS_V50-PowerBI-ML`
- Rama: `work/codex-local`
- SHA base mínimo: `6d7c5da8357785bd9253afbe742f3471ee15ff41`
- Página: `NS.Report/definition/pages/71af1998e2cb472d9799`

## Etiquetas requeridas, de izquierda a derecha

1. `RESUMEN EJECUTIVO`
2. `TRACKING OPERATIVO`
3. `CUELLOS DE BOTELLA`
4. `COLA DIARIA`

El primer botón es el activo y debe conservar fondo azul con texto blanco. Los tres restantes deben conservar fondo claro y mostrar texto azul oscuro.

## Ejecución

Desde la raíz del repositorio:

```powershell
git fetch origin --prune
git checkout work/codex-local
git reset --hard origin/work/codex-local

python tools/fix_ux3_resumen_botones.py --apply `
  --report validation/ux3_00_resumen_botones.json
```

## Controles obligatorios antes de abrir Power BI

```powershell
Get-ChildItem `
  "NS.Report\definition\pages\71af1998e2cb472d9799" `
  -Recurse -Filter "*.json" |
ForEach-Object {
    Get-Content $_.FullName -Raw -Encoding UTF8 |
        ConvertFrom-Json -ErrorAction Stop |
        Out-Null
    Write-Host "JSON OK: $($_.FullName)" -ForegroundColor Green
}

git diff --name-only
git diff --check
```

## Validación visual en Power BI Desktop

1. Abrir el `.pbip` desde la raíz correcta.
2. Ir a **00 Resumen Ejecutivo Mayorista**.
3. Confirmar que los cuatro nombres se leen completos y centrados.
4. Confirmar que no se cortan con DPI de Windows al 150 %.
5. Probar cada botón con `Ctrl + clic`:
   - Resumen ejecutivo → página 00.
   - Tracking operativo → página 01.
   - Cuellos de botella → página 02.
   - Cola diaria → página 05.
6. Volver a página 00 y capturar pantalla completa como evidencia.
7. Confirmar que no aparezcan errores de JSON, TMDL, Power Query ni visuales en blanco.

## Regla de corrección

- No crear textboxes superpuestos.
- No reemplazar los botones.
- No cambiar posiciones, tamaños, rellenos, bordes o acciones.
- Modificar únicamente el objeto `text` de los `actionButton` existentes.
- `visualContainerObjects` debe permanecer dentro de `visual` y como sibling de `objects`.

## Cierre Git

```powershell
git add `
  "NS.Report/definition/pages/71af1998e2cb472d9799" `
  "validation/ux3_00_resumen_botones.json"

git diff --cached --check
git commit -m "fix(powerbi): completa navegación de resumen ejecutivo UX-3"
git push origin work/codex-local

$LocalSHA = git rev-parse HEAD
$RemoteSHA = git ls-remote origin refs/heads/work/codex-local |
    ForEach-Object { ($_ -split "`t")[0] }

Write-Host "SHA local : $LocalSHA"
Write-Host "SHA remoto: $RemoteSHA"

if ($LocalSHA -ne $RemoteSHA) {
    throw "El SHA local no coincide con origin/work/codex-local"
}
```

## Evidencia de cierre requerida

- SHA local y remoto coincidentes.
- Cantidad total de JSON validados.
- IDs de los cuatro visuales modificados.
- Etiqueta final de cada botón.
- Resultado de navegación de los cuatro botones.
- Captura de la página completa.

No declarar UX-3 cerrado sin evidencia visual y funcional.
