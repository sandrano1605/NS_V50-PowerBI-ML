param(
    [string]$RunName = "auditoria_integral",
    [string]$ExpectedBranch = "work/ns-lienzo-02-ingreso-pedidos"
)

$ErrorActionPreference = "Stop"

function Invoke-GitText {
    param([string[]]$GitArgs)
    $out = & git @GitArgs 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "git $($GitArgs -join ' ') fallo: $($out -join [Environment]::NewLine)"
    }
    return ($out -join [Environment]::NewLine).Trim()
}

$repoRoot = Invoke-GitText -GitArgs @("rev-parse", "--show-toplevel")
Set-Location $repoRoot

$branch = Invoke-GitText -GitArgs @("branch", "--show-current")
$sha = Invoke-GitText -GitArgs @("rev-parse", "HEAD")
$shortSha = Invoke-GitText -GitArgs @("rev-parse", "--short=7", "HEAD")
$remoteUrl = Invoke-GitText -GitArgs @("remote", "get-url", "origin")
$remoteRaw = (& git ls-remote origin "refs/heads/$branch" 2>&1) -join [Environment]::NewLine
$remoteSha = if ($LASTEXITCODE -eq 0 -and $remoteRaw.Trim()) { ($remoteRaw -split "\s+")[0] } else { $null }
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$timestampIso = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
$runId = "${timestamp}_${RunName}_${shortSha}"
$runDir = Join-Path $repoRoot "Docs/AUDITORIA_LIVE/local_runs/$runId"
$rawDir = Join-Path $runDir "raw"

New-Item -ItemType Directory -Force -Path $rawDir | Out-Null

$statusLines = @(& git status --porcelain=v1)
$dirty = $statusLines.Count -gt 0
$branchWarning = if ($branch -ne $ExpectedBranch) { "WARNING_BRANCH_MISMATCH expected=$ExpectedBranch actual=$branch" } else { "OK" }
$remoteWarning = if ($remoteSha -and $remoteSha -ne $sha) { "WARNING_LOCAL_REMOTE_SHA_MISMATCH" } else { "OK" }

$gitState = @()
$gitState += "RUN_ID=$runId"
$gitState += "TIMESTAMP_LOCAL=$timestampIso"
$gitState += "REPO_ROOT=$repoRoot"
$gitState += "BRANCH=$branch"
$gitState += "EXPECTED_BRANCH=$ExpectedBranch"
$gitState += "BRANCH_CHECK=$branchWarning"
$gitState += "LOCAL_SHA=$sha"
$gitState += "REMOTE_SHA=$remoteSha"
$gitState += "REMOTE_SHA_CHECK=$remoteWarning"
$gitState += "REMOTE_URL=$remoteUrl"
$gitState += "WORKTREE_DIRTY=$dirty"
$gitState += ""
$gitState += "--- git status --porcelain=v1 ---"
$gitState += if ($statusLines.Count) { $statusLines } else { "<clean>" }
$gitState += ""
$gitState += "--- git log -8 --oneline --decorate ---"
$gitState += @(& git log -8 --oneline --decorate)
$gitState += ""
$gitState += "--- git diff --name-status ---"
$diffNames = @(& git diff --name-status)
$gitState += if ($diffNames.Count) { $diffNames } else { "<none>" }
$gitState | Set-Content -Encoding UTF8 (Join-Path $runDir "01_git_state.txt")

$pbis = @(Get-Process PBIDesktop -ErrorAction SilentlyContinue)
$pythonVersion = try { (& python --version 2>&1) -join " " } catch { "NO_DISPONIBLE" }
$envLines = @(
    "RUN_ID=$runId",
    "TIMESTAMP_LOCAL=$timestampIso",
    "COMPUTERNAME=$env:COMPUTERNAME",
    "USERNAME=$env:USERNAME",
    "OS=$([System.Environment]::OSVersion.VersionString)",
    "POWERSHELL=$($PSVersionTable.PSVersion)",
    "PYTHON=$pythonVersion",
    "PBIDESKTOP_PROCESS_COUNT=$($pbis.Count)"
)
foreach ($p in $pbis) {
    $processPath = try { $p.Path } catch { $null }
    $processStart = try { $p.StartTime.ToString('s') } catch { "NO_DISPONIBLE" }
    $envLines += "PBIDESKTOP_PID=$($p.Id);START=$processStart;PATH=$processPath"
}
$envLines += "POWERBI_PORT=POR_RESOLVER_POR_AUDITOR"
$envLines += "POWERBI_DATABASE=POR_RESOLVER_POR_AUDITOR"
$envLines | Set-Content -Encoding UTF8 (Join-Path $runDir "02_environment.txt")

$manifest = [ordered]@{
    schema_version = 1
    run_id = $runId
    timestamp_local = $timestampIso
    repository = "sandrano1605/NS_V50-PowerBI-ML"
    repo_root = $repoRoot
    branch = $branch
    expected_branch = $ExpectedBranch
    local_sha = $sha
    remote_sha_at_start = $remoteSha
    local_remote_equal_at_start = ($remoteSha -eq $sha)
    worktree_dirty_at_start = $dirty
    preexisting_status = @($statusLines)
    pbip_path = "NS.pbip"
    power_bi = [ordered]@{
        process_count = $pbis.Count
        pids = @($pbis | ForEach-Object { $_.Id })
        port = $null
        database = $null
        refresh_executed = $false
        refresh_result = "NO_EJECUTADO"
    }
    audit_mode = "READ_ONLY_FUNCTIONAL_EVIDENCE_WRITER"
    status = "RUNNING"
    validation_status = "PENDING"
    evidence_commit_sha = $null
    findings = [ordered]@{ red = 0; orange = 0; yellow = 0; info = 0 }
    notes = @()
}
$manifest | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 (Join-Path $runDir "00_manifest.json")

