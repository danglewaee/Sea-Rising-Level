param(
    [Parameter(Mandatory=$false)][string]$NoaaStation = "1612340",
    [Parameter(Mandatory=$false)][string]$BeginDate = "20100101",
    [Parameter(Mandatory=$false)][string]$EndDate = "20241231",
    [Parameter(Mandatory=$false)][string]$SeaCsv = "data/honolulu_hourly.csv",
    [Parameter(Mandatory=$false)][string]$DemPath = "data/honolulu_dem.tif",
    [Parameter(Mandatory=$false)][string]$PopulationPath = "",
    [Parameter(Mandatory=$false)][string]$InfraPath = "",
    [Parameter(Mandatory=$false)][ValidateSet("lstm","temporal_cnn","axial_lstm")][string]$ModelType = "lstm",
    [Parameter(Mandatory=$false)][int]$Horizon = 6,
    [Parameter(Mandatory=$false)][string]$OutDir = "Backend/sea_level_risk/outputs",
    [Parameter(Mandatory=$false)][switch]$SkipDownload,
    [Parameter(Mandatory=$false)][switch]$ReuseModel
)

$ErrorActionPreference = "Stop"

if (Test-Path "Backend/.venv311/Scripts/python.exe") {
    $venvPython = "Backend/.venv311/Scripts/python.exe"
} elseif (Test-Path "Backend/.venv/Scripts/python.exe") {
    $venvPython = "Backend/.venv/Scripts/python.exe"
} else {
    throw "Khong tim thay virtual env. Hay chay: powershell -ExecutionPolicy Bypass -File Backend/setup_py311_env.ps1"
}

if (-not $SkipDownload) {
    Write-Host "[1/3] Download NOAA data -> $SeaCsv"
    & $venvPython -m Backend.sea_level_risk.download_data noaa --station $NoaaStation --begin $BeginDate --end $EndDate --out $SeaCsv
    if ($LASTEXITCODE -ne 0) {
        throw "Download NOAA that bai (exit code: $LASTEXITCODE)"
    }
}

if (-not (Test-Path $SeaCsv)) {
    throw "Khong tim thay file sea-level CSV: $SeaCsv"
}
if (-not (Test-Path $DemPath)) {
    throw "Khong tim thay DEM raster: $DemPath"
}

Write-Host "[2/3] Kiem tra TensorFlow"
$tfCheck = & $venvPython -c "import importlib.util;print('OK' if importlib.util.find_spec('tensorflow') else 'MISSING')"
if ($tfCheck -ne "OK") {
    Write-Host "TensorFlow chua duoc cai trong env hien tai."
    Write-Host "Hay chay: powershell -ExecutionPolicy Bypass -File Backend/setup_py311_env.ps1"
    exit 2
}

Write-Host "[3/3] Chay full pipeline"
$cmd = @(
    "-m", "Backend.sea_level_risk.run_pipeline",
    "--csv", $SeaCsv,
    "--dem", $DemPath,
    "--value-col", "sea_level",
    "--time-col", "timestamp",
    "--model-type", $ModelType,
    "--horizon", "$Horizon",
    "--out", $OutDir
)
if ($ReuseModel) {
    $cmd += "--reuse-model"
}
if ($PopulationPath -ne "") {
    $cmd += @("--population", $PopulationPath)
}
if ($InfraPath -ne "") {
    $cmd += @("--infra", $InfraPath)
}

& $venvPython @cmd
if ($LASTEXITCODE -ne 0) {
    throw "Pipeline that bai (exit code: $LASTEXITCODE)"
}

Write-Host "Hoan tat. Kiem tra output tai: $OutDir"
