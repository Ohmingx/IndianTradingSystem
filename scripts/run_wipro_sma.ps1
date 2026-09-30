param(
    [string]$LeanRoot = "D:\LeanT\Lean",
    [int]$TimeoutSeconds = 600,
    [string]$AlgoName = "wipro_sma_algorithm.py",
    [string]$AlgoTypeName = "WiproSmaAlgorithm"
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

# Verify WIPRO.NS ZIP exists
$DailyDataDir = Join-Path $DataDir "equity\india\daily"
$WiproZip = Join-Path $DailyDataDir "wipro.ns.zip"

if (-not (Test-Path $WiproZip)) {
    throw "Missing LEAN ZIP for WIPRO.NS: $WiproZip. Run prepare_wipro.py first."
}

Write-Host ""
Write-Host "=========================================="
Write-Host "  WIPRO.NS SMA CROSSOVER LEAN BACKTEST"
Write-Host "=========================================="
Write-Host ""
Write-Host "WIPRO.NS ZIP verified: $WiproZip"

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

$ConfigJson | ConvertTo-Json -Depth 10 | Out-File -FilePath $TempConfigPath -Encoding UTF8

Write-Host "Generated config: $TempConfigPath"
Write-Host ""

# Show data folder contents
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

    Write-Host "Starting LEAN engine for WIPRO.NS SMA backtest..."
    Write-Host "Timeout: $TimeoutSeconds seconds"
    Write-Host ""

    $StartInfo = New-Object System.Diagnostics.ProcessStartInfo

    $StartInfo.FileName = $LauncherExe
    $StartInfo.WorkingDirectory = $LauncherDir
    $StartInfo.UseShellExecute = $false
    $StartInfo.CreateNoWindow = $true

    $Process = New-Object System.Diagnostics.Process
    $Process.StartInfo = $StartInfo

    Write-Host "Launching:"
    Write-Host $LauncherExe
    Write-Host ""

    [void]$Process.Start()

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

        if ($LogContent -match "Analysis Completed and Results Posted") {
            $Completed = $true
            break
        }
    }

    if (-not $Completed) {

        Write-Host ""
        Write-Host "LEAN did not report completion within $TimeoutSeconds seconds."
        Write-Host "Stopping LEAN..."

        if ($Process -and -not $Process.HasExited) {
            try {
                $Process.Kill($true)
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

    $AlgorithmLogPath = Get-ChildItem -Path (Join-Path $LauncherDir "results") -Filter "*-log.txt" |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if ($AlgorithmLogPath) {
        Write-Host ""
        Write-Host "========== WIPRO SMA ALGORITHM LOG =========="
        Get-Content $AlgorithmLogPath.FullName
    }

    # --------------------------------------------------------
    # Stop launcher if still alive
    # --------------------------------------------------------

    if ($Process -and -not $Process.HasExited) {
        Write-Host ""
        Write-Host "LEAN engine finished. Stopping launcher process..."
        try {
            $Process.Kill($true)
            $Process.WaitForExit(5000)
        }
        catch {
            Write-Warning "Launcher process could not be terminated automatically."
        }
    }

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
            $Process.Kill($true)
            $Process.WaitForExit(5000)
        }
        catch {
        }
    }

    Set-Location $ProjectRoot
}

Write-Host ""
Write-Host "=========================================="
Write-Host "  WIPRO.NS SMA backtest completed."
Write-Host "  Check results\ folder for JSON output."
Write-Host "=========================================="
