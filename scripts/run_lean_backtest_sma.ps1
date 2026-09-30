param(
    [string]$LeanRoot = "D:\LeanT\Lean",
    [int]$TimeoutSeconds = 600,
    [string]$AlgoName = "sma_crossover_algorithm.py",
    [string]$AlgoTypeName = "SmaCrossoverAlgorithm",
    [string]$RuntimeConfigPath = "",
    [string]$ExecutionConfigPath = "",
    [string]$RunnerTranscriptPath = "",
    [string]$RunnerErrorPath = ""
)

$ErrorActionPreference = "Stop"

# ------------------------------------------------------------
# 1. Resolve paths
# ------------------------------------------------------------

$ProjectRoot = (Resolve-Path "$PSScriptRoot\..").Path
$DataDir = Join-Path $ProjectRoot "data"
$AlgoPath = Join-Path $ProjectRoot "src\lean_integration\$AlgoName"
$TemplatePath = Join-Path $ProjectRoot "config\lean_config_template.json"
$TempConfigPath = Join-Path $ProjectRoot "config\temp_config.json"

$LauncherDir = Join-Path $LeanRoot "Launcher\bin\Debug"
$LauncherExe = Join-Path $LauncherDir "QuantConnect.Lean.Launcher.exe"

$LeanConfigPath = Join-Path $LauncherDir "config.json"
$BackupConfigPath = Join-Path $LauncherDir "config.backup.json"

$LeanDataDir = Join-Path $LeanRoot "Data"
$LogPath = Join-Path $LauncherDir "results\log.txt"
$RuntimeMode = -not [string]::IsNullOrWhiteSpace($RuntimeConfigPath)

if ($RuntimeMode) {
    if ([string]::IsNullOrWhiteSpace($ExecutionConfigPath)) {
        throw "ExecutionConfigPath is required with RuntimeConfigPath."
    }

    $RuntimeRoot = [System.IO.Path]::GetFullPath((Join-Path $ProjectRoot ".runtime"))
    $RuntimeRootPrefix = $RuntimeRoot + [System.IO.Path]::DirectorySeparatorChar
    $RuntimeConfigPath = [System.IO.Path]::GetFullPath($RuntimeConfigPath)
    $ExecutionConfigPath = [System.IO.Path]::GetFullPath($ExecutionConfigPath)
    $RunnerTranscriptPath = [System.IO.Path]::GetFullPath($RunnerTranscriptPath)
    $RunnerErrorPath = [System.IO.Path]::GetFullPath($RunnerErrorPath)
    if (-not $RuntimeConfigPath.StartsWith($RuntimeRootPrefix, [System.StringComparison]::OrdinalIgnoreCase) -or
        -not $ExecutionConfigPath.StartsWith($RuntimeRootPrefix, [System.StringComparison]::OrdinalIgnoreCase) -or
        -not $RunnerTranscriptPath.StartsWith($RuntimeRootPrefix, [System.StringComparison]::OrdinalIgnoreCase) -or
        -not $RunnerErrorPath.StartsWith($RuntimeRootPrefix, [System.StringComparison]::OrdinalIgnoreCase) -or
        [System.IO.Path]::GetDirectoryName($RuntimeConfigPath) -ne [System.IO.Path]::GetDirectoryName($ExecutionConfigPath) -or
        [System.IO.Path]::GetDirectoryName($RuntimeConfigPath) -ne [System.IO.Path]::GetDirectoryName($RunnerTranscriptPath) -or
        [System.IO.Path]::GetDirectoryName($RuntimeConfigPath) -ne [System.IO.Path]::GetDirectoryName($RunnerErrorPath)) {
        throw "Runtime configuration paths must share one directory inside .runtime."
    }
    if (-not (Test-Path -LiteralPath $RuntimeConfigPath -PathType Leaf) -or
        -not (Test-Path -LiteralPath $ExecutionConfigPath -PathType Leaf)) {
        throw "Runtime or execution configuration file is missing."
    }

    try {
        $RuntimeConfig = Get-Content -LiteralPath $RuntimeConfigPath -Raw | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        throw "Runtime configuration is malformed JSON."
    }
    $AllowedSymbols = @("RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "WIPRO.NS")
    if ($RuntimeConfig.strategy -ne "sma_crossover" -or
        @($RuntimeConfig.symbols | Where-Object { $_ -notin $AllowedSymbols -or $_ -eq "WIPRO.NS" }).Count -gt 0) {
        throw "Runtime SMA configuration contains an unsupported strategy or symbol."
    }

    $AlgoPath = Join-Path $ProjectRoot "backend\lean_runtime\runtime_algorithm.py"
    $AlgoTypeName = "RuntimeSmaCrossoverAlgorithm"
    $TempConfigPath = $ExecutionConfigPath
    $BackupConfigPath = Join-Path ([System.IO.Path]::GetDirectoryName($RuntimeConfigPath)) "config.backup.json"
    $env:INDIAN_TRADING_RUNTIME_CONFIG = $RuntimeConfigPath
}

# ------------------------------------------------------------
# 2. Validate required files
# ------------------------------------------------------------

if (-not (Test-Path $LauncherExe)) {
    throw "LEAN launcher not found: $LauncherExe"
}

if (-not (Test-Path $AlgoPath)) {
    throw "Algorithm file not found: $AlgoPath"
}

if (-not (Test-Path $TemplatePath)) {
    throw "LEAN config template not found: $TemplatePath"
}

if (-not (Test-Path $LeanDataDir)) {
    throw "LEAN Data directory not found: $LeanDataDir"
}

# Verify all 5 symbol ZIPs exist
$ExpectedZips = @(
    "reliance.ns.zip",
    "tcs.ns.zip",
    "infy.ns.zip",
    "hdfcbank.ns.zip",
    "icicibank.ns.zip"
)
if ($RuntimeMode) {
    $ExpectedZips = @($RuntimeConfig.symbols | ForEach-Object { ($_.ToLowerInvariant() + ".zip") })
}

$DailyDataDir = Join-Path $DataDir "equity\india\daily"

foreach ($zip in $ExpectedZips) {
    $zipPath = Join-Path $DailyDataDir $zip
    if (-not (Test-Path $zipPath)) {
        throw "Missing LEAN ZIP: $zipPath. Run export_lean_format.py first."
    }
}

Write-Host ""
Write-Host "All 5 symbol ZIPs verified in: $DailyDataDir"

$SymbolProperties = Join-Path `
    $LeanDataDir `
    "symbol-properties\symbol-properties-database.csv"

if (-not (Test-Path $SymbolProperties)) {
    throw "LEAN symbol properties database not found: $SymbolProperties"
}

# ------------------------------------------------------------
# 3. Environment variables
# ------------------------------------------------------------

$env:INDIAN_TRADING_SYSTEM_ROOT = $ProjectRoot
$env:INDIAN_TRADING_SYSTEM_DATA_DIR = $DataDir

Write-Host ""
Write-Host "Project Root : $ProjectRoot"
Write-Host "Data Dir     : $DataDir"
Write-Host "Algorithm    : $AlgoPath"
Write-Host "LEAN Root    : $LeanRoot"
Write-Host "LEAN Data    : $LeanDataDir"
Write-Host ""

# ------------------------------------------------------------
# 4. Python configuration
# ------------------------------------------------------------

$PythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    throw "Python environment not found: $PythonExe"
}

