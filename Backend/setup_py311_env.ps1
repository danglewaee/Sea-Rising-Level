param(
    [Parameter(Mandatory=$false)][string]$VenvPath = "Backend/.venv311"
)

$ErrorActionPreference = "Stop"

function Get-Python311Path {
    try {
        $null = & py -3.11 -V
        if ($LASTEXITCODE -eq 0) {
            $pyExe = & py -3.11 -c "import sys; print(sys.executable)"
            if ($pyExe) { return $pyExe.Trim() }
        }
    } catch {}

    $candidates = @(
        "C:\Python311\python.exe",
        "$env:LocalAppData\Programs\Python\Python311\python.exe",
        "$env:ProgramFiles\Python311\python.exe",
        "$env:ProgramFiles(x86)\Python311\python.exe"
    )
    foreach ($p in $candidates) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

$py311 = Get-Python311Path
if (-not $py311) {
    Write-Host "Python 3.11 chua co. Thu cai bang Chocolatey..."
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        choco install python311 -y --no-progress
        $py311 = Get-Python311Path
    }
}

if (-not $py311) {
    Write-Host "Khong the tu dong cai Python 3.11."
    Write-Host "Hay cai thu cong tai: https://www.python.org/downloads/release/python-3119/"
    Write-Host "Sau do chay lai script nay."
    exit 1
}

Write-Host "Dung Python: $py311"

if (-not (Test-Path $VenvPath)) {
    & $py311 -m venv $VenvPath
}

$venvPython = Join-Path $VenvPath "Scripts/python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Khong tao duoc venv tai: $VenvPath"
}

& $venvPython -m pip install --upgrade pip setuptools wheel
& $venvPython -m pip install -r Backend/requirements-ml.txt

Write-Host "Setup hoan tat. Dung interpreter: $venvPython"
Write-Host "Kiem tra nhanh:"
& $venvPython -c "import tensorflow as tf; print('tensorflow', tf.__version__)"