$csvHeaders = [ordered]@{
    "03_model_inventory.csv" = "LAYER,OBJECT_TYPE,OBJECT_NAME,FILE_PATH,STATUS,DETAIL"
    "04_code_findings.csv" = "FINDING_ID,SEVERITY,STATUS,LAYER,OBJECT_TYPE,OBJECT_NAME,FILE_PATH,LINE_START,LINE_END,RULE,EXPECTED,ACTUAL,EVIDENCE_FILE,CONFIDENCE,REQUIRES_BUSINESS_DECISION,RECOMMENDED_CHANGE,NOTES"
    "05_business_rule_matrix.csv" = "RULE_ID,RULE,EXPECTED_CURRENT_RULE,CODE_IMPLEMENTATION,DATA_RESULT,STATUS,EVIDENCE,NOTES"
    "07_live_results.csv" = "TEST_ID,CATEGORY,METRIC,DIMENSION,SELECTION,VALUE,EXPECTED,STATUS,EVIDENCE,NOTES"
    "08_regression_cases_results.csv" = "PEDIDO,CASO,HISTORICAL_EXPECTED,CURRENT_ACTUAL,STATUS,EVIDENCE,NOTES"
    "09_inc_status.csv" = "INC_ID,PREVIOUS_STATUS,CURRENT_STATUS,SEVERITY,IMPACT_CURRENT,EVIDENCE,REQUIRES_BUSINESS_DECISION,RECOMMENDATION"
    "10_visual_bindings.csv" = "PAGE,VISUAL,OBJECT_PATH,MEASURES_FIELDS,FILTERS,SORT,SLICER_INTERACTION,STATUS,EVIDENCE,NOTES"
    "11_data_quality.csv" = "CHECK_ID,CATEGORY,OBJECT,METRIC,VALUE,EXPECTED,STATUS,EVIDENCE,NOTES"
    "12_recommendations.csv" = "PRIORITY,FINDING_ID,TARGET_FILE,TARGET_OBJECT,RECOMMENDED_CHANGE,WHY,EXPECTED_IMPACT,VALIDATION_REQUIRED,BUSINESS_DECISION_REQUIRED"
}
foreach ($entry in $csvHeaders.GetEnumerator()) {
    $path = Join-Path $runDir $entry.Key
    if (-not (Test-Path $path)) {
        $entry.Value | Set-Content -Encoding UTF8 $path
    }
}

@"
# Consultas vivas ejecutadas

RUN_ID: $runId
SHA auditado: $sha

Registrar aquí cada consulta DAX/DMV/M ejecutada, su objetivo y el archivo de resultados asociado.

Estado inicial: NO_EJECUTADO.
"@ | Set-Content -Encoding UTF8 (Join-Path $runDir "06_live_queries.md")

@"
# READY FOR CHATGPT

RUN_ID: $runId
Rama: $branch
SHA auditado: $sha
SHA remoto al iniciar: $remoteSha
Commit evidencia: PENDIENTE
Working tree sucio al iniciar: $dirty
Power BI: PENDIENTE DE AUDITAR

## Resumen
PENDIENTE

## Hallazgos RED confirmados
PENDIENTE

## Hallazgos ORANGE confirmados
PENDIENTE

## Falsos positivos relevantes
PENDIENTE

## Decisiones de negocio necesarias
PENDIENTE

## Cambios recomendados para implementación remota
PENDIENTE

## Evidencia principal
PENDIENTE

## No resuelto
PENDIENTE
"@ | Set-Content -Encoding UTF8 (Join-Path $runDir "READY_FOR_CHATGPT.md")

@"
# RESULTADO AUDITORÍA LOCAL

RUN_ID: $runId
SHA auditado: $sha
Estado: EN_PROCESO

Completar al terminar la corrida. El auditor local no implementa fixes.
"@ | Set-Content -Encoding UTF8 (Join-Path $runDir "RESULTADO.md")

$latestPath = Join-Path $repoRoot "Docs/AUDITORIA_LIVE/LOCAL_LATEST.json"
$latest = [ordered]@{
    schema_version = 1
    status = "RUNNING_LOCAL_AUDIT"
    run_id = $runId
    audit_branch = $branch
    audited_sha = $sha
    evidence_commit_sha = $null
    run_path = "Docs/AUDITORIA_LIVE/local_runs/$runId"
    ready_for_chatgpt = "Docs/AUDITORIA_LIVE/local_runs/$runId/READY_FOR_CHATGPT.md"
    updated_at_local = $timestampIso
    note = "Corrida local iniciada; no consumir como evidencia final hasta status READY_FOR_CHATGPT."
}
$latest | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 $latestPath

Write-Host "RUN_ID=$runId"
Write-Host "RUN_DIR=$runDir"
Write-Host "LOCAL_SHA=$sha"
Write-Host "REMOTE_SHA=$remoteSha"
Write-Host "WORKTREE_DIRTY=$dirty"
Write-Host "BRANCH_CHECK=$branchWarning"
Write-Host "REMOTE_SHA_CHECK=$remoteWarning"
Write-Host "AUDIT_MODE=READ_ONLY_FUNCTIONAL_EVIDENCE_WRITER"