$PythonDllPath = & $PythonExe -c `
    "import sys, os; print(os.path.join(sys.base_prefix, f'python{sys.version_info.major}{sys.version_info.minor}.dll'))"

$PythonDllPath = $PythonDllPath.Trim()

if (-not (Test-Path $PythonDllPath)) {
    throw "Python DLL not found: $PythonDllPath"
}

$env:PYTHONNET_PYDLL = $PythonDllPath

Write-Host "Python       : $PythonExe"
Write-Host "Python DLL   : $PythonDllPath"
Write-Host ""

# ------------------------------------------------------------
# 5. Build LEAN configuration
# ------------------------------------------------------------

$ConfigJson = Get-Content $TemplatePath -Raw | ConvertFrom-Json

$ConfigJson."algorithm-location" = $AlgoPath
$ConfigJson."algorithm-type-name" = $AlgoTypeName
$ConfigJson."data-folder" = $DataDir

# Ensure necessary LEAN metadata folders exist in our DataDir
if (-not (Test-Path "$DataDir\market-hours")) {
    Copy-Item "$LeanDataDir\market-hours" "$DataDir\market-hours" -Recurse
}
if (-not (Test-Path "$DataDir\symbol-properties")) {
    Copy-Item "$LeanDataDir\symbol-properties" "$DataDir\symbol-properties" -Recurse
}

if ($RuntimeMode) {
    $RunConfig = Get-Content -LiteralPath $ExecutionConfigPath -Raw | ConvertFrom-Json -ErrorAction Stop
    if ($RunConfig."algorithm-location" -ne $AlgoPath -or
        $RunConfig."algorithm-type-name" -ne $AlgoTypeName -or
        $RunConfig."data-folder" -ne $DataDir) {
        throw "Execution config does not match the fixed runtime adapter configuration."
    }
    $ConfigJson = $RunConfig
}
else {
    $ConfigJson | ConvertTo-Json -Depth 10 | Out-File -FilePath $TempConfigPath -Encoding UTF8
}

Write-Host "Generated config: $TempConfigPath"
Write-Host ""

# Show data-folder contents summary
Write-Host "Data folder contents (equity/india/daily):"
Get-ChildItem $DailyDataDir | ForEach-Object { Write-Host "  $($_.Name)" }
Write-Host ""

# ------------------------------------------------------------
# 6. Backup and replace LEAN config
# ------------------------------------------------------------

$HadOriginalConfig = Test-Path $LeanConfigPath

if ($HadOriginalConfig) {
    Copy-Item `
        $LeanConfigPath `
        $BackupConfigPath `
        -Force
}

