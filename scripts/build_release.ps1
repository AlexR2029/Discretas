$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$pythonCommand = $null

if (Test-Path -LiteralPath $venvPython) {
    try {
        & $venvPython -c "import sys" 2>$null
        if ($LASTEXITCODE -eq 0) {
            $pythonCommand = $venvPython
        }
    } catch {
        $pythonCommand = $null
    }
}

if (-not $pythonCommand) {
    $pythonEntry = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonEntry) {
        try {
            & $pythonEntry.Source -c "import sys" 2>$null
            if ($LASTEXITCODE -eq 0) {
                $pythonCommand = $pythonEntry.Source
            }
        } catch {
            $pythonCommand = $null
        }
    }
}

if (-not $pythonCommand) {
    throw "No hay un intérprete Python funcional. Instala Python 3.11+ y vuelve a crear .venv."
}

$versionText = (& $pythonCommand -c "import sys; print('.'.join(map(str, sys.version_info[:3])))").Trim()
$pythonVersion = [version]$versionText
if ($pythonVersion -lt [version]"3.11") {
    throw "Se requiere Python 3.11 o superior; se encontró $versionText."
}

$requirementsPath = Join-Path $projectRoot "requirements.txt"
if (-not (Test-Path -LiteralPath $requirementsPath)) {
    throw "No existe requirements.txt en la raíz del proyecto."
}
$requirements = Get-Content -LiteralPath $requirementsPath
foreach ($package in @("mysql-connector-python", "pyinstaller")) {
    $pinned = $requirements | Where-Object {
        $_ -match "^\s*$([regex]::Escape($package))==\d+(\.\d+)+\s*$"
    }
    if (-not $pinned) {
        throw "Falta fijar la versión exacta de $package en requirements.txt antes de compilar."
    }
}

& $pythonCommand -c "import tkinter; import mysql.connector; import PyInstaller"
if ($LASTEXITCODE -ne 0) {
    throw "Faltan dependencias de ejecución o empaquetado. Instala las versiones de requirements.txt en .venv."
}

$releaseRoot = Join-Path $projectRoot "docs\release"
$distPath = Join-Path $releaseRoot "dist"
$workPath = Join-Path $releaseRoot "build"
New-Item -ItemType Directory -Force -Path $releaseRoot, $distPath, $workPath | Out-Null

$entryPoint = Join-Path $projectRoot "main.py"
if (-not (Test-Path -LiteralPath $entryPoint)) {
    throw "No se encuentra main.py."
}

& $pythonCommand -m PyInstaller `
    --noconfirm `
    --onefile `
    --windowed `
    --name NormalizadorBD `
    --distpath $distPath `
    --workpath $workPath `
    --specpath $releaseRoot `
    $entryPoint

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller terminó con error $LASTEXITCODE."
}

Write-Output "Ejecutable generado: $(Join-Path $distPath 'NormalizadorBD.exe')"