Copy-Item `
    $TempConfigPath `
    $LeanConfigPath `
    -Force

# ------------------------------------------------------------
# 7. Launch LEAN
# ------------------------------------------------------------

$Process = $null

try {

    if ($RuntimeMode) {
        Start-Transcript -Path $RunnerTranscriptPath -Force | Out-Null
    }

    Write-Host "Starting LEAN..."
    Write-Host "Timeout: $TimeoutSeconds seconds"
    Write-Host ""

    $RunStartedAt = Get-Date
    $StartInfo = New-Object System.Diagnostics.ProcessStartInfo

    $StartInfo.FileName = $LauncherExe
    $StartInfo.WorkingDirectory = $LauncherDir
    $StartInfo.UseShellExecute = $false
    $StartInfo.CreateNoWindow = $true

    if ($RuntimeMode -and (Test-Path $LogPath)) {
        try {
            [System.IO.File]::WriteAllText($LogPath, "")
        }
        catch {
            throw "Cannot start LEAN because its shared engine log is still in use."
        }
    }

    $Process = New-Object System.Diagnostics.Process
    $Process.StartInfo = $StartInfo

    Write-Host "Launching:"
    Write-Host $LauncherExe
    Write-Host ""

    [void]$Process.Start()

    if ($RuntimeMode) {
        $ProcessRecordPath = Join-Path ([System.IO.Path]::GetDirectoryName($RuntimeConfigPath)) "lean_process.json"
        $ProcessRecord = @{ processId = $Process.Id; startedAt = $RunStartedAt.ToUniversalTime().ToString("o") } |
            ConvertTo-Json -Compress
        [System.IO.File]::WriteAllText($ProcessRecordPath, $ProcessRecord, [System.Text.UTF8Encoding]::new($false))
    }

    # --------------------------------------------------------
    # Monitor LEAN's log for successful completion.
    # --------------------------------------------------------

    $StartTime = Get-Date
    $Completed = $false

    while (((Get-Date) - $StartTime).TotalSeconds -lt $TimeoutSeconds) {

        Start-Sleep -Milliseconds 500

        if (-not (Test-Path $LogPath)) {
            continue
        }

        $LogContent = Get-Content $LogPath -Raw

        if ((Get-Item $LogPath).LastWriteTime -gt $RunStartedAt -and
            $LogContent -match "Analysis Completed and Results Posted") {
            $Completed = $true
            break
        }

        if ($RuntimeMode -and $Process.HasExited) {
            throw "LEAN launcher exited before reporting completion (exit code $($Process.ExitCode))."
        }
    }

    if (-not $Completed) {

        Write-Host ""
        Write-Host "LEAN did not report completion within $TimeoutSeconds seconds."
        Write-Host "Stopping LEAN..."

        if ($Process -and -not $Process.HasExited) {
            try {
                $Process.Kill()
                $Process.WaitForExit(5000)
            }
            catch {
                Write-Warning "Could not terminate LEAN cleanly."
            }
        }

        throw "LEAN backtest timed out."
    }

    Write-Host ""
    Write-Host "LEAN reported successful completion."

    # Give LEAN a moment to finish writing result files.
    Start-Sleep -Milliseconds 1000

    # --------------------------------------------------------
    # Display algorithm log output
    # --------------------------------------------------------

    $AlgorithmLogFilter = if ($RuntimeMode) { "$AlgoTypeName-log.txt" } else { "*-log.txt" }
    $AlgorithmLogPath = Get-ChildItem -Path (Join-Path $LauncherDir "results") -Filter $AlgorithmLogFilter |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if ($AlgorithmLogPath) {
        Write-Host ""
        Write-Host "========== ALGORITHM LOG =========="
        Get-Content $AlgorithmLogPath.FullName
    }

    # --------------------------------------------------------
    # Stop launcher if still alive
    # --------------------------------------------------------

    if ($Process -and -not $Process.HasExited) {
        Write-Host ""
        Write-Host "LEAN engine finished. Stopping launcher process..."
        try {
            $Process.Kill()
            $Process.WaitForExit(5000)
        }
        catch {
            Write-Warning "Launcher process could not be terminated automatically."
        }
    }

}
catch {
    if ($RuntimeMode -and $RunnerErrorPath) {
        [System.IO.File]::WriteAllText(
            $RunnerErrorPath,
            ($_ | Out-String),
            [System.Text.UTF8Encoding]::new($false)
        )
    }
    throw
}
finally {

    # --------------------------------------------------------
    # 8. Restore original LEAN config
    # --------------------------------------------------------

    if ($HadOriginalConfig -and (Test-Path $BackupConfigPath)) {
        Copy-Item `
            $BackupConfigPath `
            $LeanConfigPath `
            -Force
        Remove-Item `
            $BackupConfigPath `
            -Force
    }
    elseif (-not $HadOriginalConfig -and (Test-Path $LeanConfigPath)) {
        Remove-Item `
            $LeanConfigPath `
            -Force
    }

    if ($Process -and -not $Process.HasExited) {
        try {
            $Process.Kill()
            $Process.WaitForExit(5000)
        }
        catch {
        }
    }

    Set-Location $ProjectRoot
    if ($RuntimeMode) {
        Stop-Transcript | Out-Null
    }
}

Write-Host ""
Write-Host "========================================"
Write-Host "SMA Crossover backtest completed."
Write-Host "========================================"
